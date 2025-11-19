"""
Analysis Agent - Specialized in data analysis, visualization, and insights.
Capabilities: Statistical analysis, data visualization, trend identification, forecasting.
"""

from typing import Dict, Any, Optional, List
from loguru import logger

from backend.agents.base_agent import BaseAgent
from backend.tools.data_analysis import DataAnalysisTool


class AnalysisAgent(BaseAgent):
    """
    Analysis Agent for data analysis and visualization.

    Specializes in:
    - Data cleaning and transformation
    - Statistical analysis and modeling
    - Data visualization and dashboards
    - Trend identification and forecasting
    - Performance benchmarking
    """

    def __init__(self, **kwargs):
        """Initialize the Analysis Agent."""
        super().__init__(
            agent_type="analysis",
            role="Senior Data Analyst",
            goal="Analyze data, identify trends, and generate actionable insights through visualization and statistical analysis",
            backstory="""You are an expert data analyst with deep knowledge of statistics,
            data science, and business intelligence. You excel at transforming raw data
            into meaningful insights, creating compelling visualizations, and identifying
            patterns that drive business decisions. Your analyses are rigorous, accurate,
            and clearly communicated.""",
            tools=[],
            **kwargs,
        )

        # Initialize analysis tools
        self.data_tool = DataAnalysisTool()

    async def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute an analysis task.

        Args:
            task: Analysis task description
            context: Additional context including data

        Returns:
            Analysis results
        """
        logger.info(f"Analysis Agent executing task: {task[:100]}...")

        context = context or {}
        analysis_type = context.get("analysis_type", "descriptive")
        data = context.get("data")

        if not data:
            return {
                "status": "failed",
                "error": "No data provided for analysis",
            }

        try:
            # Load data
            load_result = self.data_tool.load_data("analysis_data", data)
            if not load_result.get("success"):
                return {
                    "status": "failed",
                    "error": f"Failed to load data: {load_result.get('error')}",
                }

            # Perform analysis based on type
            if analysis_type == "descriptive":
                results = await self._descriptive_analysis(task, context)
            elif analysis_type == "statistical":
                results = await self._statistical_analysis(task, context)
            elif analysis_type == "visualization":
                results = await self._create_visualizations(task, context)
            elif analysis_type == "trend":
                results = await self._trend_analysis(task, context)
            else:
                results = await self._comprehensive_analysis(task, context)

            return {
                "status": "completed",
                "analysis_type": analysis_type,
                "results": results,
                "tokens_used": 0,
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Error in analysis task: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "results": None,
            }

    async def _descriptive_analysis(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform descriptive statistical analysis.

        Args:
            task: Analysis task
            context: Context with data

        Returns:
            Descriptive statistics
        """
        result = self.data_tool.describe_data("analysis_data")

        return {
            "description": result,
            "insights": self._generate_insights(result),
        }

    async def _statistical_analysis(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform statistical analysis.

        Args:
            task: Analysis task
            context: Context with configuration

        Returns:
            Statistical analysis results
        """
        columns = context.get("columns", [])
        statistics = {}

        describe_result = self.data_tool.describe_data("analysis_data")
        if not describe_result.get("success"):
            return describe_result

        # Calculate statistics for each column
        for column in columns:
            statistics[column] = {
                "mean": self.data_tool.calculate_statistics(
                    "analysis_data", column, "mean"
                ),
                "median": self.data_tool.calculate_statistics(
                    "analysis_data", column, "median"
                ),
                "std": self.data_tool.calculate_statistics(
                    "analysis_data", column, "std"
                ),
            }

        return {
            "statistics": statistics,
            "summary": describe_result,
        }

    async def _create_visualizations(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create data visualizations.

        Args:
            task: Visualization task
            context: Visualization configuration

        Returns:
            Visualization results
        """
        charts = context.get("charts", [])
        visualizations = []

        for chart_config in charts:
            chart_type = chart_config.get("type", "line")
            x_column = chart_config.get("x_column")
            y_column = chart_config.get("y_column")
            title = chart_config.get("title", "Data Visualization")

            viz_result = self.data_tool.create_visualization(
                "analysis_data",
                chart_type,
                x_column,
                y_column,
                title,
            )

            visualizations.append(viz_result)

        return {
            "visualizations": visualizations,
            "count": len(visualizations),
        }

    async def _trend_analysis(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze trends in data.

        Args:
            task: Trend analysis task
            context: Configuration

        Returns:
            Trend analysis results
        """
        time_column = context.get("time_column")
        value_columns = context.get("value_columns", [])

        trends = {}

        for column in value_columns:
            # Create trend visualization
            viz = self.data_tool.create_visualization(
                "analysis_data",
                "line",
                time_column,
                column,
                f"Trend: {column} over time",
            )

            # Calculate statistics
            stats = {
                "mean": self.data_tool.calculate_statistics(
                    "analysis_data", column, "mean"
                ),
                "std": self.data_tool.calculate_statistics(
                    "analysis_data", column, "std"
                ),
            }

            trends[column] = {
                "visualization": viz,
                "statistics": stats,
                "trend_direction": self._determine_trend(stats),
            }

        return trends

    async def _comprehensive_analysis(
        self,
        task: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining multiple techniques.

        Args:
            task: Analysis task
            context: Context

        Returns:
            Comprehensive analysis results
        """
        # Descriptive statistics
        description = self.data_tool.describe_data("analysis_data")

        # Key visualizations
        visualizations = []

        # Histogram for first numeric column
        if description.get("success"):
            numeric_columns = [
                col for col, dtype in description.get("dtypes", {}).items()
                if "int" in str(dtype) or "float" in str(dtype)
            ]

            if numeric_columns:
                # Distribution plot
                hist = self.data_tool.create_visualization(
                    "analysis_data",
                    "histogram",
                    x_column=numeric_columns[0],
                    title=f"Distribution of {numeric_columns[0]}",
                )
                visualizations.append(hist)

                # Correlation heatmap
                heatmap = self.data_tool.create_visualization(
                    "analysis_data",
                    "heatmap",
                    title="Correlation Heatmap",
                )
                visualizations.append(heatmap)

        return {
            "descriptive_statistics": description,
            "visualizations": visualizations,
            "insights": self._generate_comprehensive_insights(description),
        }

    def _generate_insights(self, stats: Dict[str, Any]) -> List[str]:
        """Generate insights from statistics."""
        insights = []

        if not stats.get("success"):
            return insights

        shape = stats.get("shape", [0, 0])
        missing = stats.get("missing_values", {})

        insights.append(f"Dataset contains {shape[0]} rows and {shape[1]} columns")

        # Check for missing values
        missing_cols = [col for col, count in missing.items() if count > 0]
        if missing_cols:
            insights.append(
                f"Missing values detected in {len(missing_cols)} columns: {', '.join(missing_cols[:3])}"
            )

        return insights

    def _generate_comprehensive_insights(self, stats: Dict[str, Any]) -> List[str]:
        """Generate comprehensive insights."""
        insights = self._generate_insights(stats)

        if stats.get("success") and "statistics" in stats:
            statistics = stats["statistics"]
            insights.append(f"Statistical analysis completed for {len(statistics)} numeric columns")

        return insights

    def _determine_trend(self, stats: Dict[str, Any]) -> str:
        """Determine trend direction from statistics."""
        # Simple heuristic (in production, use time series analysis)
        return "stable"  # Could be 'increasing', 'decreasing', 'stable', 'volatile'
