"""
Learning Report Generator
Creates comprehensive reports on system performance and learning insights

This system:
- Generates weekly learning reports
- Analyzes performance trends
- Identifies improvement opportunities
- Tracks weight evolution
- Provides actionable recommendations
- Exports reports in multiple formats
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import json

from src.learning.learning_engine import LearningEngine
from src.learning.pattern_recognizer import PatternRecognizer
from src.learning.adaptive_weights import AdaptiveWeightsSystem
from src.learning.backtester import Backtester
from src.utils.logger import get_logger
from src.config.config_loader import get_config


logger = get_logger("report_generator")


# ============================================================================
# REPORT GENERATOR
# ============================================================================

class ReportGenerator:
    """
    Generates comprehensive learning and performance reports
    """

    def __init__(self):
        self.logger = logger
        self.config = get_config()
        self.learning_engine = LearningEngine()
        self.pattern_recognizer = PatternRecognizer()
        self.adaptive_weights = AdaptiveWeightsSystem()
        self.backtester = Backtester()

        # Reports directory
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    def generate_weekly_report(
        self,
        save_to_file: bool = True
    ) -> Dict:
        """
        Generate comprehensive weekly learning report

        Args:
            save_to_file: Whether to save report to file

        Returns:
            Report dictionary
        """
        self.logger.info("Generating weekly learning report...")

        # Get date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        report = {
            'report_type': 'Weekly Learning Report',
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'sections': {}
        }

        # Section 1: Performance Overview
        report['sections']['performance'] = self._generate_performance_section(days_back=7)

        # Section 2: Pattern Analysis
        report['sections']['patterns'] = self._generate_patterns_section()

        # Section 3: Weight Evolution
        report['sections']['weights'] = self._generate_weights_section()

        # Section 4: Success Factors
        report['sections']['success_factors'] = self._generate_success_factors_section()

        # Section 5: Recommendations
        report['sections']['recommendations'] = self._generate_recommendations_section()

        # Section 6: Backtesting Results
        report['sections']['backtesting'] = self._generate_backtesting_section(
            start_date,
            end_date
        )

        # Section 7: Learning Insights
        report['sections']['insights'] = self._generate_insights_section()

        # Summary
        report['summary'] = self._generate_summary(report)

        # Save to file
        if save_to_file:
            self._save_report(report, 'weekly')

        return report

    def generate_monthly_report(
        self,
        save_to_file: bool = True
    ) -> Dict:
        """
        Generate comprehensive monthly learning report

        Args:
            save_to_file: Whether to save report to file

        Returns:
            Report dictionary
        """
        self.logger.info("Generating monthly learning report...")

        # Get date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        report = {
            'report_type': 'Monthly Learning Report',
            'generated_at': datetime.now().isoformat(),
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'sections': {}
        }

        # Performance overview
        report['sections']['performance'] = self._generate_performance_section(days_back=30)

        # Patterns
        report['sections']['patterns'] = self._generate_patterns_section()

        # Weights evolution
        report['sections']['weights'] = self._generate_weights_section()

        # Success factors
        report['sections']['success_factors'] = self._generate_success_factors_section()

        # Monthly trends
        report['sections']['trends'] = self._generate_trends_section()

        # Recommendations
        report['sections']['recommendations'] = self._generate_recommendations_section()

        # Backtesting
        report['sections']['backtesting'] = self._generate_backtesting_section(
            start_date,
            end_date
        )

        # Summary
        report['summary'] = self._generate_summary(report)

        # Save to file
        if save_to_file:
            self._save_report(report, 'monthly')

        return report

    def generate_performance_report(
        self,
        days_back: int = 30,
        save_to_file: bool = True
    ) -> Dict:
        """
        Generate focused performance report

        Args:
            days_back: Days to analyze
            save_to_file: Whether to save report to file

        Returns:
            Report dictionary
        """
        self.logger.info(f"Generating performance report ({days_back} days)...")

        report = {
            'report_type': 'Performance Report',
            'generated_at': datetime.now().isoformat(),
            'days_analyzed': days_back,
            'sections': {}
        }

        # Performance metrics
        report['sections']['performance'] = self._generate_performance_section(days_back)

        # By catalyst type
        report['sections']['by_catalyst'] = report['sections']['performance'].get('by_catalyst', {})

        # By confidence level
        report['sections']['by_confidence'] = report['sections']['performance'].get('confidence_accuracy_details', {})

        # Top performers
        report['sections']['top_performers'] = self._generate_top_performers_section(days_back)

        # Summary
        report['summary'] = self._generate_summary(report)

        # Save to file
        if save_to_file:
            self._save_report(report, 'performance')

        return report

    def _generate_performance_section(self, days_back: int) -> Dict:
        """Generate performance overview section"""
        analysis = self.learning_engine.analyze_performance(days_back=days_back)

        return {
            'title': 'Performance Overview',
            'total_signals': analysis.get('total_signals', 0),
            'success_rate': analysis.get('success_rate', 0),
            'avg_gain': analysis.get('avg_gain', 0),
            'confidence_accuracy': analysis.get('confidence_accuracy', 0),
            'by_catalyst': analysis.get('by_catalyst', {}),
            'by_signal_type': analysis.get('by_signal_type', {}),
            'recent_performance': analysis.get('recent_trend', 'stable')
        }

    def _generate_patterns_section(self) -> Dict:
        """Generate pattern analysis section"""
        patterns = self.pattern_recognizer.analyze_all_patterns()

        # Get top patterns by success rate
        top_patterns = sorted(
            [p for p in patterns if p['sample_size'] >= 5],
            key=lambda x: x['success_rate'],
            reverse=True
        )[:10]

        return {
            'title': 'Pattern Analysis',
            'total_patterns_discovered': len(patterns),
            'validated_patterns': len([p for p in patterns if p['sample_size'] >= 10]),
            'top_patterns': [
                {
                    'type': p['pattern_type'],
                    'description': p['description'],
                    'success_rate': p['success_rate'],
                    'sample_size': p['sample_size'],
                    'confidence': p['statistical_confidence']
                }
                for p in top_patterns
            ],
            'pattern_coverage': self._calculate_pattern_coverage(patterns)
        }

    def _generate_weights_section(self) -> Dict:
        """Generate weight evolution section"""
        weights = self.adaptive_weights.get_adjusted_weights()
        history = self.adaptive_weights.get_weight_history(last_n=10)

        # Calculate weight trends
        trends = {}
        if len(history) >= 2:
            latest = history[-1]['new_weights']
            previous = history[-2]['new_weights']

            for key in latest:
                if key in previous:
                    change = latest[key] - previous[key]
                    trends[key] = 'increasing' if change > 0 else 'decreasing' if change < 0 else 'stable'

        return {
            'title': 'Weight Evolution',
            'current_weights': weights['signal_generation'],
            'current_version': weights['version'],
            'last_updated': weights['last_updated'],
            'weight_trends': trends,
            'recent_adjustments': [
                {
                    'timestamp': adj['timestamp'],
                    'reason': adj['reason'],
                    'performance_improvement': self._calculate_improvement(adj)
                }
                for adj in history[-5:]
            ],
            'catalyst_multipliers': weights['catalyst_multipliers']
        }

    def _generate_success_factors_section(self) -> Dict:
        """Generate success factors section"""
        analysis = self.learning_engine.analyze_performance(days_back=30)
        success_factors = analysis.get('success_factors', [])

        return {
            'title': 'Success Factors',
            'top_factors': success_factors[:10],
            'factor_categories': self._categorize_factors(success_factors),
            'actionable_insights': self._extract_actionable_insights(success_factors)
        }

    def _generate_trends_section(self) -> Dict:
        """Generate trends analysis section"""
        # Analyze performance over time
        weekly_performance = []
        for week in range(4):
            start_days = (week + 1) * 7
            end_days = week * 7
            analysis = self.learning_engine.analyze_performance(days_back=start_days)

            weekly_performance.append({
                'week': f"Week {4 - week}",
                'success_rate': analysis.get('success_rate', 0),
                'total_signals': analysis.get('total_signals', 0)
            })

        # Calculate trend direction
        if len(weekly_performance) >= 2:
            recent_rate = weekly_performance[-1]['success_rate']
            older_rate = weekly_performance[0]['success_rate']
            trend = 'improving' if recent_rate > older_rate else 'declining' if recent_rate < older_rate else 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'title': 'Performance Trends',
            'weekly_breakdown': weekly_performance,
            'overall_trend': trend,
            'trend_strength': self._calculate_trend_strength(weekly_performance)
        }

    def _generate_recommendations_section(self) -> Dict:
        """Generate recommendations section"""
        recommendations = self.adaptive_weights.get_recommended_adjustments()

        # Categorize recommendations
        by_priority = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        for rec in recommendations:
            rec_type = rec.get('type', 'info')
            if rec_type == 'warning':
                by_priority['high'].append(rec)
            elif rec_type == 'success':
                by_priority['low'].append(rec)
            else:
                by_priority['medium'].append(rec)

        return {
            'title': 'Recommendations',
            'total_recommendations': len(recommendations),
            'by_priority': by_priority,
            'top_actions': [
                rec.get('action', rec.get('message'))
                for rec in recommendations[:5]
            ]
        }

    def _generate_backtesting_section(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Generate backtesting results section"""
        try:
            result = self.backtester.backtest_historical_signals(start_date, end_date)

            return {
                'title': 'Backtesting Results',
                'period': f"{start_date.date()} to {end_date.date()}",
                'total_signals': result.total_signals,
                'success_rate': result.success_rate,
                'total_return': result.total_return,
                'sharpe_ratio': result.sharpe_ratio,
                'max_drawdown': result.max_drawdown,
                'win_loss_ratio': result.win_loss_ratio,
                'best_trade': result.best_trade,
                'worst_trade': result.worst_trade
            }
        except Exception as e:
            self.logger.error(f"Error generating backtesting section: {e}")
            return {
                'title': 'Backtesting Results',
                'error': str(e)
            }

    def _generate_insights_section(self) -> Dict:
        """Generate key insights section"""
        # Get various analyses
        performance = self.learning_engine.analyze_performance(days_back=30)
        patterns = self.pattern_recognizer.analyze_all_patterns()

        insights = []

        # Performance insights
        if performance['total_signals'] >= 20:
            success_rate = performance['success_rate']
            if success_rate >= 70:
                insights.append({
                    'type': 'positive',
                    'category': 'performance',
                    'message': f"Excellent success rate of {success_rate:.1f}% over last 30 days",
                    'impact': 'high'
                })
            elif success_rate < 50:
                insights.append({
                    'type': 'negative',
                    'category': 'performance',
                    'message': f"Success rate below target at {success_rate:.1f}%",
                    'impact': 'high'
                })

        # Pattern insights
        strong_patterns = [p for p in patterns if p['success_rate'] > 75 and p['sample_size'] >= 10]
        if strong_patterns:
            insights.append({
                'type': 'positive',
                'category': 'patterns',
                'message': f"Discovered {len(strong_patterns)} high-confidence patterns",
                'impact': 'medium'
            })

        # Confidence calibration insights
        calibration = performance.get('confidence_accuracy', 0)
        if calibration >= 80:
            insights.append({
                'type': 'positive',
                'category': 'calibration',
                'message': f"Well-calibrated confidence scoring ({calibration:.1f}%)",
                'impact': 'medium'
            })
        elif calibration < 60:
            insights.append({
                'type': 'negative',
                'category': 'calibration',
                'message': f"Confidence scoring needs improvement ({calibration:.1f}%)",
                'impact': 'high'
            })

        return {
            'title': 'Key Insights',
            'insights': insights,
            'insight_count': len(insights)
        }

    def _generate_top_performers_section(self, days_back: int) -> Dict:
        """Generate top performers section"""
        analysis = self.learning_engine.analyze_performance(days_back=days_back)

        # Get best performing catalysts
        by_catalyst = analysis.get('by_catalyst', {})
        top_catalysts = sorted(
            [(k, v) for k, v in by_catalyst.items() if v['total'] >= 5],
            key=lambda x: x[1]['success_rate'],
            reverse=True
        )[:5]

        return {
            'title': 'Top Performers',
            'best_catalysts': [
                {
                    'catalyst': catalyst,
                    'success_rate': stats['success_rate'],
                    'total_signals': stats['total']
                }
                for catalyst, stats in top_catalysts
            ]
        }

    def _generate_summary(self, report: Dict) -> Dict:
        """Generate executive summary"""
        sections = report.get('sections', {})
        performance = sections.get('performance', {})

        # Key metrics
        total_signals = performance.get('total_signals', 0)
        success_rate = performance.get('success_rate', 0)

        # Overall assessment
        if total_signals < 10:
            assessment = 'insufficient_data'
            recommendation = 'Continue collecting data for meaningful analysis'
        elif success_rate >= 70:
            assessment = 'excellent'
            recommendation = 'System performing well - maintain current strategy'
        elif success_rate >= 60:
            assessment = 'good'
            recommendation = 'Good performance - minor optimizations recommended'
        elif success_rate >= 50:
            assessment = 'fair'
            recommendation = 'Moderate performance - review and adjust parameters'
        else:
            assessment = 'needs_improvement'
            recommendation = 'Below target - significant adjustments needed'

        return {
            'overall_assessment': assessment,
            'key_metrics': {
                'total_signals': total_signals,
                'success_rate': success_rate,
                'confidence_accuracy': performance.get('confidence_accuracy', 0)
            },
            'recommendation': recommendation,
            'report_completeness': self._calculate_report_completeness(report)
        }

    def _calculate_pattern_coverage(self, patterns: List[Dict]) -> float:
        """Calculate what % of signals match discovered patterns"""
        # Simplified - would need actual signal matching in production
        validated_patterns = len([p for p in patterns if p['sample_size'] >= 10])
        total_patterns = len(patterns) if patterns else 1
        return (validated_patterns / total_patterns) * 100

    def _calculate_improvement(self, adjustment: Dict) -> float:
        """Calculate performance improvement from adjustment"""
        perf_data = adjustment.get('performance_data', {})
        success_rate = perf_data.get('success_rate', 0)

        # Simplified - would compare to previous period
        return success_rate - 50  # Baseline 50%

    def _categorize_factors(self, factors: List[Dict]) -> Dict:
        """Categorize success factors"""
        categories = {
            'catalyst_related': [],
            'technical_related': [],
            'sentiment_related': [],
            'other': []
        }

        for factor in factors:
            factor_name = factor.get('factor', '').lower()

            if any(word in factor_name for word in ['fda', 'm&a', 'earnings', 'catalyst']):
                categories['catalyst_related'].append(factor)
            elif any(word in factor_name for word in ['rsi', 'macd', 'volume', 'technical']):
                categories['technical_related'].append(factor)
            elif any(word in factor_name for word in ['sentiment', 'positive', 'negative']):
                categories['sentiment_related'].append(factor)
            else:
                categories['other'].append(factor)

        return categories

    def _extract_actionable_insights(self, factors: List[Dict]) -> List[str]:
        """Extract actionable insights from success factors"""
        insights = []

        for factor in factors[:5]:
            percentage = factor.get('percentage', 0)
            factor_name = factor.get('factor', '')

            if percentage >= 70:
                insights.append(
                    f"Prioritize signals with '{factor_name}' (present in {percentage:.0f}% of winners)"
                )

        return insights

    def _calculate_trend_strength(self, weekly_performance: List[Dict]) -> str:
        """Calculate strength of performance trend"""
        if len(weekly_performance) < 2:
            return 'unknown'

        rates = [w['success_rate'] for w in weekly_performance]
        avg_change = sum(rates[i] - rates[i-1] for i in range(1, len(rates))) / (len(rates) - 1)

        if abs(avg_change) < 2:
            return 'weak'
        elif abs(avg_change) < 5:
            return 'moderate'
        else:
            return 'strong'

    def _calculate_report_completeness(self, report: Dict) -> float:
        """Calculate how complete the report is"""
        sections = report.get('sections', {})
        expected_sections = ['performance', 'patterns', 'weights', 'recommendations']

        complete_sections = sum(1 for section in expected_sections if section in sections)
        return (complete_sections / len(expected_sections)) * 100

    def _save_report(self, report: Dict, report_type: str):
        """Save report to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{report_type}_report_{timestamp}.json"
            filepath = self.reports_dir / filename

            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Report saved to {filepath}")

            # Also save as latest
            latest_filepath = self.reports_dir / f"{report_type}_report_latest.json"
            with open(latest_filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error saving report: {e}")

    def export_markdown(self, report: Dict) -> str:
        """
        Export report as markdown

        Args:
            report: Report dictionary

        Returns:
            Markdown formatted string
        """
        md = []

        # Header
        md.append(f"# {report['report_type']}")
        md.append(f"**Generated:** {report['generated_at']}")
        md.append("")

        # Summary
        if 'summary' in report:
            summary = report['summary']
            md.append("## Executive Summary")
            md.append("")
            md.append(f"**Overall Assessment:** {summary['overall_assessment'].upper()}")
            md.append("")
            md.append("**Key Metrics:**")
            for key, value in summary['key_metrics'].items():
                md.append(f"- {key.replace('_', ' ').title()}: {value}")
            md.append("")
            md.append(f"**Recommendation:** {summary['recommendation']}")
            md.append("")

        # Sections
        for section_name, section_data in report.get('sections', {}).items():
            if isinstance(section_data, dict):
                title = section_data.get('title', section_name.title())
                md.append(f"## {title}")
                md.append("")
                md.append(self._format_section_markdown(section_data))
                md.append("")

        return "\n".join(md)

    def _format_section_markdown(self, section: Dict) -> str:
        """Format a section as markdown"""
        lines = []

        for key, value in section.items():
            if key == 'title':
                continue

            if isinstance(value, list):
                lines.append(f"**{key.replace('_', ' ').title()}:**")
                for item in value[:10]:  # Limit to 10 items
                    if isinstance(item, dict):
                        lines.append(f"- {item}")
                    else:
                        lines.append(f"- {item}")
            elif isinstance(value, dict):
                lines.append(f"**{key.replace('_', ' ').title()}:**")
                for k, v in value.items():
                    lines.append(f"- {k}: {v}")
            else:
                lines.append(f"**{key.replace('_', ' ').title()}:** {value}")

        return "\n".join(lines)


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test report generator"""
    print("=" * 70)
    print("Report Generator Test")
    print("=" * 70)
    print()

    generator = ReportGenerator()

    # Generate weekly report
    print("GENERATING WEEKLY REPORT:")
    print("=" * 70)

    report = generator.generate_weekly_report(save_to_file=True)

    print(f"\nReport Type: {report['report_type']}")
    print(f"Generated: {report['generated_at']}")
    print(f"\nSections Included: {len(report['sections'])}")

    # Show summary
    if 'summary' in report:
        summary = report['summary']
        print(f"\nOVERALL ASSESSMENT: {summary['overall_assessment'].upper()}")
        print(f"Recommendation: {summary['recommendation']}")

    # Show performance
    if 'performance' in report['sections']:
        perf = report['sections']['performance']
        print(f"\nPERFORMANCE:")
        print(f"  Total Signals: {perf.get('total_signals', 0)}")
        print(f"  Success Rate: {perf.get('success_rate', 0):.1f}%")
        print(f"  Confidence Accuracy: {perf.get('confidence_accuracy', 0):.1f}%")

    # Export as markdown
    print(f"\n{'='*70}")
    print("EXPORTING AS MARKDOWN:")
    print("=" * 70)

    md = generator.export_markdown(report)
    md_file = generator.reports_dir / "latest_report.md"

    with open(md_file, 'w') as f:
        f.write(md)

    print(f"\n✓ Markdown report saved to {md_file}")


if __name__ == "__main__":
    main()
