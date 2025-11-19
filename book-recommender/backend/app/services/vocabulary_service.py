"""
Vocabulary Builder Service - Track and learn new words from reading.
"""
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from ..database.database import execute_query


class VocabularyService:
    """Service for vocabulary tracking and learning."""

    def __init__(self):
        """Initialize vocabulary service."""
        self.dictionary_api = "https://api.dictionaryapi.dev/api/v2/entries/en"

    async def add_word(
        self,
        word: str,
        context_sentence: str,
        book_id: int,
        page_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add a new word to vocabulary.

        Args:
            word: The word to add
            context_sentence: Sentence where word was encountered
            book_id: Source book ID
            page_number: Optional page number

        Returns:
            Word entry with definition
        """
        word = word.lower().strip()

        # Check if word already exists
        existing = execute_query("SELECT * FROM vocabulary WHERE word = ?", (word,))

        if existing:
            return {
                "status": "already_exists",
                "word_id": existing[0]['id'],
                "word": existing[0]
            }

        # Fetch definition from API
        definition_data = await self._fetch_definition(word)

        # Insert into database
        query = """
            INSERT INTO vocabulary (
                word, definition, pronunciation, part_of_speech,
                context_sentence, book_id, page_number, next_review_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        next_review = (date.today() + timedelta(days=1)).isoformat()

        params = (
            word,
            definition_data.get('definition', 'Definition not found'),
            definition_data.get('pronunciation', ''),
            definition_data.get('part_of_speech', ''),
            context_sentence,
            book_id,
            page_number,
            next_review
        )

        word_id = execute_query(query, params)

        return {
            "status": "added",
            "word_id": word_id,
            "word": word,
            "definition": definition_data.get('definition'),
            "pronunciation": definition_data.get('pronunciation'),
            "next_review": next_review
        }

    async def _fetch_definition(self, word: str) -> Dict[str, Any]:
        """Fetch word definition from dictionary API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.dictionary_api}/{word}")

                if response.status_code == 200:
                    data = response.json()

                    if data and len(data) > 0:
                        entry = data[0]
                        meanings = entry.get('meanings', [])

                        if meanings:
                            first_meaning = meanings[0]
                            definitions = first_meaning.get('definitions', [])

                            definition_text = definitions[0].get('definition', '') if definitions else ''
                            part_of_speech = first_meaning.get('partOfSpeech', '')

                            # Get pronunciation
                            phonetics = entry.get('phonetics', [])
                            pronunciation = ''
                            for phonetic in phonetics:
                                if phonetic.get('text'):
                                    pronunciation = phonetic.get('text', '')
                                    break

                            return {
                                "definition": definition_text,
                                "part_of_speech": part_of_speech,
                                "pronunciation": pronunciation
                            }

        except Exception as e:
            print(f"Error fetching definition: {e}")

        return {
            "definition": "Definition not available",
            "part_of_speech": "",
            "pronunciation": ""
        }

    def get_words_for_review(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get words due for review today.

        Args:
            limit: Maximum number of words to return

        Returns:
            List of words due for review
        """
        query = """
            SELECT v.*, b.title as book_title
            FROM vocabulary v
            LEFT JOIN books b ON v.book_id = b.id
            WHERE v.next_review_date <= ? AND v.mastery_level != 'mastered'
            ORDER BY v.next_review_date ASC, v.times_reviewed ASC
            LIMIT ?
        """

        today = date.today().isoformat()
        return execute_query(query, (today, limit))

    def review_word(self, word_id: int, knew_it: bool) -> Dict[str, Any]:
        """
        Record a word review session.

        Args:
            word_id: Word ID being reviewed
            knew_it: Whether user knew the word

        Returns:
            Updated word info with next review date
        """
        # Get current word data
        word_data = execute_query("SELECT * FROM vocabulary WHERE id = ?", (word_id,))

        if not word_data:
            return {"error": "Word not found"}

        word = word_data[0]
        times_reviewed = word.get('times_reviewed', 0) + 1

        # Calculate next review interval using spaced repetition
        if knew_it:
            # Increase interval
            intervals = [1, 3, 7, 14, 30, 60]  # days
            current_interval_index = min(times_reviewed, len(intervals) - 1)
            next_interval = intervals[current_interval_index]

            # Update mastery level
            if times_reviewed >= 5:
                mastery_level = 'mastered'
            elif times_reviewed >= 2:
                mastery_level = 'familiar'
            else:
                mastery_level = 'learning'
        else:
            # Reset to 1 day
            next_interval = 1
            mastery_level = 'learning'

        next_review = (date.today() + timedelta(days=next_interval)).isoformat()

        # Update vocabulary entry
        update_query = """
            UPDATE vocabulary
            SET times_reviewed = ?,
                mastery_level = ?,
                next_review_date = ?
            WHERE id = ?
        """
        execute_query(update_query, (times_reviewed, mastery_level, next_review, word_id))

        # Log the review
        log_query = """
            INSERT INTO vocabulary_review_log (word_id, knew_it, review_interval_days)
            VALUES (?, ?, ?)
        """
        execute_query(log_query, (word_id, knew_it, next_interval))

        return {
            "word_id": word_id,
            "knew_it": knew_it,
            "times_reviewed": times_reviewed,
            "mastery_level": mastery_level,
            "next_review_date": next_review,
            "next_interval_days": next_interval
        }

    def get_vocabulary_stats(self) -> Dict[str, Any]:
        """
        Get vocabulary statistics.

        Returns:
            Stats about vocabulary learning
        """
        # Total words
        total_query = "SELECT COUNT(*) as count FROM vocabulary"
        total = execute_query(total_query)[0]['count']

        # By mastery level
        mastery_query = """
            SELECT mastery_level, COUNT(*) as count
            FROM vocabulary
            GROUP BY mastery_level
        """
        mastery_counts = execute_query(mastery_query)
        mastery_dict = {row['mastery_level']: row['count'] for row in mastery_counts}

        # Words due today
        due_query = """
            SELECT COUNT(*) as count
            FROM vocabulary
            WHERE next_review_date <= ? AND mastery_level != 'mastered'
        """
        due_today = execute_query(due_query, (date.today().isoformat(),))[0]['count']

        # Words by source book
        books_query = """
            SELECT b.title, COUNT(v.id) as word_count
            FROM vocabulary v
            JOIN books b ON v.book_id = b.id
            GROUP BY b.title
            ORDER BY word_count DESC
            LIMIT 5
        """
        top_books = execute_query(books_query)

        # Review streak
        streak = self._calculate_review_streak()

        return {
            "total_words": total,
            "mastery": {
                "learning": mastery_dict.get('learning', 0),
                "familiar": mastery_dict.get('familiar', 0),
                "mastered": mastery_dict.get('mastered', 0)
            },
            "due_today": due_today,
            "top_source_books": top_books,
            "review_streak_days": streak
        }

    def search_vocabulary(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search vocabulary by word or definition.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            Matching vocabulary entries
        """
        search_query = """
            SELECT v.*, b.title as book_title
            FROM vocabulary v
            LEFT JOIN books b ON v.book_id = b.id
            WHERE v.word LIKE ? OR v.definition LIKE ?
            ORDER BY v.word ASC
            LIMIT ?
        """

        search_term = f"%{query}%"
        return execute_query(search_query, (search_term, search_term, limit))

    def get_words_by_mastery(self, mastery_level: str) -> List[Dict[str, Any]]:
        """Get words filtered by mastery level."""
        query = """
            SELECT v.*, b.title as book_title
            FROM vocabulary v
            LEFT JOIN books b ON v.book_id = b.id
            WHERE v.mastery_level = ?
            ORDER BY v.date_encountered DESC
        """

        return execute_query(query, (mastery_level,))

    def _calculate_review_streak(self) -> int:
        """Calculate consecutive days with reviews."""
        query = """
            SELECT DISTINCT DATE(review_date) as review_date
            FROM vocabulary_review_log
            ORDER BY review_date DESC
            LIMIT 365
        """

        review_dates = execute_query(query)

        if not review_dates:
            return 0

        streak = 0
        expected_date = date.today()

        for row in review_dates:
            review_date = datetime.fromisoformat(row['review_date']).date()

            if review_date == expected_date:
                streak += 1
                expected_date = expected_date - timedelta(days=1)
            else:
                break

        return streak
