"""
Sentiment Analysis Engine
Uses FREE local NLP libraries - no API costs!
- VADER: Financial text sentiment (free, local)
- TextBlob: Backup sentiment analysis (free, local)
- Optional: FinBERT transformer model (free, runs locally)
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum

# Free NLP libraries
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob

from src.utils.logger import get_logger
from src.utils.helpers import clean_text
from src.config.config_loader import get_config


logger = get_logger("sentiment_analyzer")


# ============================================================================
# ENUMS
# ============================================================================

class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class ImpactMagnitude(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"


# ============================================================================
# FINANCIAL KEYWORDS (For enhanced analysis)
# ============================================================================

# Positive indicators
POSITIVE_KEYWORDS = {
    # Earnings
    "beat earnings", "exceeded expectations", "strong earnings", "record profit",
    "revenue growth", "earnings beat", "profit surge", "robust growth",

    # Performance
    "outperform", "rally", "surge", "soar", "jump", "climb", "gain", "rise",
    "bullish", "upgrade", "raised guidance", "positive outlook",

    # M&A
    "acquisition", "merger", "buyout", "takeover", "strategic partnership",

    # Products/Innovation
    "breakthrough", "innovation", "approved", "launched", "won contract",
    "major deal", "partnership", "expansion",

    # Market
    "all-time high", "market leader", "dominant position", "competitive advantage"
}

# Negative indicators
NEGATIVE_KEYWORDS = {
    # Earnings
    "missed earnings", "below expectations", "weak earnings", "loss",
    "revenue decline", "earnings miss", "profit warning", "poor results",

    # Performance
    "underperform", "plunge", "crash", "drop", "fall", "decline", "slump",
    "bearish", "downgrade", "lowered guidance", "negative outlook",

    # Problems
    "lawsuit", "investigation", "recall", "scandal", "fraud", "bankruptcy",
    "layoff", "restructuring", "chapter 11", "default",

    # Market
    "regulatory issues", "compliance failure", "missed deadline", "delayed",
    "competition", "market share loss", "pressure"
}

# Event type keywords
EVENT_KEYWORDS = {
    "earnings": ["earnings", "eps", "revenue", "profit", "quarterly results", "q1", "q2", "q3", "q4"],
    "m&a": ["merger", "acquisition", "buyout", "takeover", "acquired", "merge"],
    "fda": ["fda", "approval", "clinical trial", "drug", "therapy", "phase"],
    "contract": ["contract", "deal", "agreement", "partnership", "signed"],
    "product": ["launched", "release", "product", "innovation", "announced"],
    "analyst": ["upgrade", "downgrade", "rating", "price target", "analyst"],
    "insider": ["insider", "ceo", "cfo", "executive", "director", "bought", "sold"],
    "legal": ["lawsuit", "investigation", "settlement", "regulatory"],
}


# ============================================================================
# SENTIMENT ANALYZER
# ============================================================================

class SentimentAnalyzer:
    """
    Financial sentiment analyzer using free local tools
    """

    def __init__(self):
        self.logger = logger

        # Initialize VADER (best for social media and news)
        self.vader = SentimentIntensityAnalyzer()

        # Load config
        self.config = get_config()
        self.positive_threshold = self.config.get('sentiment.positive_threshold', 0.3)
        self.negative_threshold = self.config.get('sentiment.negative_threshold', -0.3)

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of text using multiple methods

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment analysis results
        """
        if not text:
            return self._empty_result()

        text = clean_text(text)

        # 1. VADER Sentiment (compound score from -1 to 1)
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores['compound']

        # 2. TextBlob Sentiment (polarity from -1 to 1)
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity

        # 3. Keyword-based sentiment boost
        keyword_score = self._analyze_keywords(text.lower())

        # 4. Combine scores (VADER gets most weight as it's best for financial news)
        combined_score = (
            vader_compound * 0.5 +
            textblob_polarity * 0.3 +
            keyword_score * 0.2
        )

        # Determine sentiment type
        sentiment_type = self._classify_sentiment(combined_score)

        # Calculate confidence
        confidence = abs(combined_score)

        return {
            "sentiment_score": combined_score,
            "sentiment_type": sentiment_type.value,
            "confidence": confidence,
            "vader_score": vader_compound,
            "textblob_score": textblob_polarity,
            "keyword_score": keyword_score,
            "vader_breakdown": vader_scores,
        }

    def _classify_sentiment(self, score: float) -> SentimentType:
        """Classify sentiment based on score"""
        if score >= self.positive_threshold:
            return SentimentType.POSITIVE
        elif score <= self.negative_threshold:
            return SentimentType.NEGATIVE
        else:
            return SentimentType.NEUTRAL

    def _analyze_keywords(self, text: str) -> float:
        """
        Analyze financial keywords in text

        Returns:
            Score from -1 to 1 based on keywords found
        """
        text_lower = text.lower()

        positive_count = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text_lower)
        negative_count = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return 0.0

        # Calculate score
        score = (positive_count - negative_count) / total
        return max(-1.0, min(1.0, score))

    def analyze_title_and_content(
        self,
        title: str,
        content: str
    ) -> Dict:
        """
        Analyze both title and content, giving more weight to title

        Args:
            title: Article title
            content: Article content

        Returns:
            Combined sentiment analysis
        """
        title_sentiment = self.analyze_text(title)
        content_sentiment = self.analyze_text(content)

        # Title gets more weight (2x)
        combined_score = (
            title_sentiment["sentiment_score"] * 0.6 +
            content_sentiment["sentiment_score"] * 0.4
        )

        sentiment_type = self._classify_sentiment(combined_score)
        confidence = abs(combined_score)

        return {
            "sentiment_score": combined_score,
            "sentiment_type": sentiment_type.value,
            "confidence": confidence,
            "title_sentiment": title_sentiment,
            "content_sentiment": content_sentiment,
        }

    def detect_event_type(self, text: str) -> Tuple[Optional[str], float]:
        """
        Detect what type of event this news is about

        Args:
            text: Text to analyze

        Returns:
            Tuple of (event_type, confidence)
        """
        text_lower = text.lower()
        event_scores = {}

        for event_type, keywords in EVENT_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                event_scores[event_type] = score

        if not event_scores:
            return None, 0.0

        # Get event with highest score
        best_event = max(event_scores, key=event_scores.get)
        confidence = min(1.0, event_scores[best_event] / 3.0)  # Normalize

        return best_event, confidence

    def estimate_impact_magnitude(
        self,
        sentiment_score: float,
        event_type: Optional[str] = None
    ) -> ImpactMagnitude:
        """
        Estimate the magnitude of impact on stock price

        Args:
            sentiment_score: Sentiment score (-1 to 1)
            event_type: Type of event (affects impact)

        Returns:
            Impact magnitude
        """
        # Base impact from sentiment strength
        abs_sentiment = abs(sentiment_score)

        # Event type multipliers
        multipliers = self.config.get('sentiment.impact_multipliers', {})
        multiplier = multipliers.get(event_type, 1.0) if event_type else 1.0

        # Calculate adjusted impact
        impact = abs_sentiment * multiplier

        # Classify magnitude
        if impact >= 0.7:
            return ImpactMagnitude.MAJOR
        elif impact >= 0.4:
            return ImpactMagnitude.MODERATE
        else:
            return ImpactMagnitude.MINOR

    def _empty_result(self) -> Dict:
        """Return empty result for invalid input"""
        return {
            "sentiment_score": 0.0,
            "sentiment_type": SentimentType.NEUTRAL.value,
            "confidence": 0.0,
            "vader_score": 0.0,
            "textblob_score": 0.0,
            "keyword_score": 0.0,
            "vader_breakdown": {"pos": 0, "neu": 1, "neg": 0, "compound": 0},
        }


