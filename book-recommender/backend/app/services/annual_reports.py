"""
Annual Reading Reports - Beautiful year-end summaries.
"""
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime, date
from anthropic import AsyncAnthropic
from ..database.database import execute_query


class AnnualReportsService:
    """Generate comprehensive annual reading reports."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize annual reports service."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None

    async def generate_annual_report(self, year: int) -> Dict[str, Any]:
        """
        Generate comprehensive annual reading report.

        Args:
            year: Year to generate report for

        Returns:
            Complete annual report with stats and narrative
        """
        # Gather all statistics
        stats = self._collect_year_statistics(year)

        # Generate AI narrative
        narrative = None
        if self.client:
            narrative = await self._generate_ai_narrative(year, stats)

        # Compile complete report
        report = {
            "year": year,
            "generated_date": datetime.now().isoformat(),
            **stats,
            "ai_narrative": narrative,
            "milestones": self._identify_milestones(stats),
            "highlights": self._create_highlights(stats),
            "growth_summary": self._analyze_growth(stats, year)
        }

        # Save to database
        self._save_annual_report(year, report)

        return report

    def _collect_year_statistics(self, year: int) -> Dict[str, Any]:
        """Collect all statistics for the year."""
        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31"

        # Total books
        total_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            AND date_completed >= ? AND date_completed <= ?
        """
        total_books = execute_query(total_query, (year_start, year_end))[0]['count']

        # Total pages
        pages_query = """
            SELECT SUM(b.page_count) as total
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.date_completed >= ? AND rl.date_completed <= ?
            AND b.page_count IS NOT NULL
        """
        total_pages = execute_query(pages_query, (year_start, year_end))[0]['total'] or 0

        # Genre distribution
        genre_query = """
            SELECT b.genre, COUNT(*) as count
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.date_completed >= ? AND rl.date_completed <= ?
            GROUP BY b.genre
            ORDER BY count DESC
        """
        genres = execute_query(genre_query, (year_start, year_end))
        favorite_genre = genres[0]['genre'] if genres else "Unknown"

        # Top rated books
        top_rated_query = """
            SELECT b.*, rl.rating, rl.date_completed
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.date_completed >= ? AND rl.date_completed <= ?
            AND rl.rating = 5
            ORDER BY rl.date_completed
        """
        top_rated = execute_query(top_rated_query, (year_start, year_end))

        # Monthly breakdown
        monthly_query = """
            SELECT
                strftime('%m', date_completed) as month,
                COUNT(*) as books,
                SUM(b.page_count) as pages
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND date_completed >= ? AND date_completed <= ?
            GROUP BY month
            ORDER BY month
        """
        monthly_data = execute_query(monthly_query, (year_start, year_end))

        # Reading speed
        speed_query = """
            SELECT AVG(CAST(b.page_count AS FLOAT) / rl.reading_duration_days) as avg_speed
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.date_completed >= ? AND rl.date_completed <= ?
            AND rl.reading_duration_days > 0
            AND b.page_count IS NOT NULL
        """
        avg_speed = execute_query(speed_query, (year_start, year_end))[0]['avg_speed'] or 0

        # Longest/shortest books
        longest_query = """
            SELECT b.title, b.author, b.page_count
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.date_completed >= ? AND rl.date_completed <= ?
            AND b.page_count IS NOT NULL
            ORDER BY b.page_count DESC
            LIMIT 1
        """
        longest = execute_query(longest_query, (year_start, year_end))

        shortest_query = """
            SELECT b.title, b.author, b.page_count
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.date_completed >= ? AND rl.date_completed <= ?
            AND b.page_count IS NOT NULL
            AND b.page_count > 0
            ORDER BY b.page_count ASC
            LIMIT 1
        """
        shortest = execute_query(shortest_query, (year_start, year_end))

        # New authors discovered
        new_authors_query = """
            SELECT COUNT(DISTINCT b.author) as count
            FROM reading_log rl
            JOIN books b ON rl.book_id = b.id
            WHERE rl.status = 'completed'
            AND rl.date_completed >= ? AND rl.date_completed <= ?
        """
        new_authors = execute_query(new_authors_query, (year_start, year_end))[0]['count']

        # Find busiest month
        busiest_month = max(monthly_data, key=lambda x: x['books']) if monthly_data else None

        return {
            "total_books": total_books,
            "total_pages": total_pages,
            "favorite_genre": favorite_genre,
            "genre_distribution": [{"genre": g['genre'], "count": g['count']} for g in genres],
            "top_rated_books": top_rated[:10],
            "monthly_breakdown": monthly_data,
            "average_speed_pages_per_day": round(avg_speed, 1),
            "longest_book": longest[0] if longest else None,
            "shortest_book": shortest[0] if shortest else None,
            "new_authors_discovered": new_authors,
            "busiest_month": busiest_month
        }

    async def _generate_ai_narrative(self, year: int, stats: Dict[str, Any]) -> str:
        """Generate AI narrative about the reading year."""
        if not self.client:
            return "Your reading journey this year has been remarkable!"

        prompt = f"""Create an engaging, personal narrative about a reader's {year} reading year.

**Their Year in Numbers:**
- {stats['total_books']} books completed
- {stats['total_pages']:,} pages read
- Favorite genre: {stats['favorite_genre']}
- {stats['new_authors_discovered']} new authors discovered
- Average reading speed: {stats['average_speed_pages_per_day']} pages/day

**Highlights:**
- Busiest month: {stats.get('busiest_month', {}).get('month', 'Unknown')} ({stats.get('busiest_month', {}).get('books', 0)} books)
- Longest book: "{stats.get('longest_book', {}).get('title', 'N/A')}" ({stats.get('longest_book', {}).get('page_count', 0)} pages)
- {len(stats['top_rated_books'])} five-star reads

**Task:**
Write a warm, celebratory 3-4 paragraph narrative about their reading year. Make it:
1. Personal and engaging
2. Highlight their achievements and growth
3. Acknowledge milestones
4. Express genuine appreciation for their reading journey
5. Look forward to next year

Tone: Warm, encouraging, slightly playful, like a friend celebrating their achievements.

Return only the narrative text, no JSON."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Error generating narrative: {e}")
            return f"What a year of reading! You completed {stats['total_books']} books and discovered so many new stories."

    def _identify_milestones(self, stats: Dict[str, Any]) -> list:
        """Identify special milestones achieved."""
        milestones = []

        if stats['total_books'] >= 50:
            milestones.append({"type": "book_count", "message": f"🎉 Read {stats['total_books']} books - incredible!"})
        elif stats['total_books'] >= 25:
            milestones.append({"type": "book_count", "message": f"📚 Completed {stats['total_books']} books this year!"})

        if stats['total_pages'] >= 10000:
            milestones.append({"type": "pages", "message": f"📖 Read over {stats['total_pages']:,} pages!"})

        if stats['new_authors_discovered'] >= 20:
            milestones.append({"type": "authors", "message": f"🌟 Discovered {stats['new_authors_discovered']} new authors!"})

        if len(stats['top_rated_books']) >= 10:
            milestones.append({"type": "favorites", "message": f"⭐ Gave {len(stats['top_rated_books'])} books 5 stars!"})

        return milestones

    def _create_highlights(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Create shareable highlights."""
        return {
            "by_the_numbers": {
                "books": stats['total_books'],
                "pages": stats['total_pages'],
                "authors": stats['new_authors_discovered']
            },
            "favorites": {
                "genre": stats['favorite_genre'],
                "five_star_count": len(stats['top_rated_books'])
            },
            "achievements": {
                "longest_book": stats.get('longest_book', {}).get('title'),
                "busiest_month": stats.get('busiest_month', {}).get('month')
            }
        }

    def _analyze_growth(self, stats: Dict[str, Any], year: int) -> str:
        """Analyze reading growth compared to previous year."""
        prev_year = year - 1

        prev_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            AND strftime('%Y', date_completed) = ?
        """

        prev_count = execute_query(prev_query, (str(prev_year),))[0]['count']

        if prev_count > 0:
            growth = ((stats['total_books'] - prev_count) / prev_count) * 100

            if growth > 0:
                return f"Up {growth:.1f}% from {prev_year}!"
            elif growth < 0:
                return f"Down {abs(growth):.1f}% from {prev_year}, but that's okay!"
            else:
                return f"Same as {prev_year} - consistent reading!"
        else:
            return f"First full year tracked!"

    def _save_annual_report(self, year: int, report: Dict[str, Any]):
        """Save annual report to database."""
        try:
            query = """
                INSERT OR REPLACE INTO annual_reports
                (year, total_books, total_pages, favorite_genre, top_rated_books,
                 reading_highlights, ai_narrative, growth_summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            params = (
                year,
                report['total_books'],
                report['total_pages'],
                report['favorite_genre'],
                json.dumps(report.get('top_rated_books', [])),
                json.dumps(report.get('highlights', {})),
                report.get('ai_narrative', ''),
                report.get('growth_summary', '')
            )

            execute_query(query, params)

        except Exception as e:
            print(f"Error saving annual report: {e}")

    def get_saved_report(self, year: int) -> Optional[Dict[str, Any]]:
        """Retrieve saved annual report."""
        query = "SELECT * FROM annual_reports WHERE year = ?"
        result = execute_query(query, (year,))

        if result:
            report = result[0]
            # Parse JSON fields
            report['top_rated_books'] = json.loads(report.get('top_rated_books', '[]'))
            report['reading_highlights'] = json.loads(report.get('reading_highlights', '{}'))
            return report

        return None
