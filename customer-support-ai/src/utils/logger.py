"""
Structured logging setup for the Customer Support AI system.
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from pathlib import Path
import traceback
from contextvars import ContextVar

# Context variable for request ID tracking
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON formatted log string
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }

        # Add extra fields from the record
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Custom text formatter for human-readable logging"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as text.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        base_message = super().format(record)

        # Add request ID if available
        request_id = request_id_var.get()
        if request_id:
            base_message = f"[{request_id}] {base_message}"

        # Add extra data if present
        if hasattr(record, "extra_data"):
            base_message += f" | Extra: {record.extra_data}"

        return base_message


class StructuredLogger:
    """Wrapper for structured logging with extra context"""

    def __init__(self, name: str):
        """
        Initialize structured logger.

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)

    def _log(
        self,
        level: int,
        message: str,
        extra_data: Optional[Dict[str, Any]] = None,
        exc_info: bool = False
    ):
        """
        Internal log method with extra data support.

        Args:
            level: Log level
            message: Log message
            extra_data: Additional structured data
            exc_info: Include exception info
        """
        extra = {"extra_data": extra_data} if extra_data else {}
        self.logger.log(level, message, extra=extra, exc_info=exc_info)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(logging.DEBUG, message, extra_data=kwargs)

    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(logging.INFO, message, extra_data=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(logging.WARNING, message, extra_data=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message"""
        exc_info = kwargs.pop("exc_info", False)
        self._log(logging.ERROR, message, extra_data=kwargs, exc_info=exc_info)

    def critical(self, message: str, **kwargs):
        """Log critical message"""
        exc_info = kwargs.pop("exc_info", False)
        self._log(logging.CRITICAL, message, extra_data=kwargs, exc_info=exc_info)

    def exception(self, message: str, **kwargs):
        """Log exception with traceback"""
        self._log(logging.ERROR, message, extra_data=kwargs, exc_info=True)


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: Optional[Path] = None
) -> None:
    """
    Setup logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type (json or text)
        log_file: Optional file path to write logs to
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # Choose formatter
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)


def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)


def set_request_id(request_id: str):
    """
    Set the request ID for the current context.

    Args:
        request_id: Unique request identifier
    """
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """
    Get the request ID for the current context.

    Returns:
        Request ID or None
    """
    return request_id_var.get()


def clear_request_id():
    """Clear the request ID from the current context"""
    request_id_var.set(None)


class LoggerContextManager:
    """Context manager for request-scoped logging"""

    def __init__(self, request_id: str):
        """
        Initialize context manager.

        Args:
            request_id: Unique request identifier
        """
        self.request_id = request_id
        self.previous_request_id = None

    def __enter__(self):
        """Enter context"""
        self.previous_request_id = get_request_id()
        set_request_id(self.request_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context"""
        if self.previous_request_id:
            set_request_id(self.previous_request_id)
        else:
            clear_request_id()


# Performance logging utilities

class PerformanceLogger:
    """Logger for performance metrics"""

    def __init__(self, logger: StructuredLogger):
        """
        Initialize performance logger.

        Args:
            logger: Structured logger instance
        """
        self.logger = logger

    def log_latency(
        self,
        operation: str,
        duration_ms: float,
        success: bool = True,
        **kwargs
    ):
        """
        Log operation latency.

        Args:
            operation: Operation name
            duration_ms: Duration in milliseconds
            success: Whether operation succeeded
            **kwargs: Additional context
        """
        self.logger.info(
            f"Performance: {operation}",
            operation=operation,
            duration_ms=round(duration_ms, 2),
            success=success,
            **kwargs
        )

    def log_token_usage(
        self,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        model: str,
        **kwargs
    ):
        """
        Log token usage and cost.

        Args:
            operation: Operation name
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost: Cost in dollars
            model: Model name
            **kwargs: Additional context
        """
        self.logger.info(
            f"Token usage: {operation}",
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost=round(cost, 6),
            model=model,
            **kwargs
        )

    def log_retrieval_metrics(
        self,
        query: str,
        num_results: int,
        top_score: float,
        duration_ms: float,
        **kwargs
    ):
        """
        Log retrieval metrics.

        Args:
            query: Search query
            num_results: Number of results returned
            top_score: Highest similarity score
            duration_ms: Duration in milliseconds
            **kwargs: Additional context
        """
        self.logger.info(
            "Retrieval metrics",
            query=query[:100],  # Truncate long queries
            num_results=num_results,
            top_score=round(top_score, 3),
            duration_ms=round(duration_ms, 2),
            **kwargs
        )


# Example usage and initialization
if __name__ == "__main__":
    # Setup logging
    setup_logging(log_level="INFO", log_format="json")

    # Get logger
    logger = get_logger(__name__)

    # Test logging
    logger.info("Application started", version="1.0.0")
    logger.debug("Debug information", user_id="12345")
    logger.warning("Warning message", threshold=0.7)

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception("An error occurred", error_code="TEST_001")

    # Test with request context
    with LoggerContextManager("req-12345"):
        logger.info("Processing request")
