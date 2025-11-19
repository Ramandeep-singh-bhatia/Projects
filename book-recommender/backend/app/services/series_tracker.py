"""
Series Tracker Service - Manage book series and reading progress.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..database.database import execute_query


class SeriesTrackerService:
    """Service for tracking book series and progress."""

    @staticmethod
    def create_series(
        series_name: str,
        primary_author: str,
        genre: str,
        total_books: Optional[int] = None,
        description: Optional[str] = None
    ) -> int:
        """
        Create a new book series.

        Args:
            series_name: Name of the series
            primary_author: Main author
            genre: Series genre
            total_books: Total number of books (if known)
            description: Series description

        Returns:
            Series ID
        """
        query = """
            INSERT INTO book_series (series_name, primary_author, genre, total_books, description)
            VALUES (?, ?, ?, ?, ?)
        """

        params = (series_name, primary_author, genre, total_books, description)
        series_id = execute_query(query, params)

        return series_id

    @staticmethod
    def add_book_to_series(
        series_id: int,
        book_id: int,
        book_number: int,
        reading_order: Optional[int] = None,
        is_standalone: bool = False
    ) -> int:
        """
        Add a book to a series.

        Args:
            series_id: Series ID
            book_id: Book ID
            book_number: Book number in series
            reading_order: Optional reading order (if different from book_number)
            is_standalone: Whether book can be read standalone

        Returns:
            Series book entry ID
        """
        query = """
            INSERT INTO series_books (series_id, book_id, book_number, reading_order, is_standalone)
            VALUES (?, ?, ?, ?, ?)
        """

        reading_order = reading_order or book_number
        params = (series_id, book_id, book_number, reading_order, is_standalone)

        return execute_query(query, params)

    @staticmethod
    def get_all_series() -> List[Dict[str, Any]]:
        """
        Get all book series.

        Returns:
            List of series with metadata
        """
        query = """
            SELECT
                bs.*,
                COUNT(sb.id) as books_in_database,
                ups.books_completed,
                ups.current_book_id
            FROM book_series bs
            LEFT JOIN series_books sb ON bs.series_id = sb.series_id
            LEFT JOIN user_series_progress ups ON bs.series_id = ups.series_id
            GROUP BY bs.series_id
            ORDER BY bs.series_name
        """

        return execute_query(query)

    @staticmethod
    def get_series_details(series_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a series.

        Args:
            series_id: Series ID

        Returns:
            Series details with all books
        """
        # Get series info
        series_query = """
            SELECT bs.*, ups.books_completed, ups.current_book_id
            FROM book_series bs
            LEFT JOIN user_series_progress ups ON bs.series_id = ups.series_id
            WHERE bs.series_id = ?
        """

        series = execute_query(series_query, (series_id,))

        if not series:
            return None

        series_data = series[0]

        # Get all books in series
        books_query = """
            SELECT
                sb.*,
                b.title,
                b.author,
                b.page_count,
                b.cover_url,
                rl.status,
                rl.rating,
                rl.date_completed
            FROM series_books sb
            JOIN books b ON sb.book_id = b.id
            LEFT JOIN reading_log rl ON b.id = rl.book_id
            WHERE sb.series_id = ?
            ORDER BY sb.reading_order
        """

        books = execute_query(books_query, (series_id,))

        series_data['books'] = books

        return series_data

    @staticmethod
    def update_series_progress(
        series_id: int,
        current_book_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update reading progress for a series.

        Args:
            series_id: Series ID
            current_book_id: Currently reading book ID

        Returns:
            Updated progress info
        """
        # Count completed books in series
        completed_query = """
            SELECT COUNT(*) as count
            FROM series_books sb
            JOIN reading_log rl ON sb.book_id = rl.book_id
            WHERE sb.series_id = ? AND rl.status = 'completed'
        """

        completed_count = execute_query(completed_query, (series_id,))[0]['count']

        # Check if progress entry exists
        existing = execute_query(
            "SELECT id FROM user_series_progress WHERE series_id = ?",
            (series_id,)
        )

        now = datetime.now()

        if existing:
            # Update existing
            query = """
                UPDATE user_series_progress
                SET books_completed = ?,
                    current_book_id = ?,
                    last_read_date = ?
                WHERE series_id = ?
            """
            execute_query(query, (completed_count, current_book_id, now, series_id))
        else:
            # Create new
            query = """
                INSERT INTO user_series_progress
                (series_id, books_completed, current_book_id, started_date, last_read_date)
                VALUES (?, ?, ?, ?, ?)
            """
            execute_query(query, (series_id, completed_count, current_book_id, now, now))

        return {
            "series_id": series_id,
            "books_completed": completed_count,
            "current_book_id": current_book_id,
            "last_updated": now.isoformat()
        }

    @staticmethod
    def get_in_progress_series() -> List[Dict[str, Any]]:
        """
        Get series currently being read.

        Returns:
            List of in-progress series
        """
        query = """
            SELECT
                bs.*,
                ups.books_completed,
                ups.current_book_id,
                b.title as current_book_title,
                (SELECT COUNT(*) FROM series_books WHERE series_id = bs.series_id) as total_books_in_db
            FROM user_series_progress ups
            JOIN book_series bs ON ups.series_id = bs.series_id
            LEFT JOIN books b ON ups.current_book_id = b.id
            WHERE ups.books_completed > 0
            AND (bs.total_books IS NULL OR ups.books_completed < bs.total_books)
            ORDER BY ups.last_read_date DESC
        """

        return execute_query(query)

    @staticmethod
    def get_completed_series() -> List[Dict[str, Any]]:
        """
        Get completed series.

        Returns:
            List of completed series
        """
        query = """
            SELECT
                bs.*,
                ups.books_completed,
                (SELECT COUNT(*) FROM series_books WHERE series_id = bs.series_id) as total_books_in_db
            FROM user_series_progress ups
            JOIN book_series bs ON ups.series_id = bs.series_id
            WHERE bs.total_books IS NOT NULL
            AND ups.books_completed >= bs.total_books
            ORDER BY bs.series_name
        """

        return execute_query(query)

    @staticmethod
    def get_next_book_in_series(series_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the next unread book in a series.

        Args:
            series_id: Series ID

        Returns:
            Next book to read or None
        """
        query = """
            SELECT
                sb.*,
                b.title,
                b.author,
                b.page_count,
                b.cover_url,
                b.description
            FROM series_books sb
            JOIN books b ON sb.book_id = b.id
            LEFT JOIN reading_log rl ON b.id = rl.book_id
            WHERE sb.series_id = ?
            AND (rl.status IS NULL OR rl.status NOT IN ('completed', 'reading'))
            ORDER BY sb.reading_order ASC
            LIMIT 1
        """

        result = execute_query(query, (series_id,))

        return result[0] if result else None

    @staticmethod
    def detect_series_from_book(book: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Attempt to detect if a book is part of a series.

        Args:
            book: Book dictionary

        Returns:
            Detected series info or None
        """
        title = book.get('title', '')

        # Common series indicators
        series_patterns = [
            r'Book (\d+)',
            r'#(\d+)',
            r'Volume (\d+)',
            r'\(.*?(\d+)\)',
        ]

        import re

        for pattern in series_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                # Potential series detected
                book_number = int(match.group(1))

                # Try to find series by author
                author = book.get('author', '')

                existing_series_query = """
                    SELECT DISTINCT bs.*
                    FROM book_series bs
                    WHERE bs.primary_author = ?
                    LIMIT 1
                """

                existing = execute_query(existing_series_query, (author,))

                if existing:
                    return {
                        "detected": True,
                        "series": existing[0],
                        "book_number": book_number,
                        "confidence": "medium"
                    }
                else:
                    # Suggest creating new series
                    return {
                        "detected": True,
                        "series": None,
                        "book_number": book_number,
                        "confidence": "low",
                        "suggestion": f"This might be book {book_number} of a series"
                    }

        return None

    @staticmethod
    def get_series_statistics() -> Dict[str, Any]:
        """
        Get statistics about series reading.

        Returns:
            Series reading stats
        """
        # Total series
        total_query = "SELECT COUNT(*) as count FROM book_series"
        total = execute_query(total_query)[0]['count']

        # In progress
        in_progress_query = """
            SELECT COUNT(*) as count
            FROM user_series_progress ups
            JOIN book_series bs ON ups.series_id = bs.series_id
            WHERE ups.books_completed > 0
            AND (bs.total_books IS NULL OR ups.books_completed < bs.total_books)
        """
        in_progress = execute_query(in_progress_query)[0]['count']

        # Completed
        completed_query = """
            SELECT COUNT(*) as count
            FROM user_series_progress ups
            JOIN book_series bs ON ups.series_id = bs.series_id
            WHERE bs.total_books IS NOT NULL
            AND ups.books_completed >= bs.total_books
        """
        completed = execute_query(completed_query)[0]['count']

        # Longest series
        longest_query = """
            SELECT series_name, total_books
            FROM book_series
            WHERE total_books IS NOT NULL
            ORDER BY total_books DESC
            LIMIT 1
        """
        longest = execute_query(longest_query)

        return {
            "total_series": total,
            "in_progress": in_progress,
            "completed": completed,
            "not_started": max(0, total - in_progress - completed),
            "longest_series": longest[0] if longest else None
        }
