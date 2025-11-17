"""
Logging utility for Stock Analysis Agent
Provides structured logging with file rotation
"""

import sys
import logging
from pathlib import Path
from typing import Optional
from loguru import logger
from datetime import datetime


class Logger:
    """Custom logger with file rotation and structured output"""

    def __init__(
        self,
        name: str,
        log_dir: Optional[Path] = None,
        level: str = "INFO",
        log_to_file: bool = True,
        log_to_console: bool = True,
    ):
        self.name = name
        self.level = level
        self.log_dir = log_dir or Path("logs")
        self.log_to_file = log_to_file
        self.log_to_console = log_to_console

        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Remove default logger
        logger.remove()

        # Configure loguru
        self._configure_logger()

    def _configure_logger(self):
        """Configure loguru logger with custom settings"""

        # Console logging format
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{extra[module_name]}</cyan> | "
            "<level>{message}</level>"
        )

        # File logging format (more detailed)
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
            "{level: <8} | "
            "{extra[module_name]: <20} | "
            "{message}"
        )

        # Add console handler
        if self.log_to_console:
            logger.add(
                sys.stderr,
                format=console_format,
                level=self.level,
                colorize=True,
                enqueue=True,
            )

        # Add file handlers
        if self.log_to_file:
            # Main log file
            logger.add(
                self.log_dir / f"{self.name}.log",
                format=file_format,
                level=self.level,
                rotation="10 MB",
                retention="30 days",
                compression="zip",
                enqueue=True,
            )

            # Error log file
            logger.add(
                self.log_dir / "errors.log",
                format=file_format,
                level="ERROR",
                rotation="10 MB",
                retention="60 days",
                compression="zip",
                enqueue=True,
            )

        # Configure with module name
        logger.configure(extra={"module_name": self.name})

    def get_logger(self):
        """Get the configured logger"""
        return logger.bind(module_name=self.name)

    @staticmethod
    def create_module_logger(
        module_name: str,
        log_dir: Optional[Path] = None,
        level: str = "INFO"
    ):
        """Factory method to create a logger for a specific module"""
        return Logger(module_name, log_dir, level).get_logger()


class APICallLogger:
    """Specialized logger for API calls to track usage"""

    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True, parents=True)
        self.log_file = self.log_dir / "api_calls.log"

        # Configure API logger
        self.logger = logging.getLogger("api_calls")
        self.logger.setLevel(logging.INFO)

        # File handler
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_call(
        self,
        api_name: str,
        endpoint: str,
        success: bool = True,
        response_time_ms: Optional[int] = None,
        error: Optional[str] = None
    ):
        """Log an API call"""
        status = "SUCCESS" if success else "FAILED"
        message = f"{api_name:20s} | {endpoint:50s} | {status}"

        if response_time_ms:
            message += f" | {response_time_ms}ms"

        if error:
            message += f" | Error: {error}"

        if success:
            self.logger.info(message)
        else:
            self.logger.error(message)

    def get_daily_usage(self, api_name: str) -> int:
        """Get number of API calls today for a specific API"""
        today = datetime.now().date()
        count = 0

        if not self.log_file.exists():
            return 0

        with open(self.log_file, 'r') as f:
            for line in f:
                if api_name in line and str(today) in line and "SUCCESS" in line:
                    count += 1

        return count


# Convenience functions

def get_logger(module_name: str) -> logger:
    """Get a logger for a module"""
    from src.config.config_loader import get_config
    config = get_config()
    return Logger.create_module_logger(
        module_name,
        log_dir=config.log_dir,
        level=config.log_level
    )


def get_api_logger() -> APICallLogger:
    """Get the API call logger"""
    from src.config.config_loader import get_config
    config = get_config()
    return APICallLogger(log_dir=config.log_dir)


if __name__ == "__main__":
    # Test logging
    test_logger = get_logger("test")

    test_logger.info("This is an info message")
    test_logger.warning("This is a warning")
    test_logger.error("This is an error")
    test_logger.success("This is a success message")

    # Test API logger
    api_logger = get_api_logger()
    api_logger.log_call("NewsAPI", "/everything", success=True, response_time_ms=234)
    api_logger.log_call("AlphaVantage", "/quote", success=False, error="Rate limit exceeded")

    print(f"\nAPI calls today: {api_logger.get_daily_usage('NewsAPI')}")
