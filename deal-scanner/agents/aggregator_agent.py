"""
Deal Aggregator Agent.
Monitors RSS feeds from Slickdeals, Reddit, and other sources.
"""
import re
from typing import List, Dict, Any
import feedparser
from loguru import logger

from config.settings import RSS_FEEDS
from agents.analyzer_agent import analyzer
from utils.database import db
from utils.notifier import send_deal_notification


class AggregatorAgent:
    """Agent for aggregating deals from RSS feeds."""

    def __init__(self):
        """Initialize aggregator agent."""
        self.feeds = RSS_FEEDS
        self.name = "Deal Aggregator"

    def scan_feeds(self, watchlist_items: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Scan all RSS feeds for deals.

        Args:
            watchlist_items: Optional list of watchlist items to filter by

        Returns:
            List of deals found
        """
        logger.info(f"{self.name}: Scanning RSS feeds")

        all_deals = []

        for feed_name, feed_url in self.feeds.items():
            try:
                logger.info(f"{self.name}: Scanning {feed_name}")
                deals = self._scan_feed(feed_url, feed_name, watchlist_items)
                all_deals.extend(deals)

            except Exception as e:
                logger.error(f"{self.name}: Error scanning {feed_name}: {e}")
                continue

        logger.info(f"{self.name}: Found {len(all_deals)} deals from RSS feeds")
        return all_deals

    def _scan_feed(self, feed_url: str, feed_name: str, watchlist_items: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Scan a single RSS feed.

        Args:
            feed_url: URL of the RSS feed
            feed_name: Name of the feed
            watchlist_items: Optional watchlist items to filter by

        Returns:
            List of deals found
        """
        deals = []

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:50]:  # Limit to recent 50 items
                try:
                    # Extract deal information
                    title = entry.get('title', '')
                    link = entry.get('link', '')
                    description = entry.get('description', '') or entry.get('summary', '')

                    # Extract price from title/description
                    price = self._extract_price(title + ' ' + description)

                    # Check if matches watchlist
                    if watchlist_items:
                        matched = False
                        category = None

                        for item in watchlist_items:
                            keywords = item.get('keywords', [])
                            max_price = item.get('max_price')

                            # Check if any keyword matches
                            if any(keyword.lower() in title.lower() for keyword in keywords):
                                matched = True
                                category = item['category']

                                # Check price constraint
                                if max_price and price and price > max_price:
                                    matched = False

                                if matched:
                                    break

                        if not matched:
                            continue
                    else:
                        category = self._guess_category(title)

                    # Create product data
                    product = {
                        'product_id': f"{feed_name}_{self._generate_id(link)}",
                        'title': title,
                        'url': link,
                        'current_price': price,
                        'category': category or 'General',
                        'retailer': self._extract_retailer(title, link),
                        'availability': 'Unknown',
                        'source': feed_name,
                    }

                    # Skip if no price found
                    if not price:
                        continue

                    # Save to database
                    product_id = db.upsert_product(product)

                    # Add price history
                    db.add_price_history(product_id, price)

                    # Get historical data
                    db_product = db.get_product_by_id(product['product_id'])
                    if db_product:
                        product.update(db_product)

                    # Analyze deal
                    enriched_product = analyzer.enrich_product_data(product)

                    # RSS deals get a small boost as they're curated
                    enriched_product['deal_score'] = min(100, enriched_product['deal_score'] + 5)

                    db.upsert_product({'product_id': product['product_id'], 'deal_score': enriched_product['deal_score']})

                    # Check if worth notifying
                    analysis = {'score': enriched_product.get('deal_score', 0)}

                    if analyzer.should_notify(analysis):
                        if enriched_product.get('average_price'):
                            enriched_product['savings'] = enriched_product['average_price'] - enriched_product['current_price']

                        deals.append(enriched_product)

                        # Send notification
                        send_deal_notification(enriched_product, product_id)

                        logger.info(
                            f"{self.name}: Found deal from {feed_name} - {title[:50]}... "
                            f"(${price}, score: {enriched_product['deal_score']})"
                        )

                except Exception as e:
                    logger.warning(f"{self.name}: Error processing feed entry: {e}")
                    continue

        except Exception as e:
            logger.error(f"{self.name}: Error parsing feed {feed_name}: {e}")

        return deals

    @staticmethod
    def _extract_price(text: str) -> float:
        """Extract price from text."""
        # Look for patterns like $X.XX or $X,XXX.XX
        patterns = [
            r'\$(\d+,?\d*\.?\d{2})',  # $123.45 or $1,234.56
            r'\$(\d+)',  # $123
            r'(\d+,?\d*\.?\d{2})\s*dollars?',  # 123.45 dollars
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    price_str = matches[0].replace(',', '')
                    return float(price_str)
                except ValueError:
                    continue

        return None

    @staticmethod
    def _extract_retailer(title: str, url: str) -> str:
        """Extract retailer from title or URL."""
        text = (title + ' ' + url).lower()

        retailers = {
            'amazon': 'amazon',
            'bestbuy': 'bestbuy',
            'best buy': 'bestbuy',
            'walmart': 'walmart',
            'target': 'target',
        }

        for keyword, retailer in retailers.items():
            if keyword in text:
                return retailer

        return 'unknown'

    @staticmethod
    def _guess_category(title: str) -> str:
        """Guess category from title."""
        title_lower = title.lower()

        categories = {
            'tv': ['tv', 'television', 'oled', 'qled', '4k'],
            'laptop': ['laptop', 'notebook', 'macbook'],
            'gaming': ['xbox', 'playstation', 'nintendo', 'gaming', 'console'],
            'headphones': ['headphones', 'earbuds', 'airpods'],
            'baby': ['baby', 'stroller', 'crib', 'diaper'],
        }

        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category.title()

        return 'General'

    @staticmethod
    def _generate_id(url: str) -> str:
        """Generate a unique ID from URL."""
        return str(hash(url))[:16]


# Singleton instance
aggregator_agent = AggregatorAgent()
