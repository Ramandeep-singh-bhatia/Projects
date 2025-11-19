"""
AI Reading Coach Service - Personalized reading plans and guidance.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from anthropic import AsyncAnthropic
from ..database.database import execute_query


class ReadingCoachService:
    """AI-powered reading coach for personalized plans and guidance."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize reading coach service."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None

    async def generate_reading_plan(
        self,
        goal: str,
        duration_days: int,
        difficulty: str,
        reading_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a personalized reading plan.

        Args:
            goal: User's reading goal (e.g., "explore philosophy", "improve in sci-fi")
            duration_days: Plan duration in days
            difficulty: "gradual" or "challenging"
            reading_history: User's reading history

        Returns:
            Reading plan with book sequence and reasoning
        """
        if not self.client:
            raise ValueError("Claude API not initialized")

        # Analyze reading history
        completed_books = [b for b in reading_history if b.get('status') == 'completed']
        avg_complexity = self._calculate_avg_complexity(completed_books)
        top_genres = self._get_top_genres(completed_books)

        # Build prompt
        prompt = f"""Create a {duration_days}-day personalized reading plan for someone who wants to: {goal}

**Reader Profile:**
- Books completed: {len(completed_books)}
- Average complexity level: {avg_complexity}/10
- Favorite genres: {', '.join(top_genres[:3])}
- Difficulty preference: {difficulty}

**Recent highly-rated books:**
{self._format_books(completed_books[:5])}

**Requirements:**
1. Generate 5-8 book recommendations in progressive order
2. Start at appropriate difficulty level for this reader
3. Gradually increase complexity (if "challenging") or maintain accessible level (if "gradual")
4. Build knowledge systematically toward the goal
5. Include diverse perspectives and styles
6. Consider pacing: spread books appropriately over {duration_days} days

**Output Format (JSON):**
```json
{{
  "plan_name": "Descriptive plan name",
  "reasoning": "2-3 sentence explanation of the plan's approach",
  "books": [
    {{
      "sequence": 1,
      "title": "Book Title",
      "author": "Author Name",
      "estimated_days": 14,
      "why_this_book": "Specific reason this book fits here in the sequence",
      "complexity_level": 6
    }}
  ],
  "success_tips": ["tip 1", "tip 2", "tip 3"]
}}
```

Return ONLY valid JSON."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            # Parse JSON
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            plan_data = json.loads(json_str)

            return plan_data

        except Exception as e:
            print(f"Error generating reading plan: {e}")
            raise

    async def analyze_reading_pace(
        self,
        book_id: int,
        target_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analyze reading pace and provide guidance.

        Args:
            book_id: Currently reading book ID
            target_date: Optional target completion date

        Returns:
            Pacing analysis and recommendations
        """
        # Get book details
        book_query = """
            SELECT b.*, rl.date_started
            FROM books b
            JOIN reading_log rl ON b.id = rl.book_id
            WHERE b.id = ? AND rl.status = 'reading'
        """
        book = execute_query(book_query, (book_id,))

        if not book:
            return {"error": "Book not found or not currently reading"}

        book = book[0]

        # Calculate days elapsed
        start_date = datetime.fromisoformat(book['date_started']).date() if book['date_started'] else date.today()
        days_elapsed = (date.today() - start_date).days

        # Get recent sessions
        sessions_query = """
            SELECT * FROM reading_sessions
            WHERE book_id = ?
            ORDER BY session_date DESC
            LIMIT 7
        """
        recent_sessions = execute_query(sessions_query, (book_id,))

        # Calculate average pace
        total_pages_recent = sum(s.get('pages_read', 0) for s in recent_sessions)
        avg_pages_per_day = total_pages_recent / max(len(recent_sessions), 1) if recent_sessions else 0

        # Estimate completion
        pages_left = book.get('page_count', 0)  # Assuming we don't track current page
        days_to_complete = pages_left / avg_pages_per_day if avg_pages_per_day > 0 else None

        # Check if on track
        if target_date and days_to_complete:
            days_available = (target_date - date.today()).days
            on_track = days_to_complete <= days_available

            pages_per_day_needed = pages_left / max(days_available, 1)

            return {
                "on_track": on_track,
                "current_pace": round(avg_pages_per_day, 1),
                "required_pace": round(pages_per_day_needed, 1),
                "estimated_completion": (date.today() + timedelta(days=int(days_to_complete))).isoformat(),
                "target_date": target_date.isoformat(),
                "days_ahead_behind": days_available - int(days_to_complete),
                "recommendation": self._get_pace_recommendation(on_track, pages_per_day_needed, avg_pages_per_day)
            }

        return {
            "current_pace": round(avg_pages_per_day, 1),
            "estimated_completion": (date.today() + timedelta(days=int(days_to_complete))).isoformat() if days_to_complete else None,
            "days_elapsed": days_elapsed
        }

    def detect_reading_slump(self) -> Optional[Dict[str, Any]]:
        """
        Detect if user is in a reading slump.

        Returns:
            Slump information if detected, None otherwise
        """
        # Get recent completion rate
        thirty_days_ago = (date.today() - timedelta(days=30)).isoformat()
        sixty_days_ago = (date.today() - timedelta(days=60)).isoformat()

        recent_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed' AND date_completed >= ?
        """
        recent_count = execute_query(recent_query, (thirty_days_ago,))[0]['count']

        previous_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'completed'
            AND date_completed >= ? AND date_completed < ?
        """
        previous_count = execute_query(previous_query, (sixty_days_ago, thirty_days_ago))[0]['count']

        # Check DNF rate
        dnf_query = """
            SELECT COUNT(*) as count
            FROM reading_log
            WHERE status = 'dnf' AND date_added >= ?
        """
        dnf_count = execute_query(dnf_query, (thirty_days_ago,))[0]['count']

        # Slump detection criteria
        significant_drop = previous_count > 0 and (recent_count / previous_count < 0.5)
        high_dnf_rate = dnf_count > recent_count
        low_completion = recent_count < 2

        if significant_drop or high_dnf_rate or low_completion:
            return {
                "in_slump": True,
                "recent_completions": recent_count,
                "previous_completions": previous_count,
                "recent_dnf": dnf_count,
                "slump_type": self._identify_slump_type(significant_drop, high_dnf_rate, low_completion),
                "detected_date": date.today().isoformat()
            }

        return None

    async def suggest_slump_recovery(
        self,
        slump_data: Dict[str, Any],
        reading_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Suggest books to help overcome reading slump.

        Args:
            slump_data: Slump detection information
            reading_history: User's reading history

        Returns:
            Recovery suggestions
        """
        if not self.client:
            return {"suggestions": ["Try rereading a favorite book", "Choose a shorter book", "Switch to a different genre"]}

        # Identify previous slump recovery successes
        favorite_books = [b for b in reading_history if b.get('rating', 0) >= 4]

        prompt = f"""A reader is experiencing a reading slump. Help them recover.

**Slump Details:**
{json.dumps(slump_data, indent=2)}

**Their Favorite Books (for reference):**
{self._format_books(favorite_books[:5])}

**Task:**
Suggest 3 "palate cleanser" books that are:
1. Shorter and faster-paced than usual
2. Highly engaging and hard to put down
3. In genres they enjoy
4. Lower complexity/easier reads
5. Proven crowd-pleasers

Also provide:
- 3-4 practical tips for overcoming the slump
- Encouragement (reading slumps are normal!)

**Output Format (JSON):**
```json
{{
  "message": "Encouraging message about slumps being normal",
  "book_suggestions": [
    {{
      "title": "Book Title",
      "author": "Author",
      "why": "Why this book will help",
      "pages": 250
    }}
  ],
  "recovery_tips": ["tip 1", "tip 2", "tip 3"],
  "success_strategy": "Overall strategy for this specific reader"
}}
```

Return ONLY valid JSON."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2048,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]

            return json.loads(json_str)

        except Exception as e:
            print(f"Error generating slump recovery: {e}")
            return {"error": str(e)}

    # Helper methods

    def _calculate_avg_complexity(self, books: List[Dict[str, Any]]) -> float:
        """Calculate average complexity from books."""
        if not books:
            return 5.0

        complexities = []
        for book in books:
            # Get complexity from database if available
            query = "SELECT complexity_score FROM book_complexity WHERE book_id = ?"
            result = execute_query(query, (book.get('id'),))
            if result and result[0].get('complexity_score'):
                complexities.append(result[0]['complexity_score'])

        return sum(complexities) / len(complexities) if complexities else 5.0

    def _get_top_genres(self, books: List[Dict[str, Any]]) -> List[str]:
        """Get most common genres from books."""
        genre_counts = {}
        for book in books:
            genre = book.get('genre', 'General')
            genre_counts[genre] = genre_counts.get(genre, 0) + 1

        sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
        return [genre for genre, _ in sorted_genres]

    def _format_books(self, books: List[Dict[str, Any]]) -> str:
        """Format books for prompts."""
        formatted = []
        for book in books:
            rating = book.get('rating', 'N/A')
            formatted.append(f"  - \"{book.get('title', 'Unknown')}\" by {book.get('author', 'Unknown')} (Rating: {rating}★)")

        return "\n".join(formatted) if formatted else "  (No books yet)"

    def _get_pace_recommendation(self, on_track: bool, required: float, current: float) -> str:
        """Generate pacing recommendation."""
        if on_track:
            return f"You're on track! Keep reading at your current pace of {current:.1f} pages/day."
        else:
            diff = required - current
            return f"Read {diff:.1f} more pages per day to reach your goal. Aim for {required:.1f} pages/day."

    def _identify_slump_type(self, drop: bool, high_dnf: bool, low_completion: bool) -> str:
        """Identify type of reading slump."""
        if high_dnf:
            return "high_abandonment"
        elif drop:
            return "productivity_drop"
        elif low_completion:
            return "low_engagement"
        else:
            return "general"
