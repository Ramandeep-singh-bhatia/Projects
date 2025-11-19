"""
Signal Tracking & Validation System
Monitors investment signals and validates their outcomes

Tracks whether predictions were successful or unsuccessful based on:
- Price movements within timeframe
- Target achievement
- Gain sustainability (24h+ persistence)
- Actual vs predicted performance

Success Classification:
- STRONG SUCCESS: >10% gain sustained 24h+
- MODERATE SUCCESS: 5-10% gain sustained 24h+
- WEAK SUCCESS: 2-5% gain sustained 24h+
- NEAR MISS: Gain achieved but not sustained
- FAILURE: No gain or loss
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from enum import Enum

from src.database.models import (
    SignalGenerated,
    SignalOutcome,
    SignalStatus,
    create_engine_and_session
)
from src.scrapers.market_data_collector import MarketDataService
from src.utils.logger import get_logger
from src.config.config_loader import get_config


logger = get_logger("signal_tracker")


# ============================================================================
# OUTCOME CLASSIFIER
# ============================================================================

class OutcomeType(str, Enum):
    STRONG_SUCCESS = "strong_success"
    MODERATE_SUCCESS = "moderate_success"
    WEAK_SUCCESS = "weak_success"
    NEAR_MISS = "near_miss"
    FAILURE = "failure"


class SignalOutcomeClassifier:
    """
    Classifies signal outcomes based on actual performance
    """

    def __init__(self):
        self.logger = logger
        self.config = get_config()

        # Success thresholds from config
        self.strong_success_threshold = 10.0
        self.moderate_success_threshold = 5.0
        self.weak_success_threshold = 2.0

    def classify_outcome(
        self,
        signal: SignalGenerated,
        peak_gain_pct: float,
        final_gain_pct: float,
        gain_sustained_24h: bool,
        gain_sustained_48h: bool,
        reached_target: bool
    ) -> Tuple[OutcomeType, bool]:
        """
        Classify the outcome of a signal

        Args:
            signal: Original signal
            peak_gain_pct: Peak gain percentage achieved
            final_gain_pct: Final gain at end of timeframe
            gain_sustained_24h: Whether gain persisted 24h after peak
            gain_sustained_48h: Whether gain persisted 48h after peak
            reached_target: Whether target price was reached

        Returns:
            Tuple of (outcome_type, success_flag)
        """
        # Get minimum gain threshold for signal type
        if signal.signal_type.value == 'short_term':
            min_gain = self.config.get('validation.short_term.min_gain_percentage', 2.0)
        else:
            min_gain = self.config.get('validation.long_term.min_gain_percentage', 5.0)

        # FAILURE CONDITIONS

        # 1. Negative movement
        if final_gain_pct < 0:
            return OutcomeType.FAILURE, False

        # 2. Didn't meet minimum gain threshold
        if final_gain_pct < min_gain:
            return OutcomeType.FAILURE, False

        # 3. Gain not sustained (intraday spike only)
        if peak_gain_pct >= min_gain but not gain_sustained_24h:
            return OutcomeType.NEAR_MISS, False

        # SUCCESS CONDITIONS (gain sustained 24h+)

        # Strong success: >10% gain sustained
        if final_gain_pct >= self.strong_success_threshold and gain_sustained_24h:
            return OutcomeType.STRONG_SUCCESS, True

        # Moderate success: 5-10% gain sustained
        if final_gain_pct >= self.moderate_success_threshold and gain_sustained_24h:
            return OutcomeType.MODERATE_SUCCESS, True

        # Weak success: 2-5% gain sustained (for short-term)
        # or 5-10% for long-term
        if final_gain_pct >= self.weak_success_threshold and gain_sustained_24h:
            return OutcomeType.WEAK_SUCCESS, True

        # Near miss: Had gains but didn't sustain well enough
        return OutcomeType.NEAR_MISS, False

    def extract_lessons_learned(
        self,
        signal: SignalGenerated,
        outcome_type: OutcomeType,
        peak_gain_pct: float,
        final_gain_pct: float,
        time_to_peak_hours: float
    ) -> str:
        """
        Generate lessons learned from the outcome

        Args:
            signal: Original signal
            outcome_type: Classified outcome
            peak_gain_pct: Peak gain achieved
            final_gain_pct: Final gain
            time_to_peak_hours: Hours to reach peak

        Returns:
            Lessons learned text
        """
        lessons = []

        if outcome_type in [OutcomeType.STRONG_SUCCESS, OutcomeType.MODERATE_SUCCESS]:
            lessons.append(f"✓ Signal was SUCCESSFUL")

            if peak_gain_pct > signal.expected_gain_pct:
                lessons.append(f"• Exceeded expectations: {peak_gain_pct:.1f}% vs predicted {signal.expected_gain_pct:.1f}%")
            else:
                lessons.append(f"• Met expectations: {peak_gain_pct:.1f}% gain")

            if time_to_peak_hours < 24:
                lessons.append(f"• Quick move: Peaked in {time_to_peak_hours:.1f} hours")
            elif time_to_peak_hours > 72:
                lessons.append(f"• Slow move: Took {time_to_peak_hours/24:.1f} days to peak")

            # What worked
            catalyst = signal.catalyst_type
            if catalyst:
                lessons.append(f"• {catalyst.upper()} catalyst was effective")

        elif outcome_type == OutcomeType.WEAK_SUCCESS:
            lessons.append(f"✓ Signal was marginally successful")
            lessons.append(f"• Achieved {final_gain_pct:.1f}% vs predicted {signal.expected_gain_pct:.1f}%")
            lessons.append(f"• Consider tighter timeframes or earlier exits")

        elif outcome_type == OutcomeType.NEAR_MISS:
            lessons.append(f"✗ Near miss - Gain not sustained")
            lessons.append(f"• Peaked at {peak_gain_pct:.1f}% but faded")
            lessons.append(f"• Consider taking profits earlier at peak")
            lessons.append(f"• {signal.catalyst_type or 'News'} impact was temporary")

        else:  # FAILURE
            lessons.append(f"✗ Signal FAILED")

            if final_gain_pct < 0:
                lessons.append(f"• Price declined {abs(final_gain_pct):.1f}%")
                lessons.append(f"• Catalyst may have been misread or already priced in")
            else:
                lessons.append(f"• Insufficient movement ({final_gain_pct:.1f}%)")
                lessons.append(f"• Market may have ignored catalyst")

            # What didn't work
            if signal.catalyst_type:
                lessons.append(f"• {signal.catalyst_type.upper()} catalyst didn't drive expected movement")

        return "\n".join(lessons)

    def identify_success_factors(
        self,
        signal: SignalGenerated,
        outcome_type: OutcomeType,
        supporting_data: Dict
    ) -> List[str]:
        """
        Identify what factors contributed to success

        Args:
            signal: Original signal
            outcome_type: Outcome classification
            supporting_data: Supporting data from signal

        Returns:
            List of success factors
        """
        factors = []

        if outcome_type in [OutcomeType.STRONG_SUCCESS, OutcomeType.MODERATE_SUCCESS, OutcomeType.WEAK_SUCCESS]:
            # High confidence prediction
            if signal.confidence >= 75:
                factors.append("high_confidence_prediction")

            # Strong catalyst
            if signal.catalyst_type in ['fda', 'm&a', 'earnings']:
                factors.append(f"strong_{signal.catalyst_type}_catalyst")

            # Positive sentiment
            sentiment_score = supporting_data.get('sentiment_score', 0)
            if sentiment_score > 0.5:
                factors.append("strong_positive_sentiment")

            # Good technical setup
            technical_score = supporting_data.get('technical_score', 0)
            if technical_score >= 70:
                factors.append("favorable_technicals")

            # Signal type aligned
            if signal.signal_type.value == 'short_term' and signal.catalyst_type in ['earnings', 'fda']:
                factors.append("appropriate_timeframe")

        return factors

    def identify_failure_factors(
        self,
        signal: SignalGenerated,
        outcome_type: OutcomeType,
        supporting_data: Dict
    ) -> List[str]:
        """
        Identify what factors contributed to failure

        Args:
            signal: Original signal
            outcome_type: Outcome classification
            supporting_data: Supporting data from signal

        Returns:
            List of failure factors
        """
        factors = []

        if outcome_type in [OutcomeType.FAILURE, OutcomeType.NEAR_MISS]:
            # Low confidence
            if signal.confidence < 60:
                factors.append("low_confidence")

            # Weak catalyst
            if not signal.catalyst_type:
                factors.append("no_clear_catalyst")

            # Weak sentiment
            sentiment_score = supporting_data.get('sentiment_score', 0)
            if abs(sentiment_score) < 0.3:
                factors.append("weak_sentiment")

            # Poor technical setup
            technical_score = supporting_data.get('technical_score', 0)
            if technical_score < 40:
                factors.append("poor_technicals")

            # Overconfidence
            if signal.confidence >= 80 and outcome_type == OutcomeType.FAILURE:
                factors.append("overconfident_prediction")

            # News already priced in
            if outcome_type == OutcomeType.NEAR_MISS:
                factors.append("catalyst_already_priced_in")

        return factors


# ============================================================================
# SIGNAL TRACKER
# ============================================================================

class SignalTracker:
    """
    Tracks and validates investment signals
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.logger = logger
        self.config = get_config()
        self.market_service = MarketDataService()
        self.outcome_classifier = SignalOutcomeClassifier()

        # Database session
        if db_session:
            self.session = db_session
        else:
            _, SessionLocal = create_engine_and_session(self.config.database.url)
            self.session = SessionLocal()

    def save_signal(self, signal_dict: Dict) -> SignalGenerated:
        """
        Save a generated signal to database

        Args:
            signal_dict: Signal dictionary from SignalGenerator

        Returns:
            Saved SignalGenerated object
        """
        try:
            # Create signal object
            signal = SignalGenerated(
                timestamp=signal_dict['timestamp'],
                ticker=signal_dict['ticker'],
                company_name=signal_dict['company_name'],
                signal_type=signal_dict['signal_type'],
                timeframe_days=signal_dict['timeframe_days'],
                entry_price=signal_dict['entry_price'],
                current_price_at_signal=signal_dict['current_price_at_signal'],
                target_price=signal_dict['target_price'],
                stop_loss=signal_dict['stop_loss'],
                expected_gain_pct=signal_dict['expected_gain_pct'],
                expected_gain_conservative=signal_dict.get('expected_gain_conservative'),
                expected_gain_moderate=signal_dict.get('expected_gain_moderate'),
                expected_gain_aggressive=signal_dict.get('expected_gain_aggressive'),
                confidence=signal_dict['confidence'],
                risk_score=signal_dict.get('risk_score'),
                risk_factors=signal_dict.get('risk_factors', []),
                rationale=signal_dict['rationale'],
                catalyst_type=signal_dict.get('catalyst_type'),
                supporting_data=signal_dict.get('supporting_data', {}),
                status=SignalStatus.ACTIVE,
                expiry_date=signal_dict['expiry_date']
            )

            self.session.add(signal)
            self.session.commit()

            self.logger.info(f"Saved signal: {signal.ticker} ({signal.signal_type}) ID={signal.id}")

            return signal

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error saving signal: {e}")
            raise

    def track_signal(self, signal_id: int) -> Optional[Dict]:
        """
        Track a specific signal and check its current status

        Args:
            signal_id: Signal ID to track

        Returns:
            Current tracking status
        """
        try:
            signal = self.session.query(SignalGenerated).get(signal_id)

            if not signal:
                self.logger.warning(f"Signal {signal_id} not found")
                return None

            # Get current price
            quote = self.market_service.stock_collector.get_quote(signal.ticker)

            if not quote or not quote.get('current_price'):
                self.logger.warning(f"Could not get current price for {signal.ticker}")
                return None

            current_price = quote['current_price']
            entry_price = signal.entry_price

            # Calculate current gain
            current_gain_pct = ((current_price - entry_price) / entry_price) * 100

            # Time elapsed
            time_elapsed = datetime.now() - signal.timestamp
            hours_elapsed = time_elapsed.total_seconds() / 3600
            days_elapsed = time_elapsed.days

            # Time remaining
            time_remaining = signal.expiry_date - datetime.now()
            days_remaining = time_remaining.days

            # Target achievement
            target_achieved = current_price >= signal.target_price
            stop_loss_hit = current_price <= signal.stop_loss

            # Update last_checked
            signal.last_checked = datetime.now()
            self.session.commit()

            return {
                'signal_id': signal.id,
                'ticker': signal.ticker,
                'status': signal.status.value,
                'entry_price': entry_price,
                'current_price': current_price,
                'target_price': signal.target_price,
                'stop_loss': signal.stop_loss,
                'current_gain_pct': current_gain_pct,
                'expected_gain_pct': signal.expected_gain_pct,
                'target_achieved': target_achieved,
                'stop_loss_hit': stop_loss_hit,
                'days_elapsed': days_elapsed,
                'days_remaining': days_remaining,
                'hours_elapsed': hours_elapsed,
                'confidence': signal.confidence
            }

        except Exception as e:
            self.logger.error(f"Error tracking signal {signal_id}: {e}")
            return None

    def validate_signal(self, signal_id: int) -> Optional[SignalOutcome]:
        """
        Validate a signal's outcome after its timeframe has expired

        Args:
            signal_id: Signal ID to validate

        Returns:
            Created SignalOutcome object
        """
        try:
            signal = self.session.query(SignalGenerated).get(signal_id)

            if not signal:
                self.logger.warning(f"Signal {signal_id} not found")
                return None

            # Check if already validated
            existing_outcome = self.session.query(SignalOutcome).filter_by(signal_id=signal_id).first()
            if existing_outcome:
                self.logger.info(f"Signal {signal_id} already validated")
                return existing_outcome

            self.logger.info(f"Validating signal {signal_id} for {signal.ticker}...")

            # Get historical price data for the signal period
            end_date = min(datetime.now(), signal.expiry_date)
            period_days = (end_date - signal.timestamp).days + 1

            # Determine period string for yfinance
            if period_days <= 5:
                period = "5d"
            elif period_days <= 30:
                period = "1mo"
            else:
                period = "3mo"

            hist_df = self.market_service.stock_collector.get_historical_data(
                signal.ticker,
                period=period,
                interval="1d"
            )

            if hist_df is None or hist_df.empty:
                self.logger.error(f"Could not get historical data for {signal.ticker}")
                return None

            # Filter to signal period only
            hist_df = hist_df[hist_df.index >= signal.timestamp]

            # Find peak price and when it occurred
            peak_price = hist_df['High'].max()
            peak_date = hist_df['High'].idxmax()
            peak_gain_pct = ((peak_price - signal.entry_price) / signal.entry_price) * 100

            # Time to peak
            time_to_peak = peak_date - signal.timestamp
            time_to_peak_hours = time_to_peak.total_seconds() / 3600

            # Check sustainability (24h and 48h after peak)
            gain_sustained_24h = False
            gain_sustained_48h = False
            price_24h_after = None
            price_48h_after = None

            try:
                # Get price 24h after peak
                date_24h = peak_date + timedelta(days=1)
                if date_24h in hist_df.index:
                    price_24h_after = hist_df.loc[date_24h, 'Close']
                    gain_24h = ((price_24h_after - signal.entry_price) / signal.entry_price) * 100
                    gain_sustained_24h = gain_24h >= (peak_gain_pct * 0.8)  # Sustained if within 80% of peak

                # Get price 48h after peak
                date_48h = peak_date + timedelta(days=2)
                if date_48h in hist_df.index:
                    price_48h_after = hist_df.loc[date_48h, 'Close']
                    gain_48h = ((price_48h_after - signal.entry_price) / signal.entry_price) * 100
                    gain_sustained_48h = gain_48h >= (peak_gain_pct * 0.75)  # 75% of peak

            except Exception as e:
                self.logger.warning(f"Could not check sustainability: {e}")

            # Final price at end of period
            final_price = hist_df['Close'].iloc[-1]
            final_gain_pct = ((final_price - signal.entry_price) / signal.entry_price) * 100

            # Holding period
            holding_period_days = (hist_df.index[-1] - signal.timestamp).days

            # Target reached?
            reached_target = peak_price >= signal.target_price

            # Classify outcome
            outcome_type, success_flag = self.outcome_classifier.classify_outcome(
                signal=signal,
                peak_gain_pct=peak_gain_pct,
                final_gain_pct=final_gain_pct,
                gain_sustained_24h=gain_sustained_24h,
                gain_sustained_48h=gain_sustained_48h,
                reached_target=reached_target
            )

            # Extract lessons
            lessons = self.outcome_classifier.extract_lessons_learned(
                signal=signal,
                outcome_type=outcome_type,
                peak_gain_pct=peak_gain_pct,
                final_gain_pct=final_gain_pct,
                time_to_peak_hours=time_to_peak_hours
            )

            # Identify success/failure factors
            supporting_data = signal.supporting_data or {}

            if success_flag:
                what_worked = self.outcome_classifier.identify_success_factors(
                    signal, outcome_type, supporting_data
                )
                what_failed = []
            else:
                what_worked = []
                what_failed = self.outcome_classifier.identify_failure_factors(
                    signal, outcome_type, supporting_data
                )

            # Create outcome record
            outcome = SignalOutcome(
                signal_id=signal.id,
                timestamp=datetime.now(),
                peak_price=float(peak_price),
                peak_timestamp=peak_date.to_pydatetime() if hasattr(peak_date, 'to_pydatetime') else peak_date,
                peak_gain_pct=float(peak_gain_pct),
                time_to_peak_hours=float(time_to_peak_hours),
                price_24h_after_peak=float(price_24h_after) if price_24h_after else None,
                price_48h_after_peak=float(price_48h_after) if price_48h_after else None,
                gain_sustained_24h=gain_sustained_24h,
                gain_sustained_48h=gain_sustained_48h,
                final_outcome=outcome_type.value,
                success_flag=success_flag,
                actual_gain_pct=float(final_gain_pct),
                holding_period_days=float(holding_period_days),
                exit_price=float(final_price),
                exit_timestamp=hist_df.index[-1].to_pydatetime() if hasattr(hist_df.index[-1], 'to_pydatetime') else hist_df.index[-1],
                exit_reason="timeframe_expired",
                what_worked=what_worked,
                what_failed=what_failed,
                lessons_learned=lessons,
                pattern_matched=signal.catalyst_type
            )

            # Update signal status
            if success_flag:
                signal.status = SignalStatus.SUCCESSFUL
            else:
                signal.status = SignalStatus.UNSUCCESSFUL

            # Save outcome
            self.session.add(outcome)
            self.session.commit()

            self.logger.info(
                f"✓ Signal {signal_id} validated: {outcome_type.value.upper()} "
                f"({final_gain_pct:+.1f}% actual vs {signal.expected_gain_pct:.1f}% predicted)"
            )

            return outcome

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error validating signal {signal_id}: {e}")
            return None

    def track_all_active_signals(self) -> List[Dict]:
        """
        Track all active signals

        Returns:
            List of tracking status dictionaries
        """
        try:
            active_signals = self.session.query(SignalGenerated).filter_by(
                status=SignalStatus.ACTIVE
            ).all()

            results = []

            for signal in active_signals:
                status = self.track_signal(signal.id)
                if status:
                    results.append(status)

                # Auto-validate if expired
                if datetime.now() > signal.expiry_date:
                    self.logger.info(f"Signal {signal.id} expired - validating...")
                    self.validate_signal(signal.id)

            return results

        except Exception as e:
            self.logger.error(f"Error tracking active signals: {e}")
            return []

    def get_signal_performance_summary(self) -> Dict:
        """
        Get overall signal performance statistics

        Returns:
            Performance summary dictionary
        """
        try:
            # Get all signals with outcomes
            signals_with_outcomes = self.session.query(SignalGenerated).filter(
                SignalGenerated.status.in_([SignalStatus.SUCCESSFUL, SignalStatus.UNSUCCESSFUL])
            ).all()

            if not signals_with_outcomes:
                return {
                    'total_signals': 0,
                    'success_rate': 0.0,
                    'avg_gain_winners': 0.0,
                    'avg_loss_losers': 0.0
                }

            total = len(signals_with_outcomes)
            successful = sum(1 for s in signals_with_outcomes if s.status == SignalStatus.SUCCESSFUL)
            unsuccessful = total - successful

            success_rate = (successful / total * 100) if total > 0 else 0.0

            # Get outcomes for detailed stats
            outcomes = [s.outcome for s in signals_with_outcomes if s.outcome]

            winners = [o for o in outcomes if o.success_flag]
            losers = [o for o in outcomes if not o.success_flag]

            avg_gain_winners = sum(o.actual_gain_pct for o in winners) / len(winners) if winners else 0.0
            avg_loss_losers = sum(o.actual_gain_pct for o in losers) / len(losers) if losers else 0.0

            # By signal type
            short_term_signals = [s for s in signals_with_outcomes if s.signal_type.value == 'short_term']
            long_term_signals = [s for s in signals_with_outcomes if s.signal_type.value == 'long_term']

            short_term_success = sum(1 for s in short_term_signals if s.status == SignalStatus.SUCCESSFUL)
            long_term_success = sum(1 for s in long_term_signals if s.status == SignalStatus.SUCCESSFUL)

            short_term_rate = (short_term_success / len(short_term_signals) * 100) if short_term_signals else 0.0
            long_term_rate = (long_term_success / len(long_term_signals) * 100) if long_term_signals else 0.0

            return {
                'total_signals': total,
                'successful_signals': successful,
                'unsuccessful_signals': unsuccessful,
                'success_rate': success_rate,
                'avg_gain_winners': avg_gain_winners,
                'avg_loss_losers': avg_loss_losers,
                'short_term': {
                    'total': len(short_term_signals),
                    'successful': short_term_success,
                    'success_rate': short_term_rate
                },
                'long_term': {
                    'total': len(long_term_signals),
                    'successful': long_term_success,
                    'success_rate': long_term_rate
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {}

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test signal tracking"""
    print("=" * 70)
    print("Signal Tracker Test")
    print("=" * 70)
    print()

    tracker = SignalTracker()

    print("Tracking all active signals...")
    results = tracker.track_all_active_signals()

    if not results:
        print("No active signals to track")
        print("\nGenerate signals first:")
        print("  python -m src.cli signals scan")
        return

    print(f"\nActive Signals ({len(results)}):")
    print("=" * 70)

    for result in results:
        print(f"\n{result['ticker']} - {result['status'].upper()}")
        print(f"  Entry: ${result['entry_price']:.2f}")
        print(f"  Current: ${result['current_price']:.2f}")
        print(f"  Target: ${result['target_price']:.2f}")
        print(f"  Current Gain: {result['current_gain_pct']:+.1f}% (Expected: {result['expected_gain_pct']:.1f}%)")
        print(f"  Days Elapsed: {result['days_elapsed']} / {result['days_elapsed'] + result['days_remaining']}")

        if result['target_achieved']:
            print(f"  ✓ TARGET ACHIEVED!")
        if result['stop_loss_hit']:
            print(f"  ✗ STOP LOSS HIT!")

    # Performance summary
    print("\n" + "=" * 70)
    print("Performance Summary:")
    print("=" * 70)

    summary = tracker.get_signal_performance_summary()

    if summary.get('total_signals', 0) > 0:
        print(f"Total Signals: {summary['total_signals']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Avg Gain (Winners): {summary['avg_gain_winners']:+.1f}%")
        print(f"Avg Loss (Losers): {summary['avg_loss_losers']:+.1f}%")
        print(f"\nShort-term Success: {summary['short_term']['success_rate']:.1f}% ({summary['short_term']['successful']}/{summary['short_term']['total']})")
        print(f"Long-term Success: {summary['long_term']['success_rate']:.1f}% ({summary['long_term']['successful']}/{summary['long_term']['total']})")
    else:
        print("No completed signals yet")


if __name__ == "__main__":
    main()
