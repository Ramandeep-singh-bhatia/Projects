"""
Manual Book Entry Service
Handles manual book additions, batch imports, and AI analysis
"""
import json
import csv
import io
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from anthropic import Anthropic


class ManualEntryService:
    """Service for manually adding books and analyzing their impact on user profile"""

    def __init__(self, db_path: str, anthropic_client: Optional[Anthropic] = None):
        self.db_path = db_path
        self.client = anthropic_client

    def add_manual_book(
        self,
        book_data: Dict[str, Any],
        source: str,
        recommender_name: Optional[str] = None,
        why_read: Optional[str] = None,
        auto_analyze: bool = True
    ) -> Dict[str, Any]:
        """
        Add a book manually with metadata

        Args:
            book_data: Book information (title, author, isbn, etc.)
            source: Source of recommendation ('friend', 'online', 'bookstore', 'other')
            recommender_name: Name of person who recommended it
            why_read: Reason for wanting to read this book
            auto_analyze: Whether to run AI analysis immediately

        Returns:
            Dict with book_id and analysis status
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Check if book already exists by ISBN
            book_id = None
            if book_data.get('isbn'):
                cursor.execute("SELECT id FROM books WHERE isbn = ?", (book_data['isbn'],))
                result = cursor.fetchone()
                if result:
                    book_id = result[0]

            # If not found, create new book entry
            if not book_id:
                cursor.execute("""
                    INSERT INTO books (title, author, isbn, genre, page_count, cover_url,
                                     description, publication_year, snoisle_available)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                """, (
                    book_data['title'],
                    book_data['author'],
                    book_data.get('isbn'),
                    book_data.get('genre', 'Unknown'),
                    book_data.get('page_count'),
                    book_data.get('cover_url'),
                    book_data.get('description'),
                    book_data.get('publication_year')
                ))
                book_id = cursor.lastrowid

            # Track this as a manually added book
            cursor.execute("""
                INSERT INTO manually_added_books
                (book_id, source_of_recommendation, recommender_name, why_read, was_outside_comfort_zone)
                VALUES (?, ?, ?, ?, 0)
            """, (book_id, source, recommender_name, why_read))

            manual_entry_id = cursor.lastrowid

            # Track the interaction
            self._track_interaction(cursor, book_id, 'added_to_read', {
                'source': source,
                'manual_entry': True
            })

            conn.commit()

            # Run AI analysis if requested and client available
            analysis_result = None
            if auto_analyze and self.client:
                analysis_result = self.analyze_book(book_id, book_data)

            return {
                'book_id': book_id,
                'manual_entry_id': manual_entry_id,
                'analysis_completed': analysis_result is not None,
                'analysis': analysis_result
            }

        finally:
            conn.close()

    async def analyze_book(self, book_id: int, book_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Perform AI analysis on a book to understand its characteristics

        Args:
            book_id: Book ID to analyze
            book_data: Optional book data (if not provided, will fetch from DB)

        Returns:
            Analysis results with complexity, themes, moods, etc.
        """
        if not self.client:
            raise ValueError("Anthropic client not initialized")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Fetch book data if not provided
            if not book_data:
                cursor.execute("""
                    SELECT title, author, genre, description, page_count
                    FROM books WHERE id = ?
                """, (book_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Book {book_id} not found")

                book_data = {
                    'title': row[0],
                    'author': row[1],
                    'genre': row[2],
                    'description': row[3],
                    'page_count': row[4]
                }

            # Build AI prompt for book analysis
            prompt = self._build_analysis_prompt(book_data)

            # Call Claude API
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.6,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse the response
            analysis_text = response.content[0].text
            analysis = json.loads(analysis_text)

            # Store analysis in database
            cursor.execute("""
                INSERT OR REPLACE INTO book_analysis
                (book_id, complexity_score, themes, mood_tags, writing_style,
                 reader_level, content_warnings, character_vs_plot_score, narrative_structure)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                book_id,
                analysis['complexity_score'],
                json.dumps(analysis['themes']),
                json.dumps(analysis['mood_tags']),
                analysis['writing_style'],
                analysis['reader_level'],
                json.dumps(analysis.get('content_warnings', [])),
                analysis.get('character_vs_plot_score', 0.0),
                analysis.get('narrative_structure', '')
            ))

            # Mark manual entry as analyzed
            cursor.execute("""
                UPDATE manually_added_books
                SET ai_analysis_complete = 1
                WHERE book_id = ?
            """, (book_id,))

            conn.commit()

            return analysis

        finally:
            conn.close()

    def _build_analysis_prompt(self, book_data: Dict[str, Any]) -> str:
        """Build AI prompt for book analysis"""
        return f"""Analyze this book and provide detailed characteristics in JSON format:

**Book Details:**
- Title: {book_data['title']}
- Author: {book_data['author']}
- Genre: {book_data.get('genre', 'Unknown')}
- Description: {book_data.get('description', 'No description available')}
- Page Count: {book_data.get('page_count', 'Unknown')}

**Analysis Required:**

Provide a comprehensive analysis as a JSON object with these fields:

1. **complexity_score** (integer 1-10): Overall reading difficulty
2. **themes** (array of strings): 3-5 main themes explored
3. **mood_tags** (object):
   - energy: "light", "balanced", or "heavy"
   - pacing: "slow", "medium", or "fast"
   - tone: "dark", "balanced", or "hopeful"
   - complexity: "escapist", "medium", or "thought-provoking"
4. **writing_style** (string): Description of prose style
5. **reader_level** (string): "beginner", "intermediate", or "advanced"
6. **content_warnings** (array of strings): Any sensitive content
7. **character_vs_plot_score** (float -1 to 1): -1=plot-driven, 1=character-driven
8. **narrative_structure** (string): Linear, non-linear, multi-POV, etc.

Return ONLY the JSON object, no additional text.

Example:
{{
  "complexity_score": 6,
  "themes": ["identity", "family", "coming-of-age"],
  "mood_tags": {{
    "energy": "balanced",
    "pacing": "medium",
    "tone": "hopeful",
    "complexity": "medium"
  }},
  "writing_style": "lyrical and descriptive",
  "reader_level": "intermediate",
  "content_warnings": ["mild violence"],
  "character_vs_plot_score": 0.7,
  "narrative_structure": "linear with flashbacks"
}}"""

    async def batch_import_goodreads(self, csv_content: str) -> Dict[str, Any]:
        """
        Import books from Goodreads CSV export

        Args:
            csv_content: CSV file content as string

        Returns:
            Import statistics
        """
        reader = csv.DictReader(io.StringIO(csv_content))

        imported = 0
        skipped = 0
        analyzed = 0
        errors = []

        for row in reader:
            try:
                # Map Goodreads CSV columns to our format
                book_data = {
                    'title': row.get('Title', '').strip(),
                    'author': row.get('Author', '').strip(),
                    'isbn': row.get('ISBN13', '').strip() or row.get('ISBN', '').strip(),
                    'page_count': int(row.get('Number of Pages', 0)) if row.get('Number of Pages') else None,
                    'publication_year': int(row.get('Year Published', 0)) if row.get('Year Published') else None,
                    'genre': row.get('Bookshelves', 'Unknown').split(',')[0].strip(),
                    'description': ''
                }

                if not book_data['title'] or not book_data['author']:
                    skipped += 1
                    continue

                # Add the book
                result = self.add_manual_book(
                    book_data,
                    source='goodreads_import',
                    why_read=f"Imported from Goodreads - {row.get('Exclusive Shelf', 'to-read')}",
                    auto_analyze=True
                )

                imported += 1
                if result['analysis_completed']:
                    analyzed += 1

            except Exception as e:
                errors.append(f"Row error: {str(e)}")

        return {
            'total_processed': imported + skipped,
            'imported': imported,
            'skipped': skipped,
            'analyzed': analyzed,
            'errors': errors
        }

    async def calculate_profile_impact(self, book_id: int) -> Dict[str, Any]:
        """
        Calculate how adding this book affects the user's reading profile

        Args:
            book_id: Book to analyze impact for

        Returns:
            Impact analysis
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get book analysis
            cursor.execute("""
                SELECT complexity_score, themes, mood_tags, character_vs_plot_score
                FROM book_analysis
                WHERE book_id = ?
            """, (book_id,))

            analysis_row = cursor.fetchone()
            if not analysis_row:
                return {'error': 'Book not analyzed yet'}

            complexity = analysis_row[0]
            themes = json.loads(analysis_row[1])
            mood_tags = json.loads(analysis_row[2])
            char_plot = analysis_row[3]

            # Get user's reading history
            cursor.execute("""
                SELECT b.genre, ba.complexity_score, ba.themes
                FROM reading_log rl
                JOIN books b ON rl.book_id = b.id
                LEFT JOIN book_analysis ba ON b.id = ba.book_id
                WHERE rl.status = 'completed' AND rl.rating >= 4
            """)

            history = cursor.fetchall()

            if not history:
                return {
                    'is_new_territory': True,
                    'complexity_match': 'unknown',
                    'thematic_overlap': 0,
                    'recommendation': 'This will be your first highly-rated book! Great starting point.'
                }

            # Calculate impact
            avg_complexity = sum(h[1] for h in history if h[1]) / len([h for h in history if h[1]]) if history else 5

            complexity_diff = complexity - avg_complexity
            if complexity_diff > 2:
                complexity_match = 'challenging'
            elif complexity_diff < -2:
                complexity_match = 'easier'
            else:
                complexity_match = 'comfortable'

            # Check thematic overlap
            all_themes = []
            for h in history:
                if h[2]:
                    all_themes.extend(json.loads(h[2]))

            theme_overlap = len(set(themes) & set(all_themes))

            is_new_territory = theme_overlap == 0 and complexity_match == 'challenging'

            # Mark as outside comfort zone if applicable
            if is_new_territory or complexity_match == 'challenging':
                cursor.execute("""
                    UPDATE manually_added_books
                    SET was_outside_comfort_zone = 1, profile_impact_calculated = 1
                    WHERE book_id = ?
                """, (book_id,))
                conn.commit()

            return {
                'is_new_territory': is_new_territory,
                'complexity_match': complexity_match,
                'complexity_difference': round(complexity_diff, 1),
                'thematic_overlap': theme_overlap,
                'total_themes': len(set(all_themes)),
                'recommendation': self._generate_impact_recommendation(
                    is_new_territory, complexity_match, theme_overlap
                )
            }

        finally:
            conn.close()

    def _generate_impact_recommendation(
        self, is_new: bool, complexity: str, theme_overlap: int
    ) -> str:
        """Generate recommendation based on profile impact"""
        if is_new and complexity == 'challenging':
            return "This book is outside your comfort zone! Consider adding to Future Reads for preparation."
        elif complexity == 'challenging':
            return "This book is more complex than your usual reads. Great for growth!"
        elif theme_overlap > 3:
            return "This aligns well with your favorite themes. You'll likely enjoy it!"
        elif is_new:
            return "This explores new themes for you. Exciting territory to discover!"
        else:
            return "This seems like a comfortable match for your reading profile."

    def _track_interaction(
        self, cursor, book_id: int, interaction_type: str, context: Dict[str, Any]
    ):
        """Track book interaction in unified table"""
        cursor.execute("""
            INSERT INTO book_interactions
            (book_id, interaction_type, interaction_context)
            VALUES (?, ?, ?)
        """, (book_id, interaction_type, json.dumps(context)))

    def add_external_recommendation(
        self, book_id: int, recommender_type: str, recommender_name: str,
        context: Optional[str] = None, trust_score: float = 0.5
    ) -> int:
        """
        Track a book recommendation from an external source

        Args:
            book_id: Book being recommended
            recommender_type: Type of recommender
            recommender_name: Name of recommender
            context: Why they recommended it
            trust_score: How much you trust this recommender (0-1)

        Returns:
            Recommendation ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO external_recommendations
                (book_id, recommender_type, recommender_name, recommendation_context, trust_score)
                VALUES (?, ?, ?, ?, ?)
            """, (book_id, recommender_type, recommender_name, context, trust_score))

            rec_id = cursor.lastrowid
            conn.commit()

            return rec_id

        finally:
            conn.close()

    def get_manual_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all manually added books with their analysis status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT
                    b.id, b.title, b.author, b.genre,
                    m.source_of_recommendation, m.recommender_name, m.why_read,
                    m.added_date, m.ai_analysis_complete, m.was_outside_comfort_zone,
                    ba.complexity_score, ba.reader_level
                FROM manually_added_books m
                JOIN books b ON m.book_id = b.id
                LEFT JOIN book_analysis ba ON b.id = ba.book_id
                ORDER BY m.added_date DESC
                LIMIT ?
            """, (limit,))

            books = []
            for row in cursor.fetchall():
                books.append({
                    'book_id': row[0],
                    'title': row[1],
                    'author': row[2],
                    'genre': row[3],
                    'source': row[4],
                    'recommender': row[5],
                    'why_read': row[6],
                    'added_date': row[7],
                    'analyzed': bool(row[8]),
                    'outside_comfort_zone': bool(row[9]),
                    'complexity_score': row[10],
                    'reader_level': row[11]
                })

            return books

        finally:
            conn.close()


# Global instance
_manual_entry_service: Optional[ManualEntryService] = None


def init_manual_entry_service(db_path: str, anthropic_client: Optional[Anthropic] = None):
    """Initialize the manual entry service"""
    global _manual_entry_service
    _manual_entry_service = ManualEntryService(db_path, anthropic_client)


def get_manual_entry_service() -> ManualEntryService:
    """Get the global manual entry service instance"""
    if _manual_entry_service is None:
        raise RuntimeError("Manual entry service not initialized")
    return _manual_entry_service
