"""
Data analysis tools for analysis agents.
Provides Python code execution, data visualization, and statistical analysis.
"""

import json
import io
import sys
import base64
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger


class DataAnalysisTool:
    """Tool for data analysis and visualization."""

    def __init__(self):
        """Initialize data analysis tool."""
        self.dataframes: Dict[str, pd.DataFrame] = {}
        sns.set_style("whitegrid")

    def load_data(
        self,
        name: str,
        data: Any,
        data_type: str = "dict",
    ) -> Dict[str, Any]:
        """
        Load data into a DataFrame.

        Args:
            name: Name to reference the dataset
            data: Data to load
            data_type: Type of data ('dict', 'csv', 'json', 'list')

        Returns:
            Status and info about loaded data
        """
        try:
            if data_type == "dict":
                df = pd.DataFrame(data)
            elif data_type == "csv":
                df = pd.read_csv(io.StringIO(data))
            elif data_type == "json":
                df = pd.read_json(io.StringIO(data))
            elif data_type == "list":
                df = pd.DataFrame(data)
            else:
                return {"success": False, "error": f"Unknown data type: {data_type}"}

            self.dataframes[name] = df

            return {
                "success": True,
                "name": name,
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "sample": df.head(5).to_dict(),
            }
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return {"success": False, "error": str(e)}

    def describe_data(self, name: str) -> Dict[str, Any]:
        """
        Get descriptive statistics for a dataset.

        Args:
            name: Name of the dataset

        Returns:
            Descriptive statistics
        """
        try:
            if name not in self.dataframes:
                return {"success": False, "error": f"Dataset '{name}' not found"}

            df = self.dataframes[name]

            return {
                "success": True,
                "shape": df.shape,
                "columns": list(df.columns),
                "dtypes": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "statistics": df.describe().to_dict(),
                "sample": df.head(10).to_dict(),
            }
        except Exception as e:
            logger.error(f"Error describing data: {e}")
            return {"success": False, "error": str(e)}

    def filter_data(
        self,
        name: str,
        conditions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Filter data based on conditions.

        Args:
            name: Name of the dataset
            conditions: List of filter conditions

        Returns:
            Filtered data info
        """
        try:
            if name not in self.dataframes:
                return {"success": False, "error": f"Dataset '{name}' not found"}

            df = self.dataframes[name].copy()

            for condition in conditions:
                column = condition.get("column")
                operator = condition.get("operator")
                value = condition.get("value")

                if operator == "==":
                    df = df[df[column] == value]
                elif operator == ">":
                    df = df[df[column] > value]
                elif operator == "<":
                    df = df[df[column] < value]
                elif operator == ">=":
                    df = df[df[column] >= value]
                elif operator == "<=":
                    df = df[df[column] <= value]
                elif operator == "contains":
                    df = df[df[column].str.contains(value, na=False)]

            return {
                "success": True,
                "filtered_shape": df.shape,
                "data": df.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error filtering data: {e}")
            return {"success": False, "error": str(e)}

    def aggregate_data(
        self,
        name: str,
        group_by: List[str],
        aggregations: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Aggregate data by groups.

        Args:
            name: Name of the dataset
            group_by: Columns to group by
            aggregations: Aggregation functions per column

        Returns:
            Aggregated data
        """
        try:
            if name not in self.dataframes:
                return {"success": False, "error": f"Dataset '{name}' not found"}

            df = self.dataframes[name]
            result = df.groupby(group_by).agg(aggregations)

            return {
                "success": True,
                "shape": result.shape,
                "data": result.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error aggregating data: {e}")
            return {"success": False, "error": str(e)}

    def create_visualization(
        self,
        name: str,
        chart_type: str,
        x_column: Optional[str] = None,
        y_column: Optional[str] = None,
        title: str = "Data Visualization",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Create a data visualization.

        Args:
            name: Name of the dataset
            chart_type: Type of chart ('line', 'bar', 'scatter', 'histogram', 'box', 'heatmap')
            x_column: Column for x-axis
            y_column: Column for y-axis
            title: Chart title
            **kwargs: Additional chart parameters

        Returns:
            Base64-encoded image and metadata
        """
        try:
            if name not in self.dataframes:
                return {"success": False, "error": f"Dataset '{name}' not found"}

            df = self.dataframes[name]
            plt.figure(figsize=(10, 6))

            if chart_type == "line":
                if x_column and y_column:
                    plt.plot(df[x_column], df[y_column])
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)
            elif chart_type == "bar":
                if x_column and y_column:
                    plt.bar(df[x_column], df[y_column])
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)
            elif chart_type == "scatter":
                if x_column and y_column:
                    plt.scatter(df[x_column], df[y_column])
                    plt.xlabel(x_column)
                    plt.ylabel(y_column)
            elif chart_type == "histogram":
                if x_column:
                    plt.hist(df[x_column], bins=kwargs.get("bins", 20))
                    plt.xlabel(x_column)
                    plt.ylabel("Frequency")
            elif chart_type == "box":
                if y_column:
                    df.boxplot(column=y_column)
                    plt.ylabel(y_column)
            elif chart_type == "heatmap":
                numeric_df = df.select_dtypes(include=[np.number])
                sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
            else:
                return {"success": False, "error": f"Unknown chart type: {chart_type}"}

            plt.title(title)
            plt.tight_layout()

            # Save to buffer
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode()
            plt.close()

            return {
                "success": True,
                "chart_type": chart_type,
                "image": image_base64,
                "format": "png",
            }
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return {"success": False, "error": str(e)}

    def calculate_statistics(
        self,
        name: str,
        column: str,
        stat_type: str,
    ) -> Dict[str, Any]:
        """
        Calculate statistical metrics.

        Args:
            name: Name of the dataset
            column: Column to analyze
            stat_type: Type of statistic ('mean', 'median', 'std', 'var', 'correlation')

        Returns:
            Statistical result
        """
        try:
            if name not in self.dataframes:
                return {"success": False, "error": f"Dataset '{name}' not found"}

            df = self.dataframes[name]

            if column not in df.columns:
                return {"success": False, "error": f"Column '{column}' not found"}

            if stat_type == "mean":
                result = float(df[column].mean())
            elif stat_type == "median":
                result = float(df[column].median())
            elif stat_type == "std":
                result = float(df[column].std())
            elif stat_type == "var":
                result = float(df[column].var())
            elif stat_type == "min":
                result = float(df[column].min())
            elif stat_type == "max":
                result = float(df[column].max())
            elif stat_type == "correlation":
                numeric_df = df.select_dtypes(include=[np.number])
                result = numeric_df.corr()[column].to_dict()
            else:
                return {"success": False, "error": f"Unknown statistic: {stat_type}"}

            return {
                "success": True,
                "column": column,
                "statistic": stat_type,
                "value": result,
            }
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {"success": False, "error": str(e)}

    def execute_python_code(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute Python code safely.

        Args:
            code: Python code to execute
            context: Context variables

        Returns:
            Execution result
        """
        try:
            # Create execution context
            exec_globals = {
                "pd": pd,
                "np": np,
                "plt": plt,
                "sns": sns,
            }

            if context:
                exec_globals.update(context)

            # Capture output
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()

            # Execute code
            exec(code, exec_globals)

            # Restore stdout
            sys.stdout = old_stdout

            output = captured_output.getvalue()

            return {
                "success": True,
                "output": output,
                "context": {k: str(v) for k, v in exec_globals.items() if not k.startswith("__")},
            }
        except Exception as e:
            sys.stdout = old_stdout
            logger.error(f"Error executing Python code: {e}")
            return {"success": False, "error": str(e)}


# Convenience function for tool integration
def analyze_data(data: Any, analysis_type: str = "describe") -> str:
    """
    Analyze data and return results.

    Args:
        data: Data to analyze
        analysis_type: Type of analysis

    Returns:
        JSON string of analysis results
    """
    tool = DataAnalysisTool()
    tool.load_data("dataset", data)

    if analysis_type == "describe":
        result = tool.describe_data("dataset")
    else:
        result = {"error": "Unknown analysis type"}

    return json.dumps(result, indent=2)
