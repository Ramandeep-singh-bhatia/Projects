"""
Backtesting System
Tests signal generation strategies on historical data

This system:
- Loads historical market data
- Simulates signal generation
- Validates against actual outcomes
- Calculates performance metrics
- Identifies optimal parameters
- Generates backtest reports
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.database.models import (
    SignalGenerated,
    SignalOutcome,
    NewsArticle,
    MarketData,
    create_engine_and_session
)
from src.signals.signal_generator import SignalGenerator
from src.signals.signal_tracker import SignalTracker
from src.scrapers.market_data_collector import MarketDataService
from src.utils.logger import get_logger
from src.config.config_loader import get_config


logger = get_logger("backtester")


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class BacktestResult:
    """Results from a backtest run"""
    start_date: datetime
    end_date: datetime
    total_signals: int
    successful_signals: int
    failed_signals: int
    success_rate: float
    avg_gain: float
    avg_loss: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_loss_ratio: float
    avg_hold_days: float
    best_trade: Optional[Dict]
    worst_trade: Optional[Dict]
    by_catalyst: Dict[str, Dict]
    by_confidence: Dict[str, Dict]
    monthly_performance: List[Dict]


@dataclass
class ParameterTest:
    """Results from parameter optimization"""
    parameter_name: str
    parameter_value: float
    success_rate: float
    avg_return: float
    total_signals: int
    sharpe_ratio: float


# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

class Backtester:
    """
    Backtesting engine for validating signal strategies
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.logger = logger
        self.config = get_config()
        self.market_service = MarketDataService()

        # Database session
        if db_session:
            self.session = db_session
        else:
            _, SessionLocal = create_engine_and_session(self.config.database.url)
            self.session = SessionLocal()

    def backtest_historical_signals(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResult:
        """
        Backtest using actual historical signals

        Args:
            start_date: Start of backtest period
            end_date: End of backtest period

        Returns:
            BacktestResult with performance metrics
        """
        self.logger.info(f"Backtesting historical signals from {start_date.date()} to {end_date.date()}")

        # Get all signals in period
        signals = self.session.query(SignalGenerated).filter(
            and_(
                SignalGenerated.generated_date >= start_date,
                SignalGenerated.generated_date <= end_date
            )
        ).all()

        if not signals:
            self.logger.warning("No signals found in backtest period")
            return self._empty_result(start_date, end_date)

        # Get outcomes for these signals
        signal_ids = [s.id for s in signals]
        outcomes = self.session.query(SignalOutcome).filter(
            SignalOutcome.signal_id.in_(signal_ids)
        ).all()

        # Create outcome lookup
        outcome_map = {o.signal_id: o for o in outcomes}

        # Calculate metrics
        return self._calculate_backtest_metrics(
            signals,
            outcome_map,
            start_date,
            end_date
        )

    def backtest_strategy(
        self,
        start_date: datetime,
        end_date: datetime,
        weights: Optional[Dict] = None,
        min_confidence: int = 60
    ) -> BacktestResult:
        """
        Backtest a strategy with specific parameters

        Args:
            start_date: Start of backtest period
            end_date: End of backtest period
            weights: Custom weights for signal generation
            min_confidence: Minimum confidence threshold

        Returns:
            BacktestResult with performance metrics
        """
        self.logger.info(f"Backtesting strategy from {start_date.date()} to {end_date.date()}")

        # Get historical news in period
        news_articles = self.session.query(NewsArticle).filter(
            and_(
                NewsArticle.published_date >= start_date,
                NewsArticle.published_date <= end_date
            )
        ).all()

        if not news_articles:
            self.logger.warning("No news articles found in backtest period")
            return self._empty_result(start_date, end_date)

        # Simulate signal generation
        simulated_signals = self._simulate_signals(
            news_articles,
            weights or {},
            min_confidence
        )

        # Validate outcomes using historical data
        validated_outcomes = self._validate_simulated_signals(simulated_signals)

        # Calculate metrics
        return self._calculate_backtest_metrics(
            simulated_signals,
            validated_outcomes,
            start_date,
            end_date
        )

    def optimize_parameters(
        self,
        start_date: datetime,
        end_date: datetime,
        parameter_name: str,
        test_values: List[float]
    ) -> List[ParameterTest]:
        """
        Test different parameter values to find optimal

        Args:
            start_date: Start of backtest period
            end_date: End of backtest period
            parameter_name: Parameter to test (e.g., 'min_confidence', 'catalyst_weight')
            test_values: List of values to test

        Returns:
            List of ParameterTest results, sorted by performance
        """
        self.logger.info(f"Optimizing {parameter_name} with {len(test_values)} values")

        results = []

        for value in test_values:
            # Run backtest with this parameter value
            if parameter_name == 'min_confidence':
                backtest = self.backtest_strategy(
                    start_date,
                    end_date,
                    min_confidence=int(value)
                )
            elif parameter_name in ['catalyst_weight', 'technical_weight', 'sentiment_weight']:
                weights = self._create_weight_variation(parameter_name, value)
                backtest = self.backtest_strategy(
                    start_date,
                    end_date,
                    weights=weights
                )
            else:
                continue

            # Record result
            results.append(ParameterTest(
                parameter_name=parameter_name,
                parameter_value=value,
                success_rate=backtest.success_rate,
                avg_return=backtest.total_return,
                total_signals=backtest.total_signals,
                sharpe_ratio=backtest.sharpe_ratio
            ))

        # Sort by Sharpe ratio (risk-adjusted return)
        results.sort(key=lambda x: x.sharpe_ratio, reverse=True)

        return results

    def walk_forward_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        train_days: int = 90,
        test_days: int = 30
    ) -> List[Dict]:
        """
        Walk-forward analysis to test adaptive learning

        Args:
            start_date: Start date
            end_date: End date
            train_days: Days to use for training
            test_days: Days to use for testing

        Returns:
            List of period results
        """
        self.logger.info(f"Running walk-forward analysis: {train_days}d train / {test_days}d test")

        results = []
        current_date = start_date

        while current_date < end_date:
            train_start = current_date
            train_end = current_date + timedelta(days=train_days)
            test_start = train_end
            test_end = test_start + timedelta(days=test_days)

            if test_end > end_date:
                break

            # Train on period (get optimal weights)
            train_signals = self.session.query(SignalGenerated).filter(
                and_(
                    SignalGenerated.generated_date >= train_start,
                    SignalGenerated.generated_date < train_end
                )
            ).all()

            if len(train_signals) < 10:
                current_date = test_end
                continue

            # Calculate optimal weights from training period
            optimal_weights = self._calculate_optimal_weights_from_signals(train_signals)

            # Test on next period
            test_result = self.backtest_strategy(
                test_start,
                test_end,
                weights=optimal_weights
            )

            results.append({
                'train_period': f"{train_start.date()} to {train_end.date()}",
                'test_period': f"{test_start.date()} to {test_end.date()}",
                'train_signals': len(train_signals),
                'test_signals': test_result.total_signals,
                'success_rate': test_result.success_rate,
                'total_return': test_result.total_return,
                'sharpe_ratio': test_result.sharpe_ratio,
                'weights_used': optimal_weights
            })

            current_date = test_end

        return results

    def _simulate_signals(
        self,
        news_articles: List[NewsArticle],
        weights: Dict,
        min_confidence: int
    ) -> List[Dict]:
        """Simulate signal generation on historical news"""
        simulated = []

        # Group news by ticker and date
        news_by_ticker = {}
        for article in news_articles:
            for ticker in article.tickers:
                if ticker not in news_by_ticker:
                    news_by_ticker[ticker] = []
                news_by_ticker[ticker].append(article)

        # Generate signals for each ticker
        for ticker, ticker_news in news_by_ticker.items():
            # Analyze catalysts
            for article in ticker_news:
                # Simplified catalyst scoring (real system is more complex)
                catalyst_score = self._score_catalyst(article)

                if catalyst_score >= 60:
                    simulated.append({
                        'ticker': ticker,
                        'generated_date': article.published_date,
                        'catalyst_score': catalyst_score,
                        'article_id': article.id,
                        'weights': weights
                    })

        return simulated

    def _validate_simulated_signals(
        self,
        simulated_signals: List[Dict]
    ) -> Dict[int, SignalOutcome]:
        """Validate simulated signals against historical price data"""
        validated = {}

        for idx, signal in enumerate(simulated_signals):
            ticker = signal['ticker']
            signal_date = signal['generated_date']

            # Get price at signal date
            entry_price = self._get_historical_price(ticker, signal_date)

            if not entry_price:
                continue

            # Check price after 7 days (short-term signal)
            check_date = signal_date + timedelta(days=7)
            exit_price = self._get_historical_price(ticker, check_date)

            if not exit_price:
                continue

            # Calculate outcome
            gain_pct = ((exit_price - entry_price) / entry_price) * 100

            # Create outcome
            outcome = SignalOutcome()
            outcome.signal_id = idx
            outcome.ticker = ticker
            outcome.peak_gain_pct = max(0, gain_pct)
            outcome.was_successful = gain_pct >= 5.0  # 5% gain threshold

            validated[idx] = outcome

        return validated

    def _calculate_backtest_metrics(
        self,
        signals: List,
        outcomes: Dict,
        start_date: datetime,
        end_date: datetime
    ) -> BacktestResult:
        """Calculate comprehensive backtest metrics"""

        # Filter to signals with outcomes
        validated_signals = [s for s in signals if (
            hasattr(s, 'id') and s.id in outcomes
        ) or (
            isinstance(s, dict) and signals.index(s) in outcomes
        )]

        if not validated_signals:
            return self._empty_result(start_date, end_date)

        # Success metrics
        successful = []
        failed = []
        all_returns = []

        for signal in validated_signals:
            if hasattr(signal, 'id'):
                outcome = outcomes.get(signal.id)
            else:
                outcome = outcomes.get(signals.index(signal))

            if outcome and outcome.was_successful:
                successful.append(outcome)
                all_returns.append(outcome.peak_gain_pct or 0)
            else:
                failed.append(outcome)
                all_returns.append(-(outcome.peak_gain_pct or 0))

        total_signals = len(validated_signals)
        success_rate = (len(successful) / total_signals * 100) if total_signals > 0 else 0

        # Calculate average gains/losses
        gains = [o.peak_gain_pct for o in successful if o.peak_gain_pct]
        losses = [o.peak_gain_pct for o in failed if o.peak_gain_pct]

        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0

        # Total return
        total_return = sum(all_returns)

        # Sharpe ratio (simplified)
        if all_returns:
            avg_return = sum(all_returns) / len(all_returns)
            std_dev = (sum((r - avg_return) ** 2 for r in all_returns) / len(all_returns)) ** 0.5
            sharpe_ratio = (avg_return / std_dev) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0

        # Max drawdown
        max_drawdown = self._calculate_max_drawdown(all_returns)

        # Win/loss ratio
        win_loss_ratio = (avg_gain / abs(avg_loss)) if avg_loss != 0 else 0

        # Best and worst trades
        best_trade = max(successful, key=lambda x: x.peak_gain_pct) if successful else None
        worst_trade = min(failed, key=lambda x: x.peak_gain_pct) if failed else None

        # By catalyst type
        by_catalyst = self._group_by_catalyst(validated_signals, outcomes)

        # By confidence level
        by_confidence = self._group_by_confidence(validated_signals, outcomes)

        # Monthly performance
        monthly_performance = self._calculate_monthly_performance(
            validated_signals,
            outcomes,
            start_date,
            end_date
        )

        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            total_signals=total_signals,
            successful_signals=len(successful),
            failed_signals=len(failed),
            success_rate=success_rate,
            avg_gain=avg_gain,
            avg_loss=avg_loss,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_loss_ratio=win_loss_ratio,
            avg_hold_days=7.0,  # Simplified
            best_trade={
                'ticker': best_trade.ticker,
                'gain': best_trade.peak_gain_pct
            } if best_trade else None,
            worst_trade={
                'ticker': worst_trade.ticker,
                'loss': worst_trade.peak_gain_pct
            } if worst_trade else None,
            by_catalyst=by_catalyst,
            by_confidence=by_confidence,
            monthly_performance=monthly_performance
        )

    def _calculate_max_drawdown(self, returns: List[float]) -> float:
        """Calculate maximum drawdown"""
        if not returns:
            return 0.0

        cumulative = 0
        peak = 0
        max_dd = 0

        for ret in returns:
            cumulative += ret
            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_dd:
                max_dd = drawdown

        return max_dd

    def _group_by_catalyst(
        self,
        signals: List,
        outcomes: Dict
    ) -> Dict[str, Dict]:
        """Group results by catalyst type"""
        by_catalyst = {}

        for signal in signals:
            # Get catalyst type
            if hasattr(signal, 'catalyst_event_type'):
                catalyst = signal.catalyst_event_type
            else:
                catalyst = 'unknown'

            if catalyst not in by_catalyst:
                by_catalyst[catalyst] = {
                    'total': 0,
                    'successful': 0,
                    'avg_gain': 0
                }

            by_catalyst[catalyst]['total'] += 1

            # Get outcome
            if hasattr(signal, 'id'):
                outcome = outcomes.get(signal.id)
            else:
                outcome = outcomes.get(signals.index(signal))

            if outcome and outcome.was_successful:
                by_catalyst[catalyst]['successful'] += 1

        # Calculate success rates
        for catalyst, stats in by_catalyst.items():
            stats['success_rate'] = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0

        return by_catalyst

    def _group_by_confidence(
        self,
        signals: List,
        outcomes: Dict
    ) -> Dict[str, Dict]:
        """Group results by confidence level"""
        by_confidence = {
            'high': {'total': 0, 'successful': 0},
            'medium': {'total': 0, 'successful': 0},
            'low': {'total': 0, 'successful': 0}
        }

        for signal in signals:
            # Get confidence
            if hasattr(signal, 'confidence_score'):
                confidence = signal.confidence_score
            else:
                confidence = 60

            # Categorize
            if confidence >= 75:
                category = 'high'
            elif confidence >= 60:
                category = 'medium'
            else:
                category = 'low'

            by_confidence[category]['total'] += 1

            # Get outcome
            if hasattr(signal, 'id'):
                outcome = outcomes.get(signal.id)
            else:
                outcome = outcomes.get(signals.index(signal))

            if outcome and outcome.was_successful:
                by_confidence[category]['successful'] += 1

        # Calculate success rates
        for category, stats in by_confidence.items():
            stats['success_rate'] = (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0

        return by_confidence

    def _calculate_monthly_performance(
        self,
        signals: List,
        outcomes: Dict,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Calculate performance by month"""
        monthly = {}

        for signal in signals:
            # Get month
            if hasattr(signal, 'generated_date'):
                month = signal.generated_date.strftime('%Y-%m')
            else:
                month = signal.get('generated_date', start_date).strftime('%Y-%m')

            if month not in monthly:
                monthly[month] = {
                    'month': month,
                    'total': 0,
                    'successful': 0,
                    'total_return': 0
                }

            monthly[month]['total'] += 1

            # Get outcome
            if hasattr(signal, 'id'):
                outcome = outcomes.get(signal.id)
            else:
                outcome = outcomes.get(signals.index(signal))

            if outcome:
                if outcome.was_successful:
                    monthly[month]['successful'] += 1
                    monthly[month]['total_return'] += outcome.peak_gain_pct or 0

        # Calculate success rates
        for month_data in monthly.values():
            month_data['success_rate'] = (
                month_data['successful'] / month_data['total'] * 100
            ) if month_data['total'] > 0 else 0

        return sorted(monthly.values(), key=lambda x: x['month'])

    def _get_historical_price(self, ticker: str, date: datetime) -> Optional[float]:
        """Get historical price for ticker on date"""
        try:
            # Query market data
            market_data = self.session.query(MarketData).filter(
                and_(
                    MarketData.ticker == ticker,
                    MarketData.timestamp >= date,
                    MarketData.timestamp < date + timedelta(days=1)
                )
            ).first()

            if market_data:
                return market_data.close_price

            # Fallback: try to fetch from yfinance
            quote = self.market_service.stock_collector.get_quote(ticker)
            if quote:
                return quote.get('current_price')

            return None

        except Exception as e:
            self.logger.error(f"Error getting historical price for {ticker}: {e}")
            return None

    def _score_catalyst(self, article: NewsArticle) -> int:
        """Simplified catalyst scoring"""
        # In real system, this would use full catalyst evaluation
        score = 60  # Base score

        # Check for high-impact keywords
        title_lower = article.title.lower()

        if any(word in title_lower for word in ['fda', 'approval', 'breakthrough']):
            score += 20
        elif any(word in title_lower for word in ['acquisition', 'merger', 'buyout']):
            score += 15
        elif any(word in title_lower for word in ['earnings', 'beat', 'revenue']):
            score += 10

        # Sentiment boost
        if article.sentiment_label == 'positive':
            score += 5
        elif article.sentiment_label == 'negative':
            score -= 5

        return min(100, max(0, score))

    def _calculate_optimal_weights_from_signals(
        self,
        signals: List[SignalGenerated]
    ) -> Dict[str, float]:
        """Calculate optimal weights from training signals"""
        # Simplified - real system would use learning engine
        return {
            'catalyst_weight': 0.4,
            'technical_weight': 0.3,
            'sentiment_weight': 0.3
        }

    def _create_weight_variation(
        self,
        parameter_name: str,
        value: float
    ) -> Dict[str, float]:
        """Create weight dictionary with one parameter varied"""
        # Start with defaults
        weights = {
            'catalyst_weight': 0.4,
            'technical_weight': 0.3,
            'sentiment_weight': 0.3
        }

        # Adjust the specified parameter
        if parameter_name in weights:
            old_value = weights[parameter_name]
            weights[parameter_name] = value

            # Redistribute the difference
            diff = value - old_value
            other_keys = [k for k in weights.keys() if k != parameter_name]

            for key in other_keys:
                weights[key] -= diff / len(other_keys)

        return weights

    def _empty_result(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """Return empty result when no data"""
        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            total_signals=0,
            successful_signals=0,
            failed_signals=0,
            success_rate=0.0,
            avg_gain=0.0,
            avg_loss=0.0,
            total_return=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            win_loss_ratio=0.0,
            avg_hold_days=0.0,
            best_trade=None,
            worst_trade=None,
            by_catalyst={},
            by_confidence={},
            monthly_performance=[]
        )

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test backtester"""
    print("=" * 70)
    print("Backtesting System Test")
    print("=" * 70)
    print()

    backtester = Backtester()

    # Test historical signals backtest
    print("BACKTESTING HISTORICAL SIGNALS:")
    print("=" * 70)

    # Last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    result = backtester.backtest_historical_signals(start_date, end_date)

    print(f"\nPeriod: {start_date.date()} to {end_date.date()}")
    print(f"Total Signals: {result.total_signals}")
    print(f"Successful: {result.successful_signals}")
    print(f"Failed: {result.failed_signals}")
    print(f"Success Rate: {result.success_rate:.1f}%")
    print(f"Total Return: {result.total_return:.2f}%")
    print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")
    print(f"Max Drawdown: {result.max_drawdown:.2f}%")

    if result.by_catalyst:
        print(f"\nBy Catalyst Type:")
        for catalyst, stats in result.by_catalyst.items():
            print(f"  {catalyst}: {stats['success_rate']:.1f}% ({stats['successful']}/{stats['total']})")

    # Test parameter optimization
    print(f"\n{'='*70}")
    print("PARAMETER OPTIMIZATION:")
    print("=" * 70)

    if result.total_signals >= 10:
        test_values = [55, 60, 65, 70, 75]
        optimization = backtester.optimize_parameters(
            start_date,
            end_date,
            'min_confidence',
            test_values
        )

        print(f"\nTesting min_confidence values: {test_values}")
        print(f"\nTop 3 Results:")
        for i, test in enumerate(optimization[:3], 1):
            print(f"{i}. Confidence={test.parameter_value}: "
                  f"Success={test.success_rate:.1f}%, "
                  f"Sharpe={test.sharpe_ratio:.2f}, "
                  f"Signals={test.total_signals}")
    else:
        print("\nNeed at least 10 signals for optimization")


if __name__ == "__main__":
    main()
