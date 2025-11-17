"""
Amazon Deal Hunter Agent.
Coordinates Amazon product searches and deal finding.
"""
from typing import List, Dict, Any
from loguru import logger

from scrapers.amazon_scraper import AmazonScraper
from agents.analyzer_agent import analyzer
from utils.database import db
from utils.notifier import send_deal_notification


class AmazonAgent:
    """Agent for hunting Amazon deals."""

    def __init__(self):
        """Initialize Amazon agent."""
        self.scraper = AmazonScraper()
        self.name = "Amazon Deal Hunter"

    def search_deals(self, watchlist_item: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for deals based on watchlist item.

        Args:
            watchlist_item: Watchlist configuration

        Returns:
            List of deals found
        """
        logger.info(f"{self.name}: Searching for {watchlist_item['category']}")

        keywords = ' '.join(watchlist_item['keywords'])
        max_price = watchlist_item.get('max_price')

        deals = []

        # Try API first
        products = self.scraper.search_products_api(keywords, max_results=20)

        # Fallback to scraping if API fails or returns no results
        if not products:
            logger.info(f"{self.name}: API failed, falling back to scraping")
            products = self.scraper.search_products_scrape(keywords, max_results=20)

        # Process each product
        for product in products:
            try:
                # Add category
                product['category'] = watchlist_item['category']

                # Filter by price
                if max_price and product.get('current_price'):
                    if product['current_price'] > max_price:
                        continue

                # Save to database and get historical data
                product_id = db.upsert_product(product)

                # Add price history
                if product.get('current_price'):
                    db.add_price_history(
                        product_id,
                        product['current_price'],
                        product.get('availability')
                    )

                # Get updated product with historical data
                db_product = db.get_product_by_id(product['product_id'])
                if db_product:
                    product.update(db_product)

                # Analyze deal quality
                enriched_product = analyzer.enrich_product_data(product)

                # Update deal score in database
                db.upsert_product({'product_id': product['product_id'], 'deal_score': enriched_product['deal_score']})

                # Check if worth notifying
                analysis = {
                    'score': enriched_product.get('deal_score', 0),
                    'recommendation': enriched_product.get('deal_recommendation')
                }

                if analyzer.should_notify(analysis):
                    # Calculate savings for notification
                    if enriched_product.get('previous_price'):
                        enriched_product['savings'] = enriched_product['previous_price'] - enriched_product['current_price']
                    elif enriched_product.get('average_price'):
                        enriched_product['savings'] = enriched_product['average_price'] - enriched_product['current_price']

                    deals.append(enriched_product)

                    # Send notification
                    send_deal_notification(enriched_product, product_id)

                    logger.info(
                        f"{self.name}: Found deal - {enriched_product['title'][:50]}... "
                        f"(${enriched_product['current_price']}, score: {enriched_product['deal_score']})"
                    )

            except Exception as e:
                logger.error(f"{self.name}: Error processing product: {e}")
                continue

        logger.info(f"{self.name}: Found {len(deals)} qualifying deals")
        return deals

    def cleanup(self):
        """Cleanup resources."""
        self.scraper.close()


# Singleton instance
amazon_agent = AmazonAgent()
