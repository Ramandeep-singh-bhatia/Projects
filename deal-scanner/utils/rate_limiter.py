"""
Rate limiter to ensure we stay within API and scraping limits.
Implements token bucket algorithm and tracks usage in database.
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from threading import Lock
from loguru import logger

from config.settings import MAX_REQUESTS_PER_HOUR
from utils.database import db


class RateLimiter:
    """Rate limiter using token bucket algorithm with database tracking."""

    def __init__(self):
        """Initialize rate limiter."""
        self.locks: Dict[str, Lock] = {}
        self.buckets: Dict[str, Dict] = {}

    def _get_lock(self, api_name: str) -> Lock:
        """Get or create a lock for an API."""
        if api_name not in self.locks:
            self.locks[api_name] = Lock()
        return self.locks[api_name]

    def _get_bucket(self, api_name: str) -> Dict:
        """Get or create a token bucket for an API."""
        if api_name not in self.buckets:
            max_requests = MAX_REQUESTS_PER_HOUR.get(api_name, 100)
            self.buckets[api_name] = {
                'tokens': max_requests,
                'max_tokens': max_requests,
                'last_refill': datetime.now(),
                'refill_rate': max_requests / 3600.0,  # tokens per second
            }
        return self.buckets[api_name]

    def _refill_bucket(self, bucket: Dict):
        """Refill tokens based on elapsed time."""
        now = datetime.now()
        elapsed = (now - bucket['last_refill']).total_seconds()

        # Add tokens based on elapsed time
        new_tokens = elapsed * bucket['refill_rate']
        bucket['tokens'] = min(bucket['max_tokens'], bucket['tokens'] + new_tokens)
        bucket['last_refill'] = now

    def can_make_request(self, api_name: str) -> bool:
        """Check if a request can be made without blocking."""
        lock = self._get_lock(api_name)
        with lock:
            bucket = self._get_bucket(api_name)
            self._refill_bucket(bucket)
            return bucket['tokens'] >= 1

    def wait_for_token(self, api_name: str, timeout: Optional[float] = None) -> bool:
        """
        Wait for a token to become available.

        Args:
            api_name: Name of the API/service
            timeout: Maximum time to wait in seconds (None = wait forever)

        Returns:
            True if token acquired, False if timeout
        """
        lock = self._get_lock(api_name)
        start_time = time.time()

        while True:
            with lock:
                bucket = self._get_bucket(api_name)
                self._refill_bucket(bucket)

                if bucket['tokens'] >= 1:
                    bucket['tokens'] -= 1
                    logger.debug(
                        f"Token acquired for {api_name}. "
                        f"Remaining: {bucket['tokens']:.2f}/{bucket['max_tokens']}"
                    )
                    return True

            # Check timeout
            if timeout and (time.time() - start_time) >= timeout:
                logger.warning(f"Timeout waiting for rate limit token: {api_name}")
                return False

            # Wait before checking again
            time.sleep(0.1)

    def acquire(self, api_name: str, timeout: Optional[float] = 60) -> bool:
        """
        Acquire a token for making a request.

        Args:
            api_name: Name of the API/service
            timeout: Maximum time to wait in seconds

        Returns:
            True if token acquired, False if timeout or limit exceeded
        """
        # Check database for recent usage (backup check)
        usage_count = db.get_api_usage_count(api_name, hours=1)
        max_requests = MAX_REQUESTS_PER_HOUR.get(api_name, 100)

        if usage_count >= max_requests:
            logger.warning(
                f"Rate limit exceeded for {api_name}: "
                f"{usage_count}/{max_requests} requests in last hour"
            )
            return False

        # Acquire token from bucket
        return self.wait_for_token(api_name, timeout)

    def get_remaining_requests(self, api_name: str) -> int:
        """Get the number of available requests."""
        lock = self._get_lock(api_name)
        with lock:
            bucket = self._get_bucket(api_name)
            self._refill_bucket(bucket)
            return int(bucket['tokens'])

    def get_time_until_available(self, api_name: str) -> float:
        """Get time in seconds until next request is available."""
        lock = self._get_lock(api_name)
        with lock:
            bucket = self._get_bucket(api_name)
            self._refill_bucket(bucket)

            if bucket['tokens'] >= 1:
                return 0.0

            # Calculate time needed to refill one token
            tokens_needed = 1 - bucket['tokens']
            seconds = tokens_needed / bucket['refill_rate']
            return seconds

    def reset(self, api_name: str):
        """Reset the rate limiter for an API."""
        lock = self._get_lock(api_name)
        with lock:
            if api_name in self.buckets:
                bucket = self.buckets[api_name]
                bucket['tokens'] = bucket['max_tokens']
                bucket['last_refill'] = datetime.now()
                logger.info(f"Rate limiter reset for {api_name}")

    def get_statistics(self) -> Dict[str, Dict]:
        """Get statistics for all rate limiters."""
        stats = {}
        for api_name in self.buckets:
            lock = self._get_lock(api_name)
            with lock:
                bucket = self._get_bucket(api_name)
                self._refill_bucket(bucket)

                # Get database stats
                usage_count = db.get_api_usage_count(api_name, hours=1)

                stats[api_name] = {
                    'available_tokens': int(bucket['tokens']),
                    'max_tokens': bucket['max_tokens'],
                    'usage_last_hour': usage_count,
                    'limit_per_hour': MAX_REQUESTS_PER_HOUR.get(api_name, 100),
                    'time_until_next': self.get_time_until_available(api_name),
                }

        return stats


class RequestThrottler:
    """Simple delay-based throttler for scraping."""

    def __init__(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """
        Initialize throttler.

        Args:
            min_delay: Minimum delay between requests in seconds
            max_delay: Maximum delay between requests in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time: Dict[str, float] = {}
        self.locks: Dict[str, Lock] = {}

    def _get_lock(self, key: str) -> Lock:
        """Get or create a lock for a key."""
        if key not in self.locks:
            self.locks[key] = Lock()
        return self.locks[key]

    def throttle(self, key: str = 'default'):
        """
        Throttle requests by adding delay.

        Args:
            key: Identifier for the throttle (e.g., 'amazon', 'bestbuy')
        """
        import random

        lock = self._get_lock(key)
        with lock:
            now = time.time()
            last_time = self.last_request_time.get(key, 0)

            elapsed = now - last_time
            delay = random.uniform(self.min_delay, self.max_delay)

            if elapsed < delay:
                sleep_time = delay - elapsed
                logger.debug(f"Throttling {key}: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)

            self.last_request_time[key] = time.time()


# Singleton instances
rate_limiter = RateLimiter()
scraper_throttler = RequestThrottler(min_delay=2.0, max_delay=5.0)
