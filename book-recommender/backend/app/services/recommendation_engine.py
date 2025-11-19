"""
AI-powered recommendation engine using Claude API.
"""
import os
import json
from typing import List, Dict, Any, Optional
from anthropic import AsyncAnthropic
from datetime import datetime


class RecommendationEngine:
    """AI-powered book recommendation engine."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the recommendation engine.

        Args:
            api_key: Anthropic API key (defaults to env variable)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = AsyncAnthropic(api_key=self.api_key)

    async def generate_recommendations(
        self,
        genre: str,
        user_profile: Dict[str, Any],
        reading_history: List[Dict[str, Any]],
        count: int = 3,
        trending_context: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized book recommendations for a genre.

        Args:
            genre: Target genre for recommendations
            user_profile: User reading profile and preferences
            reading_history: List of previously read books with ratings
            count: Number of recommendations to generate
            trending_context: Optional context about trending books

        Returns:
            List of recommended books with reasoning
        """
        # Build the prompt
        prompt = self._build_recommendation_prompt(
            genre=genre,
            user_profile=user_profile,
            reading_history=reading_history,
            count=count,
            trending_context=trending_context
        )

        try:
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
            content = response.content[0].text
            recommendations = self._parse_recommendations(content)

            return recommendations[:count]

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return []

    def _build_recommendation_prompt(
        self,
        genre: str,
        user_profile: Dict[str, Any],
        reading_history: List[Dict[str, Any]],
        count: int,
        trending_context: Optional[str]
    ) -> str:
        """Build the AI prompt for generating recommendations."""

        # Determine user reading level
        reading_level = user_profile.get("reading_level", "naive")
        total_books_read = user_profile.get("total_books_read", 0)

        # Analyze reading history
        high_rated = [b for b in reading_history if b.get("rating", 0) >= 4]
        low_rated = [b for b in reading_history if b.get("rating", 0) <= 2]

        prompt = f"""You are an expert book curator helping a reader discover their next great read.

**Reader Profile:**
- Reading Experience: {reading_level.title()} ({total_books_read} books read)
- Target Genre: {genre}

"""

        # Add reading level guidance
        if reading_level == "naive" or total_books_read < 20:
            prompt += """**Recommendation Style:**
- Prioritize accessible, well-paced narratives
- Focus on clear writing styles and engaging plots
- Avoid overly complex themes or experimental structures
- Recommend popular, well-reviewed entry points to the genre
- Books should be inviting and not intimidating

"""

        # Add reading history context
        if high_rated:
            prompt += f"""**Books They Loved (Rated 4-5 stars):**
{self._format_book_list(high_rated[:5])}

"""

        if low_rated:
            prompt += f"""**Books They Didn't Enjoy (Rated 1-2 stars):**
{self._format_book_list(low_rated[:3])}

"""

        # Add trending context if available
        if trending_context:
            prompt += f"""**Current Trends:**
{trending_context}

"""

        # Add the main request
        prompt += f"""**Task:**
Generate {count} personalized book recommendations in the {genre} genre that:
1. Match the reader's experience level and preferences
2. Aren't too similar to what they've already read (no same-author repetition)
3. Consider current trends and new releases (last 6 months) alongside timeless classics
4. Analyze themes, writing style, pacing, and character development
5. Provide genuine variety while staying accessible

**Output Format (JSON):**
Return a JSON array with exactly {count} book recommendations. Each recommendation must include:

```json
[
  {{
    "title": "Book Title",
    "author": "Author Name",
    "isbn": "ISBN if known, else null",
    "publication_year": 2024,
    "page_count": 350,
    "reason": "A compelling 2-3 sentence explanation of why this book is recommended for this reader, focusing on themes, style, and appeal",
    "score": 0.95,
    "tags": ["accessible", "trending", "character-driven"]
  }}
]
```

**Important:**
- Ensure variety in publication years (mix of new releases and established favorites)
- Each recommendation should be distinct in style and themes
- Focus on WHY this book matches the reader's preferences
- Be specific and insightful in your reasoning
- Return ONLY the JSON array, no additional text
"""

        return prompt

    def _format_book_list(self, books: List[Dict[str, Any]]) -> str:
        """Format a list of books for the prompt."""
        formatted = []
        for book in books:
            rating = book.get("rating", "N/A")
            title = book.get("title", "Unknown")
            author = book.get("author", "Unknown")
            formatted.append(f"  - \"{title}\" by {author} (Rating: {rating}★)")

        return "\n".join(formatted)

    def _parse_recommendations(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse Claude's JSON response into recommendations."""
        try:
            # Extract JSON from response
            # Look for JSON array in the text
            start = response_text.find("[")
            end = response_text.rfind("]") + 1

            if start == -1 or end == 0:
                print("No JSON array found in response")
                return []

            json_str = response_text[start:end]
            recommendations = json.loads(json_str)

            return recommendations

        except json.JSONDecodeError as e:
            print(f"Error parsing recommendations JSON: {e}")
            print(f"Response text: {response_text}")
            return []

    async def generate_book_summary(
        self,
        book_title: str,
        book_author: str,
        user_notes: Optional[str] = None
    ) -> str:
        """
        Generate an AI summary of a completed book.

        Args:
            book_title: Book title
            book_author: Book author
            user_notes: Optional user notes about the book

        Returns:
            AI-generated summary
        """
        prompt = f"""Generate a concise, insightful summary of the book "{book_title}" by {book_author}.

**Include:**
1. Brief plot overview (2-3 sentences)
2. Key themes and ideas
3. Notable memorable aspects
4. Overall tone and style

"""

        if user_notes:
            prompt += f"""**Reader's Personal Notes:**
{user_notes}

"""

        prompt += """**Format:**
Write a clear, engaging summary in 4-5 sentences that captures the essence of the book.
Focus on what makes this book memorable and meaningful.
"""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Error generating book summary: {e}")
            return "Unable to generate summary at this time."

    async def analyze_reading_patterns(
        self,
        reading_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze user's reading patterns and provide insights.

        Args:
            reading_history: Complete reading history with ratings

        Returns:
            Analysis insights
        """
        if not reading_history:
            return {
                "insights": "Not enough reading data yet. Start logging your books!",
                "suggestions": []
            }

        prompt = f"""Analyze this reader's reading patterns and provide insights.

**Reading History:**
{json.dumps(reading_history, indent=2)}

**Task:**
Provide a brief analysis covering:
1. Favorite genres and themes
2. Reading preferences (what they consistently rate highly)
3. Patterns in books they didn't enjoy
4. Suggestions for growth and exploration
5. Strengths in their reading diversity

**Output Format (JSON):**
```json
{{
  "insights": "A 3-4 sentence summary of key patterns",
  "favorite_themes": ["theme1", "theme2"],
  "suggestions": [
    "Specific, actionable suggestion 1",
    "Specific, actionable suggestion 2"
  ],
  "diversity_score": 0.75
}}
```

Return ONLY the JSON object.
"""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            content = response.content[0].text

            # Parse JSON
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]

            return json.loads(json_str)

        except Exception as e:
            print(f"Error analyzing reading patterns: {e}")
            return {
                "insights": "Unable to analyze patterns at this time.",
                "suggestions": []
            }
