"""
Enhanced Recommendation Engine - Mood-based, context-aware, and Reading DNA.
"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from anthropic import AsyncAnthropic
from ..database.database import execute_query


class EnhancedRecommendationEngine:
    """Enhanced recommendation engine with mood, context, and DNA profiling."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize enhanced recommendation engine."""
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            self.client = AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None

    async def recommend_by_mood(
        self,
        mood_selections: Dict[str, Any],
        reading_history: List[Dict[str, Any]],
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate mood-based book recommendations.

        Args:
            mood_selections: Dict of mood dimensions and values
                Example: {"energy": "light", "pacing": "fast", "tone": "hopeful"}
            reading_history: User's reading history
            count: Number of recommendations

        Returns:
            List of mood-matched book recommendations
        """
        if not self.client:
            raise ValueError("Claude API not initialized")

        # Get favorite books for context
        favorites = [b for b in reading_history if b.get('rating', 0) >= 4]

        prompt = f"""Recommend books matching a specific mood and reader's taste.

**Requested Mood:**
{json.dumps(mood_selections, indent=2)}

**Reader's Favorite Books:**
{self._format_books(favorites[:8])}

**Task:**
Recommend {count} books that:
1. Match the requested mood perfectly
2. Align with this reader's demonstrated preferences
3. Are engaging and well-reviewed
4. Provide variety in authors and sub-genres

**Mood Interpretation:**
- Energy level: {mood_selections.get('energy', 'balanced')} (light/heavy)
- Pacing: {mood_selections.get('pacing', 'medium')} (slow-burn/fast-paced)
- Emotional tone: {mood_selections.get('tone', 'balanced')} (dark/hopeful)
- Intellectual demand: {mood_selections.get('complexity', 'medium')} (escapist/thought-provoking)

**Output Format (JSON):**
```json
[
  {{
    "title": "Book Title",
    "author": "Author Name",
    "genre": "Genre",
    "mood_match_score": 0.95,
    "why_this_mood": "Specific explanation of how this book matches the requested mood",
    "why_for_you": "Why this reader will specifically enjoy it",
    "estimated_pages": 350,
    "estimated_enjoyment": 0.9
  }}
]
```

Return ONLY valid JSON array."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3072,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            start = content.find("[")
            end = content.rfind("]") + 1
            json_str = content[start:end]
            recommendations = json.loads(json_str)

            # Save mood session
            self._save_mood_session(mood_selections, recommendations)

            return recommendations

        except Exception as e:
            print(f"Error generating mood recommendations: {e}")
            raise

    async def generate_reading_dna(
        self,
        reading_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive Reading DNA profile.

        Args:
            reading_history: Complete reading history

        Returns:
            Reading DNA profile with personality analysis
        """
        if not self.client:
            raise ValueError("Claude API not initialized")

        # Get highly rated books for analysis
        favorites = [b for b in reading_history if b.get('rating', 0) >= 4]

        if len(favorites) < 5:
            return {
                "error": "Need at least 5 rated books to generate Reading DNA",
                "current_count": len(favorites)
            }

        prompt = f"""Analyze this reader's personality based on their favorite books.

**Highly-Rated Books ({len(favorites)} books):**
{self._format_books(favorites)}

**Task:**
Perform deep pattern analysis across these books to identify:

1. **Narrative Style Preference**
   - Character-driven vs Plot-driven (score from -1 to 1)
   - Preferred POV (first/third/multiple)
   - Linear vs Non-linear narrative preference

2. **Pacing & Complexity**
   - Preferred pacing (slow-burn vs fast-paced)
   - Complexity comfort level (1-10)
   - Tolerance for ambiguity

3. **Thematic Interests**
   - Top 5 recurring themes
   - Emotional tone preferences (dark/hopeful/balanced)
   - Topics that resonate

4. **Writing Style**
   - Prose style (lyrical/straightforward/experimental)
   - Dialogue vs description preference
   - Atmosphere/world-building importance

5. **Character Preferences**
   - Types of protagonists they connect with
   - Ensemble vs single protagonist
   - Character arc preferences

**Output Format (JSON):**
```json
{{
  "character_vs_plot_score": 0.7,
  "narrative_preferences": {{
    "pov": "First person",
    "structure": "Linear with flashbacks",
    "pacing": "Moderately fast"
  }},
  "complexity_profile": {{
    "comfort_level": 7,
    "vocabulary_challenge": "Enjoys moderate challenge",
    "theme_depth": "Appreciates layered meanings"
  }},
  "thematic_dna": [
    {{"theme": "Human resilience", "frequency": 12, "importance": "high"}},
    {{"theme": "Identity and belonging", "frequency": 9, "importance": "high"}},
    {{"theme": "Family dynamics", "frequency": 7, "importance": "medium"}}
  ],
  "writing_style_preferences": {{
    "prose": "Lyrical but accessible",
    "dialogue_importance": "High",
    "atmosphere": "Strong sense of place"
  }},
  "character_patterns": {{
    "protagonist_types": ["Flawed heroes", "Unreliable narrators", "Coming-of-age"],
    "relationship_focus": "Medium-high",
    "character_development": "Essential"
  }},
  "reading_personality_summary": "2-3 sentence narrative describing this reader's unique DNA",
  "recommendations_guidance": "What to prioritize in future recommendations",
  "unique_traits": ["Trait 1", "Trait 2", "Trait 3"]
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
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            dna_profile = json.loads(json_str)

            # Save to database
            self._save_dna_profile(dna_profile)

            return dna_profile

        except Exception as e:
            print(f"Error generating Reading DNA: {e}")
            raise

    async def predict_completion_probability(
        self,
        book: Dict[str, Any],
        user_patterns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict likelihood of completing a book.

        Args:
            book: Book to evaluate
            user_patterns: User's reading patterns and history

        Returns:
            Prediction with probability and reasoning
        """
        if not self.client:
            # Simple rule-based fallback
            return self._simple_completion_prediction(book, user_patterns)

        prompt = f"""Predict if this reader will complete a book.

**Book:**
- Title: {book.get('title')}
- Author: {book.get('author')}
- Genre: {book.get('genre')}
- Pages: {book.get('page_count', 'Unknown')}
- Complexity: {book.get('complexity_score', 'Unknown')}/10
- Description: {book.get('description', 'N/A')[:200]}

**Reader's Patterns:**
- Completion rate in {book.get('genre')}: {user_patterns.get('genre_completion_rate', 'Unknown')}%
- Average completed book length: {user_patterns.get('avg_completed_length', 'Unknown')} pages
- Average complexity: {user_patterns.get('avg_complexity', 'Unknown')}/10
- DNF common traits: {user_patterns.get('dnf_patterns', 'None identified')}
- Typical genres: {user_patterns.get('top_genres', [])}

**Task:**
Predict completion probability considering:
1. Genre match with reader's preferences
2. Book length vs reader's typical completed length
3. Complexity vs reader's usual level
4. Similar book outcomes
5. Red flags from DNF patterns

**Output Format (JSON):**
```json
{{
  "probability": 0.85,
  "confidence": "high",
  "match_score": 0.9,
  "reasoning": "Detailed explanation of the prediction",
  "concerns": ["Any potential issue 1", "Any potential issue 2"],
  "strengths": ["Positive indicator 1", "Positive indicator 2"],
  "verdict": "Highly likely to finish" | "Moderate chance" | "Risk of DNF",
  "recommendation": "Go for it!" | "Consider carefully" | "Maybe skip this one"
}}
```

Return ONLY valid JSON."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1536,
                temperature=0.6,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            prediction = json.loads(json_str)

            # Save prediction to database
            self._save_completion_prediction(book.get('id'), prediction)

            return prediction

        except Exception as e:
            print(f"Error predicting completion: {e}")
            return self._simple_completion_prediction(book, user_patterns)

    async def suggest_book_pairing(
        self,
        completed_book: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest a complementary book to read next.

        Args:
            completed_book: Just-completed book

        Returns:
            Pairing suggestion with explanation
        """
        if not self.client:
            return None

        prompt = f"""Suggest a perfect book pairing.

**Just Finished:**
- Title: {completed_book.get('title')}
- Author: {completed_book.get('author')}
- Genre: {completed_book.get('genre')}
- Description: {completed_book.get('description', 'N/A')[:300]}

**Task:**
Suggest ONE complementary book that:
1. Extends the learning (if non-fiction)
2. Provides contrasting perspective (same topic, different angle)
3. Explores similar themes in a different genre
4. Creates meaningful dialogue between the two books

Choose the pairing type most appropriate for this book.

**Output Format (JSON):**
```json
{{
  "paired_book": {{
    "title": "Book Title",
    "author": "Author Name",
    "genre": "Genre"
  }},
  "pairing_type": "learning_followup" | "perspective_flip" | "fiction_nonfiction" | "contrasting",
  "relationship": "How these books relate to each other",
  "why_read_together": "Specific benefits of reading these in sequence",
  "reading_order_matters": true | false,
  "combined_insight": "What reading both books together reveals"
}}
```

Return ONLY valid JSON."""

        try:
            response = await self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1536,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            start = content.find("{")
            end = content.rfind("}") + 1
            json_str = content[start:end]
            pairing = json.loads(json_str)

            return pairing

        except Exception as e:
            print(f"Error suggesting pairing: {e}")
            return None

    # Helper methods

    def _format_books(self, books: List[Dict[str, Any]]) -> str:
        """Format books for prompts."""
        formatted = []
        for i, book in enumerate(books, 1):
            rating = book.get('rating', 'N/A')
            title = book.get('title', 'Unknown')
            author = book.get('author', 'Unknown')
            genre = book.get('genre', 'Unknown')
            formatted.append(f"{i}. \"{title}\" by {author} ({genre}) - Rating: {rating}★")

        return "\n".join(formatted) if formatted else "(No books yet)"

    def _save_mood_session(self, mood_selections: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """Save mood session to database."""
        try:
            book_ids = [r.get('title', '') for r in recommendations]  # Would need to lookup actual IDs
            query = """
                INSERT INTO mood_sessions (selected_moods, recommendations_generated)
                VALUES (?, ?)
            """
            execute_query(query, (json.dumps(mood_selections), json.dumps(book_ids)))
        except Exception as e:
            print(f"Error saving mood session: {e}")

    def _save_dna_profile(self, dna_profile: Dict[str, Any]):
        """Save Reading DNA profile to database."""
        try:
            query = """
                INSERT INTO reading_dna_profile (
                    character_vs_plot_score, pacing_preference, narrative_style_preference,
                    complexity_comfort_level, favorite_themes, writing_style_preferences,
                    profile_summary, ai_generated_narrative
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                dna_profile.get('character_vs_plot_score'),
                json.dumps(dna_profile.get('narrative_preferences', {})),
                json.dumps(dna_profile.get('narrative_preferences', {})),
                dna_profile.get('complexity_profile', {}).get('comfort_level'),
                json.dumps([t['theme'] for t in dna_profile.get('thematic_dna', [])[:5]]),
                json.dumps(dna_profile.get('writing_style_preferences', {})),
                dna_profile.get('reading_personality_summary', ''),
                dna_profile.get('reading_personality_summary', '')
            )
            execute_query(query, params)
        except Exception as e:
            print(f"Error saving DNA profile: {e}")

    def _save_completion_prediction(self, book_id: int, prediction: Dict[str, Any]):
        """Save completion prediction to database."""
        try:
            query = """
                INSERT INTO completion_predictions (
                    book_id, predicted_probability, reasoning, confidence_level
                ) VALUES (?, ?, ?, ?)
            """
            params = (
                book_id,
                prediction.get('probability', 0.5),
                prediction.get('reasoning', ''),
                prediction.get('confidence', 'medium')
            )
            execute_query(query, params)
        except Exception as e:
            print(f"Error saving prediction: {e}")

    def _simple_completion_prediction(self, book: Dict[str, Any], user_patterns: Dict[str, Any]) -> Dict[str, Any]:
        """Simple rule-based completion prediction fallback."""
        probability = 0.7  # Default

        # Adjust based on genre match
        if book.get('genre') in user_patterns.get('top_genres', []):
            probability += 0.1

        # Adjust based on length
        avg_length = user_patterns.get('avg_completed_length', 300)
        book_length = book.get('page_count', avg_length)

        if book_length <= avg_length * 1.2:
            probability += 0.1
        elif book_length > avg_length * 1.5:
            probability -= 0.2

        probability = max(0.1, min(0.95, probability))

        return {
            "probability": probability,
            "confidence": "low",
            "reasoning": "Simple rule-based prediction (AI unavailable)",
            "verdict": "Moderate chance" if probability > 0.6 else "Uncertain"
        }
