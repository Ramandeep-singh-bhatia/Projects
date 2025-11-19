"""
Book Evaluation Service
Implements "Should I Read This?" intelligent book readiness assessment
"""
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from anthropic import Anthropic


class BookEvaluationService:
    """Service for evaluating book readiness and generating preparation paths"""

    def __init__(self, db_path: str, anthropic_client: Optional[Anthropic] = None):
        self.db_path = db_path
        self.client = anthropic_client

    async def evaluate_readiness(self, book_id: int) -> Dict[str, Any]:
        """
        Evaluate if user is ready to read this book

        Args:
            book_id: Book to evaluate

        Returns:
            Comprehensive readiness assessment with score 0-100 and recommendation
        """
        if not self.client:
            raise ValueError("Anthropic client not initialized")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get book details and analysis
            cursor.execute("""
                SELECT b.title, b.author, b.genre, b.description, b.page_count,
                       ba.complexity_score, ba.themes, ba.mood_tags,
                       ba.reader_level, ba.character_vs_plot_score
                FROM books b
                LEFT JOIN book_analysis ba ON b.id = ba.book_id
                WHERE b.id = ?
            """, (book_id,))

            book_row = cursor.fetchone()
            if not book_row:
                raise ValueError(f"Book {book_id} not found")

            book_info = {
                'title': book_row[0],
                'author': book_row[1],
                'genre': book_row[2],
                'description': book_row[3],
                'page_count': book_row[4],
                'complexity_score': book_row[5],
                'themes': json.loads(book_row[6]) if book_row[6] else [],
                'mood_tags': json.loads(book_row[7]) if book_row[7] else {},
                'reader_level': book_row[8],
                'character_vs_plot_score': book_row[9]
            }

            # Get user's reading DNA
            reading_dna = self._get_reading_dna(cursor)

            # Get reading history
            reading_history = self._get_reading_history(cursor)

            # Build evaluation prompt
            prompt = self._build_evaluation_prompt(book_info, reading_dna, reading_history)

            # Call Claude API
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse the response
            evaluation_text = response.content[0].text
            evaluation = json.loads(evaluation_text)

            # Track this evaluation
            self._track_evaluation(cursor, book_id, evaluation)

            conn.commit()

            return evaluation

        finally:
            conn.close()

    def _build_evaluation_prompt(
        self, book_info: Dict[str, Any], reading_dna: Dict[str, Any],
        reading_history: List[Dict[str, Any]]
    ) -> str:
        """Build AI prompt for book readiness evaluation"""
        return f"""Evaluate if this reader is ready for this book right now.

**BOOK TO EVALUATE:**
- Title: {book_info['title']}
- Author: {book_info['author']}
- Genre: {book_info['genre']}
- Complexity: {book_info.get('complexity_score', 'Unknown')}/10
- Reader Level: {book_info.get('reader_level', 'Unknown')}
- Themes: {', '.join(book_info.get('themes', []))}
- Character vs Plot: {book_info.get('character_vs_plot_score', 0)}
- Description: {book_info.get('description', 'No description')}

**READER PROFILE:**
Reading DNA:
- Complexity Comfort: {reading_dna.get('complexity_comfort_level', 5)}/10
- Character vs Plot Preference: {reading_dna.get('character_vs_plot_score', 0)}
- Favorite Themes: {', '.join(reading_dna.get('favorite_themes', []))}
- Pacing Preference: {reading_dna.get('pacing_preference', 'Unknown')}

Recent Reading History:
{self._format_history_for_prompt(reading_history)}

**EVALUATION CRITERIA:**

Analyze and provide a JSON response with:

1. **readiness_score** (integer 0-100):
   - 75-100: Ready now
   - 50-74: Maybe later (close but missing something)
   - 25-49: Not yet (significant gaps)
   - 0-24: Different direction (poor match)

2. **recommendation_type** (string): "read_now", "maybe_later", "not_yet", or "different_direction"

3. **factors_breakdown** (object with scores 0-100):
   - complexity_match: How well book complexity matches reader's comfort level
   - interest_alignment: How well themes align with reader's interests
   - completion_likelihood: Probability reader will finish the book
   - enjoyment_potential: Expected enjoyment level
   - growth_opportunity: How much this book will expand reader's horizons

4. **gaps_identified** (array of strings): What's missing for ideal readiness

5. **strengths** (array of strings): What makes this a good potential match

6. **detailed_reasoning** (string): 2-3 sentences explaining the assessment

7. **preparation_needed** (boolean): Whether a preparation plan would help

8. **estimated_ready_in_days** (integer or null): Days until reader might be ready (if not ready now)

9. **quick_wins** (array of strings): 1-2 book suggestions that would help bridge gaps

10. **alternative_suggestions** (array of strings): If "different_direction", suggest 2-3 better-matched books

Example response:
{{
  "readiness_score": 82,
  "recommendation_type": "read_now",
  "factors_breakdown": {{
    "complexity_match": 85,
    "interest_alignment": 90,
    "completion_likelihood": 75,
    "enjoyment_potential": 85,
    "growth_opportunity": 70
  }},
  "gaps_identified": ["Limited experience with non-linear narratives"],
  "strengths": ["Strong thematic alignment", "Comfortable complexity level"],
  "detailed_reasoning": "This book aligns perfectly with your love of character-driven stories and explores themes you've enjoyed before. The complexity is just right for your current comfort level.",
  "preparation_needed": false,
  "estimated_ready_in_days": null,
  "quick_wins": [],
  "alternative_suggestions": []
}}

Return ONLY the JSON object, no additional text."""

    def _format_history_for_prompt(self, history: List[Dict[str, Any]]) -> str:
        """Format reading history for the prompt"""
        if not history:
            return "No reading history yet"

        lines = []
        for book in history[:10]:  # Last 10 books
            lines.append(
                f"- {book['title']} by {book['author']} "
                f"({book['genre']}, complexity {book.get('complexity', '?')}/10) "
                f"- Rating: {book['rating']}/5"
            )
        return '\n'.join(lines)

    def _get_reading_dna(self, cursor) -> Dict[str, Any]:
        """Get user's reading DNA profile"""
        cursor.execute("""
            SELECT character_vs_plot_score, pacing_preference,
                   complexity_comfort_level, favorite_themes
            FROM reading_dna_profile
            ORDER BY generated_date DESC
            LIMIT 1
        """)

        row = cursor.fetchone()
        if not row:
            return {
                'character_vs_plot_score': 0,
                'pacing_preference': 'medium',
                'complexity_comfort_level': 5,
                'favorite_themes': []
            }

        return {
            'character_vs_plot_score': row[0],
            'pacing_preference': row[1],
            'complexity_comfort_level': row[2],
            'favorite_themes': json.loads(row[3]) if row[3] else []
        }

    def _get_reading_history(self, cursor) -> List[Dict[str, Any]]:
        """Get user's reading history"""
        cursor.execute("""
            SELECT b.title, b.author, b.genre, rl.rating,
                   ba.complexity_score, ba.themes
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            LEFT JOIN book_analysis ba ON b.id = ba.book_id
            WHERE rl.status = 'completed'
            ORDER BY rl.date_completed DESC
            LIMIT 20
        """)

        history = []
        for row in cursor.fetchall():
            history.append({
                'title': row[0],
                'author': row[1],
                'genre': row[2],
                'rating': row[3],
                'complexity': row[4],
                'themes': json.loads(row[5]) if row[5] else []
            })

        return history

    def _track_evaluation(self, cursor, book_id: int, evaluation: Dict[str, Any]):
        """Track the evaluation interaction"""
        cursor.execute("""
            INSERT INTO book_interactions
            (book_id, interaction_type, interaction_context)
            VALUES (?, 'evaluated', ?)
        """, (book_id, json.dumps({
            'readiness_score': evaluation['readiness_score'],
            'recommendation_type': evaluation['recommendation_type']
        })))

    async def add_to_future_reads(
        self, book_id: int, evaluation: Dict[str, Any],
        user_notes: Optional[str] = None,
        reminder_preference: str = 'when_ready'
    ) -> int:
        """
        Add book to Future Reads list for later

        Args:
            book_id: Book to add
            evaluation: The evaluation result
            user_notes: Optional user notes
            reminder_preference: When to remind user

        Returns:
            Future reads ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Calculate estimated ready date
            estimated_days = evaluation.get('estimated_ready_in_days', 90)
            estimated_date = datetime.now() + timedelta(days=estimated_days) if estimated_days else None

            cursor.execute("""
                INSERT INTO future_reads
                (book_id, current_readiness_score, target_readiness_score,
                 estimated_ready_date, reason_deferred, user_notes, reminder_preference)
                VALUES (?, ?, 75, ?, ?, ?, ?)
            """, (
                book_id,
                evaluation['readiness_score'],
                estimated_date.date() if estimated_date else None,
                evaluation['detailed_reasoning'],
                user_notes,
                reminder_preference
            ))

            future_read_id = cursor.lastrowid

            # Create initial checkpoint
            cursor.execute("""
                INSERT INTO readiness_checkpoints
                (future_read_id, readiness_score, factors_assessed, gaps_identified, ai_insights)
                VALUES (?, ?, ?, ?, ?)
            """, (
                future_read_id,
                evaluation['readiness_score'],
                json.dumps(evaluation['factors_breakdown']),
                json.dumps(evaluation['gaps_identified']),
                evaluation['detailed_reasoning']
            ))

            conn.commit()

            return future_read_id

        finally:
            conn.close()

    async def generate_preparation_plan(
        self, book_id: int, evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a reading plan to prepare user for a challenging book

        Args:
            book_id: Target book
            evaluation: The evaluation result

        Returns:
            Preparation plan with recommended books
        """
        if not self.client:
            raise ValueError("Anthropic client not initialized")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get book info
            cursor.execute("""
                SELECT b.title, b.author, b.genre,
                       ba.complexity_score, ba.themes, ba.reader_level
                FROM books b
                LEFT JOIN book_analysis ba ON b.id = ba.book_id
                WHERE b.id = ?
            """, (book_id,))

            book_row = cursor.fetchone()

            prompt = f"""Create a preparation reading plan to help a reader become ready for this book:

**TARGET BOOK:**
- Title: {book_row[0]}
- Author: {book_row[1]}
- Genre: {book_row[2]}
- Complexity: {book_row[3]}/10
- Reader Level: {book_row[5]}
- Themes: {json.loads(book_row[4]) if book_row[4] else []}

**CURRENT READINESS:**
- Score: {evaluation['readiness_score']}/100
- Gaps: {', '.join(evaluation['gaps_identified'])}

**TASK:**
Create a 3-4 book reading plan that bridges the gaps. Each book should:
1. Be slightly easier than the target book
2. Address one or more identified gaps
3. Build progressively toward the target

Return JSON:
{{
  "plan_name": "Preparation for [Book Title]",
  "duration_days": 60,
  "recommended_books": [
    {{
      "title": "Book Title",
      "author": "Author Name",
      "why_this_helps": "Explanation",
      "sequence_order": 1
    }}
  ],
  "milestones": ["After book 1: ...", "After book 2: ..."]
}}

Return ONLY the JSON object."""

            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            plan = json.loads(response.content[0].text)

            # Save the plan
            cursor.execute("""
                INSERT INTO reading_plans
                (plan_name, goal, duration_days, difficulty_progression, ai_reasoning)
                VALUES (?, ?, ?, 'progressive', ?)
            """, (
                plan['plan_name'],
                f"Prepare for reading: {book_row[0]}",
                plan['duration_days'],
                json.dumps(plan['milestones'])
            ))

            plan_id = cursor.lastrowid

            # Link to future read
            cursor.execute("""
                UPDATE future_reads
                SET preparation_plan_id = ?, status = 'preparing'
                WHERE book_id = ?
            """, (plan_id, book_id))

            conn.commit()

            plan['plan_id'] = plan_id
            return plan

        finally:
            conn.close()

    async def check_readiness_updates(self) -> List[Dict[str, Any]]:
        """
        Check all future reads for readiness updates

        Returns:
            List of books that are now ready or have improved readiness
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get all active future reads
            cursor.execute("""
                SELECT fr.id, fr.book_id, fr.current_readiness_score,
                       b.title, b.author
                FROM future_reads fr
                JOIN books b ON fr.book_id = b.id
                WHERE fr.status IN ('waiting', 'preparing')
                AND (fr.last_checked IS NULL OR fr.last_checked < datetime('now', '-7 days'))
            """)

            updates = []

            for row in cursor.fetchall():
                future_read_id, book_id, old_score, title, author = row

                # Re-evaluate readiness
                evaluation = await self.evaluate_readiness(book_id)
                new_score = evaluation['readiness_score']

                # Create new checkpoint
                cursor.execute("""
                    INSERT INTO readiness_checkpoints
                    (future_read_id, readiness_score, factors_assessed,
                     gaps_identified, progress_since_last, ai_insights)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    future_read_id,
                    new_score,
                    json.dumps(evaluation['factors_breakdown']),
                    json.dumps(evaluation['gaps_identified']),
                    new_score - old_score,
                    evaluation['detailed_reasoning']
                ))

                # Update future read
                new_status = 'ready' if new_score >= 75 else 'waiting'
                cursor.execute("""
                    UPDATE future_reads
                    SET current_readiness_score = ?, last_checked = datetime('now'), status = ?
                    WHERE id = ?
                """, (new_score, new_status, future_read_id))

                if new_score >= 75 or (new_score - old_score) >= 10:
                    updates.append({
                        'book_id': book_id,
                        'title': title,
                        'author': author,
                        'old_score': old_score,
                        'new_score': new_score,
                        'status': new_status,
                        'message': self._generate_update_message(old_score, new_score)
                    })

            conn.commit()

            return updates

        finally:
            conn.close()

    def _generate_update_message(self, old_score: int, new_score: int) -> str:
        """Generate a message about readiness change"""
        diff = new_score - old_score

        if new_score >= 75:
            return f"🎉 You're ready! Readiness improved from {old_score} to {new_score}."
        elif diff >= 15:
            return f"📈 Great progress! Readiness increased by {diff} points to {new_score}."
        elif diff >= 10:
            return f"✨ Making progress! Readiness now at {new_score} (+{diff})."
        else:
            return f"Readiness updated: {new_score} (was {old_score})."

    def get_future_reads(
        self, status: Optional[str] = None, min_readiness: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get future reads list with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            query = """
                SELECT fr.id, b.id, b.title, b.author, b.genre, b.cover_url,
                       fr.current_readiness_score, fr.estimated_ready_date,
                       fr.status, fr.user_notes, fr.recommended_by,
                       fr.preparation_plan_id
                FROM future_reads fr
                JOIN books b ON fr.book_id = b.id
                WHERE 1=1
            """
            params = []

            if status:
                query += " AND fr.status = ?"
                params.append(status)

            if min_readiness is not None:
                query += " AND fr.current_readiness_score >= ?"
                params.append(min_readiness)

            query += " ORDER BY fr.current_readiness_score DESC, fr.added_date ASC"

            cursor.execute(query, params)

            books = []
            for row in cursor.fetchall():
                books.append({
                    'future_read_id': row[0],
                    'book_id': row[1],
                    'title': row[2],
                    'author': row[3],
                    'genre': row[4],
                    'cover_url': row[5],
                    'readiness_score': row[6],
                    'estimated_ready_date': row[7],
                    'status': row[8],
                    'notes': row[9],
                    'recommended_by': row[10],
                    'has_preparation_plan': row[11] is not None
                })

            return books

        finally:
            conn.close()


# Global instance
_evaluation_service: Optional[BookEvaluationService] = None


def init_evaluation_service(db_path: str, anthropic_client: Optional[Anthropic] = None):
    """Initialize the evaluation service"""
    global _evaluation_service
    _evaluation_service = BookEvaluationService(db_path, anthropic_client)


def get_evaluation_service() -> BookEvaluationService:
    """Get the global evaluation service instance"""
    if _evaluation_service is None:
        raise RuntimeError("Evaluation service not initialized")
    return _evaluation_service
