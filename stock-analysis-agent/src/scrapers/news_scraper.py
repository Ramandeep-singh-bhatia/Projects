"""
News Scraper Module
Aggregates financial news from multiple FREE sources:
- RSS feeds (unlimited, no API key needed)
- NewsAPI (100 requests/day free)
- SEC EDGAR filings (unlimited, free)
"""

import time
import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from urllib.parse import quote
import hashlib

from src.utils.logger import get_logger, get_api_logger
from src.utils.helpers import (
    extract_tickers,
    extract_tickers_with_dollar,
    clean_text,
    generate_text_hash,
    is_valid_url,
    get_rate_limiter
)
from src.config.config_loader import get_config


logger = get_logger("news_scraper")
api_logger = get_api_logger()


# ============================================================================
# BASE NEWS ARTICLE CLASS
# ============================================================================

class NewsArticle:
    """Represents a news article"""

    def __init__(
        self,
        title: str,
        content: str,
        url: str,
        source: str,
        source_name: str,
        published_date: Optional[datetime] = None,
        tickers: Optional[List[str]] = None
    ):
        self.title = title
        self.content = content
        self.url = url
        self.source = source
        self.source_name = source_name
        self.published_date = published_date or datetime.now()
        self.tickers = tickers or []

        # Generate unique hash for deduplication
        self.hash = generate_text_hash(f"{title}{url}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "source": self.source,
            "source_name": self.source_name,
            "published_date": self.published_date,
            "tickers": self.tickers,
            "hash": self.hash
        }

    def __repr__(self):
        return f"<NewsArticle: {self.title[:50]}... from {self.source_name}>"


# ============================================================================
# RSS FEED SCRAPER (FREE, UNLIMITED)
# ============================================================================

class RSSFeedScraper:
    """Scrape news from RSS feeds - completely free"""

    def __init__(self):
        self.logger = logger
        self.feeds = self._load_feed_config()

    def _load_feed_config(self) -> List[Dict[str, str]]:
        """Load RSS feed configuration"""
        config = get_config()
        feeds = config.get('data_sources.rss_feeds.sources', [])

        if not feeds:
            # Default feeds if not configured
            feeds = [
                {
                    "name": "Bloomberg Markets",
                    "url": "https://feeds.bloomberg.com/markets/news.rss",
                    "priority": "high"
                },
                {
                    "name": "CNBC Top News",
                    "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
                    "priority": "high"
                },
                {
                    "name": "MarketWatch",
                    "url": "https://www.marketwatch.com/rss/topstories",
                    "priority": "medium"
                },
            ]

        return feeds

    def scrape_feed(self, feed_url: str, feed_name: str) -> List[NewsArticle]:
        """
        Scrape a single RSS feed

        Args:
            feed_url: URL of the RSS feed
            feed_name: Name of the feed

        Returns:
            List of NewsArticle objects
        """
        articles = []

        try:
            self.logger.info(f"Scraping RSS feed: {feed_name}")

            # Parse feed
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                self.logger.warning(f"RSS feed parsing error for {feed_name}: {feed.bozo_exception}")
                return articles

            # Process entries
            for entry in feed.entries:
                try:
                    # Extract data
                    title = entry.get('title', '')
                    summary = entry.get('summary', entry.get('description', ''))
                    url = entry.get('link', '')
                    published = entry.get('published_parsed', entry.get('updated_parsed'))

                    # Convert published date
                    if published:
                        published_date = datetime(*published[:6])
                    else:
                        published_date = datetime.now()

                    # Clean text
                    title = clean_text(title)
                    content = clean_text(summary)

                    # Extract tickers
                    text_to_search = f"{title} {content}"
                    tickers = extract_tickers(text_to_search)
                    tickers.extend(extract_tickers_with_dollar(text_to_search))
                    tickers = list(set(tickers))  # Deduplicate

                    # Create article
                    if title and url:
                        article = NewsArticle(
                            title=title,
                            content=content,
                            url=url,
                            source="rss",
                            source_name=feed_name,
                            published_date=published_date,
                            tickers=tickers
                        )
                        articles.append(article)

                except Exception as e:
                    self.logger.error(f"Error processing RSS entry: {e}")
                    continue

            self.logger.info(f"Scraped {len(articles)} articles from {feed_name}")

        except Exception as e:
            self.logger.error(f"Error scraping RSS feed {feed_name}: {e}")

        return articles

    def scrape_all_feeds(self, max_articles_per_feed: int = 20) -> List[NewsArticle]:
        """
        Scrape all configured RSS feeds

        Args:
            max_articles_per_feed: Maximum articles per feed

        Returns:
            List of NewsArticle objects
        """
        all_articles = []

        for feed_config in self.feeds:
            feed_url = feed_config.get('url')
            feed_name = feed_config.get('name', 'Unknown Feed')

            if not feed_url:
                continue

            articles = self.scrape_feed(feed_url, feed_name)
            all_articles.extend(articles[:max_articles_per_feed])

            # Small delay to be respectful
            time.sleep(0.5)

        # Deduplicate by hash
        seen_hashes = set()
        unique_articles = []
        for article in all_articles:
            if article.hash not in seen_hashes:
                seen_hashes.add(article.hash)
                unique_articles.append(article)

        self.logger.info(f"Total unique articles from RSS: {len(unique_articles)}")
        return unique_articles


