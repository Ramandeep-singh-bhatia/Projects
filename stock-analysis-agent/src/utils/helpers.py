"""
Helper utilities for Stock Analysis Agent
Common functions used across modules
"""

import re
import hashlib
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pytz


# ============================================================================
# TICKER EXTRACTION
# ============================================================================

# Common stock ticker pattern (1-5 uppercase letters)
TICKER_PATTERN = re.compile(r'\b[A-Z]{1,5}\b')

# Common false positives to filter out
TICKER_BLACKLIST = {
    'A', 'I', 'CEO', 'CFO', 'CTO', 'IPO', 'ETF', 'USA', 'US', 'UK', 'EU',
    'AI', 'API', 'GDP', 'CPI', 'FDA', 'SEC', 'NYSE', 'NASDAQ', 'DOW',
    'PM', 'AM', 'EST', 'PST', 'GMT', 'UTC', 'Q1', 'Q2', 'Q3', 'Q4',
    'YOY', 'MOM', 'YTD', 'EPS', 'PE', 'ROI', 'ROE', 'EBITDA', 'LLC',
    'INC', 'CORP', 'LTD', 'CO', 'THE', 'AND', 'FOR', 'WITH', 'FROM',
    'THIS', 'THAT', 'WILL', 'HAVE', 'BEEN', 'WERE', 'WAS', 'ARE', 'CAN',
    'NOT', 'BUT', 'ALL', 'NEW', 'GET', 'ONE', 'TWO', 'OUT', 'NOW', 'WAY',
    'MAY', 'WHO', 'OIL', 'GAS', 'FED', 'ATH', 'ATL', 'BUY', 'SELL', 'HOLD'
}


def extract_tickers(text: str, validate: bool = True) -> List[str]:
    """
    Extract stock ticker symbols from text

    Args:
        text: Input text
        validate: If True, filter out common false positives

    Returns:
        List of ticker symbols found
    """
    # Find all potential tickers
    matches = TICKER_PATTERN.findall(text)

    # Remove duplicates while preserving order
    tickers = list(dict.fromkeys(matches))

    # Filter out blacklisted words if validation enabled
    if validate:
        tickers = [t for t in tickers if t not in TICKER_BLACKLIST]

    return tickers


def extract_tickers_with_dollar(text: str) -> List[str]:
    """
    Extract tickers prefixed with $ (e.g., $AAPL)
    This is more accurate for social media/informal sources

    Args:
        text: Input text

    Returns:
        List of ticker symbols found
    """
    pattern = re.compile(r'\$([A-Z]{1,5})\b')
    return pattern.findall(text)


# ============================================================================
# TEXT PROCESSING
# ============================================================================

def clean_text(text: str) -> str:
    """
    Clean and normalize text

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:()\-$%]', '', text)

    return text.strip()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)].strip() + suffix


def generate_text_hash(text: str) -> str:
    """
    Generate a hash for text (useful for deduplication)

    Args:
        text: Input text

    Returns:
        MD5 hash of text
    """
    return hashlib.md5(text.encode()).hexdigest()


# ============================================================================
# DATE/TIME UTILITIES
# ============================================================================

def get_current_time_utc() -> datetime:
    """Get current time in UTC"""
    return datetime.now(pytz.UTC)


def get_current_time_eastern() -> datetime:
    """Get current time in Eastern timezone (market hours)"""
    eastern = pytz.timezone('America/New_York')
    return datetime.now(eastern)


def is_market_open(dt: Optional[datetime] = None) -> bool:
    """
    Check if US stock market is currently open

    Args:
        dt: DateTime to check (default: now)

    Returns:
        True if market is open
    """
    if dt is None:
        dt = get_current_time_eastern()
    else:
        eastern = pytz.timezone('America/New_York')
        dt = dt.astimezone(eastern)

    # Check if weekend
    if dt.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Check market hours (9:30 AM - 4:00 PM ET)
    market_open = dt.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = dt.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= dt <= market_close


def time_until_market_open() -> Optional[timedelta]:
    """
    Get time until market opens

    Returns:
        Timedelta until market opens, or None if market is open
    """
    now = get_current_time_eastern()

    if is_market_open(now):
        return None

    # If weekend, calculate to Monday
    if now.weekday() >= 5:
        days_until_monday = (7 - now.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 1
        next_open = now + timedelta(days=days_until_monday)
        next_open = next_open.replace(hour=9, minute=30, second=0, microsecond=0)
    else:
        # If before market open today
        market_open_today = now.replace(hour=9, minute=30, second=0, microsecond=0)
        if now < market_open_today:
            next_open = market_open_today
        else:
            # After market close, next day
            next_open = now + timedelta(days=1)
            next_open = next_open.replace(hour=9, minute=30, second=0, microsecond=0)

    return next_open - now


def get_trading_days_between(start: datetime, end: datetime) -> int:
    """
    Get number of trading days between two dates (approximate)

    Args:
        start: Start date
        end: End date

    Returns:
        Approximate number of trading days
    """
    total_days = (end - start).days
    weeks = total_days // 7
    remaining_days = total_days % 7

    # Approximate: ~5 trading days per week
    trading_days = weeks * 5

    # Add remaining days, excluding weekends
    for i in range(remaining_days):
        day = start + timedelta(days=i)
        if day.weekday() < 5:  # Monday = 0, Friday = 4
            trading_days += 1

    return trading_days


# ============================================================================
# NUMBER FORMATTING
# ============================================================================

def format_currency(amount: float, decimals: int = 2) -> str:
    """
    Format number as currency

    Args:
        amount: Amount to format
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "$1,234.56")
    """
    return f"${amount:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2, show_sign: bool = True) -> str:
    """
    Format number as percentage

    Args:
        value: Value to format (e.g., 5.0 for 5%)
        decimals: Number of decimal places
        show_sign: Whether to show + for positive values

    Returns:
        Formatted string (e.g., "+5.23%")
    """
    sign = "+" if value > 0 and show_sign else ""
    return f"{sign}{value:.{decimals}f}%"


def format_large_number(number: float) -> str:
    """
    Format large numbers with K, M, B suffixes

    Args:
        number: Number to format

    Returns:
        Formatted string (e.g., "1.23M")
    """
    if abs(number) >= 1_000_000_000:
        return f"{number / 1_000_000_000:.2f}B"
    elif abs(number) >= 1_000_000:
        return f"{number / 1_000_000:.2f}M"
    elif abs(number) >= 1_000:
        return f"{number / 1_000:.2f}K"
    else:
        return f"{number:.2f}"


# ============================================================================
# VALIDATION
# ============================================================================

def is_valid_ticker(ticker: str) -> bool:
    """
    Validate if string looks like a valid ticker

    Args:
        ticker: Ticker to validate

    Returns:
        True if valid
    """
    if not ticker:
        return False

    # Must be 1-5 uppercase letters
    if not re.match(r'^[A-Z]{1,5}$', ticker):
        return False

    # Not in blacklist
    if ticker in TICKER_BLACKLIST:
        return False

    return True


def is_valid_url(url: str) -> bool:
    """
    Validate if string is a valid URL

    Args:
        url: URL to validate

    Returns:
        True if valid
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


