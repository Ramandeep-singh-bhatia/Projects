"""
Amazon product scraper with API fallback.
Uses RapidAPI first, then falls back to web scraping with Selenium.
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
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import API_ENDPOINTS, SCRAPING_CONFIG, RETAILERS
from utils.rate_limiter import rate_limiter, scraper_throttler
from utils.proxy_rotator import ua_rotator
from utils.database import db


class AmazonScraper:
    """Scrape Amazon product data using API and web scraping."""

    def __init__(self):
        """Initialize Amazon scraper."""
        self.base_url = RETAILERS['amazon']['base_url']
        self.search_url = RETAILERS['amazon']['search_url']
        self.api_config = API_ENDPOINTS.get('rapidapi', {})
        self.driver = None

    def search_products_api(self, keywords: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Amazon products using RapidAPI.

        Args:
            keywords: Search keywords
            max_results: Maximum number of results to return

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('rapidapi', timeout=5):
            logger.warning("RapidAPI rate limit exceeded, skipping API search")
            return []

        try:
            url = f"{self.api_config['base_url']}/search"
            params = {
                'query': keywords,
                'page': '1',
                'country': 'US',
            }

            response = requests.get(
                url,
                headers=self.api_config['headers'],
                params=params,
                timeout=SCRAPING_CONFIG['timeout']
            )

            db.track_api_usage('rapidapi', '/search', response.status_code == 200, response.status_code)

            if response.status_code == 200:
                data = response.json()
                products = self._parse_rapidapi_response(data, max_results)
                logger.info(f"Found {len(products)} products via RapidAPI")
                return products
            else:
                logger.warning(f"RapidAPI returned status {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error searching Amazon API: {e}")
            db.track_api_usage('rapidapi', '/search', False, None)
            return []

    def get_product_details_api(self, asin: str) -> Optional[Dict[str, Any]]:
        """
        Get product details using RapidAPI.

        Args:
            asin: Amazon ASIN

        Returns:
            Product data dictionary or None
        """
        if not rate_limiter.acquire('rapidapi', timeout=5):
            logger.warning("RapidAPI rate limit exceeded")
            return None

        try:
            url = f"{self.api_config['base_url']}/product-details"
            params = {'asin': asin, 'country': 'US'}

            response = requests.get(
                url,
                headers=self.api_config['headers'],
                params=params,
                timeout=SCRAPING_CONFIG['timeout']
            )

            db.track_api_usage('rapidapi', '/product-details', response.status_code == 200, response.status_code)

            if response.status_code == 200:
                data = response.json()
                product = self._parse_product_details(data)
                logger.info(f"Got product details for ASIN {asin}")
                return product
            else:
                logger.warning(f"RapidAPI returned status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting Amazon product details: {e}")
            db.track_api_usage('rapidapi', '/product-details', False, None)
            return None

    def _parse_rapidapi_response(self, data: Dict, max_results: int) -> List[Dict[str, Any]]:
        """Parse RapidAPI search response."""
        products = []

        results = data.get('data', {}).get('products', [])[:max_results]

        for item in results:
            try:
                product = {
                    'product_id': f"amazon_{item.get('asin')}",
                    'asin': item.get('asin'),
                    'title': item.get('product_title'),
                    'retailer': 'amazon',
                    'url': item.get('product_url'),
                    'image_url': item.get('product_photo'),
                    'current_price': self._parse_price(item.get('product_price')),
                    'rating': item.get('product_star_rating'),
                    'review_count': item.get('product_num_ratings'),
                    'availability': 'In Stock' if item.get('is_prime') else 'Unknown',
                }
                products.append(product)
            except Exception as e:
                logger.warning(f"Error parsing product: {e}")
                continue

        return products

    def _parse_product_details(self, data: Dict) -> Dict[str, Any]:
        """Parse RapidAPI product details response."""
        product_data = data.get('data', {})

        return {
            'product_id': f"amazon_{product_data.get('asin')}",
            'asin': product_data.get('asin'),
            'title': product_data.get('product_title'),
            'retailer': 'amazon',
            'url': product_data.get('product_url'),
            'image_url': product_data.get('product_photo'),
            'current_price': self._parse_price(product_data.get('product_price')),
            'rating': product_data.get('product_star_rating'),
            'review_count': product_data.get('product_num_ratings'),
            'availability': product_data.get('product_availability', 'Unknown'),
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def search_products_scrape(self, keywords: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Amazon products using web scraping.

        Args:
            keywords: Search keywords
            max_results: Maximum number of results

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('amazon', timeout=10):
            logger.warning("Amazon rate limit exceeded")
            return []

        scraper_throttler.throttle('amazon')

        try:
            driver = self._get_driver()
            url = f"{self.search_url}?k={keywords.replace(' ', '+')}"

            logger.info(f"Scraping Amazon search: {url}")
            driver.get(url)

            # Wait for results to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-component-type='s-search-result']"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for search results")
                return []

            # Parse results
            products = self._parse_search_results(driver, max_results)

            db.track_api_usage('amazon', 'search_scrape', True, 200)
            logger.info(f"Scraped {len(products)} products from Amazon")

            return products

        except Exception as e:
            logger.error(f"Error scraping Amazon search: {e}")
            db.track_api_usage('amazon', 'search_scrape', False, None)
            return []

    def get_product_details_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get product details using web scraping.

        Args:
            url: Product URL

        Returns:
            Product data dictionary or None
        """
        if not rate_limiter.acquire('amazon', timeout=10):
            logger.warning("Amazon rate limit exceeded")
            return None

        scraper_throttler.throttle('amazon')

        try:
            driver = self._get_driver()
            driver.get(url)

            # Wait for page to load
            time.sleep(2)

            product = self._parse_product_page(driver, url)

            db.track_api_usage('amazon', 'product_scrape', True, 200)

            return product

        except Exception as e:
            logger.error(f"Error scraping Amazon product: {e}")
            db.track_api_usage('amazon', 'product_scrape', False, None)
            return None

    def _get_driver(self) -> webdriver.Chrome:
        """Get or create Selenium WebDriver."""
        if self.driver is None:
            options = Options()

            # Add anti-detection options
            for option in ua_rotator.get_selenium_options(SCRAPING_CONFIG['headless']):
                options.add_argument(option)

            # Additional options
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)

                # Execute CDP commands to avoid detection
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

    def _parse_search_results(self, driver: webdriver.Chrome, max_results: int) -> List[Dict[str, Any]]:
        """Parse Amazon search results page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = []

        # Find product cards
        items = soup.select("[data-component-type='s-search-result']")[:max_results]

        for item in items:
            try:
                # Extract ASIN
                asin = item.get('data-asin')
                if not asin:
                    continue

                # Extract title
                title_elem = item.select_one('h2 a span')
                title = title_elem.text.strip() if title_elem else None

                # Extract price
                price_elem = item.select_one('.a-price .a-offscreen')
                price = self._parse_price(price_elem.text if price_elem else None)

                # Extract rating
                rating_elem = item.select_one('.a-icon-star-small .a-icon-alt')
                rating = self._parse_rating(rating_elem.text if rating_elem else None)

                # Extract review count
                review_elem = item.select_one('span[aria-label*="stars"]')
                review_count = None
                if review_elem and review_elem.get('aria-label'):
                    review_count = self._parse_review_count(review_elem.get('aria-label'))

                # Extract URL
                url_elem = item.select_one('h2 a')
                url = self.base_url + url_elem.get('href') if url_elem else None

                # Extract image
                img_elem = item.select_one('img.s-image')
                image_url = img_elem.get('src') if img_elem else None

                product = {
                    'product_id': f"amazon_{asin}",
                    'asin': asin,
                    'title': title,
                    'retailer': 'amazon',
                    'url': url,
                    'image_url': image_url,
                    'current_price': price,
                    'rating': rating,
                    'review_count': review_count,
                    'availability': 'In Stock',
                }

                if title and price:  # Only add if we have minimum required data
                    products.append(product)

            except Exception as e:
                logger.warning(f"Error parsing product item: {e}")
                continue

        return products

    def _parse_product_page(self, driver: webdriver.Chrome, url: str) -> Dict[str, Any]:
        """Parse Amazon product page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract ASIN from URL
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        asin = asin_match.group(1) if asin_match else None

        # Extract title
        title_elem = soup.select_one('#productTitle')
        title = title_elem.text.strip() if title_elem else None

        # Extract price
        price_elem = soup.select_one('.a-price .a-offscreen')
        price = self._parse_price(price_elem.text if price_elem else None)

        # Extract rating
        rating_elem = soup.select_one('.a-icon-star .a-icon-alt')
        rating = self._parse_rating(rating_elem.text if rating_elem else None)

        # Extract review count
        review_elem = soup.select_one('#acrCustomerReviewText')
        review_count = self._parse_review_count(review_elem.text if review_elem else None)

        # Extract availability
        avail_elem = soup.select_one('#availability span')
        availability = avail_elem.text.strip() if avail_elem else 'Unknown'

        # Extract image
        img_elem = soup.select_one('#landingImage')
        image_url = img_elem.get('src') if img_elem else None

        return {
            'product_id': f"amazon_{asin}",
            'asin': asin,
            'title': title,
            'retailer': 'amazon',
            'url': url,
            'image_url': image_url,
            'current_price': price,
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
            # Remove currency symbols and commas
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
            # Extract number before "out of"
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
            # Remove commas and extract number
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
                logger.info("Amazon scraper closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
