"""
Best Buy Scanner Agent.
Coordinates Best Buy product searches and deal finding.
"""
from typing import List, Dict, Any
from loguru import logger

from scrapers.bestbuy_scraper import BestBuyScraper
from agents.analyzer_agent import analyzer
from utils.database import db
from utils.notifier import send_deal_notification


class BestBuyAgent:
    """Agent for scanning Best Buy deals."""

    def __init__(self):
        """Initialize Best Buy agent."""
        self.scraper = BestBuyScraper()
        self.name = "Best Buy Scanner"

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

        # Search products
        products = self.scraper.search_products(keywords, max_results=20)

        # Process each product
        for product in products:
            try:
                product['category'] = watchlist_item['category']

                # Filter by price
                if max_price and product.get('current_price'):
                    if product['current_price'] > max_price:
                        continue

                # Save to database
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

                # Update deal score
                db.upsert_product({'product_id': product['product_id'], 'deal_score': enriched_product['deal_score']})

                # Check if worth notifying
                analysis = {
                    'score': enriched_product.get('deal_score', 0),
                    'recommendation': enriched_product.get('deal_recommendation')
                }

                if analyzer.should_notify(analysis):
                    # Calculate savings
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

    def scan_top_deals(self) -> List[Dict[str, Any]]:
        """
        Scan Best Buy top deals page.

        Returns:
            List of deals found
        """
        logger.info(f"{self.name}: Scanning top deals")

        deals = []
        products = self.scraper.get_top_deals(max_results=30)

        for product in products:
            try:
                # Save and analyze
                product_id = db.upsert_product(product)

                if product.get('current_price'):
                    db.add_price_history(product_id, product['current_price'])

                # Get historical data
                db_product = db.get_product_by_id(product['product_id'])
                if db_product:
                    product.update(db_product)

                # Analyze
                enriched_product = analyzer.enrich_product_data(product)
                db.upsert_product({'product_id': product['product_id'], 'deal_score': enriched_product['deal_score']})

                analysis = {'score': enriched_product.get('deal_score', 0)}

                if analyzer.should_notify(analysis):
                    if enriched_product.get('previous_price'):
                        enriched_product['savings'] = enriched_product['previous_price'] - enriched_product['current_price']

                    deals.append(enriched_product)
                    send_deal_notification(enriched_product, product_id)

            except Exception as e:
                logger.error(f"{self.name}: Error processing top deal: {e}")
                continue

        logger.info(f"{self.name}: Found {len(deals)} top deals")
        return deals

    def cleanup(self):
        """Cleanup resources."""
        self.scraper.close()


# Singleton instance
bestbuy_agent = BestBuyAgent()
