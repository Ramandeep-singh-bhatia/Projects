"""
Reading Journal Service - Enhanced note-taking and AI insights.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import AsyncAnthropic
from ..database.database import execute_query


class ReadingJournalService:
    """Service for reading journal and notes."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize reading journal service."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None

    def add_note(
        self,
        book_id: int,
        content: str,
        note_type: str = "thought",
        page_number: Optional[int] = None,
        chapter: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Add a reading note.

        Args:
            book_id: Book ID
            content: Note content
            note_type: Type of note (thought, quote, question, reaction, analysis)
            page_number: Optional page number
            chapter: Optional chapter name
            tags: Optional tags

        Returns:
            Note ID
        """
        query = """
            INSERT INTO reading_notes
            (book_id, note_type, content, page_number, chapter, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """

        tags_json = json.dumps(tags) if tags else None

        params = (book_id, note_type, content, page_number, chapter, tags_json)

        return execute_query(query, params)

    def get_notes_for_book(
        self,
        book_id: int,
        note_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all notes for a book.

        Args:
            book_id: Book ID
            note_type: Optional filter by note type

        Returns:
            List of notes
        """
        if note_type:
            query = """
                SELECT * FROM reading_notes
                WHERE book_id = ? AND note_type = ?
                ORDER BY page_number ASC, created_date ASC
            """
            params = (book_id, note_type)
        else:
            query = """
                SELECT * FROM reading_notes
                WHERE book_id = ?
                ORDER BY page_number ASC, created_date ASC
            """
            params = (book_id,)

        notes = execute_query(query, params)

        # Parse tags JSON
        for note in notes:
            if note.get('tags'):
                note['tags'] = json.loads(note['tags'])

        return notes

    def update_note(self, note_id: int, updates: Dict[str, Any]) -> bool:
        """Update a note."""
        fields = []
        values = []

        for key, value in updates.items():
            if key in ['content', 'note_type', 'page_number', 'chapter', 'is_favorite']:
                if key == 'tags' and isinstance(value, list):
                    value = json.dumps(value)
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return False

        values.append(note_id)

        query = f"""
            UPDATE reading_notes
            SET {', '.join(fields)}
            WHERE id = ?
        """

        execute_query(query, tuple(values))
        return True

    def delete_note(self, note_id: int) -> bool:
        """Delete a note."""
        execute_query("DELETE FROM reading_notes WHERE id = ?", (note_id,))
        return True

    async def analyze_notes(self, book_id: int) -> Optional[Dict[str, Any]]:
        """
        Analyze all notes for a book using AI.

        Args:
            book_id: Book ID

        Returns:
            AI analysis of notes
        """
        if not self.client:
            return None

        notes = self.get_notes_for_book(book_id)

        if not notes:
            return {"message": "No notes to analyze"}

        # Get book info
        book_query = "SELECT * FROM books WHERE id = ?"
        book = execute_query(book_query, (book_id,))[0]

        # Format notes for AI
        formatted_notes = self._format_notes_for_ai(notes)

        prompt = f"""Analyze these reading notes for: "{book['title']}" by {book['author']}

**Notes:**
{formatted_notes}

**Task:**
Provide a comprehensive analysis of the reader's journey through this book:

1. **Thought Evolution**: How did their understanding/feelings change throughout?
2. **Key Themes**: What themes resonated most with them?
3. **Emotional Journey**: Track their emotional responses
4. **Insights**: What did they learn or discover?
5. **Connections**: Any patterns or recurring thoughts?

**Output Format (JSON):**
```json
{{
  "thought_evolution": "How their thinking evolved chapter by chapter",
  "key_themes_identified": ["theme 1", "theme 2", "theme 3"],
  "emotional_arc": "Description of their emotional journey",
  "deepest_insights": ["insight 1", "insight 2"],
  "memorable_moments": ["What stood out most"],
  "reading_experience_summary": "Overall summary of their reading experience",
  "suggested_reflections": ["Question 1 to ponder", "Question 2 to ponder"]
}}
```

Return ONLY valid JSON."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]

            return json.loads(json_str)

        except Exception as e:
            print(f"Error analyzing notes: {e}")
            return None

    def get_favorite_notes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get favorite notes across all books."""
        query = """
            SELECT rn.*, b.title, b.author
            FROM reading_notes rn
            JOIN books b ON rn.book_id = b.id
            WHERE rn.is_favorite = 1
            ORDER BY rn.created_date DESC
            LIMIT ?
        """

        notes = execute_query(query, (limit,))

        for note in notes:
            if note.get('tags'):
                note['tags'] = json.loads(note['tags'])

        return notes

    def search_notes(
        self,
        query_text: str,
        note_type: Optional[str] = None,
        tag: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search notes by content, type, or tag.

        Args:
            query_text: Search query
            note_type: Optional filter by type
            tag: Optional filter by tag

        Returns:
            Matching notes
        """
        base_query = """
            SELECT rn.*, b.title, b.author
            FROM reading_notes rn
            JOIN books b ON rn.book_id = b.id
            WHERE rn.content LIKE ?
        """

        params = [f"%{query_text}%"]

        if note_type:
            base_query += " AND rn.note_type = ?"
            params.append(note_type)

        if tag:
            base_query += " AND rn.tags LIKE ?"
            params.append(f"%{tag}%")

        base_query += " ORDER BY rn.created_date DESC LIMIT 100"

        notes = execute_query(base_query, tuple(params))

        for note in notes:
            if note.get('tags'):
                note['tags'] = json.loads(note['tags'])

        return notes

    def get_notes_by_theme(self, theme: str) -> List[Dict[str, Any]]:
        """Get all notes tagged with a specific theme."""
        query = """
            SELECT rn.*, b.title, b.author
            FROM reading_notes rn
            JOIN books b ON rn.book_id = b.id
            WHERE rn.tags LIKE ?
            ORDER BY b.title, rn.page_number
        """

        notes = execute_query(query, (f"%{theme}%",))

        for note in notes:
            if note.get('tags'):
                note['tags'] = json.loads(note['tags'])

        return notes

    def get_journal_statistics(self) -> Dict[str, Any]:
        """Get statistics about journaling activity."""
        # Total notes
        total_query = "SELECT COUNT(*) as count FROM reading_notes"
        total = execute_query(total_query)[0]['count']

        # By type
        type_query = """
            SELECT note_type, COUNT(*) as count
            FROM reading_notes
            GROUP BY note_type
        """
        by_type = execute_query(type_query)

        # Books with notes
        books_query = """
            SELECT COUNT(DISTINCT book_id) as count
            FROM reading_notes
        """
        books_with_notes = execute_query(books_query)[0]['count']

        # Most common tags
        tag_query = "SELECT tags FROM reading_notes WHERE tags IS NOT NULL"
        all_tags = execute_query(tag_query)

        tag_counts = {}
        for row in all_tags:
            tags = json.loads(row['tags']) if row['tags'] else []
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return {
            "total_notes": total,
            "by_type": {row['note_type']: row['count'] for row in by_type},
            "books_with_notes": books_with_notes,
            "top_tags": [{"tag": tag, "count": count} for tag, count in top_tags],
            "favorite_count": sum(1 for row in by_type if row.get('is_favorite'))
        }

    def _format_notes_for_ai(self, notes: List[Dict[str, Any]]) -> str:
        """Format notes for AI analysis."""
        formatted = []

        for note in notes:
            note_str = f"[{note['note_type'].upper()}]"

            if note.get('page_number'):
                note_str += f" (Page {note['page_number']})"

            if note.get('chapter'):
                note_str += f" ({note['chapter']})"

            note_str += f": {note['content']}"

            if note.get('tags'):
                tags = json.loads(note['tags']) if isinstance(note['tags'], str) else note['tags']
                note_str += f" [Tags: {', '.join(tags)}]"

            formatted.append(note_str)

        return "\n\n".join(formatted)
