"""
Signal Generation Engine
Generates investment signals based on news, sentiment, and market data

This engine combines multiple factors to identify potential investment opportunities:
- News catalysts (earnings, M&A, FDA, contracts, etc.)
- Sentiment analysis scores
- Technical indicators (RSI, MACD, price trends)
- Market context (sector performance, volume)
- Risk assessment

Generates two types of signals:
1. SHORT-TERM (3-14 days): Quick momentum plays
2. LONG-TERM (30-180 days): Fundamental value plays
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random

from src.utils.logger import get_logger
from src.config.config_loader import get_config
from src.scrapers.news_scraper import NewsAggregator, NewsArticle
from src.analysis.sentiment_analyzer import ArticleAnalyzer, SentimentType
from src.scrapers.market_data_collector import MarketDataService


logger = get_logger("signal_generator")


# ============================================================================
# ENUMS
# ============================================================================

class SignalType(str, Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class SignalStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"


# ============================================================================
# SIGNAL RULES ENGINE
# ============================================================================

class SignalRulesEngine:
    """
    Rule-based engine for generating investment signals
    Uses a scoring system to identify opportunities
    """

    def __init__(self):
        self.logger = logger
        self.config = get_config()

        # Load thresholds from config
        self.min_confidence = self.config.get('signals.short_term.min_confidence', 60)
        self.min_sentiment_strength = self.config.get('sentiment.strong_sentiment_threshold', 0.6)

    def evaluate_news_catalyst(
        self,
        article: NewsArticle,
        sentiment_result: Dict
    ) -> Dict:
        """
        Evaluate if news article is a strong catalyst

        Args:
            article: News article
            sentiment_result: Sentiment analysis results

        Returns:
            Catalyst evaluation with score
        """
        score = 0
        factors = []

        # 1. Sentiment strength (0-30 points)
        sentiment_score = abs(sentiment_result.get('sentiment_score', 0))
        if sentiment_score >= 0.7:
            score += 30
            factors.append("Very strong sentiment")
        elif sentiment_score >= 0.5:
            score += 20
            factors.append("Strong sentiment")
        elif sentiment_score >= 0.3:
            score += 10
            factors.append("Moderate sentiment")

        # 2. Event type importance (0-25 points)
        event_type = sentiment_result.get('event_type')
        event_scores = {
            'fda': 25,  # FDA approval = major catalyst
            'm&a': 25,  # Merger/acquisition = major catalyst
            'earnings': 20,  # Earnings beat = strong catalyst
            'contract': 15,  # Contract win = moderate catalyst
            'product': 15,  # Product launch = moderate catalyst
            'analyst': 10,  # Analyst upgrade = minor catalyst
        }

        if event_type in event_scores:
            event_score = event_scores[event_type]
            score += event_score
            factors.append(f"{event_type.upper()} event detected")

        # 3. Relevance (0-20 points)
        relevance = sentiment_result.get('relevance_score', 0)
        if relevance >= 0.8:
            score += 20
            factors.append("Highly relevant to trading")
        elif relevance >= 0.5:
            score += 10
            factors.append("Moderately relevant")

        # 4. Impact magnitude (0-15 points)
        impact = sentiment_result.get('impact_magnitude', 'minor')
        if impact == 'major':
            score += 15
            factors.append("Major impact expected")
        elif impact == 'moderate':
            score += 10
            factors.append("Moderate impact expected")
        elif impact == 'minor':
            score += 5
            factors.append("Minor impact expected")

        # 5. Recency (0-10 points)
        hours_old = (datetime.now() - article.published_date).total_seconds() / 3600
        if hours_old <= 2:
            score += 10
            factors.append("Breaking news (< 2 hours)")
        elif hours_old <= 24:
            score += 5
            factors.append("Recent news (< 24 hours)")

        return {
            'catalyst_score': score,
            'max_score': 100,
            'factors': factors,
            'is_strong_catalyst': score >= 60
        }

    def evaluate_technical_setup(
        self,
        ticker: str,
        market_data: Dict,
        indicators: Optional[Dict]
    ) -> Dict:
        """
        Evaluate technical setup for entry

        Args:
            ticker: Stock ticker
            market_data: Current market data
            indicators: Technical indicators

        Returns:
            Technical evaluation with score
        """
        score = 0
        factors = []
        signals = []

        if not market_data or not indicators:
            return {
                'technical_score': 0,
                'max_score': 100,
                'factors': ['Insufficient technical data'],
                'signals': []
            }

        current_price = market_data.get('current_price')
        if not current_price:
            return {
                'technical_score': 0,
                'max_score': 100,
                'factors': ['No price data'],
                'signals': []
            }

        # 1. RSI Analysis (0-25 points)
        rsi = indicators.get('rsi')
        if rsi:
            if 30 <= rsi <= 40:
                score += 25
                factors.append(f"RSI oversold recovery zone ({rsi:.1f})")
                signals.append("RSI_OVERSOLD_RECOVERY")
            elif 40 < rsi <= 60:
                score += 15
                factors.append(f"RSI neutral ({rsi:.1f})")
                signals.append("RSI_NEUTRAL")
            elif 60 < rsi <= 70:
                score += 10
                factors.append(f"RSI moderately overbought ({rsi:.1f})")
            elif rsi > 70:
                score -= 10
                factors.append(f"RSI overbought - caution ({rsi:.1f})")
                signals.append("RSI_OVERBOUGHT")

        # 2. MACD Analysis (0-25 points)
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        if macd is not None and macd_signal is not None:
            if macd > macd_signal and macd > 0:
                score += 25
                factors.append("MACD bullish crossover above zero")
                signals.append("MACD_BULLISH")
            elif macd > macd_signal:
                score += 15
                factors.append("MACD bullish crossover")
                signals.append("MACD_CROSSOVER_UP")
            elif macd < macd_signal and macd < 0:
                score -= 10
                factors.append("MACD bearish")
                signals.append("MACD_BEARISH")

        # 3. Moving Average Analysis (0-25 points)
        sma_20 = indicators.get('sma_20')
        sma_50 = indicators.get('sma_50')
        sma_200 = indicators.get('sma_200')

        if sma_20 and sma_50:
            if current_price > sma_20 > sma_50:
                score += 25
                factors.append("Price above SMA20 and SMA50 - uptrend")
                signals.append("UPTREND")
            elif current_price > sma_20:
                score += 15
                factors.append("Price above SMA20")
                signals.append("ABOVE_SMA20")
            elif current_price < sma_20:
                score += 5
                factors.append("Price below SMA20 - potential bounce play")

        if sma_200:
            if current_price > sma_200:
                score += 10
                factors.append(f"Above 200-day MA - long-term uptrend")
                signals.append("ABOVE_SMA200")

        # 4. Volume Analysis (0-15 points)
        volume = market_data.get('volume', 0)
        avg_volume = market_data.get('avg_volume', 1)
        if avg_volume > 0:
            volume_ratio = volume / avg_volume
            if volume_ratio > 2.0:
                score += 15
                factors.append(f"High volume ({volume_ratio:.1f}x average)")
                signals.append("HIGH_VOLUME")
            elif volume_ratio > 1.5:
                score += 10
                factors.append(f"Above average volume ({volume_ratio:.1f}x)")
                signals.append("ABOVE_AVG_VOLUME")

        # 5. Price Action (0-10 points)
        change_pct = market_data.get('change_percent', 0)
        if change_pct > 0:
            score += 10
            factors.append(f"Positive momentum ({change_pct:+.2f}%)")
            signals.append("POSITIVE_MOMENTUM")

        return {
            'technical_score': min(score, 100),
            'max_score': 100,
            'factors': factors,
            'signals': signals
        }

    def calculate_price_targets(
        self,
        current_price: float,
        sentiment_score: float,
        catalyst_score: int,
        technical_score: int,
        signal_type: SignalType,
        event_type: Optional[str] = None
    ) -> Dict:
        """
        Calculate entry, target, and stop-loss prices

        Args:
            current_price: Current stock price
            sentiment_score: Sentiment score (-1 to 1)
            catalyst_score: Catalyst strength score
            technical_score: Technical setup score
            signal_type: Short-term or long-term
            event_type: Type of catalyst

        Returns:
            Price targets and expected gains
        """
        # Base gain expectations by signal type
        if signal_type == SignalType.SHORT_TERM:
            base_gain = 5.0  # 5% base for short-term
            max_gain = 20.0  # Cap at 20%
            stop_loss_pct = 3.0  # 3% stop loss
        else:  # LONG_TERM
            base_gain = 10.0  # 10% base for long-term
            max_gain = 50.0  # Cap at 50%
            stop_loss_pct = 8.0  # 8% stop loss

        # Adjust based on catalyst strength
        catalyst_multiplier = 1.0 + (catalyst_score / 100) * 0.5  # Up to 1.5x

        # Adjust based on sentiment strength
        sentiment_multiplier = 1.0 + abs(sentiment_score) * 0.3  # Up to 1.3x

        # Adjust based on technical setup
        technical_multiplier = 1.0 + (technical_score / 100) * 0.3  # Up to 1.3x

        # Special multipliers for event types
        event_multipliers = {
            'fda': 1.5,  # FDA approvals can have huge moves
            'm&a': 1.4,  # M&A often has defined upside
            'earnings': 1.2,
            'contract': 1.1,
        }
        event_multiplier = event_multipliers.get(event_type, 1.0)

        # Calculate expected gains
        conservative_gain = base_gain * catalyst_multiplier
        moderate_gain = base_gain * catalyst_multiplier * sentiment_multiplier
        aggressive_gain = base_gain * catalyst_multiplier * sentiment_multiplier * technical_multiplier * event_multiplier

        # Cap the gains
        conservative_gain = min(conservative_gain, max_gain * 0.5)
        moderate_gain = min(moderate_gain, max_gain * 0.75)
        aggressive_gain = min(aggressive_gain, max_gain)

        # Calculate prices
        entry_price = current_price
        target_conservative = entry_price * (1 + conservative_gain / 100)
        target_moderate = entry_price * (1 + moderate_gain / 100)
        target_aggressive = entry_price * (1 + aggressive_gain / 100)
        stop_loss = entry_price * (1 - stop_loss_pct / 100)

        return {
            'entry_price': round(entry_price, 2),
            'target_conservative': round(target_conservative, 2),
            'target_moderate': round(target_moderate, 2),
            'target_aggressive': round(target_aggressive, 2),
            'stop_loss': round(stop_loss, 2),
            'expected_gain_conservative': round(conservative_gain, 2),
            'expected_gain_moderate': round(moderate_gain, 2),
            'expected_gain_aggressive': round(aggressive_gain, 2),
            'stop_loss_pct': round(stop_loss_pct, 2),
        }

    def identify_risk_factors(
        self,
        ticker: str,
        market_data: Dict,
        indicators: Optional[Dict],
        sentiment_result: Dict
    ) -> List[str]:
        """
        Identify potential risk factors

        Args:
            ticker: Stock ticker
            market_data: Market data
            indicators: Technical indicators
            sentiment_result: Sentiment analysis

        Returns:
            List of risk factors
        """
        risks = []

        # 1. Technical risks
        if indicators:
            rsi = indicators.get('rsi')
            if rsi and rsi > 75:
                risks.append("Extremely overbought (RSI > 75) - potential pullback")

            current_price = market_data.get('current_price')
            bb_upper = indicators.get('bb_upper')
            if current_price and bb_upper and current_price > bb_upper:
                risks.append("Price above upper Bollinger Band - overextended")

        # 2. Volume risks
        volume = market_data.get('volume', 0)
        avg_volume = market_data.get('avg_volume', 1)
        if avg_volume > 0 and volume < avg_volume * 0.5:
            risks.append("Low volume - lack of conviction")

        # 3. Market cap risks
        market_cap = market_data.get('market_cap')
        if market_cap:
            if market_cap < 300_000_000:  # < $300M
                risks.append("Small cap stock - higher volatility and risk")
            elif market_cap < 2_000_000_000:  # < $2B
                risks.append("Mid cap stock - moderate volatility")

        # 4. Sentiment risks
        if sentiment_result.get('sentiment_type') == 'negative':
            risks.append("Negative sentiment - potential reversal play (higher risk)")

        confidence = sentiment_result.get('sentiment_confidence', 0)
        if confidence < 0.3:
            risks.append("Low sentiment confidence - unclear market reaction")

        # 5. Price action risks
        change_pct = market_data.get('change_percent', 0)
        if abs(change_pct) > 10:
            risks.append(f"Large intraday move ({change_pct:+.1f}%) - potential volatility")

        # General risks
        risks.append("Past performance does not guarantee future results")
        risks.append("News may already be priced in")
        risks.append("Market conditions can change rapidly")

        return risks


# ============================================================================
# SIGNAL GENERATOR
# ============================================================================

class SignalGenerator:
    """
    Main signal generator that combines all analysis
    """

    def __init__(self):
        self.logger = logger
        self.rules_engine = SignalRulesEngine()
        self.news_aggregator = NewsAggregator()
        self.article_analyzer = ArticleAnalyzer()
        self.market_service = MarketDataService()

    def generate_signal_from_news(
        self,
        article: NewsArticle,
        ticker: str
    ) -> Optional[Dict]:
        """
        Generate a signal from a news article

        Args:
            article: News article
            ticker: Stock ticker

        Returns:
            Signal dictionary or None
        """
        try:
            self.logger.info(f"Generating signal for {ticker} from news: {article.title[:50]}...")

            # 1. Analyze sentiment
            sentiment_result = self.article_analyzer.analyze_article(
                article.title,
                article.content,
                [ticker]
            )

            # Skip if sentiment is neutral and weak
            if (sentiment_result['sentiment_type'] == 'neutral' and
                sentiment_result['sentiment_confidence'] < 0.3):
                self.logger.debug(f"Skipping {ticker} - weak neutral sentiment")
                return None

            # 2. Evaluate news catalyst
            catalyst_eval = self.rules_engine.evaluate_news_catalyst(article, sentiment_result)

            # Skip if not a strong catalyst
            if not catalyst_eval['is_strong_catalyst']:
                self.logger.debug(f"Skipping {ticker} - weak catalyst (score: {catalyst_eval['catalyst_score']})")
                return None

            # 3. Get market data
            market_data = self.market_service.stock_collector.get_quote(ticker)
            if not market_data or not market_data.get('current_price'):
                self.logger.warning(f"Could not fetch market data for {ticker}")
                return None

            # 4. Get technical indicators
            indicators = self.market_service.indicator_calculator.get_latest_indicators(ticker)

            # 5. Evaluate technical setup
            technical_eval = self.rules_engine.evaluate_technical_setup(
                ticker,
                market_data,
                indicators
            )

            # 6. Calculate overall confidence
            # Weighted average: catalyst 40%, technical 30%, sentiment 30%
            catalyst_score = catalyst_eval['catalyst_score']
            technical_score = technical_eval['technical_score']
            sentiment_confidence = sentiment_result['sentiment_confidence'] * 100

            confidence = (
                catalyst_score * 0.4 +
                technical_score * 0.3 +
                sentiment_confidence * 0.3
            )

            # Skip if confidence too low
            min_confidence = self.rules_engine.min_confidence
            if confidence < min_confidence:
                self.logger.debug(f"Skipping {ticker} - low confidence ({confidence:.1f}% < {min_confidence}%)")
                return None

            # 7. Determine signal type and timeframe
            event_type = sentiment_result.get('event_type')

            # High-impact events = short-term momentum plays
            # Lower-impact events = longer-term plays
            if event_type in ['fda', 'm&a', 'earnings'] and catalyst_score >= 70:
                signal_type = SignalType.SHORT_TERM
                timeframe_days = 7 if event_type == 'earnings' else 14
            else:
                signal_type = SignalType.LONG_TERM
                timeframe_days = 90

            # 8. Calculate price targets
            price_targets = self.rules_engine.calculate_price_targets(
                current_price=market_data['current_price'],
                sentiment_score=sentiment_result['sentiment_score'],
                catalyst_score=catalyst_score,
                technical_score=technical_score,
                signal_type=signal_type,
                event_type=event_type
            )

            # 9. Identify risk factors
            risks = self.rules_engine.identify_risk_factors(
                ticker,
                market_data,
                indicators,
                sentiment_result
            )

            # 10. Build rationale
            rationale = self._build_rationale(
                article,
                sentiment_result,
                catalyst_eval,
                technical_eval,
                market_data
            )

            # 11. Create signal
            signal = {
                'timestamp': datetime.now(),
                'ticker': ticker,
                'company_name': market_data.get('company_name', ticker),
                'signal_type': signal_type.value,
                'timeframe_days': timeframe_days,
                'expiry_date': datetime.now() + timedelta(days=timeframe_days),

                # Prices
                'entry_price': price_targets['entry_price'],
                'current_price_at_signal': market_data['current_price'],
                'target_price': price_targets['target_moderate'],
                'target_conservative': price_targets['target_conservative'],
                'target_aggressive': price_targets['target_aggressive'],
                'stop_loss': price_targets['stop_loss'],

                # Expected gains
                'expected_gain_pct': price_targets['expected_gain_moderate'],
                'expected_gain_conservative': price_targets['expected_gain_conservative'],
                'expected_gain_moderate': price_targets['expected_gain_moderate'],
                'expected_gain_aggressive': price_targets['expected_gain_aggressive'],

                # Confidence and risk
                'confidence': round(confidence, 1),
                'risk_score': round(100 - confidence, 1),
                'risk_factors': risks,

                # Rationale
                'rationale': rationale,
                'catalyst_type': event_type,
                'news_article_id': article.hash,
                'news_title': article.title,
                'news_url': article.url,

                # Supporting data
                'supporting_data': {
                    'sentiment_score': sentiment_result['sentiment_score'],
                    'sentiment_type': sentiment_result['sentiment_type'],
                    'catalyst_score': catalyst_score,
                    'technical_score': technical_score,
                    'catalyst_factors': catalyst_eval['factors'],
                    'technical_factors': technical_eval['factors'],
                    'technical_signals': technical_eval['signals'],
                },

                # Status
                'status': 'active',
            }

            self.logger.info(f"✓ Generated {signal_type.value} signal for {ticker}: "
                           f"{confidence:.1f}% confidence, "
                           f"{price_targets['expected_gain_moderate']:.1f}% expected gain")

            return signal

        except Exception as e:
            self.logger.error(f"Error generating signal for {ticker}: {e}")
            return None

    def _build_rationale(
        self,
        article: NewsArticle,
        sentiment_result: Dict,
        catalyst_eval: Dict,
        technical_eval: Dict,
        market_data: Dict
    ) -> str:
        """Build detailed rationale for the signal"""

        parts = []

        # News catalyst
        parts.append(f"**NEWS CATALYST:** {article.title}")
        parts.append(f"Sentiment: {sentiment_result['sentiment_type'].upper()} "
                    f"({sentiment_result['sentiment_score']:+.2f})")

        if catalyst_eval['factors']:
            parts.append("Catalyst Factors:")
            for factor in catalyst_eval['factors'][:3]:
                parts.append(f"  • {factor}")

        # Technical setup
        if technical_eval['factors']:
            parts.append("\n**TECHNICAL SETUP:**")
            for factor in technical_eval['factors'][:3]:
                parts.append(f"  • {factor}")

        # Price context
        current_price = market_data.get('current_price')
        change_pct = market_data.get('change_percent')
        if current_price and change_pct:
            parts.append(f"\n**CURRENT PRICE:** ${current_price:.2f} ({change_pct:+.2f}% today)")

        return "\n".join(parts)

    def scan_for_signals(
        self,
        max_signals: int = 10,
        use_newsapi: bool = False
    ) -> List[Dict]:
        """
        Scan news for potential signals

        Args:
            max_signals: Maximum number of signals to generate
            use_newsapi: Whether to use NewsAPI (consumes quota)

        Returns:
            List of generated signals
        """
        self.logger.info("Scanning for investment signals...")

        # Fetch latest news
        articles = self.news_aggregator.fetch_latest_news(
            max_articles=50,
            use_newsapi=use_newsapi
        )

        self.logger.info(f"Analyzing {len(articles)} news articles...")

        signals = []

        for article in articles:
            # Only process articles with tickers
            if not article.tickers:
                continue

            # Process each ticker mentioned
            for ticker in article.tickers[:2]:  # Max 2 tickers per article
                signal = self.generate_signal_from_news(article, ticker)

                if signal:
                    signals.append(signal)

                    if len(signals) >= max_signals:
                        self.logger.info(f"Reached max signals limit ({max_signals})")
                        return signals

        self.logger.info(f"Generated {len(signals)} signals from {len(articles)} articles")
        return signals


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test signal generation"""
    print("=" * 70)
    print("Signal Generator Test")
    print("=" * 70)
    print()

    generator = SignalGenerator()

    print("Scanning for signals (this may take a minute)...")
    signals = generator.scan_for_signals(max_signals=5, use_newsapi=False)

    if not signals:
        print("No signals generated. Try again later when there's more market-moving news.")
        return

    print(f"\nGenerated {len(signals)} signals:\n")

    for i, signal in enumerate(signals, 1):
        print(f"{i}. {signal['ticker']} - {signal['signal_type'].upper()}")
        print(f"   Catalyst: {signal['news_title'][:60]}...")
        print(f"   Confidence: {signal['confidence']:.1f}%")
        print(f"   Entry: ${signal['entry_price']:.2f}")
        print(f"   Target: ${signal['target_price']:.2f} ({signal['expected_gain_pct']:+.1f}%)")
        print(f"   Stop Loss: ${signal['stop_loss']:.2f}")
        print(f"   Timeframe: {signal['timeframe_days']} days")
        print()


if __name__ == "__main__":
    main()