# ============================================================================
# NEWSAPI SCRAPER (100 requests/day FREE)
# ============================================================================

class NewsAPIScraper:
    """Scrape news from NewsAPI - 100 requests/day free tier"""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_config().api.news_api_key
        self.logger = logger
        self.rate_limiter = get_rate_limiter()
        self.api_logger = api_logger

    def _check_rate_limit(self) -> bool:
        """Check if we can make a NewsAPI call (100/day limit)"""
        # Check daily limit
        daily_usage = self.api_logger.get_daily_usage("NewsAPI")
        if daily_usage >= 90:  # Leave some buffer
            self.logger.warning(f"NewsAPI daily limit reached: {daily_usage}/100")
            return False

        return True

    def search_news(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        language: str = "en",
        sort_by: str = "publishedAt"
    ) -> List[NewsArticle]:
        """
        Search for news articles

        Args:
            query: Search query
            from_date: Search from this date (default: 24h ago)
            language: Language code
            sort_by: Sort by (publishedAt, relevancy, popularity)

        Returns:
            List of NewsArticle objects
        """
        if not self.api_key:
            self.logger.warning("NewsAPI key not configured")
            return []

        if not self._check_rate_limit():
            return []

        articles = []

        try:
            # Default to last 24 hours
            if from_date is None:
                from_date = datetime.now() - timedelta(days=1)

            # Prepare request
            endpoint = f"{self.BASE_URL}/everything"
            params = {
                "q": query,
                "from": from_date.strftime("%Y-%m-%d"),
                "language": language,
                "sortBy": sort_by,
                "apiKey": self.api_key
            }

            # Make request
            start_time = time.time()
            response = requests.get(endpoint, params=params, timeout=10)
            response_time_ms = int((time.time() - start_time) * 1000)

            # Log API call
            self.api_logger.log_call(
                "NewsAPI",
                f"/everything?q={query}",
                success=response.status_code == 200,
                response_time_ms=response_time_ms
            )

            if response.status_code == 200:
                data = response.json()

                for item in data.get('articles', []):
                    try:
                        title = item.get('title', '')
                        description = item.get('description', '')
                        content = item.get('content', description)
                        url = item.get('url', '')
                        source_name = item.get('source', {}).get('name', 'Unknown')
                        published_at = item.get('publishedAt')

                        # Parse published date
                        if published_at:
                            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        else:
                            published_date = datetime.now()

                        # Clean text
                        title = clean_text(title)
                        content = clean_text(content)

                        # Extract tickers
                        text_to_search = f"{title} {content}"
                        tickers = extract_tickers(text_to_search)
                        tickers.extend(extract_tickers_with_dollar(text_to_search))
                        tickers = list(set(tickers))

                        if title and url:
                            article = NewsArticle(
                                title=title,
                                content=content,
                                url=url,
                                source="newsapi",
                                source_name=source_name,
                                published_date=published_date,
                                tickers=tickers
                            )
                            articles.append(article)

                    except Exception as e:
                        self.logger.error(f"Error processing NewsAPI article: {e}")
                        continue

                self.logger.info(f"Fetched {len(articles)} articles from NewsAPI for query: {query}")

            else:
                self.logger.error(f"NewsAPI error: {response.status_code} - {response.text}")
                self.api_logger.log_call(
                    "NewsAPI",
                    f"/everything?q={query}",
                    success=False,
                    error=f"HTTP {response.status_code}"
                )

        except Exception as e:
            self.logger.error(f"NewsAPI request failed: {e}")
            self.api_logger.log_call("NewsAPI", f"/everything?q={query}", success=False, error=str(e))

        return articles

    def get_top_headlines(
        self,
        category: str = "business",
        country: str = "us"
    ) -> List[NewsArticle]:
        """
        Get top headlines (counts against daily limit)

        Args:
            category: News category
            country: Country code

        Returns:
            List of NewsArticle objects
        """
        if not self.api_key:
            self.logger.warning("NewsAPI key not configured")
            return []

        if not self._check_rate_limit():
            return []

        articles = []

        try:
            endpoint = f"{self.BASE_URL}/top-headlines"
            params = {
                "category": category,
                "country": country,
                "apiKey": self.api_key
            }

            start_time = time.time()
            response = requests.get(endpoint, params=params, timeout=10)
            response_time_ms = int((time.time() - start_time) * 1000)

            self.api_logger.log_call(
                "NewsAPI",
                f"/top-headlines?category={category}",
                success=response.status_code == 200,
                response_time_ms=response_time_ms
            )

            if response.status_code == 200:
                data = response.json()

                for item in data.get('articles', []):
                    try:
                        title = clean_text(item.get('title', ''))
                        description = clean_text(item.get('description', ''))
                        content = clean_text(item.get('content', description))
                        url = item.get('url', '')
                        source_name = item.get('source', {}).get('name', 'Unknown')
                        published_at = item.get('publishedAt')

                        if published_at:
                            published_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        else:
                            published_date = datetime.now()

                        # Extract tickers
                        text_to_search = f"{title} {content}"
                        tickers = extract_tickers(text_to_search)
                        tickers.extend(extract_tickers_with_dollar(text_to_search))
                        tickers = list(set(tickers))

                        if title and url:
                            article = NewsArticle(
                                title=title,
                                content=content,
                                url=url,
                                source="newsapi",
                                source_name=source_name,
                                published_date=published_date,
                                tickers=tickers
                            )
                            articles.append(article)

                    except Exception as e:
                        self.logger.error(f"Error processing headline: {e}")
                        continue

                self.logger.info(f"Fetched {len(articles)} headlines from NewsAPI")

        except Exception as e:
            self.logger.error(f"NewsAPI headlines request failed: {e}")

        return articles


