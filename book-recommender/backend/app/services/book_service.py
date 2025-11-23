"""
Book tracking CRUD service.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from ..database.database import execute_query
from ..models.book import (
    Book, BookCreate, ReadingLog, ReadingLogCreate,
    ReadingLogUpdate, ReadingStatus, BookWithReadingStatus
)


class BookService:
    """Service for managing books and reading logs."""

    @staticmethod
    def create_book(book_data: BookCreate) -> int:
        """
        Create a new book entry.

        Args:
            book_data: Book creation data

        Returns:
            Book ID
        """
        query = """
            INSERT INTO books (
                title, author, isbn, genre, page_count,
                cover_url, description, publication_year,
                snoisle_available, format_available
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            book_data.title,
            book_data.author,
            book_data.isbn,
            book_data.genre,
            book_data.page_count,
            book_data.cover_url,
            book_data.description,
            book_data.publication_year,
            book_data.snoisle_available,
            book_data.format_available
        )

        book_id = execute_query(query, params)
        return book_id

    @staticmethod
    def get_book_by_id(book_id: int) -> Optional[Dict[str, Any]]:
        """Get book by ID."""
        query = "SELECT * FROM books WHERE id = ?"
        results = execute_query(query, (book_id,))
        return results[0] if results else None

    @staticmethod
    def get_book_by_isbn(isbn: str) -> Optional[Dict[str, Any]]:
        """Get book by ISBN."""
        query = "SELECT * FROM books WHERE isbn = ?"
        results = execute_query(query, (isbn,))
        return results[0] if results else None

    @staticmethod
    def search_books(query_text: str, genre: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search books in the database.

        Args:
            query_text: Search query
            genre: Optional genre filter

        Returns:
            List of matching books
        """
        if genre:
            query = """
                SELECT * FROM books
                WHERE (title LIKE ? OR author LIKE ?) AND genre = ?
                ORDER BY created_at DESC
                LIMIT 50
            """
            params = (f"%{query_text}%", f"%{query_text}%", genre)
        else:
            query = """
                SELECT * FROM books
                WHERE title LIKE ? OR author LIKE ?
                ORDER BY created_at DESC
                LIMIT 50
            """
            params = (f"%{query_text}%", f"%{query_text}%")

        return execute_query(query, params)

    @staticmethod
    def get_all_books(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all books with pagination."""
        query = """
            SELECT * FROM books
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        return execute_query(query, (limit, offset))

    @staticmethod
    def update_book(book_id: int, update_data: Dict[str, Any]) -> bool:
        """Update book information."""
        fields = []
        values = []

        for key, value in update_data.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return False

        values.append(datetime.now())
        values.append(book_id)

        query = f"""
            UPDATE books
            SET {', '.join(fields)}, updated_at = ?
            WHERE id = ?
        """

        execute_query(query, tuple(values))
        return True

    @staticmethod
    def delete_book(book_id: int) -> bool:
        """Delete a book (and cascade delete reading logs)."""
        query = "DELETE FROM books WHERE id = ?"
        execute_query(query, (book_id,))
        return True

    # Reading Log operations

    @staticmethod
    def create_reading_log(log_data: ReadingLogCreate) -> int:
        """
        Create a reading log entry.

        Args:
            log_data: Reading log data

        Returns:
            Reading log ID
        """
        query = """
            INSERT INTO reading_log (
                book_id, status, date_started, date_completed,
                rating, reading_duration_days, format_used,
                personal_notes, ai_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            log_data.book_id,
            log_data.status.value,
            log_data.date_started,
            log_data.date_completed,
            log_data.rating,
            log_data.reading_duration_days,
            log_data.format_used,
            log_data.personal_notes,
            log_data.ai_summary
        )

        log_id = execute_query(query, params)
        return log_id

    @staticmethod
    def get_reading_log_by_book(book_id: int) -> Optional[Dict[str, Any]]:
        """Get reading log for a specific book."""
        query = "SELECT * FROM reading_log WHERE book_id = ? ORDER BY created_at DESC LIMIT 1"
        results = execute_query(query, (book_id,))
        return results[0] if results else None

    @staticmethod
    def get_reading_logs_by_status(status: ReadingStatus) -> List[Dict[str, Any]]:
        """Get all reading logs with a specific status."""
        query = """
            SELECT rl.*, b.*,
                   rl.id as log_id,
                   b.id as book_id
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = ?
            ORDER BY rl.updated_at DESC
        """
        return execute_query(query, (status.value,))

    @staticmethod
    def update_reading_log(log_id: int, update_data: ReadingLogUpdate) -> bool:
        """Update a reading log entry."""
        fields = []
        values = []

        update_dict = update_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            if value is not None:
                if key == 'status' and isinstance(value, ReadingStatus):
                    fields.append(f"{key} = ?")
                    values.append(value.value)
                else:
                    fields.append(f"{key} = ?")
                    values.append(value)

        if not fields:
            return False

        values.append(datetime.now())
        values.append(log_id)

        query = f"""
            UPDATE reading_log
            SET {', '.join(fields)}, updated_at = ?
            WHERE id = ?
        """

        execute_query(query, tuple(values))
        return True

    @staticmethod
    def get_all_reading_logs() -> List[Dict[str, Any]]:
        """Get all reading logs with book information."""
        query = """
            SELECT rl.*, b.*,
                   rl.id as log_id,
                   b.id as book_id
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            ORDER BY rl.updated_at DESC
        """
        return execute_query(query)

    @staticmethod
    def get_books_with_reading_status() -> List[Dict[str, Any]]:
        """Get all books with their reading status."""
        query = """
            SELECT b.*, rl.status, rl.rating, rl.date_started, rl.date_completed,
                   rl.id as reading_log_id
            FROM books b
            LEFT JOIN reading_log rl ON b.id = rl.book_id
            ORDER BY b.created_at DESC
        """
        return execute_query(query)

    @staticmethod
    def mark_book_completed(
        log_id: int,
        rating: int,
        personal_notes: Optional[str] = None
    ) -> bool:
        """
        Mark a book as completed.

        Args:
            log_id: Reading log ID
            rating: Book rating (1-5)
            personal_notes: Optional notes

        Returns:
            Success status
        """
        now = datetime.now()

        # Get the log to calculate reading duration
        query = "SELECT date_started FROM reading_log WHERE id = ?"
        results = execute_query(query, (log_id,))

        if not results:
            return False

        date_started = results[0].get('date_started')

        reading_duration = None
        if date_started:
            started = datetime.fromisoformat(date_started) if isinstance(date_started, str) else date_started
            duration = (now - started).days
            reading_duration = max(1, duration)  # At least 1 day

        # Update the log
        update_query = """
            UPDATE reading_log
            SET status = ?, date_completed = ?, rating = ?,
                reading_duration_days = ?, personal_notes = ?, updated_at = ?
            WHERE id = ?
        """

        params = (
            ReadingStatus.COMPLETED.value,
            now,
            rating,
            reading_duration,
            personal_notes,
            now,
            log_id
        )

        execute_query(update_query, params)
        return True

    @staticmethod
    def start_reading_book(book_id: int, format_used: str = "Physical") -> int:
        """
        Mark a book as currently reading.

        Args:
            book_id: Book ID
            format_used: Reading format

        Returns:
            Reading log ID
        """
        # Check if already has a log
        existing = BookService.get_reading_log_by_book(book_id)

        if existing:
            # Update existing log
            update_query = """
                UPDATE reading_log
                SET status = ?, date_started = ?, format_used = ?, updated_at = ?
                WHERE book_id = ?
            """
            params = (
                ReadingStatus.READING.value,
                datetime.now(),
                format_used,
                datetime.now(),
                book_id
            )
            execute_query(update_query, params)
            return existing['id']
        else:
            # Create new log
            log_data = ReadingLogCreate(
                book_id=book_id,
                status=ReadingStatus.READING,
                date_started=datetime.now(),
                format_used=format_used
            )
            return BookService.create_reading_log(log_data)
