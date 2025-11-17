"""
Learning Engine
Analyzes historical outcomes to extract success factors and improve the system

This engine:
- Analyzes what worked and what didn't
- Extracts success factors from winning signals
- Identifies failure patterns from losing signals
- Calculates optimal weights for signal generation
- Provides recommendations for system improvements
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict
import statistics

from src.database.models import (
    SignalGenerated,
    SignalOutcome,
    SignalStatus,
    PerformanceMetrics,
    create_engine_and_session
)
from src.learning.pattern_recognizer import PatternRecognizer
from src.utils.logger import get_logger
from src.config.config_loader import get_config


logger = get_logger("learning_engine")


# ============================================================================
# LEARNING ENGINE
# ============================================================================

class LearningEngine:
    """
    Analyzes historical performance and extracts learnings
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.logger = logger
        self.config = get_config()
        self.pattern_recognizer = PatternRecognizer(db_session)

        # Database session
        if db_session:
            self.session = db_session
        else:
            _, SessionLocal = create_engine_and_session(self.config.database.url)
            self.session = SessionLocal()

    def analyze_performance(self, days_back: int = 30) -> Dict:
        """
        Comprehensive performance analysis

        Args:
            days_back: Number of days to analyze

        Returns:
            Performance analysis dictionary
        """
        self.logger.info(f"Analyzing performance for last {days_back} days...")

        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Get signals in period
        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.timestamp >= cutoff_date,
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        if not signals:
            return {
                'period_days': days_back,
                'total_signals': 0,
                'message': 'No completed signals in period'
            }

        # Basic stats
        total = len(signals)
        successful = sum(1 for s in signals if s.status == SignalStatus.SUCCESSFUL)
        unsuccessful = total - successful
        success_rate = (successful / total * 100) if total > 0 else 0

        # Get outcomes for detailed analysis
        outcomes = [s.outcome for s in signals if s.outcome]

        # Winners and losers
        winners = [o for o in outcomes if o.success_flag]
        losers = [o for o in outcomes if not o.success_flag]

        # Calculate gains
        avg_gain_winners = statistics.mean([o.actual_gain_pct for o in winners]) if winners else 0
        avg_loss_losers = statistics.mean([o.actual_gain_pct for o in losers]) if losers else 0

        max_gain = max([o.actual_gain_pct for o in winners], default=0)
        max_loss = min([o.actual_gain_pct for o in losers], default=0)

        # Time to peak analysis
        avg_time_to_peak = statistics.mean([o.time_to_peak_hours for o in outcomes]) if outcomes else 0

        # Confidence calibration
        confidence_accuracy = self._calculate_confidence_accuracy(signals)

        # By signal type
        short_term = [s for s in signals if s.signal_type.value == 'short_term']
        long_term = [s for s in signals if s.signal_type.value == 'long_term']

        short_success = sum(1 for s in short_term if s.status == SignalStatus.SUCCESSFUL)
        long_success = sum(1 for s in long_term if s.status == SignalStatus.SUCCESSFUL)

        short_rate = (short_success / len(short_term) * 100) if short_term else 0
        long_rate = (long_success / len(long_term) * 100) if long_term else 0

        # By catalyst type
        by_catalyst = self._analyze_by_catalyst(signals)

        # Success factors
        success_factors = self._extract_success_factors(winners)
        failure_factors = self._extract_failure_factors(losers)

        return {
            'period_days': days_back,
            'analysis_date': datetime.now(),

            # Overall metrics
            'total_signals': total,
            'successful_signals': successful,
            'unsuccessful_signals': unsuccessful,
            'success_rate': success_rate,

            # Returns
            'avg_gain_winners': avg_gain_winners,
            'avg_loss_losers': avg_loss_losers,
            'max_gain': max_gain,
            'max_loss': max_loss,
            'avg_time_to_peak_hours': avg_time_to_peak,

            # Calibration
            'confidence_accuracy': confidence_accuracy,

            # By type
            'short_term': {
                'total': len(short_term),
                'successful': short_success,
                'success_rate': short_rate
            },
            'long_term': {
                'total': len(long_term),
                'successful': long_success,
                'success_rate': long_rate
            },

            # By catalyst
            'by_catalyst': by_catalyst,

            # Learnings
            'success_factors': success_factors,
            'failure_factors': failure_factors,

            # Recommendations
            'recommendations': self._generate_recommendations(
                success_rate, confidence_accuracy, success_factors, failure_factors
            )
        }

    def _calculate_confidence_accuracy(self, signals: List[SignalGenerated]) -> float:
        """
        Calculate how well confidence scores predict success

        Returns:
            Accuracy score 0-100
        """
        if not signals:
            return 0.0

        # Group by confidence buckets
        buckets = {
            'high': [],      # 75-100
            'medium': [],    # 60-75
            'low': []        # < 60
        }

        for signal in signals:
            if signal.confidence >= 75:
                buckets['high'].append(signal)
            elif signal.confidence >= 60:
                buckets['medium'].append(signal)
            else:
                buckets['low'].append(signal)

        # Calculate success rate per bucket
        accuracies = []

        for bucket_name, bucket_signals in buckets.items():
            if bucket_signals:
                success_count = sum(1 for s in bucket_signals if s.status == SignalStatus.SUCCESSFUL)
                success_rate = success_count / len(bucket_signals)

                # Expected success rate for this confidence level
                if bucket_name == 'high':
                    expected = 0.75
                elif bucket_name == 'medium':
                    expected = 0.65
                else:
                    expected = 0.50

                # How close is actual to expected?
                accuracy = 1.0 - abs(success_rate - expected)
                accuracies.append(accuracy)

        return statistics.mean(accuracies) * 100 if accuracies else 0.0

    def _analyze_by_catalyst(self, signals: List[SignalGenerated]) -> Dict:
        """Analyze performance by catalyst type"""
        by_catalyst = defaultdict(lambda: {'total': 0, 'successful': 0})

        for signal in signals:
            if signal.catalyst_type:
                by_catalyst[signal.catalyst_type]['total'] += 1
                if signal.status == SignalStatus.SUCCESSFUL:
                    by_catalyst[signal.catalyst_type]['successful'] += 1

        # Calculate rates
        result = {}
        for catalyst, stats in by_catalyst.items():
            result[catalyst] = {
                'total': stats['total'],
                'successful': stats['successful'],
                'success_rate': (stats['successful'] / stats['total'] * 100) if stats['total'] > 0 else 0
            }

        return result

    def _extract_success_factors(self, winners: List[SignalOutcome]) -> List[Dict]:
        """Extract common factors from successful signals"""
        if not winners:
            return []

        # Aggregate success factors
        factor_counts = defaultdict(int)

        for outcome in winners:
            for factor in outcome.what_worked or []:
                factor_counts[factor] += 1

        # Convert to list with percentages
        total = len(winners)
        factors = [
            {
                'factor': factor,
                'count': count,
                'percentage': (count / total * 100)
            }
            for factor, count in factor_counts.items()
        ]

        # Sort by frequency
        factors.sort(key=lambda x: x['count'], reverse=True)

        return factors[:10]  # Top 10

    def _extract_failure_factors(self, losers: List[SignalOutcome]) -> List[Dict]:
        """Extract common factors from failed signals"""
        if not losers:
            return []

        factor_counts = defaultdict(int)

        for outcome in losers:
            for factor in outcome.what_failed or []:
                factor_counts[factor] += 1

        total = len(losers)
        factors = [
            {
                'factor': factor,
                'count': count,
                'percentage': (count / total * 100)
            }
            for factor, count in factor_counts.items()
        ]

        factors.sort(key=lambda x: x['count'], reverse=True)

        return factors[:10]

    def _generate_recommendations(
        self,
        success_rate: float,
        confidence_accuracy: float,
        success_factors: List[Dict],
        failure_factors: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Success rate recommendations
        if success_rate < 50:
            recommendations.append("⚠️ Success rate below 50% - Consider raising minimum confidence threshold")
            recommendations.append("💡 Focus on high-confidence patterns that are working")
        elif success_rate > 70:
            recommendations.append("✓ Strong success rate - Current strategy is working well")

        # Confidence calibration
        if confidence_accuracy < 60:
            recommendations.append("⚠️ Confidence scores not well-calibrated - Review scoring formula")
        elif confidence_accuracy > 80:
            recommendations.append("✓ Confidence scores are well-calibrated")

        # Success factors
        if success_factors:
            top_factor = success_factors[0]
            if top_factor['percentage'] > 60:
                recommendations.append(f"💡 '{top_factor['factor']}' appears in {top_factor['percentage']:.0f}% of winners - Prioritize this")

        # Failure factors
        if failure_factors:
            top_failure = failure_factors[0]
            if top_failure['percentage'] > 60:
                recommendations.append(f"⚠️ '{top_failure['factor']}' appears in {top_failure['percentage']:.0f}% of losers - Avoid this")

        return recommendations

    def calculate_optimal_weights(self) -> Dict[str, float]:
        """
        Calculate optimal weights for signal generation based on historical performance

        Returns:
            Dictionary of weight adjustments
        """
        self.logger.info("Calculating optimal weights...")

        # Get all completed signals
        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        if len(signals) < 20:
            self.logger.warning("Not enough data for weight optimization (need 20+)")
            return {}

        # Analyze correlation between scores and success
        catalyst_correlation = self._calculate_correlation('catalyst', signals)
        technical_correlation = self._calculate_correlation('technical', signals)
        sentiment_correlation = self._calculate_correlation('sentiment', signals)

        # Current weights
        current_weights = {
            'catalyst': 0.4,
            'technical': 0.3,
            'sentiment': 0.3
        }

        # Calculate new weights based on correlations
        total_correlation = catalyst_correlation + technical_correlation + sentiment_correlation

        if total_correlation > 0:
            new_weights = {
                'catalyst': catalyst_correlation / total_correlation,
                'technical': technical_correlation / total_correlation,
                'sentiment': sentiment_correlation / total_correlation
            }
        else:
            new_weights = current_weights

        # Gradual adjustment (don't change too fast)
        adjustment_rate = self.config.get('learning.weight_adjustment_rate', 0.1)

        adjusted_weights = {}
        for key in current_weights:
            current = current_weights[key]
            new = new_weights[key]
            adjusted = current + (new - current) * adjustment_rate
            adjusted_weights[key] = round(adjusted, 3)

        return {
            'current_weights': current_weights,
            'correlations': {
                'catalyst': catalyst_correlation,
                'technical': technical_correlation,
                'sentiment': sentiment_correlation
            },
            'optimal_weights': new_weights,
            'adjusted_weights': adjusted_weights,
            'adjustment_rate': adjustment_rate
        }

    def _calculate_correlation(self, score_type: str, signals: List[SignalGenerated]) -> float:
        """Calculate correlation between a score type and success"""

        # Extract scores and outcomes
        data_points = []

        for signal in signals:
            supporting_data = signal.supporting_data or {}

            if score_type == 'catalyst':
                score = supporting_data.get('catalyst_score', 0)
            elif score_type == 'technical':
                score = supporting_data.get('technical_score', 0)
            elif score_type == 'sentiment':
                score = supporting_data.get('sentiment_score', 0) * 100
            else:
                score = 0

            success = 1 if signal.status == SignalStatus.SUCCESSFUL else 0
            data_points.append((score, success))

        if len(data_points) < 2:
            return 0.0

        # Calculate correlation (simplified)
        scores = [x[0] for x in data_points]
        outcomes = [x[1] for x in data_points]

        # Normalize scores to 0-1
        max_score = max(scores) if scores else 1
        normalized_scores = [s / max_score for s in scores] if max_score > 0 else scores

        # Simple correlation: average score for successes vs failures
        success_scores = [s for s, o in zip(normalized_scores, outcomes) if o == 1]
        failure_scores = [s for s, o in zip(normalized_scores, outcomes) if o == 0]

        avg_success = statistics.mean(success_scores) if success_scores else 0
        avg_failure = statistics.mean(failure_scores) if failure_scores else 0

        # Higher score for successes = positive correlation
        correlation = avg_success - avg_failure

        # Normalize to 0-1
        return max(0, min(1, (correlation + 1) / 2))

    def save_performance_metrics(self, analysis: Dict) -> PerformanceMetrics:
        """
        Save performance metrics to database

        Args:
            analysis: Performance analysis dictionary

        Returns:
            Saved PerformanceMetrics object
        """
        try:
            # Check if metrics for today already exist
            today = datetime.now().date()
            existing = self.session.query(PerformanceMetrics).filter(
                PerformanceMetrics.date >= datetime.combine(today, datetime.min.time())
            ).first()

            if existing:
                # Update existing
                metrics = existing
            else:
                # Create new
                metrics = PerformanceMetrics(
                    date=datetime.now(),
                    period_type='daily'
                )
                self.session.add(metrics)

            # Update fields
            metrics.total_signals = analysis['total_signals']
            metrics.successful_signals = analysis['successful_signals']
            metrics.unsuccessful_signals = analysis['unsuccessful_signals']
            metrics.overall_success_rate = analysis['success_rate']

            metrics.success_rate_short_term = analysis['short_term']['success_rate']
            metrics.success_rate_long_term = analysis['long_term']['success_rate']

            metrics.avg_gain_winners = analysis['avg_gain_winners']
            metrics.avg_loss_losers = analysis['avg_loss_losers']
            metrics.max_gain = analysis['max_gain']
            metrics.max_loss = analysis['max_loss']

            metrics.confidence_accuracy = analysis['confidence_accuracy']

            # Catalyst-specific rates
            by_catalyst = analysis.get('by_catalyst', {})
            if 'earnings' in by_catalyst:
                metrics.success_rate_earnings = by_catalyst['earnings']['success_rate']
            if 'm&a' in by_catalyst:
                metrics.success_rate_ma = by_catalyst['m&a']['success_rate']
            if 'fda' in by_catalyst:
                metrics.success_rate_fda = by_catalyst['fda']['success_rate']
            if 'contract' in by_catalyst:
                metrics.success_rate_contract = by_catalyst['contract']['success_rate']

            self.session.commit()

            self.logger.info(f"Saved performance metrics for {today}")
            return metrics

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error saving performance metrics: {e}")
            raise

    def generate_weekly_report(self) -> Dict:
        """
        Generate comprehensive weekly learning report

        Returns:
            Weekly report dictionary
        """
        self.logger.info("Generating weekly learning report...")

        # Analyze last 7 days
        weekly_analysis = self.analyze_performance(days_back=7)

        # Compare to previous week
        previous_week = self.analyze_performance(days_back=14)

        # Calculate trends
        trends = self._calculate_trends(weekly_analysis, previous_week)

        # Get pattern insights
        patterns = self.pattern_recognizer.get_active_patterns(min_confidence=0.6)

        # Get optimal weights
        weight_analysis = self.calculate_optimal_weights()

        return {
            'report_date': datetime.now(),
            'period': 'Last 7 days',
            'current_week': weekly_analysis,
            'previous_week': {
                'success_rate': previous_week['success_rate'],
                'total_signals': previous_week['total_signals']
            },
            'trends': trends,
            'top_patterns': [
                {
                    'name': p.pattern_name,
                    'success_rate': p.success_rate,
                    'sample_size': p.sample_size
                }
                for p in patterns[:5]
            ],
            'weight_optimization': weight_analysis,
            'key_insights': self._generate_key_insights(weekly_analysis, trends, patterns)
        }

    def _calculate_trends(self, current: Dict, previous: Dict) -> Dict:
        """Calculate week-over-week trends"""
        trends = {}

        # Success rate trend
        if previous['total_signals'] > 0:
            success_rate_change = current['success_rate'] - previous['success_rate']
            trends['success_rate'] = {
                'current': current['success_rate'],
                'previous': previous['success_rate'],
                'change': success_rate_change,
                'direction': 'improving' if success_rate_change > 0 else 'declining'
            }

        # Volume trend
        signal_change = current['total_signals'] - previous['total_signals']
        trends['signal_volume'] = {
            'current': current['total_signals'],
            'previous': previous['total_signals'],
            'change': signal_change,
            'direction': 'increasing' if signal_change > 0 else 'decreasing'
        }

        return trends

    def _generate_key_insights(
        self,
        analysis: Dict,
        trends: Dict,
        patterns: List
    ) -> List[str]:
        """Generate key insights from the week"""
        insights = []

        # Performance insight
        success_rate = analysis['success_rate']
        if success_rate >= 70:
            insights.append(f"🎯 Excellent performance: {success_rate:.1f}% success rate")
        elif success_rate >= 50:
            insights.append(f"✓ Solid performance: {success_rate:.1f}% success rate")
        else:
            insights.append(f"⚠️ Below target: {success_rate:.1f}% success rate - Review strategy")

        # Trend insight
        if 'success_rate' in trends:
            trend = trends['success_rate']
            if abs(trend['change']) > 5:
                if trend['direction'] == 'improving':
                    insights.append(f"📈 Success rate improving: +{trend['change']:.1f}% vs last week")
                else:
                    insights.append(f"📉 Success rate declining: {trend['change']:.1f}% vs last week")

        # Pattern insight
        if patterns:
            best_pattern = patterns[0]
            insights.append(f"💡 Top pattern: '{best_pattern.pattern_name}' ({best_pattern.success_rate:.1%} success)")

        # Success factor insight
        if analysis.get('success_factors'):
            top_factor = analysis['success_factors'][0]
            insights.append(f"✓ Key success factor: {top_factor['factor']} ({top_factor['percentage']:.0f}% of winners)")

        return insights

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test learning engine"""
    print("=" * 70)
    print("Learning Engine Test")
    print("=" * 70)
    print()

    engine = LearningEngine()

    print("Analyzing performance (last 30 days)...")
    analysis = engine.analyze_performance(days_back=30)

    if analysis['total_signals'] == 0:
        print("No completed signals yet")
        print("\nGenerate signals and wait for outcomes:")
        print("  1. python -m src.cli signals scan")
        print("  2. Wait for timeframes to expire")
        print("  3. python -m src.cli signals validate <id>")
        return

    print(f"\nPERFORMANCE ANALYSIS:")
    print("=" * 70)
    print(f"Period: {analysis['period_days']} days")
    print(f"Total Signals: {analysis['total_signals']}")
    print(f"Success Rate: {analysis['success_rate']:.1f}%")
    print(f"Avg Gain (Winners): {analysis['avg_gain_winners']:+.1f}%")
    print(f"Avg Loss (Losers): {analysis['avg_loss_losers']:+.1f}%")
    print(f"Confidence Accuracy: {analysis['confidence_accuracy']:.1f}%")

    print(f"\nBy Timeframe:")
    print(f"  Short-term: {analysis['short_term']['success_rate']:.1f}% ({analysis['short_term']['successful']}/{analysis['short_term']['total']})")
    print(f"  Long-term: {analysis['long_term']['success_rate']:.1f}% ({analysis['long_term']['successful']}/{analysis['long_term']['total']})")

    if analysis.get('success_factors'):
        print(f"\nTop Success Factors:")
        for factor in analysis['success_factors'][:3]:
            print(f"  • {factor['factor']} ({factor['percentage']:.0f}% of winners)")

    if analysis.get('recommendations'):
        print(f"\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"  {rec}")

    # Optimal weights
    print(f"\n{'='*70}")
    print("OPTIMAL WEIGHTS:")
    print("=" * 70)
    weights = engine.calculate_optimal_weights()

    if weights:
        print(f"Current: Catalyst={weights['current_weights']['catalyst']:.2f}, "
              f"Technical={weights['current_weights']['technical']:.2f}, "
              f"Sentiment={weights['current_weights']['sentiment']:.2f}")
        print(f"Adjusted: Catalyst={weights['adjusted_weights']['catalyst']:.2f}, "
              f"Technical={weights['adjusted_weights']['technical']:.2f}, "
              f"Sentiment={weights['adjusted_weights']['sentiment']:.2f}")


if __name__ == "__main__":
    main()