# ============================================================================
# MASTER NEWS AGGREGATOR
# ============================================================================

class NewsAggregator:
    """
    Master news aggregator - combines all sources
    Prioritizes free sources (RSS) over limited APIs
    """

    def __init__(self):
        self.logger = logger
        self.rss_scraper = RSSFeedScraper()
        self.newsapi_scraper = NewsAPIScraper()

    def fetch_latest_news(
        self,
        max_articles: int = 100,
        use_newsapi: bool = False,
        newsapi_queries: Optional[List[str]] = None
    ) -> List[NewsArticle]:
        """
        Fetch latest news from all sources

        Args:
            max_articles: Maximum total articles to return
            use_newsapi: Whether to use NewsAPI (uses daily quota)
            newsapi_queries: Specific queries for NewsAPI

        Returns:
            List of NewsArticle objects
        """
        all_articles = []

        # 1. ALWAYS fetch from RSS (unlimited, free)
        self.logger.info("Fetching news from RSS feeds (free, unlimited)...")
        rss_articles = self.rss_scraper.scrape_all_feeds()
        all_articles.extend(rss_articles)

        # 2. OPTIONALLY fetch from NewsAPI (limited to 100/day)
        if use_newsapi and self.newsapi_scraper.api_key:
            self.logger.info("Fetching news from NewsAPI (limited quota)...")

            # Default queries if none provided
            if newsapi_queries is None:
                newsapi_queries = [
                    "stock market earnings",
                    "merger acquisition",
                    "FDA approval"
                ]

            for query in newsapi_queries:
                newsapi_articles = self.newsapi_scraper.search_news(query)
                all_articles.extend(newsapi_articles)
                time.sleep(1)  # Rate limiting

        # Deduplicate
        seen_hashes = set()
        unique_articles = []
        for article in all_articles:
            if article.hash not in seen_hashes:
                seen_hashes.add(article.hash)
                unique_articles.append(article)

        # Sort by published date (newest first)
        unique_articles.sort(key=lambda x: x.published_date, reverse=True)

        # Limit to max_articles
        unique_articles = unique_articles[:max_articles]

        self.logger.info(f"Total unique articles: {len(unique_articles)}")
        self.logger.info(f"  - From RSS: {sum(1 for a in unique_articles if a.source == 'rss')}")
        self.logger.info(f"  - From NewsAPI: {sum(1 for a in unique_articles if a.source == 'newsapi')}")

        return unique_articles

    def fetch_ticker_news(self, ticker: str, max_articles: int = 20) -> List[NewsArticle]:
        """
        Fetch news for a specific ticker

        Args:
            ticker: Stock ticker symbol
            max_articles: Maximum articles to return

        Returns:
            List of NewsArticle objects mentioning the ticker
        """
        # First try NewsAPI for ticker-specific news (if quota available)
        articles = []

        if self.newsapi_scraper.api_key:
            articles = self.newsapi_scraper.search_news(f"{ticker} stock")

        # Also search through recent RSS articles
        rss_articles = self.rss_scraper.scrape_all_feeds()
        for article in rss_articles:
            if ticker in article.tickers or ticker in article.title or ticker in article.content:
                articles.append(article)

        # Deduplicate
        seen_hashes = set()
        unique_articles = []
        for article in articles:
            if article.hash not in seen_hashes:
                seen_hashes.add(article.hash)
                unique_articles.append(article)

        # Sort and limit
        unique_articles.sort(key=lambda x: x.published_date, reverse=True)
        return unique_articles[:max_articles]


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test the news scraper"""
    print("=" * 60)
    print("Stock Analysis Agent - News Scraper Test")
    print("=" * 60)

    aggregator = NewsAggregator()

    print("\nFetching latest news (RSS only - FREE)...")
    articles = aggregator.fetch_latest_news(max_articles=10, use_newsapi=False)

    print(f"\nFound {len(articles)} articles:\n")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article.title}")
        print(f"   Source: {article.source_name}")
        print(f"   Published: {article.published_date}")
        print(f"   Tickers: {', '.join(article.tickers) if article.tickers else 'None'}")
        print(f"   URL: {article.url}")
        print()

    print("=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    main()
