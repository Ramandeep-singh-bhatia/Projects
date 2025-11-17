"""
Best Buy product scraper using Selenium.
Scrapes deal pages, top deals, and product searches.
"""
import re
import time
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import SCRAPING_CONFIG, RETAILERS
from utils.rate_limiter import rate_limiter, scraper_throttler
from utils.proxy_rotator import ua_rotator
from utils.database import db


class BestBuyScraper:
    """Scrape Best Buy product data."""

    def __init__(self):
        """Initialize Best Buy scraper."""
        self.base_url = RETAILERS['bestbuy']['base_url']
        self.top_deals_url = RETAILERS['bestbuy']['top_deals_url']
        self.deal_of_day_url = RETAILERS['bestbuy']['deal_of_day_url']
        self.driver = None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_top_deals(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Get top deals from Best Buy.

        Args:
            max_results: Maximum number of results to return

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('bestbuy', timeout=10):
            logger.warning("Best Buy rate limit exceeded")
            return []

        scraper_throttler.throttle('bestbuy')

        try:
            driver = self._get_driver()
            logger.info(f"Scraping Best Buy top deals: {self.top_deals_url}")
            driver.get(self.top_deals_url)

            # Wait for products to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sku-item"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for Best Buy products")
                return []

            # Scroll to load more products
            self._scroll_page(driver)

            # Parse products
            products = self._parse_deal_page(driver, max_results)

            db.track_api_usage('bestbuy', 'top_deals', True, 200)
            logger.info(f"Scraped {len(products)} top deals from Best Buy")

            return products

        except Exception as e:
            logger.error(f"Error scraping Best Buy top deals: {e}")
            db.track_api_usage('bestbuy', 'top_deals', False, None)
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_deal_of_day(self) -> List[Dict[str, Any]]:
        """
        Get deal of the day from Best Buy.

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('bestbuy', timeout=10):
            logger.warning("Best Buy rate limit exceeded")
            return []

        scraper_throttler.throttle('bestbuy')

        try:
            driver = self._get_driver()
            logger.info(f"Scraping Best Buy deal of day: {self.deal_of_day_url}")
            driver.get(self.deal_of_day_url)

            time.sleep(3)  # Wait for page to load

            products = self._parse_deal_page(driver, max_results=10)

            db.track_api_usage('bestbuy', 'deal_of_day', True, 200)
            logger.info(f"Scraped {len(products)} deal of day from Best Buy")

            return products

        except Exception as e:
            logger.error(f"Error scraping Best Buy deal of day: {e}")
            db.track_api_usage('bestbuy', 'deal_of_day', False, None)
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_products(self, keywords: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Best Buy products.

        Args:
            keywords: Search keywords
            max_results: Maximum number of results

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('bestbuy', timeout=10):
            logger.warning("Best Buy rate limit exceeded")
            return []

        scraper_throttler.throttle('bestbuy')

        try:
            driver = self._get_driver()
            search_url = f"{self.base_url}/site/searchpage.jsp?st={keywords.replace(' ', '+')}"

            logger.info(f"Scraping Best Buy search: {search_url}")
            driver.get(search_url)

            # Wait for results
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sku-item"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for Best Buy search results")
                return []

            products = self._parse_deal_page(driver, max_results)

            db.track_api_usage('bestbuy', 'search', True, 200)
            logger.info(f"Scraped {len(products)} products from Best Buy search")

            return products

        except Exception as e:
            logger.error(f"Error scraping Best Buy search: {e}")
            db.track_api_usage('bestbuy', 'search', False, None)
            return []

    def get_product_details(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get product details from product page.

        Args:
            url: Product URL

        Returns:
            Product data dictionary or None
        """
        if not rate_limiter.acquire('bestbuy', timeout=10):
            logger.warning("Best Buy rate limit exceeded")
            return None

        scraper_throttler.throttle('bestbuy')

        try:
            driver = self._get_driver()
            driver.get(url)

            time.sleep(3)  # Wait for page to load

            product = self._parse_product_page(driver, url)

            db.track_api_usage('bestbuy', 'product_details', True, 200)

            return product

        except Exception as e:
            logger.error(f"Error scraping Best Buy product: {e}")
            db.track_api_usage('bestbuy', 'product_details', False, None)
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
            time.sleep(1)

    def _parse_deal_page(self, driver: webdriver.Chrome, max_results: int) -> List[Dict[str, Any]]:
        """Parse Best Buy deal/search results page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = []

        # Find product items
        items = soup.select(".sku-item")[:max_results]

        for item in items:
            try:
                # Extract SKU
                sku = item.get('data-sku-id')
                if not sku:
                    continue

                # Extract title
                title_elem = item.select_one('.sku-title a, .sku-header a')
                title = title_elem.text.strip() if title_elem else None

                # Extract price
                price_elem = item.select_one('.priceView-customer-price span[aria-hidden="true"]')
                price = self._parse_price(price_elem.text if price_elem else None)

                # Extract original price (if on sale)
                original_price_elem = item.select_one('.pricing-price__regular-price')
                original_price = self._parse_price(original_price_elem.text if original_price_elem else None)

                # Extract savings
                savings_elem = item.select_one('.pricing-price__savings')
                savings_text = savings_elem.text if savings_elem else None

                # Extract URL
                url_elem = item.select_one('.sku-title a, .sku-header a')
                url = self.base_url + url_elem.get('href') if url_elem else None

                # Extract image
                img_elem = item.select_one('.product-image img')
                image_url = img_elem.get('src') if img_elem else None

                # Extract rating
                rating_elem = item.select_one('.c-ratings-reviews')
                rating = self._parse_rating(rating_elem.get('aria-label') if rating_elem else None)

                # Extract review count
                review_elem = item.select_one('.c-reviews')
                review_count = self._parse_review_count(review_elem.text if review_elem else None)

                # Check if open box
                condition_elem = item.select_one('.open-box-option')
                condition = 'Open Box' if condition_elem else 'New'

                product = {
                    'product_id': f"bestbuy_{sku}",
                    'sku': sku,
                    'title': title,
                    'retailer': 'bestbuy',
                    'url': url,
                    'image_url': image_url,
                    'current_price': price,
                    'previous_price': original_price,
                    'rating': rating,
                    'review_count': review_count,
                    'availability': 'In Stock',
                    'condition': condition,
                }

                if title and price:
                    products.append(product)

            except Exception as e:
                logger.warning(f"Error parsing Best Buy product: {e}")
                continue

        return products

    def _parse_product_page(self, driver: webdriver.Chrome, url: str) -> Dict[str, Any]:
        """Parse Best Buy product page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract SKU from URL
        sku_match = re.search(r'skuId=(\d+)', url)
        sku = sku_match.group(1) if sku_match else None

        # Extract title
        title_elem = soup.select_one('.sku-title h1, .heading-5')
        title = title_elem.text.strip() if title_elem else None

        # Extract price
        price_elem = soup.select_one('.priceView-customer-price span[aria-hidden="true"]')
        price = self._parse_price(price_elem.text if price_elem else None)

        # Extract original price
        original_price_elem = soup.select_one('.pricing-price__regular-price')
        original_price = self._parse_price(original_price_elem.text if original_price_elem else None)

        # Extract rating
        rating_elem = soup.select_one('.ugc-ratings .c-ratings-reviews')
        rating = self._parse_rating(rating_elem.get('aria-label') if rating_elem else None)

        # Extract review count
        review_elem = soup.select_one('.c-reviews-v2')
        review_count = self._parse_review_count(review_elem.text if review_elem else None)

        # Extract availability
        avail_elem = soup.select_one('.fulfillment-add-to-cart-button button')
        availability = 'In Stock' if avail_elem and not avail_elem.get('disabled') else 'Out of Stock'

        # Extract image
        img_elem = soup.select_one('.primary-image')
        image_url = img_elem.get('src') if img_elem else None

        return {
            'product_id': f"bestbuy_{sku}",
            'sku': sku,
            'title': title,
            'retailer': 'bestbuy',
            'url': url,
            'image_url': image_url,
            'current_price': price,
            'previous_price': original_price,
            'rating': rating,
            'review_count': review_count,
            'availability': availability,
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
            match = re.search(r'([\d.]+)\s*out of', rating_str)
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
                logger.info("Best Buy scraper closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
