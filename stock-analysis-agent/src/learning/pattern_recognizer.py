"""
Pattern Recognition Engine
Identifies recurring patterns from historical signal outcomes

Analyzes validated signals to discover:
- Which catalyst types are most reliable
- Optimal timeframes for different events
- Best market conditions for signals
- Technical indicator combinations that work
- Sentiment thresholds that predict success

Creates pattern library with statistical validation
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict, Counter
import statistics

from src.database.models import (
    SignalGenerated,
    SignalOutcome,
    SignalStatus,
    LearningPattern,
    create_engine_and_session
)
from src.utils.logger import get_logger
from src.config.config_loader import get_config


logger = get_logger("pattern_recognizer")


# ============================================================================
# PATTERN RECOGNIZER
# ============================================================================

class PatternRecognizer:
    """
    Identifies and validates patterns from historical signal outcomes
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.logger = logger
        self.config = get_config()

        # Database session
        if db_session:
            self.session = db_session
        else:
            _, SessionLocal = create_engine_and_session(self.config.database.url)
            self.session = SessionLocal()

        # Minimum samples for pattern validation
        self.min_sample_size = self.config.get('learning.min_sample_size', 10)
        self.min_success_rate = self.config.get('learning.pattern_min_success_rate', 0.65)

    def analyze_all_patterns(self) -> List[Dict]:
        """
        Analyze all historical data to identify patterns

        Returns:
            List of identified patterns
        """
        self.logger.info("Analyzing historical data for patterns...")

        patterns = []

        # 1. Catalyst type patterns
        patterns.extend(self._analyze_catalyst_patterns())

        # 2. Timeframe patterns
        patterns.extend(self._analyze_timeframe_patterns())

        # 3. Market condition patterns
        patterns.extend(self._analyze_market_condition_patterns())

        # 4. Technical indicator patterns
        patterns.extend(self._analyze_technical_patterns())

        # 5. Sentiment patterns
        patterns.extend(self._analyze_sentiment_patterns())

        # 6. Combined patterns
        patterns.extend(self._analyze_combined_patterns())

        self.logger.info(f"Identified {len(patterns)} patterns")

        return patterns

    def _analyze_catalyst_patterns(self) -> List[Dict]:
        """Analyze patterns by catalyst type"""
        patterns = []

        # Get all completed signals grouped by catalyst
        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        # Group by catalyst type
        by_catalyst = defaultdict(list)
        for signal in signals:
            if signal.catalyst_type:
                by_catalyst[signal.catalyst_type].append(signal)

        # Analyze each catalyst type
        for catalyst_type, catalyst_signals in by_catalyst.items():
            if len(catalyst_signals) >= self.min_sample_size:
                success_count = sum(1 for s in catalyst_signals if s.status == SignalStatus.SUCCESSFUL)
                success_rate = success_count / len(catalyst_signals)

                if success_rate >= self.min_success_rate:
                    # Get outcomes for additional stats
                    outcomes = [s.outcome for s in catalyst_signals if s.outcome]
                    avg_gain = statistics.mean([o.actual_gain_pct for o in outcomes if o.success_flag]) if any(o.success_flag for o in outcomes) else 0

                    patterns.append({
                        'pattern_type': 'catalyst',
                        'pattern_name': f"{catalyst_type.upper()} Catalyst",
                        'description': f"{catalyst_type.upper()} events show {success_rate:.1%} success rate",
                        'conditions': {'catalyst_type': catalyst_type},
                        'success_rate': success_rate,
                        'sample_size': len(catalyst_signals),
                        'avg_gain_on_success': avg_gain,
                        'confidence': self._calculate_statistical_confidence(success_rate, len(catalyst_signals))
                    })

        return patterns

    def _analyze_timeframe_patterns(self) -> List[Dict]:
        """Analyze patterns by signal timeframe"""
        patterns = []

        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        # Group by signal type
        by_timeframe = defaultdict(list)
        for signal in signals:
            by_timeframe[signal.signal_type.value].append(signal)

        for timeframe, tf_signals in by_timeframe.items():
            if len(tf_signals) >= self.min_sample_size:
                success_count = sum(1 for s in tf_signals if s.status == SignalStatus.SUCCESSFUL)
                success_rate = success_count / len(tf_signals)

                outcomes = [s.outcome for s in tf_signals if s.outcome]
                avg_time_to_peak = statistics.mean([o.time_to_peak_hours for o in outcomes]) if outcomes else 0

                patterns.append({
                    'pattern_type': 'timeframe',
                    'pattern_name': f"{timeframe.replace('_', ' ').title()} Signals",
                    'description': f"{timeframe} signals: {success_rate:.1%} success, avg {avg_time_to_peak/24:.1f} days to peak",
                    'conditions': {'signal_type': timeframe},
                    'success_rate': success_rate,
                    'sample_size': len(tf_signals),
                    'avg_time_to_peak_days': avg_time_to_peak / 24,
                    'confidence': self._calculate_statistical_confidence(success_rate, len(tf_signals))
                })

        return patterns

    def _analyze_market_condition_patterns(self) -> List[Dict]:
        """Analyze patterns based on market conditions at signal time"""
        patterns = []

        # This would analyze broader market conditions
        # For now, we'll analyze by month/season as a proxy

        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        # Group by month
        by_month = defaultdict(list)
        for signal in signals:
            month = signal.timestamp.month
            by_month[month].append(signal)

        # Find months with consistent patterns
        for month, month_signals in by_month.items():
            if len(month_signals) >= 5:  # Lower threshold for time-based
                success_count = sum(1 for s in month_signals if s.status == SignalStatus.SUCCESSFUL)
                success_rate = success_count / len(month_signals)

                if success_rate >= 0.7 or success_rate <= 0.3:  # Very good or very bad
                    month_name = datetime(2000, month, 1).strftime('%B')

                    patterns.append({
                        'pattern_type': 'market_condition',
                        'pattern_name': f"{month_name} Pattern",
                        'description': f"Signals in {month_name} have {success_rate:.1%} success rate",
                        'conditions': {'month': month},
                        'success_rate': success_rate,
                        'sample_size': len(month_signals),
                        'confidence': self._calculate_statistical_confidence(success_rate, len(month_signals))
                    })

        return patterns

    def _analyze_technical_patterns(self) -> List[Dict]:
        """Analyze patterns in technical indicators"""
        patterns = []

        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        # Analyze technical signals from supporting data
        technical_signal_counts = defaultdict(lambda: {'total': 0, 'success': 0})

        for signal in signals:
            supporting_data = signal.supporting_data or {}
            tech_signals = supporting_data.get('technical_signals', [])

            for tech_signal in tech_signals:
                technical_signal_counts[tech_signal]['total'] += 1
                if signal.status == SignalStatus.SUCCESSFUL:
                    technical_signal_counts[tech_signal]['success'] += 1

        # Find significant patterns
        for tech_signal, counts in technical_signal_counts.items():
            if counts['total'] >= self.min_sample_size:
                success_rate = counts['success'] / counts['total']

                if success_rate >= self.min_success_rate:
                    patterns.append({
                        'pattern_type': 'technical',
                        'pattern_name': f"{tech_signal} Signal",
                        'description': f"When {tech_signal} present: {success_rate:.1%} success rate",
                        'conditions': {'technical_signal': tech_signal},
                        'success_rate': success_rate,
                        'sample_size': counts['total'],
                        'confidence': self._calculate_statistical_confidence(success_rate, counts['total'])
                    })

        return patterns

    def _analyze_sentiment_patterns(self) -> List[Dict]:
        """Analyze sentiment strength patterns"""
        patterns = []

        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        # Group by sentiment strength buckets
        sentiment_buckets = {
            'very_strong': [],  # > 0.7
            'strong': [],        # 0.5 - 0.7
            'moderate': [],      # 0.3 - 0.5
            'weak': []           # < 0.3
        }

        for signal in signals:
            supporting_data = signal.supporting_data or {}
            sentiment_score = abs(supporting_data.get('sentiment_score', 0))

            if sentiment_score > 0.7:
                sentiment_buckets['very_strong'].append(signal)
            elif sentiment_score > 0.5:
                sentiment_buckets['strong'].append(signal)
            elif sentiment_score > 0.3:
                sentiment_buckets['moderate'].append(signal)
            else:
                sentiment_buckets['weak'].append(signal)

        # Analyze each bucket
        for bucket_name, bucket_signals in sentiment_buckets.items():
            if len(bucket_signals) >= self.min_sample_size:
                success_count = sum(1 for s in bucket_signals if s.status == SignalStatus.SUCCESSFUL)
                success_rate = success_count / len(bucket_signals)

                patterns.append({
                    'pattern_type': 'sentiment',
                    'pattern_name': f"{bucket_name.replace('_', ' ').title()} Sentiment",
                    'description': f"{bucket_name} sentiment signals: {success_rate:.1%} success rate",
                    'conditions': {'sentiment_strength': bucket_name},
                    'success_rate': success_rate,
                    'sample_size': len(bucket_signals),
                    'confidence': self._calculate_statistical_confidence(success_rate, len(bucket_signals))
                })

        return patterns

    def _analyze_combined_patterns(self) -> List[Dict]:
        """Analyze combinations of factors"""
        patterns = []

        signals = self.session.query(SignalGenerated).filter(
            SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
        ).all()

        # Example: FDA + short-term combination
        fda_short_term = [
            s for s in signals
            if s.catalyst_type == 'fda' and s.signal_type.value == 'short_term'
        ]

        if len(fda_short_term) >= 5:
            success_count = sum(1 for s in fda_short_term if s.status == SignalStatus.SUCCESSFUL)
            success_rate = success_count / len(fda_short_term)

            if success_rate >= 0.7:
                patterns.append({
                    'pattern_type': 'combined',
                    'pattern_name': "FDA + Short-term Combo",
                    'description': f"FDA approvals in short-term timeframe: {success_rate:.1%} success",
                    'conditions': {'catalyst_type': 'fda', 'signal_type': 'short_term'},
                    'success_rate': success_rate,
                    'sample_size': len(fda_short_term),
                    'confidence': self._calculate_statistical_confidence(success_rate, len(fda_short_term))
                })

        # Example: Earnings + high confidence combination
        earnings_high_conf = [
            s for s in signals
            if s.catalyst_type == 'earnings' and s.confidence >= 75
        ]

        if len(earnings_high_conf) >= 5:
            success_count = sum(1 for s in earnings_high_conf if s.status == SignalStatus.SUCCESSFUL)
            success_rate = success_count / len(earnings_high_conf)

            if success_rate >= 0.7:
                patterns.append({
                    'pattern_type': 'combined',
                    'pattern_name': "Earnings + High Confidence",
                    'description': f"Earnings with 75%+ confidence: {success_rate:.1%} success",
                    'conditions': {'catalyst_type': 'earnings', 'min_confidence': 75},
                    'success_rate': success_rate,
                    'sample_size': len(earnings_high_conf),
                    'confidence': self._calculate_statistical_confidence(success_rate, len(earnings_high_conf))
                })

        return patterns

    def _calculate_statistical_confidence(self, success_rate: float, sample_size: int) -> float:
        """
        Calculate statistical confidence in pattern

        Uses simplified confidence interval calculation
        """
        if sample_size < 5:
            return 0.0

        # Wilson score interval (simplified)
        z = 1.96  # 95% confidence
        phat = success_rate
        n = sample_size

        denominator = 1 + z**2 / n
        center = (phat + z**2 / (2*n)) / denominator

        # Return confidence as 0-1
        # More samples = higher confidence
        confidence = min(1.0, (sample_size / 50) * (1 - abs(0.5 - phat)))

        return confidence

    def save_patterns(self, patterns: List[Dict]) -> int:
        """
        Save discovered patterns to database

        Args:
            patterns: List of pattern dictionaries

        Returns:
            Number of patterns saved
        """
        saved_count = 0

        for pattern_data in patterns:
            try:
                # Check if pattern already exists
                existing = self.session.query(LearningPattern).filter_by(
                    pattern_type=pattern_data['pattern_type'],
                    pattern_name=pattern_data['pattern_name']
                ).first()

                if existing:
                    # Update existing pattern
                    existing.success_rate = pattern_data['success_rate']
                    existing.sample_size = pattern_data['sample_size']
                    existing.confidence = pattern_data['confidence']
                    existing.description = pattern_data['description']
                    existing.conditions = pattern_data['conditions']
                    existing.last_validated = datetime.now()
                else:
                    # Create new pattern
                    pattern = LearningPattern(
                        timestamp=datetime.now(),
                        pattern_type=pattern_data['pattern_type'],
                        pattern_name=pattern_data['pattern_name'],
                        description=pattern_data['description'],
                        conditions=pattern_data['conditions'],
                        indicators={},
                        success_rate=pattern_data['success_rate'],
                        sample_size=pattern_data['sample_size'],
                        confidence=pattern_data['confidence'],
                        active=True,
                        last_validated=datetime.now(),
                        avg_gain_on_success=pattern_data.get('avg_gain_on_success', 0),
                        avg_loss_on_failure=0
                    )
                    self.session.add(pattern)

                saved_count += 1

            except Exception as e:
                self.logger.error(f"Error saving pattern {pattern_data['pattern_name']}: {e}")

        self.session.commit()
        self.logger.info(f"Saved {saved_count} patterns to database")

        return saved_count

    def get_active_patterns(
        self,
        pattern_type: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> List[LearningPattern]:
        """
        Get active patterns from database

        Args:
            pattern_type: Filter by pattern type
            min_confidence: Minimum confidence threshold

        Returns:
            List of LearningPattern objects
        """
        query = self.session.query(LearningPattern).filter(
            LearningPattern.active == True,
            LearningPattern.confidence >= min_confidence
        )

        if pattern_type:
            query = query.filter(LearningPattern.pattern_type == pattern_type)

        patterns = query.order_by(LearningPattern.success_rate.desc()).all()

        return patterns

    def match_signal_to_patterns(self, signal_dict: Dict) -> List[Tuple[LearningPattern, float]]:
        """
        Match a signal to discovered patterns

        Args:
            signal_dict: Signal dictionary to match

        Returns:
            List of (pattern, match_score) tuples
        """
        active_patterns = self.get_active_patterns()
        matches = []

        for pattern in active_patterns:
            match_score = self._calculate_pattern_match(signal_dict, pattern)

            if match_score > 0.5:  # 50% match threshold
                matches.append((pattern, match_score))

        # Sort by match score
        matches.sort(key=lambda x: x[1], reverse=True)

        return matches

    def _calculate_pattern_match(self, signal_dict: Dict, pattern: LearningPattern) -> float:
        """Calculate how well a signal matches a pattern"""
        conditions = pattern.conditions or {}
        match_count = 0
        total_conditions = len(conditions)

        if total_conditions == 0:
            return 0.0

        # Check each condition
        if 'catalyst_type' in conditions:
            if signal_dict.get('catalyst_type') == conditions['catalyst_type']:
                match_count += 1

        if 'signal_type' in conditions:
            if signal_dict.get('signal_type') == conditions['signal_type']:
                match_count += 1

        if 'min_confidence' in conditions:
            if signal_dict.get('confidence', 0) >= conditions['min_confidence']:
                match_count += 1

        # Sentiment strength matching
        if 'sentiment_strength' in conditions:
            supporting_data = signal_dict.get('supporting_data', {})
            sentiment_score = abs(supporting_data.get('sentiment_score', 0))

            bucket = conditions['sentiment_strength']
            if bucket == 'very_strong' and sentiment_score > 0.7:
                match_count += 1
            elif bucket == 'strong' and 0.5 < sentiment_score <= 0.7:
                match_count += 1
            elif bucket == 'moderate' and 0.3 < sentiment_score <= 0.5:
                match_count += 1
            elif bucket == 'weak' and sentiment_score <= 0.3:
                match_count += 1

        return match_count / total_conditions

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test pattern recognizer"""
    print("=" * 70)
    print("Pattern Recognizer Test")
    print("=" * 70)
    print()

    recognizer = PatternRecognizer()

    print("Analyzing historical data for patterns...")
    patterns = recognizer.analyze_all_patterns()

    if not patterns:
        print("No patterns found yet")
        print("\nNeed more historical data:")
        print("  1. Generate signals: python -m src.cli signals scan")
        print("  2. Wait for timeframes to expire")
        print("  3. Validate outcomes: python -m src.cli signals validate <id>")
        print("  4. Run pattern analysis again")
        return

    print(f"\nDiscovered {len(patterns)} patterns:\n")

    # Group by type
    by_type = defaultdict(list)
    for pattern in patterns:
        by_type[pattern['pattern_type']].append(pattern)

    for pattern_type, type_patterns in by_type.items():
        print(f"\n{pattern_type.upper()} PATTERNS ({len(type_patterns)}):")
        print("-" * 70)

        for p in type_patterns[:5]:  # Top 5 per type
            print(f"\n• {p['pattern_name']}")
            print(f"  Success Rate: {p['success_rate']:.1%}")
            print(f"  Sample Size: {p['sample_size']}")
            print(f"  Confidence: {p['confidence']:.1%}")
            print(f"  {p['description']}")

    # Save patterns
    print(f"\n{'='*70}")
    saved = recognizer.save_patterns(patterns)
    print(f"✓ Saved {saved} patterns to database")


if __name__ == "__main__":
    main()