# ============================================================================
# DATA STRUCTURE HELPERS
# ============================================================================

def safe_get(dictionary: Dict, *keys, default=None) -> Any:
    """
    Safely get nested dictionary value

    Args:
        dictionary: Dictionary to search
        *keys: Sequence of keys to traverse
        default: Default value if key not found

    Returns:
        Value at key path or default

    Example:
        safe_get(data, 'user', 'profile', 'name', default='Unknown')
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def deduplicate_list(items: List[Any], key: Optional[callable] = None) -> List[Any]:
    """
    Deduplicate list while preserving order

    Args:
        items: List to deduplicate
        key: Optional function to extract comparison key

    Returns:
        Deduplicated list
    """
    if key is None:
        # Simple deduplication
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        # Deduplication with key function
        seen = set()
        result = []
        for item in items:
            k = key(item)
            if k not in seen:
                seen.add(k)
                result.append(item)
        return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


# ============================================================================
# RATE LIMITING
# ============================================================================

class SimpleRateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.call_times: Dict[str, List[datetime]] = {}

    def can_call(
        self,
        key: str,
        max_calls: int,
        window_seconds: int
    ) -> bool:
        """
        Check if call is allowed within rate limit

        Args:
            key: Rate limit key (e.g., API name)
            max_calls: Maximum calls allowed
            window_seconds: Time window in seconds

        Returns:
            True if call is allowed
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        # Initialize if first time
        if key not in self.call_times:
            self.call_times[key] = []

        # Remove old calls
        self.call_times[key] = [
            t for t in self.call_times[key] if t > cutoff
        ]

        # Check if under limit
        return len(self.call_times[key]) < max_calls

    def record_call(self, key: str):
        """Record a call"""
        if key not in self.call_times:
            self.call_times[key] = []
        self.call_times[key].append(datetime.now())

    def get_remaining_calls(
        self,
        key: str,
        max_calls: int,
        window_seconds: int
    ) -> int:
        """Get number of remaining calls in current window"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=window_seconds)

        if key not in self.call_times:
            return max_calls

        # Remove old calls
        self.call_times[key] = [
            t for t in self.call_times[key] if t > cutoff
        ]

        return max(0, max_calls - len(self.call_times[key]))


# Global rate limiter instance
_rate_limiter = SimpleRateLimiter()


def get_rate_limiter() -> SimpleRateLimiter:
    """Get global rate limiter instance"""
    return _rate_limiter


if __name__ == "__main__":
    # Test utilities
    print("Testing ticker extraction...")
    text = "Apple $AAPL reported strong earnings. MSFT and GOOGL also up."
    print(f"Text: {text}")
    print(f"Tickers: {extract_tickers(text)}")
    print(f"$ Tickers: {extract_tickers_with_dollar(text)}")

    print("\nTesting market hours...")
    print(f"Market open: {is_market_open()}")
    print(f"Current time (ET): {get_current_time_eastern()}")

    print("\nTesting formatting...")
    print(f"Currency: {format_currency(1234567.89)}")
    print(f"Percentage: {format_percentage(5.678)}")
    print(f"Large number: {format_large_number(1234567890)}")
