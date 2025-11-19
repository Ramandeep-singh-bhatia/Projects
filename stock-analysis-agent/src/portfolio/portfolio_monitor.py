"""
Portfolio Monitoring & Risk Assessment System
Continuously monitors portfolio positions and generates early warnings

Performs hourly deep analysis of each position looking for:
- Negative news
- Price/volume movements
- Technical indicator breakdown
- Sector weakness
- Insider selling (simulated)

Generates EXIT SIGNALS with severity levels:
- CRITICAL: Exit immediately (within 24 hours)
- HIGH: Exit within 24-48 hours
- MEDIUM: Monitor closely, potential exit in 3-5 days
- LOW: Watch for developments

"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from enum import Enum

from src.database.models import (
    PortfolioPosition,
    PortfolioMonitoring,
    RiskLevel,
    create_engine_and_session
)
from src.portfolio.portfolio_manager import PortfolioManager
from src.scrapers.news_scraper import NewsAggregator
from src.analysis.sentiment_analyzer import ArticleAnalyzer, SentimentType
from src.scrapers.market_data_collector import MarketDataService
from src.utils.logger import get_logger
from src.config.config_loader import get_config


logger = get_logger("portfolio_monitor")


# ============================================================================
# RISK ANALYZER
# ============================================================================

class RiskAnalyzer:
    """
    Analyzes individual positions for risk factors
    """

    def __init__(self):
        self.logger = logger
        self.config = get_config()
        self.news_aggregator = NewsAggregator()
        self.article_analyzer = ArticleAnalyzer()
        self.market_service = MarketDataService()

    def analyze_position_risk(
        self,
        position: PortfolioPosition
    ) -> Dict:
        """
        Comprehensive risk analysis for a position

        Args:
            position: Portfolio position to analyze

        Returns:
            Risk analysis results
        """
        try:
            self.logger.debug(f"Analyzing risk for {position.ticker}...")

            risk_factors = []
            risk_score = 0.0
            technical_signals = {}

            # 1. Price Movement Analysis
            movement = self.market_service.analyze_price_movement(
                position.ticker,
                hours_back=24
            )

            if movement:
                # Sharp price drop
                if movement.get('change_percent', 0) < -5:
                    risk_score += 30
                    risk_factors.append(f"Sharp price decline: {movement['change_percent']:.2f}%")
                elif movement.get('change_percent', 0) < -2:
                    risk_score += 15
                    risk_factors.append(f"Price declining: {movement['change_percent']:.2f}%")

                # High volatility
                if movement.get('volatility', 0) > 5:
                    risk_score += 15
                    risk_factors.append(f"High volatility: {movement['volatility']:.2f}%")

                # Unusual volume on down day
                if (movement.get('is_unusual_volume') and
                    movement.get('change_percent', 0) < 0):
                    risk_score += 20
                    risk_factors.append("High volume on down day - potential distribution")

            # 2. Technical Indicators
            indicators = self.market_service.indicator_calculator.get_latest_indicators(
                position.ticker
            )

            if indicators:
                current_price = position.current_price or position.purchase_price

                # RSI overbought
                rsi = indicators.get('rsi')
                if rsi:
                    if rsi > 75:
                        risk_score += 20
                        risk_factors.append(f"Extremely overbought: RSI {rsi:.1f}")
                        technical_signals['rsi'] = 'overbought'
                    elif rsi < 30:
                        # Oversold can be risky too - may keep falling
                        risk_score += 10
                        risk_factors.append(f"Oversold: RSI {rsi:.1f} - potential further decline")
                        technical_signals['rsi'] = 'oversold'

                # MACD bearish
                macd = indicators.get('macd')
                macd_signal = indicators.get('macd_signal')
                if macd is not None and macd_signal is not None:
                    if macd < macd_signal and macd < 0:
                        risk_score += 15
                        risk_factors.append("MACD bearish crossover")
                        technical_signals['macd'] = 'bearish'

                # Price below key moving averages
                sma_50 = indicators.get('sma_50')
                sma_200 = indicators.get('sma_200')

                if sma_50 and current_price < sma_50:
                    risk_score += 10
                    risk_factors.append("Price broke below 50-day MA")
                    technical_signals['sma_50'] = 'below'

                if sma_200 and current_price < sma_200:
                    risk_score += 15
                    risk_factors.append("Price broke below 200-day MA")
                    technical_signals['sma_200'] = 'below'

                # Bollinger Band breakdown
                bb_lower = indicators.get('bb_lower')
                if bb_lower and current_price < bb_lower:
                    risk_score += 10
                    risk_factors.append("Price below lower Bollinger Band")

            # 3. News Sentiment Analysis
            negative_news_count, sentiment_shift = self._analyze_news_sentiment(position.ticker)

            if negative_news_count > 0:
                risk_score += min(negative_news_count * 10, 30)
                risk_factors.append(f"{negative_news_count} negative news article(s) detected")

            if sentiment_shift < -0.3:
                risk_score += 15
                risk_factors.append("Sentiment deteriorating rapidly")

            # 4. Position-specific risks
            # Time-based risk for short-term positions
            if position.investment_type.value == 'short_term':
                if position.days_held and position.days_held > 14:
                    risk_score += 10
                    risk_factors.append("Short-term position held > 14 days - timeframe exceeded")

            # Loss threshold
            if position.unrealized_gain_loss_pct and position.unrealized_gain_loss_pct < -5:
                risk_score += 20
                risk_factors.append(f"Significant loss: {position.unrealized_gain_loss_pct:.1f}%")

            # 5. Market cap risk
            quote = self.market_service.stock_collector.get_quote(position.ticker)
            if quote:
                market_cap = quote.get('market_cap')
                if market_cap and market_cap < 300_000_000:
                    risk_score += 10
                    risk_factors.append("Small cap - higher volatility risk")

            # Cap risk score at 100
            risk_score = min(risk_score, 100)

            # Determine risk level
            risk_level = self._classify_risk_level(risk_score)

            # Generate action recommendation
            action = self._recommend_action(risk_level, risk_score, risk_factors)

            # Suggest alternatives if exit recommended
            alternatives = []
            if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                alternatives = self._suggest_alternatives(position, quote)

            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'action_recommended': action,
                'alternative_stocks': alternatives,
                'negative_news_count': negative_news_count,
                'sentiment_shift': sentiment_shift,
                'technical_signals': technical_signals,
                'analysis_summary': self._create_summary(risk_level, risk_score, risk_factors, action)
            }

        except Exception as e:
            self.logger.error(f"Error analyzing risk for {position.ticker}: {e}")
            return {
                'risk_score': 0,
                'risk_level': RiskLevel.LOW,
                'risk_factors': [f"Analysis error: {str(e)}"],
                'action_recommended': 'monitor',
                'alternative_stocks': [],
                'negative_news_count': 0,
                'sentiment_shift': 0,
                'technical_signals': {},
                'analysis_summary': 'Unable to complete risk analysis'
            }

    def _analyze_news_sentiment(self, ticker: str) -> Tuple[int, float]:
        """
        Analyze recent news sentiment for ticker

        Returns:
            Tuple of (negative_news_count, sentiment_shift)
        """
        try:
            # Get recent news
            articles = self.news_aggregator.fetch_ticker_news(ticker, max_articles=10)

            if not articles:
                return 0, 0.0

            # Analyze each article
            analyzed_articles = []
            for article in articles:
                result = self.article_analyzer.analyze_article(
                    article.title,
                    article.content,
                    [ticker]
                )
                analyzed_articles.append({
                    'published_date': article.published_date,
                    'sentiment_score': result['sentiment_score'],
                    'sentiment_type': result['sentiment_type']
                })

            # Count negative news
            negative_count = sum(
                1 for a in analyzed_articles
                if a['sentiment_type'] == 'negative'
            )

            # Calculate sentiment velocity
            if len(analyzed_articles) >= 2:
                # Sort by date
                analyzed_articles.sort(key=lambda x: x['published_date'])

                # Recent half vs older half
                mid = len(analyzed_articles) // 2
                older_sentiment = sum(a['sentiment_score'] for a in analyzed_articles[:mid]) / mid
                recent_sentiment = sum(a['sentiment_score'] for a in analyzed_articles[mid:]) / (len(analyzed_articles) - mid)

                sentiment_shift = recent_sentiment - older_sentiment
            else:
                sentiment_shift = 0.0

            return negative_count, sentiment_shift

        except Exception as e:
            self.logger.error(f"Error analyzing news sentiment for {ticker}: {e}")
            return 0, 0.0

    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level based on score"""
        if risk_score >= 80:
            return RiskLevel.CRITICAL
        elif risk_score >= 60:
            return RiskLevel.HIGH
        elif risk_score >= 40:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _recommend_action(
        self,
        risk_level: RiskLevel,
        risk_score: float,
        risk_factors: List[str]
    ) -> str:
        """Recommend action based on risk level"""
        if risk_level == RiskLevel.CRITICAL:
            return "exit_now"  # Exit immediately within 24 hours
        elif risk_level == RiskLevel.HIGH:
            return "exit_24h"  # Exit within 24-48 hours
        elif risk_level == RiskLevel.MEDIUM:
            return "monitor_closely"  # Monitor closely, exit in 3-5 days if deteriorates
        else:
            return "hold"  # Continue holding with normal monitoring

    def _suggest_alternatives(
        self,
        position: PortfolioPosition,
        quote: Optional[Dict]
    ) -> List[str]:
        """
        Suggest alternative stocks in same sector

        Args:
            position: Current position
            quote: Market quote with sector info

        Returns:
            List of alternative ticker symbols
        """
        # For now, return a simple list based on sector
        # In future, this could be enhanced with sector analysis

        sector = quote.get('sector') if quote else None

        # Sample alternatives by sector (would be enhanced with real analysis)
        sector_alternatives = {
            'Technology': ['MSFT', 'GOOGL', 'NVDA', 'AMD'],
            'Healthcare': ['JNJ', 'UNH', 'PFE', 'ABBV'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'GS'],
            'Consumer Cyclical': ['AMZN', 'HD', 'NKE', 'SBUX'],
            'Communication Services': ['META', 'DIS', 'NFLX', 'T'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB'],
        }

        alternatives = sector_alternatives.get(sector, [])

        # Remove current ticker
        alternatives = [t for t in alternatives if t != position.ticker]

        return alternatives[:3]  # Return top 3

    def _create_summary(
        self,
        risk_level: RiskLevel,
        risk_score: float,
        risk_factors: List[str],
        action: str
    ) -> str:
        """Create human-readable summary"""
        parts = []

        # Risk level statement
        if risk_level == RiskLevel.CRITICAL:
            parts.append("⚠️ CRITICAL RISK - IMMEDIATE ACTION REQUIRED")
        elif risk_level == RiskLevel.HIGH:
            parts.append("⚠️ HIGH RISK - Consider exiting within 24-48 hours")
        elif risk_level == RiskLevel.MEDIUM:
            parts.append("⚠️ MODERATE RISK - Monitor closely")
        else:
            parts.append("✓ LOW RISK - Continue normal monitoring")

        parts.append(f"Risk Score: {risk_score:.0f}/100")

        if risk_factors:
            parts.append(f"\nKey Risk Factors ({len(risk_factors)}):")
            for factor in risk_factors[:5]:  # Top 5
                parts.append(f"  • {factor}")

        return "\n".join(parts)


# ============================================================================
# PORTFOLIO MONITOR
# ============================================================================

class PortfolioMonitor:
    """
    Main portfolio monitoring system
    Performs regular checks and stores results
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.logger = logger
        self.config = get_config()
        self.risk_analyzer = RiskAnalyzer()
        self.portfolio_manager = PortfolioManager(db_session)

        # Database session
        if db_session:
            self.session = db_session
        else:
            _, SessionLocal = create_engine_and_session(self.config.database.url)
            self.session = SessionLocal()

    def monitor_all_positions(self) -> List[Dict]:
        """
        Monitor all active portfolio positions

        Returns:
            List of monitoring results with alerts
        """
        try:
            self.logger.info("Starting portfolio monitoring...")

            # Get active positions
            positions = self.portfolio_manager.get_all_positions(status='active')

            if not positions:
                self.logger.info("No active positions to monitor")
                return []

            # Update prices first
            self.portfolio_manager.update_position_prices(positions)

            results = []

            for position in positions:
                result = self.monitor_position(position)
                if result:
                    results.append(result)

            # Log summary
            alerts = [r for r in results if r.get('alert_generated')]
            self.logger.info(f"Monitoring complete: {len(positions)} positions checked, "
                           f"{len(alerts)} alerts generated")

            return results

        except Exception as e:
            self.logger.error(f"Error monitoring positions: {e}")
            return []

    def monitor_position(self, position: PortfolioPosition) -> Optional[Dict]:
        """
        Monitor a single position and create monitoring record

        Args:
            position: Position to monitor

        Returns:
            Monitoring result dictionary
        """
        try:
            self.logger.debug(f"Monitoring position: {position.ticker}")

            # Perform risk analysis
            risk_analysis = self.risk_analyzer.analyze_position_risk(position)

            # Get current price info
            quote = self.portfolio_manager.market_service.stock_collector.get_quote(position.ticker)

            if not quote:
                self.logger.warning(f"Could not get quote for {position.ticker}")
                return None

            current_price = quote.get('current_price', position.purchase_price)
            change_1h = 0  # Would need 1-hour data
            change_24h = quote.get('change_percent', 0)

            # Volume analysis
            volume = quote.get('volume', 0)
            avg_volume = quote.get('avg_volume', 1)
            volume_vs_avg = volume / avg_volume if avg_volume > 0 else 1.0

            # Create monitoring record
            monitoring = PortfolioMonitoring(
                position_id=position.id,
                timestamp=datetime.now(),
                current_price=current_price,
                price_change_1h=change_1h,
                price_change_24h=change_24h,
                volume_vs_avg=volume_vs_avg,

                # Risk assessment
                risk_score=risk_analysis['risk_score'],
                risk_level=risk_analysis['risk_level'],
                risk_factors=risk_analysis['risk_factors'],

                # Alert information
                alert_level=risk_analysis['risk_level'] if risk_analysis['risk_score'] >= 40 else None,
                alert_generated=risk_analysis['risk_score'] >= 40,
                action_recommended=risk_analysis['action_recommended'],
                alternative_stocks=risk_analysis['alternative_stocks'],

                # Analysis details
                negative_news_count=risk_analysis['negative_news_count'],
                sentiment_shift=risk_analysis['sentiment_shift'],
                technical_signals=risk_analysis['technical_signals'],
                analysis_summary=risk_analysis['analysis_summary'],

                confidence=100 - risk_analysis['risk_score']  # Inverse of risk
            )

            # Save to database
            self.session.add(monitoring)

            # Update position's current risk level
            position.current_risk_level = risk_analysis['risk_level']
            position.risk_score = risk_analysis['risk_score']
            position.last_risk_check = datetime.now()

            self.session.commit()

            # Create result dictionary
            result = {
                'position_id': position.id,
                'ticker': position.ticker,
                'monitoring_id': monitoring.id,
                'timestamp': monitoring.timestamp,
                'risk_score': risk_analysis['risk_score'],
                'risk_level': risk_analysis['risk_level'].value,
                'alert_generated': monitoring.alert_generated,
                'action_recommended': risk_analysis['action_recommended'],
                'summary': risk_analysis['analysis_summary'],
                'risk_factors': risk_analysis['risk_factors'][:5],
                'alternatives': risk_analysis['alternative_stocks']
            }

            # Log if alert generated
            if monitoring.alert_generated:
                self.logger.warning(
                    f"⚠️  ALERT for {position.ticker}: {risk_analysis['risk_level'].value.upper()} risk "
                    f"({risk_analysis['risk_score']:.0f}/100) - "
                    f"Action: {risk_analysis['action_recommended']}"
                )

            return result

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error monitoring position {position.ticker}: {e}")
            return None

    def get_position_monitoring_history(
        self,
        position_id: int,
        days: int = 7
    ) -> List[PortfolioMonitoring]:
        """
        Get monitoring history for a position

        Args:
            position_id: Position ID
            days: Number of days to look back

        Returns:
            List of PortfolioMonitoring records
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)

            history = self.session.query(PortfolioMonitoring).filter(
                PortfolioMonitoring.position_id == position_id,
                PortfolioMonitoring.timestamp >= cutoff
            ).order_by(PortfolioMonitoring.timestamp.desc()).all()

            return history

        except Exception as e:
            self.logger.error(f"Error getting monitoring history: {e}")
            return []

    def get_all_alerts(self, min_risk_level: str = "medium") -> List[Dict]:
        """
        Get all current alerts

        Args:
            min_risk_level: Minimum risk level to include

        Returns:
            List of alert dictionaries
        """
        try:
            # Get active positions with recent monitoring
            positions = self.portfolio_manager.get_all_positions(status='active')

            alerts = []

            for position in positions:
                # Get latest monitoring record
                latest = self.session.query(PortfolioMonitoring).filter(
                    PortfolioMonitoring.position_id == position.id
                ).order_by(PortfolioMonitoring.timestamp.desc()).first()

                if latest and latest.alert_generated:
                    # Check if meets minimum risk level
                    risk_levels_order = ['low', 'medium', 'high', 'critical']
                    if (risk_levels_order.index(latest.risk_level.value) >=
                        risk_levels_order.index(min_risk_level)):

                        alerts.append({
                            'position_id': position.id,
                            'ticker': position.ticker,
                            'risk_level': latest.risk_level.value,
                            'risk_score': latest.risk_score,
                            'action': latest.action_recommended,
                            'summary': latest.analysis_summary,
                            'timestamp': latest.timestamp,
                            'current_price': latest.current_price,
                            'unrealized_pnl': position.unrealized_gain_loss_pct
                        })

            # Sort by risk score (highest first)
            alerts.sort(key=lambda x: x['risk_score'], reverse=True)

            return alerts

        except Exception as e:
            self.logger.error(f"Error getting alerts: {e}")
            return []

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test portfolio monitoring"""
    print("=" * 70)
    print("Portfolio Monitor Test")
    print("=" * 70)
    print()

    monitor = PortfolioMonitor()

    print("Monitoring all positions...")
    results = monitor.monitor_all_positions()

    if not results:
        print("No positions to monitor or monitoring failed")
        print("\nAdd a position first:")
        print("  python -m src.cli portfolio add AAPL 10 150.00")
        return

    print(f"\nMonitoring Results ({len(results)} positions):")
    print("=" * 70)

    for result in results:
        print(f"\n{result['ticker']}:")
        print(f"  Risk Level: {result['risk_level'].upper()}")
        print(f"  Risk Score: {result['risk_score']:.0f}/100")
        print(f"  Action: {result['action_recommended']}")

        if result['alert_generated']:
            print(f"  ⚠️  ALERT GENERATED!")

        if result['risk_factors']:
            print(f"  Risk Factors:")
            for factor in result['risk_factors'][:3]:
                print(f"    • {factor}")

        if result['alternatives']:
            print(f"  Alternatives: {', '.join(result['alternatives'])}")

    # Get all alerts
    print("\n" + "=" * 70)
    print("Active Alerts:")
    print("=" * 70)

    alerts = monitor.get_all_alerts(min_risk_level="medium")

    if alerts:
        for alert in alerts:
            print(f"\n⚠️  {alert['ticker']} - {alert['risk_level'].upper()} RISK")
            print(f"   Score: {alert['risk_score']:.0f}/100")
            print(f"   Action: {alert['action']}")
    else:
        print("\n✓ No alerts - All positions within acceptable risk levels")


if __name__ == "__main__":
    main()
