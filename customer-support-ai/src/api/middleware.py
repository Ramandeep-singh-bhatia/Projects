"""
Custom middleware for the API.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Tuple
import time
from collections import defaultdict
from datetime import datetime, timedelta

from ..utils.logger import get_logger
from ..utils.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class RateLimiter:
    """
    Simple in-memory rate limiter.

    Note: In production, use Redis or a dedicated rate limiting service.
    """

    def __init__(self, requests_per_minute: int = 10):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 300  # Clean up old entries every 5 minutes
        self.last_cleanup = time.time()

    def _cleanup_old_entries(self):
        """Remove entries older than 1 minute"""
        current_time = time.time()

        # Only cleanup periodically
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        cutoff_time = current_time - 60  # 1 minute ago
        keys_to_delete = []

        for key, timestamps in self.requests.items():
            # Remove old timestamps
            self.requests[key] = [ts for ts in timestamps if ts > cutoff_time]

            # Mark empty keys for deletion
            if not self.requests[key]:
                keys_to_delete.append(key)

        # Delete empty keys
        for key in keys_to_delete:
            del self.requests[key]

        self.last_cleanup = current_time

    def is_allowed(self, identifier: str) -> Tuple[bool, int]:
        """
        Check if request is allowed based on rate limit.

        Args:
            identifier: Unique identifier (e.g., IP address, user ID)

        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        cutoff_time = current_time - 60  # 1 minute window

        # Cleanup old entries periodically
        self._cleanup_old_entries()

        # Get timestamps for this identifier
        timestamps = self.requests[identifier]

        # Remove timestamps older than 1 minute
        recent_timestamps = [ts for ts in timestamps if ts > cutoff_time]
        self.requests[identifier] = recent_timestamps

        # Check if limit exceeded
        if len(recent_timestamps) >= self.requests_per_minute:
            # Calculate retry after
            oldest_timestamp = min(recent_timestamps)
            retry_after = int(60 - (current_time - oldest_timestamp)) + 1

            logger.warning(
                f"Rate limit exceeded",
                identifier=identifier,
                requests_in_window=len(recent_timestamps)
            )

            return False, retry_after

        # Allow request
        self.requests[identifier].append(current_time)
        return True, 0

    def get_stats(self, identifier: str) -> Dict[str, int]:
        """
        Get rate limit stats for an identifier.

        Args:
            identifier: Unique identifier

        Returns:
            Dictionary with stats
        """
        current_time = time.time()
        cutoff_time = current_time - 60

        timestamps = self.requests.get(identifier, [])
        recent_timestamps = [ts for ts in timestamps if ts > cutoff_time]

        return {
            "requests_in_window": len(recent_timestamps),
            "limit": self.requests_per_minute,
            "remaining": max(0, self.requests_per_minute - len(recent_timestamps))
        }


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=settings.rate_limit_per_minute)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response
    """
    # Skip rate limiting for health check and docs
    if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    # Get identifier (IP address or user ID from header)
    identifier = request.headers.get("X-User-ID")
    if not identifier and request.client:
        identifier = request.client.host

    if not identifier:
        identifier = "unknown"

    # Check rate limit
    is_allowed, retry_after = rate_limiter.is_allowed(identifier)

    if not is_allowed:
        logger.warning(
            f"Rate limit exceeded",
            identifier=identifier,
            path=request.url.path,
            retry_after=retry_after
        )

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate Limit Exceeded",
                "detail": f"Too many requests. Please retry after {retry_after} seconds.",
                "retry_after": retry_after
            },
            headers={"Retry-After": str(retry_after)}
        )

    # Get stats
    stats = rate_limiter.get_stats(identifier)

    # Process request
    response = await call_next(request)

    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(stats["limit"])
    response.headers["X-RateLimit-Remaining"] = str(stats["remaining"])
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)

    return response


class CircuitBreaker:
    """
    Simple circuit breaker for external service calls.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again
            expected_exception: Exception type to catch
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"

    def call(self, func, *args, **kwargs):
        """
        Call function with circuit breaker protection.

        Args:
            func: Function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception if circuit is open or function fails
        """
        if self.state == "OPEN":
            # Check if timeout has passed
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)

            # Success - reset if in HALF_OPEN
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                logger.info("Circuit breaker CLOSED after successful call")

            return result

        except self.expected_exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.error(
                f"Circuit breaker caught exception",
                failure_count=self.failure_count,
                state=self.state
            )

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                logger.warning("Circuit breaker OPENED due to failures")

            raise


# Global circuit breakers for external services
llm_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=Exception
)

embeddings_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    timeout=30,
    expected_exception=Exception
)