# ============================================================================
# ARTICLE ANALYZER (Combines sentiment + event detection)
# ============================================================================

class ArticleAnalyzer:
    """
    Complete article analyzer
    Combines sentiment analysis with event detection and impact estimation
    """

    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.logger = logger

    def analyze_article(
        self,
        title: str,
        content: str,
        tickers: Optional[List[str]] = None
    ) -> Dict:
        """
        Complete analysis of a news article

        Args:
            title: Article title
            content: Article content
            tickers: List of mentioned tickers

        Returns:
            Complete analysis results
        """
        # Sentiment analysis
        sentiment = self.sentiment_analyzer.analyze_title_and_content(title, content)

        # Event type detection
        event_text = f"{title} {content}"
        event_type, event_confidence = self.sentiment_analyzer.detect_event_type(event_text)

        # Impact magnitude
        impact = self.sentiment_analyzer.estimate_impact_magnitude(
            sentiment["sentiment_score"],
            event_type
        )

        # Relevance score (how relevant is this to stock trading)
        relevance = self._calculate_relevance(
            tickers=tickers,
            event_type=event_type,
            sentiment_confidence=sentiment["confidence"]
        )

        return {
            "sentiment_score": sentiment["sentiment_score"],
            "sentiment_type": sentiment["sentiment_type"],
            "sentiment_confidence": sentiment["confidence"],
            "event_type": event_type,
            "event_confidence": event_confidence,
            "impact_magnitude": impact.value,
            "relevance_score": relevance,
            "tickers_mentioned": tickers or [],
            "details": sentiment
        }

    def _calculate_relevance(
        self,
        tickers: Optional[List[str]] = None,
        event_type: Optional[str] = None,
        sentiment_confidence: float = 0.0
    ) -> float:
        """
        Calculate relevance score (0-1) for trading decisions

        Args:
            tickers: Mentioned tickers
            event_type: Event type
            sentiment_confidence: Sentiment confidence

        Returns:
            Relevance score 0-1
        """
        score = 0.0

        # Has tickers mentioned = more relevant
        if tickers and len(tickers) > 0:
            score += 0.4

        # Has identifiable event type = more relevant
        if event_type:
            score += 0.3

        # Strong sentiment = more relevant
        score += sentiment_confidence * 0.3

        return min(1.0, score)

    def analyze_sentiment_velocity(
        self,
        articles: List[Dict],
        ticker: str,
        window_hours: int = 24
    ) -> Dict:
        """
        Analyze how fast sentiment is changing for a ticker

        Args:
            articles: List of analyzed articles (with timestamps)
            ticker: Ticker symbol
            window_hours: Time window to analyze

        Returns:
            Sentiment velocity metrics
        """
        # Filter articles for this ticker within time window
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(hours=window_hours)

        relevant_articles = [
            a for a in articles
            if ticker in a.get("tickers_mentioned", [])
            and a.get("published_date", datetime.now()) >= cutoff
        ]

        if len(relevant_articles) < 2:
            return {
                "velocity": 0.0,
                "direction": "neutral",
                "article_count": len(relevant_articles)
            }

        # Sort by time
        relevant_articles.sort(key=lambda x: x.get("published_date", datetime.now()))

        # Calculate average sentiment over time
        sentiments = [a.get("sentiment_score", 0.0) for a in relevant_articles]
        avg_sentiment = sum(sentiments) / len(sentiments)

        # Calculate velocity (change over time)
        # Recent half vs older half
        mid = len(sentiments) // 2
        older_avg = sum(sentiments[:mid]) / mid if mid > 0 else 0
        recent_avg = sum(sentiments[mid:]) / (len(sentiments) - mid)

        velocity = recent_avg - older_avg

        # Determine direction
        if velocity > 0.2:
            direction = "improving"
        elif velocity < -0.2:
            direction = "deteriorating"
        else:
            direction = "stable"

        return {
            "velocity": velocity,
            "direction": direction,
            "article_count": len(relevant_articles),
            "avg_sentiment": avg_sentiment,
            "recent_sentiment": recent_avg,
            "older_sentiment": older_avg
        }


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test sentiment analysis"""
    print("=" * 60)
    print("Sentiment Analyzer Test (FREE local models)")
    print("=" * 60)

    analyzer = ArticleAnalyzer()

    # Test cases
    test_articles = [
        {
            "title": "Apple beats earnings expectations with strong iPhone sales",
            "content": "Apple Inc. reported quarterly earnings that exceeded analyst expectations, driven by robust iPhone sales and services revenue growth.",
            "tickers": ["AAPL"]
        },
        {
            "title": "Tesla faces regulatory investigation over safety concerns",
            "content": "Federal regulators have opened an investigation into Tesla's autopilot system following multiple accidents. The company's stock declined in after-hours trading.",
            "tickers": ["TSLA"]
        },
        {
            "title": "FDA approves new cancer drug from Moderna",
            "content": "The FDA has granted approval for Moderna's breakthrough cancer therapy, marking a major milestone for the biotech company.",
            "tickers": ["MRNA"]
        }
    ]

    for i, article in enumerate(test_articles, 1):
        print(f"\nTest {i}: {article['title']}")
        print("-" * 60)

        result = analyzer.analyze_article(
            title=article["title"],
            content=article["content"],
            tickers=article["tickers"]
        )

        print(f"Sentiment: {result['sentiment_type']} ({result['sentiment_score']:.3f})")
        print(f"Confidence: {result['sentiment_confidence']:.3f}")
        print(f"Event Type: {result['event_type']}")
        print(f"Impact: {result['impact_magnitude']}")
        print(f"Relevance: {result['relevance_score']:.3f}")
        print(f"Tickers: {', '.join(result['tickers_mentioned'])}")

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    main()
