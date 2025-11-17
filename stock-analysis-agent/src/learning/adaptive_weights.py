"""
Adaptive Weight Adjustment System
Automatically adjusts signal generation weights based on historical performance

This system:
- Uses learning engine insights to optimize weights
- Adjusts confidence scoring formulas
- Tunes risk thresholds
- Adapts to changing market conditions
- Maintains history of weight changes
"""

from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

from src.learning.learning_engine import LearningEngine
from src.learning.pattern_recognizer import PatternRecognizer
from src.utils.logger import get_logger
from src.config.config_loader import get_config


logger = get_logger("adaptive_weights")


# ============================================================================
# ADAPTIVE WEIGHTS SYSTEM
# ============================================================================

class AdaptiveWeightsSystem:
    """
    Manages adaptive weight adjustments based on learning
    """

    def __init__(self):
        self.logger = logger
        self.config = get_config()
        self.learning_engine = LearningEngine()
        self.pattern_recognizer = PatternRecognizer()

        # Weights file path
        self.weights_file = Path("data/adaptive_weights.json")
        self.weights_file.parent.mkdir(exist_ok=True)

        # Load current weights
        self.current_weights = self._load_weights()

    def _load_weights(self) -> Dict:
        """Load current weights from file"""
        if self.weights_file.exists():
            try:
                with open(self.weights_file, 'r') as f:
                    data = json.load(f)
                    self.logger.info("Loaded adaptive weights from file")
                    return data
            except Exception as e:
                self.logger.error(f"Error loading weights: {e}")

        # Default weights
        return {
            'version': 1,
            'last_updated': None,
            'signal_generation': {
                'catalyst_weight': 0.4,
                'technical_weight': 0.3,
                'sentiment_weight': 0.3
            },
            'confidence_thresholds': {
                'min_signal_confidence': 60,
                'high_confidence': 75,
                'medium_confidence': 60,
                'low_confidence': 50
            },
            'risk_thresholds': {
                'critical': 80,
                'high': 60,
                'medium': 40,
                'low': 20
            },
            'catalyst_multipliers': {
                'fda': 1.5,
                'm&a': 1.4,
                'earnings': 1.2,
                'contract': 1.1,
                'product': 1.1,
                'analyst': 1.0
            },
            'adjustment_history': []
        }

    def _save_weights(self):
        """Save weights to file"""
        try:
            with open(self.weights_file, 'w') as f:
                json.dump(self.current_weights, f, indent=2, default=str)
            self.logger.info("Saved adaptive weights to file")
        except Exception as e:
            self.logger.error(f"Error saving weights: {e}")

    def update_weights(self, min_signals: int = 20) -> Dict:
        """
        Update weights based on recent performance

        Args:
            min_signals: Minimum signals required for update

        Returns:
            Update summary
        """
        self.logger.info("Updating adaptive weights...")

        # Get optimal weights from learning engine
        weight_analysis = self.learning_engine.calculate_optimal_weights()

        if not weight_analysis:
            return {
                'updated': False,
                'reason': 'Insufficient data for weight optimization'
            }

        # Check if we have enough data
        analysis = self.learning_engine.analyze_performance(days_back=30)

        if analysis['total_signals'] < min_signals:
            return {
                'updated': False,
                'reason': f'Need at least {min_signals} signals (have {analysis["total_signals"]})'
            }

        old_weights = self.current_weights['signal_generation'].copy()
        adjusted_weights = weight_analysis['adjusted_weights']

        # Update signal generation weights
        self.current_weights['signal_generation'] = {
            'catalyst_weight': adjusted_weights['catalyst'],
            'technical_weight': adjusted_weights['technical'],
            'sentiment_weight': adjusted_weights['sentiment']
        }

        # Update catalyst multipliers based on performance
        self._update_catalyst_multipliers(analysis)

        # Update confidence thresholds based on calibration
        self._update_confidence_thresholds(analysis)

        # Record adjustment
        adjustment_record = {
            'timestamp': datetime.now().isoformat(),
            'reason': 'Automatic optimization',
            'old_weights': old_weights,
            'new_weights': self.current_weights['signal_generation'],
            'performance_data': {
                'success_rate': analysis['success_rate'],
                'total_signals': analysis['total_signals'],
                'confidence_accuracy': analysis['confidence_accuracy']
            }
        }

        self.current_weights['adjustment_history'].append(adjustment_record)
        self.current_weights['last_updated'] = datetime.now().isoformat()
        self.current_weights['version'] += 1

        # Save to file
        self._save_weights()

        return {
            'updated': True,
            'old_weights': old_weights,
            'new_weights': self.current_weights['signal_generation'],
            'changes': {
                key: new - old_weights[key.replace('_weight', '') + '_weight']
                for key, new in self.current_weights['signal_generation'].items()
            },
            'version': self.current_weights['version']
        }

    def _update_catalyst_multipliers(self, analysis: Dict):
        """Update catalyst multipliers based on performance"""
        by_catalyst = analysis.get('by_catalyst', {})

        for catalyst, stats in by_catalyst.items():
            if stats['total'] >= 5:  # Minimum sample
                success_rate = stats['success_rate']

                # Adjust multiplier based on success rate
                current = self.current_weights['catalyst_multipliers'].get(catalyst, 1.0)

                if success_rate >= 75:
                    # High success - increase multiplier
                    new_multiplier = min(2.0, current * 1.1)
                elif success_rate < 40:
                    # Low success - decrease multiplier
                    new_multiplier = max(0.8, current * 0.9)
                else:
                    # Average success - small adjustment
                    target = 1.0 + (success_rate - 50) / 100
                    new_multiplier = current + (target - current) * 0.1

                self.current_weights['catalyst_multipliers'][catalyst] = round(new_multiplier, 2)

    def _update_confidence_thresholds(self, analysis: Dict):
        """Update confidence thresholds based on calibration"""
        confidence_accuracy = analysis.get('confidence_accuracy', 0)

        current_min = self.current_weights['confidence_thresholds']['min_signal_confidence']

        # If confidence is poorly calibrated, adjust threshold
        if confidence_accuracy < 60:
            # Poor calibration - raise threshold
            new_min = min(70, current_min + 2)
            self.current_weights['confidence_thresholds']['min_signal_confidence'] = new_min
        elif confidence_accuracy > 85 and analysis['success_rate'] > 60:
            # Good calibration and good performance - can lower threshold slightly
            new_min = max(55, current_min - 1)
            self.current_weights['confidence_thresholds']['min_signal_confidence'] = new_min

    def get_adjusted_weights(self) -> Dict:
        """
        Get current adjusted weights for use in signal generation

        Returns:
            Current weights dictionary
        """
        return self.current_weights

    def apply_pattern_boost(self, signal_dict: Dict) -> float:
        """
        Apply confidence boost if signal matches successful patterns

        Args:
            signal_dict: Signal dictionary to evaluate

        Returns:
            Confidence boost (0-20 points)
        """
        # Match signal to patterns
        matches = self.pattern_recognizer.match_signal_to_patterns(signal_dict)

        if not matches:
            return 0.0

        # Calculate boost based on best matching pattern
        best_pattern, match_score = matches[0]

        # Boost = pattern success rate × match score × max boost (20)
        boost = (best_pattern.success_rate - 0.5) * match_score * 20

        return max(0, min(20, boost))  # Cap at 20 points

    def get_recommended_adjustments(self) -> List[Dict]:
        """
        Get recommended manual adjustments based on learning

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        # Analyze recent performance
        analysis = self.learning_engine.analyze_performance(days_back=30)

        if analysis['total_signals'] < 10:
            return [{
                'type': 'info',
                'message': 'Collect more signal data before adjusting weights (need 10+)'
            }]

        # Check success rate
        if analysis['success_rate'] < 50:
            recommendations.append({
                'type': 'warning',
                'category': 'confidence',
                'message': f"Success rate is low ({analysis['success_rate']:.1f}%)",
                'action': 'Increase minimum confidence threshold to 65-70'
            })

        # Check confidence calibration
        if analysis['confidence_accuracy'] < 60:
            recommendations.append({
                'type': 'warning',
                'category': 'calibration',
                'message': f"Confidence poorly calibrated ({analysis['confidence_accuracy']:.1f}%)",
                'action': 'Review confidence scoring formula'
            })

        # Catalyst-specific recommendations
        by_catalyst = analysis.get('by_catalyst', {})
        for catalyst, stats in by_catalyst.items():
            if stats['total'] >= 5:
                if stats['success_rate'] > 75:
                    recommendations.append({
                        'type': 'success',
                        'category': 'catalyst',
                        'message': f"{catalyst.upper()} signals performing well ({stats['success_rate']:.1f}%)",
                        'action': f"Prioritize {catalyst} signals - increase multiplier"
                    })
                elif stats['success_rate'] < 40:
                    recommendations.append({
                        'type': 'warning',
                        'category': 'catalyst',
                        'message': f"{catalyst.upper()} signals underperforming ({stats['success_rate']:.1f}%)",
                        'action': f"Reduce {catalyst} signal generation or lower multiplier"
                    })

        # Success factor recommendations
        if analysis.get('success_factors'):
            top_factor = analysis['success_factors'][0]
            if top_factor['percentage'] > 60:
                recommendations.append({
                    'type': 'insight',
                    'category': 'success_factor',
                    'message': f"'{top_factor['factor']}' present in {top_factor['percentage']:.0f}% of winners",
                    'action': 'Prioritize signals with this factor'
                })

        return recommendations

    def get_weight_history(self, last_n: int = 10) -> List[Dict]:
        """
        Get history of weight adjustments

        Args:
            last_n: Number of recent adjustments to return

        Returns:
            List of adjustment records
        """
        history = self.current_weights.get('adjustment_history', [])
        return history[-last_n:] if history else []


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test adaptive weights system"""
    print("=" * 70)
    print("Adaptive Weights System Test")
    print("=" * 70)
    print()

    system = AdaptiveWeightsSystem()

    # Show current weights
    print("CURRENT WEIGHTS:")
    print("=" * 70)
    weights = system.get_adjusted_weights()

    print(f"\nSignal Generation:")
    for key, value in weights['signal_generation'].items():
        print(f"  {key}: {value:.3f}")

    print(f"\nConfidence Thresholds:")
    for key, value in weights['confidence_thresholds'].items():
        print(f"  {key}: {value}")

    print(f"\nCatalyst Multipliers:")
    for key, value in weights['catalyst_multipliers'].items():
        print(f"  {key}: {value:.2f}x")

    # Try to update weights
    print(f"\n{'='*70}")
    print("UPDATING WEIGHTS:")
    print("=" * 70)

    result = system.update_weights(min_signals=10)

    if result['updated']:
        print("\n✓ Weights updated successfully!")
        print(f"Version: {result['version']}")
        print(f"\nChanges:")
        for key, change in result['changes'].items():
            symbol = '+' if change > 0 else ''
            print(f"  {key}: {symbol}{change:.3f}")
    else:
        print(f"\n✗ Weights not updated: {result['reason']}")

    # Get recommendations
    print(f"\n{'='*70}")
    print("RECOMMENDATIONS:")
    print("=" * 70)

    recs = system.get_recommended_adjustments()

    if recs:
        for rec in recs:
            symbol = {
                'warning': '⚠️',
                'success': '✓',
                'insight': '💡',
                'info': 'ℹ️'
            }.get(rec['type'], '•')

            print(f"\n{symbol} {rec['message']}")
            if 'action' in rec:
                print(f"   Action: {rec['action']}")
    else:
        print("\nNo recommendations at this time")


if __name__ == "__main__":
    main()
