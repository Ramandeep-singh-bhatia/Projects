"""
Walmart product scraper.
Uses web scraping to find deals and product information.
"""
import re
import time
import requests
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import SCRAPING_CONFIG, RETAILERS
from utils.rate_limiter import rate_limiter, scraper_throttler
from utils.proxy_rotator import ua_rotator
from utils.database import db


class WalmartScraper:
    """Scrape Walmart product data."""

    def __init__(self):
        """Initialize Walmart scraper."""
        self.base_url = RETAILERS['walmart']['base_url']
        self.search_url = RETAILERS['walmart']['search_url']
        self.driver = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_products(self, keywords: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Walmart products.

        Args:
            keywords: Search keywords
            max_results: Maximum number of results

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('walmart', timeout=10):
            logger.warning("Walmart rate limit exceeded")
            return []

        scraper_throttler.throttle('walmart')

        try:
            driver = self._get_driver()
            search_url = f"{self.search_url}?q={keywords.replace(' ', '+')}"

            logger.info(f"Scraping Walmart search: {search_url}")
            driver.get(search_url)

            # Wait for products to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-item-id]"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for Walmart products")
                return []

            time.sleep(2)  # Additional wait for dynamic content

            # Scroll to load more products
            self._scroll_page(driver)

            products = self._parse_search_results(driver, max_results)

            db.track_api_usage('walmart', 'search', True, 200)
            logger.info(f"Scraped {len(products)} products from Walmart")

            return products

        except Exception as e:
            logger.error(f"Error scraping Walmart search: {e}")
            db.track_api_usage('walmart', 'search', False, None)
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_clearance_deals(self, category: str = None, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Get clearance deals from Walmart.

        Args:
            category: Optional category filter
            max_results: Maximum number of results

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('walmart', timeout=10):
            logger.warning("Walmart rate limit exceeded")
            return []

        scraper_throttler.throttle('walmart')

        try:
            driver = self._get_driver()

            # Clearance page URL
            clearance_url = f"{self.base_url}/browse/home/clearance/1072864_4044_1032619"
            if category:
                clearance_url += f"?q={category.replace(' ', '+')}"

            logger.info(f"Scraping Walmart clearance: {clearance_url}")
            driver.get(clearance_url)

            time.sleep(3)  # Wait for page to load

            # Scroll to load more products
            self._scroll_page(driver)

            products = self._parse_search_results(driver, max_results)

            db.track_api_usage('walmart', 'clearance', True, 200)
            logger.info(f"Scraped {len(products)} clearance items from Walmart")

            return products

        except Exception as e:
            logger.error(f"Error scraping Walmart clearance: {e}")
            db.track_api_usage('walmart', 'clearance', False, None)
            return []

    def get_product_details(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get product details from product page.

        Args:
            url: Product URL

        Returns:
            Product data dictionary or None
        """
        if not rate_limiter.acquire('walmart', timeout=10):
            logger.warning("Walmart rate limit exceeded")
            return None

        scraper_throttler.throttle('walmart')

        try:
            driver = self._get_driver()
            driver.get(url)

            time.sleep(3)  # Wait for page to load

            product = self._parse_product_page(driver, url)

            db.track_api_usage('walmart', 'product_details', True, 200)

            return product

        except Exception as e:
            logger.error(f"Error scraping Walmart product: {e}")
            db.track_api_usage('walmart', 'product_details', False, None)
            return None

    def _get_driver(self) -> webdriver.Chrome:
        """Get or create Selenium WebDriver."""
        if self.driver is None:
            options = Options()

            # Add anti-detection options
            for option in ua_rotator.get_selenium_options(SCRAPING_CONFIG['headless']):
                options.add_argument(option)

            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

                # Execute CDP commands
                self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                    "userAgent": ua_rotator.get_random_user_agent()
                })
                self.driver.execute_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

            except Exception as e:
                logger.error(f"Error creating WebDriver: {e}")
                raise

        return self.driver

    def _scroll_page(self, driver: webdriver.Chrome, scrolls: int = 3):
        """Scroll page to load more products."""
        for i in range(scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

    def _parse_search_results(self, driver: webdriver.Chrome, max_results: int) -> List[Dict[str, Any]]:
        """Parse Walmart search results page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = []

        # Find product items
        items = soup.select("[data-item-id]")[:max_results]

        for item in items:
            try:
                # Extract item ID
                item_id = item.get('data-item-id')
                if not item_id:
                    continue

                # Extract title
                title_elem = item.select_one('[data-automation-id="product-title"], .product-title-link span')
                title = title_elem.text.strip() if title_elem else None

                # Extract price
                price_elem = item.select_one('[data-automation-id="product-price"] .price-main .display-inline-block')
                if not price_elem:
                    price_elem = item.select_one('.price-characteristic')

                price = self._parse_price(price_elem.text if price_elem else None)

                # Extract original price (if on sale)
                was_price_elem = item.select_one('.was-price .price-characteristic')
                was_price = self._parse_price(was_price_elem.text if was_price_elem else None)

                # Check for rollback tag
                rollback_elem = item.select_one('[data-automation-id="product-badge-rollback"]')
                is_rollback = rollback_elem is not None

                # Extract URL
                url_elem = item.select_one('a[link-identifier="product-title"]')
                if not url_elem:
                    url_elem = item.select_one('.product-title-link')

                product_url = None
                if url_elem:
                    href = url_elem.get('href')
                    product_url = href if href.startswith('http') else self.base_url + href

                # Extract image
                img_elem = item.select_one('img[data-automation-id="product-image"]')
                if not img_elem:
                    img_elem = item.select_one('.product-image img')

                image_url = img_elem.get('src') if img_elem else None

                # Extract rating
                rating_elem = item.select_one('.stars-reviews-count .stars')
                rating = self._parse_rating(rating_elem.get('aria-label') if rating_elem else None)

                # Extract review count
                review_elem = item.select_one('.stars-reviews-count .review-count')
                review_count = self._parse_review_count(review_elem.text if review_elem else None)

                product = {
                    'product_id': f"walmart_{item_id}",
                    'sku': item_id,
                    'title': title,
                    'retailer': 'walmart',
                    'url': product_url,
                    'image_url': image_url,
                    'current_price': price,
                    'previous_price': was_price,
                    'rating': rating,
                    'review_count': review_count,
                    'availability': 'In Stock',
                    'is_rollback': is_rollback,
                }

                if title and price:
                    products.append(product)

            except Exception as e:
                logger.warning(f"Error parsing Walmart product: {e}")
                continue

        return products

    def _parse_product_page(self, driver: webdriver.Chrome, url: str) -> Dict[str, Any]:
        """Parse Walmart product page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract item ID from URL
        item_id_match = re.search(r'/ip/.*?/(\d+)', url)
        item_id = item_id_match.group(1) if item_id_match else None

        # Extract title
        title_elem = soup.select_one('h1[itemprop="name"]')
        if not title_elem:
            title_elem = soup.select_one('h1.prod-ProductTitle')
        title = title_elem.text.strip() if title_elem else None

        # Extract price
        price_elem = soup.select_one('[itemprop="price"]')
        if not price_elem:
            price_elem = soup.select_one('.price-characteristic')

        price = self._parse_price(price_elem.get('content') if price_elem and price_elem.get('content')
                                   else price_elem.text if price_elem else None)

        # Extract original price
        was_price_elem = soup.select_one('.was-price .price-characteristic')
        was_price = self._parse_price(was_price_elem.text if was_price_elem else None)

        # Extract rating
        rating_elem = soup.select_one('[itemprop="ratingValue"]')
        if not rating_elem:
            rating_elem = soup.select_one('.stars-container .stars')

        rating = None
        if rating_elem:
            if rating_elem.get('content'):
                rating = float(rating_elem.get('content'))
            else:
                rating = self._parse_rating(rating_elem.get('aria-label') if rating_elem else None)

        # Extract review count
        review_elem = soup.select_one('[itemprop="ratingCount"]')
        if not review_elem:
            review_elem = soup.select_one('.rating-number')

        review_count = None
        if review_elem:
            if review_elem.get('content'):
                review_count = int(review_elem.get('content'))
            else:
                review_count = self._parse_review_count(review_elem.text if review_elem else None)

        # Extract availability
        avail_elem = soup.select_one('[itemprop="availability"]')
        availability = 'In Stock'
        if avail_elem:
            avail_text = avail_elem.get('content', '').lower()
            if 'instock' in avail_text:
                availability = 'In Stock'
            elif 'outofstock' in avail_text:
                availability = 'Out of Stock'

        # Extract image
        img_elem = soup.select_one('[itemprop="image"]')
        if not img_elem:
            img_elem = soup.select_one('.prod-hero-image img')

        image_url = img_elem.get('src') if img_elem else None

        # Check for rollback
        rollback_elem = soup.select_one('[data-automation-id="rollback-badge"]')
        is_rollback = rollback_elem is not None

        return {
            'product_id': f"walmart_{item_id}",
            'sku': item_id,
            'title': title,
            'retailer': 'walmart',
            'url': url,
            'image_url': image_url,
            'current_price': price,
            'previous_price': was_price,
            'rating': rating,
            'review_count': review_count,
            'availability': availability,
            'is_rollback': is_rollback,
        }

    @staticmethod
    def _parse_price(price_str: Optional[str]) -> Optional[float]:
        """Parse price string to float."""
        if not price_str:
            return None

        try:
            price_clean = re.sub(r'[^\d.]', '', price_str)
            return float(price_clean) if price_clean else None
        except (ValueError, AttributeError):
            return None

    @staticmethod
    def _parse_rating(rating_str: Optional[str]) -> Optional[float]:
        """Parse rating string to float."""
        if not rating_str:
            return None

        try:
            # Try to extract "X out of 5"
            match = re.search(r'([\d.]+)\s*out of', rating_str)
            if match:
                return float(match.group(1))

            # Try to extract any float
            match = re.search(r'([\d.]+)', rating_str)
            if match:
                return float(match.group(1))
        except (ValueError, AttributeError):
            pass

        return None

    @staticmethod
    def _parse_review_count(review_str: Optional[str]) -> Optional[int]:
        """Parse review count string to int."""
        if not review_str:
            return None

        try:
            numbers = re.findall(r'[\d,]+', review_str)
            if numbers:
                return int(numbers[0].replace(',', ''))
        except (ValueError, AttributeError):
            pass

        return None

    def close(self):
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Walmart scraper closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
