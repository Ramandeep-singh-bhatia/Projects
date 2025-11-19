"""
Reading statistics and analytics service.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from collections import defaultdict
from ..database.database import execute_query


class AnalyticsService:
    """Service for reading analytics and statistics."""

    @staticmethod
    def get_dashboard_stats(year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get comprehensive dashboard statistics.

        Args:
            year: Optional year filter (defaults to current year)

        Returns:
            Dashboard statistics dictionary
        """
        if year is None:
            year = datetime.now().year

        # Books read this year
        books_year_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            AND strftime('%Y', date_completed) = ?
        """
        books_year = execute_query(books_year_query, (str(year),))[0]['count']

        # Books read all time
        books_all_time_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
        """
        books_all_time = execute_query(books_all_time_query)[0]['count']

        # Total pages read
        pages_query = """
            SELECT SUM(b.page_count) as total_pages
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND b.page_count IS NOT NULL
        """
        pages_result = execute_query(pages_query)[0]
        total_pages = pages_result['total_pages'] or 0

        # Average reading speed
        avg_speed_query = """
            SELECT AVG(CAST(b.page_count AS FLOAT) / rl.reading_duration_days) as avg_speed
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.reading_duration_days > 0
            AND b.page_count IS NOT NULL
        """
        avg_speed_result = execute_query(avg_speed_query)[0]
        avg_reading_speed = round(avg_speed_result['avg_speed'] or 0, 2)

        # Completion rate
        total_started_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status IN ('reading', 'completed', 'dnf')
        """
        total_started = execute_query(total_started_query)[0]['count']

        completion_rate = (books_all_time / total_started * 100) if total_started > 0 else 0

        # Current streak
        current_streak = AnalyticsService._calculate_reading_streak()

        # Books this month
        current_month = datetime.now().month
        books_month_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            AND strftime('%Y', date_completed) = ?
            AND strftime('%m', date_completed) = ?
        """
        books_month = execute_query(
            books_month_query,
            (str(year), f"{current_month:02d}")
        )[0]['count']

        # Genre distribution
        genre_dist = AnalyticsService.get_genre_distribution()

        # Monthly trends
        monthly_trends = AnalyticsService.get_monthly_trends(year)

        # Top rated books
        top_rated = AnalyticsService.get_top_rated_books(limit=5)

        # Currently reading
        currently_reading_query = """
            SELECT b.*, rl.date_started, rl.id as log_id
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'reading'
            ORDER BY rl.date_started DESC
        """
        currently_reading = execute_query(currently_reading_query)

        # Active goals
        goals_query = """
            SELECT * FROM reading_goals
            WHERE is_active = 1
            ORDER BY created_at DESC
        """
        active_goals = execute_query(goals_query)

        return {
            "books_read_year": books_year,
            "books_read_all_time": books_all_time,
            "pages_read_total": total_pages,
            "average_reading_speed": avg_reading_speed,
            "completion_rate": round(completion_rate, 2),
            "current_streak_days": current_streak,
            "books_this_month": books_month,
            "genre_distribution": genre_dist,
            "monthly_trends": monthly_trends,
            "top_rated_books": top_rated,
            "currently_reading": currently_reading,
            "active_goals": active_goals
        }

    @staticmethod
    def get_genre_distribution() -> Dict[str, int]:
        """Get distribution of books by genre."""
        query = """
            SELECT b.genre, COUNT(*) as count
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            GROUP BY b.genre
            ORDER BY count DESC
        """

        results = execute_query(query)
        return {row['genre']: row['count'] for row in results}

    @staticmethod
    def get_monthly_trends(year: int) -> List[Dict[str, Any]]:
        """
        Get monthly reading trends for a year.

        Args:
            year: Target year

        Returns:
            List of monthly statistics
        """
        query = """
            SELECT
                strftime('%m', date_completed) as month,
                COUNT(*) as books_completed,
                SUM(b.page_count) as pages_read,
                AVG(rl.rating) as avg_rating
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND strftime('%Y', date_completed) = ?
            GROUP BY month
            ORDER BY month
        """

        results = execute_query(query, (str(year),))

        # Fill in missing months with zeros
        monthly_data = defaultdict(lambda: {
            "month": 0,
            "books_completed": 0,
            "pages_read": 0,
            "avg_rating": 0
        })

        for row in results:
            month_num = int(row['month'])
            monthly_data[month_num] = {
                "month": month_num,
                "books_completed": row['books_completed'],
                "pages_read": row['pages_read'] or 0,
                "avg_rating": round(row['avg_rating'], 2) if row['avg_rating'] else 0
            }

        # Return all 12 months
        return [monthly_data[i] for i in range(1, 13)]

    @staticmethod
    def get_top_rated_books(limit: int = 10) -> List[Dict[str, Any]]:
        """Get top-rated books."""
        query = """
            SELECT b.*, rl.rating, rl.date_completed
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.rating >= 4
            ORDER BY rl.rating DESC, rl.date_completed DESC
            LIMIT ?
        """

        return execute_query(query, (limit,))

    @staticmethod
    def _calculate_reading_streak() -> int:
        """
        Calculate current reading streak in days.

        Returns:
            Number of consecutive days with reading activity
        """
        query = """
            SELECT DISTINCT date(date_completed) as read_date
            FROM reading_log
            WHERE status = 'completed'
            ORDER BY read_date DESC
            LIMIT 365
        """

        results = execute_query(query)

        if not results:
            return 0

        today = date.today()
        streak = 0

        for row in results:
            read_date_str = row['read_date']
            read_date = datetime.strptime(read_date_str, '%Y-%m-%d').date()

            expected_date = today - timedelta(days=streak)

            if read_date == expected_date:
                streak += 1
            elif read_date < expected_date:
                break

        return streak

    @staticmethod
    def get_genre_stats() -> List[Dict[str, Any]]:
        """Get detailed statistics per genre."""
        query = """
            SELECT
                b.genre,
                COUNT(*) as books_read,
                AVG(rl.rating) as avg_rating,
                SUM(b.page_count) as total_pages,
                SUM(CASE WHEN rl.status = 'completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as completion_rate
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status IN ('reading', 'completed', 'dnf')
            GROUP BY b.genre
            ORDER BY books_read DESC
        """

        results = execute_query(query)

        return [{
            "genre": row['genre'],
            "books_read": row['books_read'],
            "average_rating": round(row['avg_rating'], 2) if row['avg_rating'] else 0,
            "total_pages": row['total_pages'] or 0,
            "completion_rate": round(row['completion_rate'], 2)
        } for row in results]

    @staticmethod
    def get_reading_patterns() -> Dict[str, Any]:
        """Analyze reading patterns."""
        # Favorite genres (highest rated)
        fav_genres_query = """
            SELECT b.genre, AVG(rl.rating) as avg_rating, COUNT(*) as count
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed' AND rl.rating IS NOT NULL
            GROUP BY b.genre
            HAVING count >= 2
            ORDER BY avg_rating DESC
            LIMIT 3
        """
        fav_genres = execute_query(fav_genres_query)
        favorite_genres = [row['genre'] for row in fav_genres]

        # Avoided genres (low rated or DNF)
        avoided_query = """
            SELECT b.genre, COUNT(*) as dnf_count
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'dnf' OR rl.rating <= 2
            GROUP BY b.genre
            ORDER BY dnf_count DESC
            LIMIT 3
        """
        avoided = execute_query(avoided_query)
        avoided_genres = [row['genre'] for row in avoided]

        # Average book length
        avg_length_query = """
            SELECT AVG(b.page_count) as avg_length
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed' AND b.page_count IS NOT NULL
        """
        avg_length = execute_query(avg_length_query)[0]['avg_length'] or 0

        # Genre diversity score (number of unique genres / total books)
        diversity_query = """
            SELECT
                COUNT(DISTINCT b.genre) as unique_genres,
                COUNT(*) as total_books
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
        """
        diversity = execute_query(diversity_query)[0]
        diversity_score = (diversity['unique_genres'] / diversity['total_books'] * 100) if diversity['total_books'] > 0 else 0

        # Most productive month
        productive_month_query = """
            SELECT strftime('%m', date_completed) as month, COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            GROUP BY month
            ORDER BY count DESC
            LIMIT 1
        """
        productive = execute_query(productive_month_query)
        most_productive_month = productive[0]['month'] if productive else None

        # Reading velocity trend (comparing last 3 months to previous 3)
        velocity = AnalyticsService._calculate_velocity_trend()

        return {
            "favorite_genres": favorite_genres,
            "avoided_genres": avoided_genres,
            "average_book_length": int(avg_length),
            "genre_diversity_score": round(diversity_score, 2),
            "most_productive_month": most_productive_month,
            "reading_velocity_trend": velocity
        }

    @staticmethod
    def _calculate_velocity_trend() -> str:
        """Calculate if reading velocity is increasing, decreasing, or stable."""
        # Get books completed in last 3 months
        three_months_ago = datetime.now() - timedelta(days=90)
        six_months_ago = datetime.now() - timedelta(days=180)

        recent_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            AND date_completed >= ?
        """
        recent_count = execute_query(recent_query, (three_months_ago.isoformat(),))[0]['count']

        previous_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            AND date_completed >= ?
            AND date_completed < ?
        """
        previous_count = execute_query(
            previous_query,
            (six_months_ago.isoformat(), three_months_ago.isoformat())
        )[0]['count']

        if recent_count > previous_count * 1.2:
            return "increasing"
        elif recent_count < previous_count * 0.8:
            return "decreasing"
        else:
            return "stable"

    @staticmethod
    def record_daily_stats(pages_read: int = 0, minutes_read: int = 0):
        """Record daily reading statistics."""
        today = date.today()

        # Check if entry exists
        check_query = "SELECT id FROM reading_stats WHERE date = ?"
        existing = execute_query(check_query, (today.isoformat(),))

        if existing:
            # Update existing
            update_query = """
                UPDATE reading_stats
                SET pages_read = pages_read + ?,
                    minutes_read = minutes_read + ?
                WHERE date = ?
            """
            execute_query(update_query, (pages_read, minutes_read, today.isoformat()))
        else:
            # Create new
            insert_query = """
                INSERT INTO reading_stats (date, pages_read, minutes_read)
                VALUES (?, ?, ?)
            """
            execute_query(insert_query, (today.isoformat(), pages_read, minutes_read))
