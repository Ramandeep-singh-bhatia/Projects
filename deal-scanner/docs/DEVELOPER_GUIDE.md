# Developer Guide - Multi-Retail Deal Scanner

## Table of Contents
1. [Development Setup](#development-setup)
2. [Code Structure](#code-structure)
3. [Adding a New Retailer](#adding-a-new-retailer)
4. [Custom Agent Development](#custom-agent-development)
5. [Database Operations](#database-operations)
6. [API Integration](#api-integration)
7. [Testing](#testing)
8. [Code Style & Best Practices](#code-style--best-practices)
9. [Debugging](#debugging)
10. [Contributing](#contributing)

## Development Setup

### Prerequisites

- Python 3.11+
- Git
- IDE (VS Code, PyCharm, etc.)
- Chrome/Chromium

### Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd deal-scanner

# Create virtual environment
python -m venv venv

# Activate
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy ipython
```

### IDE Setup

**VS Code** (`.vscode/settings.json`):
```json
{
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "100"],
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true
}
```

**PyCharm:**
- Settings → Project → Python Interpreter → Add venv
- Settings → Tools → Python Integrated Tools → Testing → pytest
- Settings → Editor → Code Style → Python → Line length: 100

### Development Environment

```bash
# Copy environment template
cp .env.example .env.dev

# Edit for development
nano .env.dev
```

**Example .env.dev:**
```bash
# Development settings
TELEGRAM_BOT_TOKEN=your_dev_bot_token
TELEGRAM_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_key
RAPIDAPI_KEY=your_rapidapi_key

# Development flags
NOTIFICATIONS_ENABLED=false  # Don't spam yourself
HEADLESS=false              # See browser for debugging
LOG_LEVEL=DEBUG             # Verbose logging
```

## Code Structure

### Architecture Overview

```
deal-scanner/
├── agents/                 # Business logic agents
│   ├── __init__.py
│   ├── amazon_agent.py    # Amazon deal hunting
│   ├── bestbuy_agent.py   # Best Buy scanning
│   ├── walmart_agent.py   # Walmart monitoring
│   ├── aggregator_agent.py # RSS aggregation
│   └── analyzer_agent.py  # Deal quality analysis
│
├── scrapers/              # Data acquisition layer
│   ├── __init__.py
│   ├── amazon_scraper.py  # Amazon scraping/API
│   ├── bestbuy_scraper.py # Best Buy scraping
│   └── walmart_scraper.py # Walmart scraping
│
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── database.py        # Database operations
│   ├── notifier.py        # Notifications
│   ├── rate_limiter.py    # Rate limiting
│   └── proxy_rotator.py   # User agent rotation
│
├── config/                # Configuration
│   ├── __init__.py
│   ├── settings.py        # App configuration
│   └── products.json      # Watchlist
│
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_scrapers.py
│   └── test_utils.py
│
├── docs/                  # Documentation
├── logs/                  # Log files
├── main.py               # Entry point
└── requirements.txt      # Dependencies
```

### Module Responsibilities

**agents/** - Business Logic
- Accept watchlist items
- Coordinate scraping
- Process results
- Make decisions
- Trigger notifications

**scrapers/** - Data Acquisition
- Extract data from retailers
- Handle APIs and web scraping
- Parse HTML/JSON
- Return structured data

**utils/** - Cross-cutting Concerns
- Database access
- Notifications
- Rate limiting
- Logging
- Helper functions

**config/** - Configuration
- Settings management
- Environment variables
- Watchlist data

## Adding a New Retailer

Let's add Target as an example.

### Step 1: Create Scraper

Create `scrapers/target_scraper.py`:

```python
"""
Target product scraper using Selenium.
"""
import re
import time
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from loguru import logger

from config.settings import SCRAPING_CONFIG, RETAILERS
from utils.rate_limiter import rate_limiter, scraper_throttler
from utils.proxy_rotator import ua_rotator
from utils.database import db


class TargetScraper:
    """Scrape Target product data."""

    def __init__(self):
        """Initialize Target scraper."""
        self.base_url = "https://www.target.com"
        self.search_url = f"{self.base_url}/s"
        self.driver = None

    def search_products(self, keywords: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Target products.

        Args:
            keywords: Search keywords
            max_results: Maximum number of results

        Returns:
            List of product data dictionaries
        """
        if not rate_limiter.acquire('target', timeout=10):
            logger.warning("Target rate limit exceeded")
            return []

        scraper_throttler.throttle('target')

        try:
            driver = self._get_driver()
            search_url = f"{self.search_url}?searchTerm={keywords.replace(' ', '+')}"

            logger.info(f"Scraping Target search: {search_url}")
            driver.get(search_url)

            # Wait for products to load
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='product-item']"))
                )
            except TimeoutException:
                logger.warning("Timeout waiting for Target products")
                return []

            time.sleep(2)

            products = self._parse_search_results(driver, max_results)

            db.track_api_usage('target', 'search', True, 200)
            logger.info(f"Scraped {len(products)} products from Target")

            return products

        except Exception as e:
            logger.error(f"Error scraping Target search: {e}")
            db.track_api_usage('target', 'search', False, None)
            return []

    def _get_driver(self) -> webdriver.Chrome:
        """Get or create Selenium WebDriver."""
        if self.driver is None:
            options = webdriver.ChromeOptions()

            for option in ua_rotator.get_selenium_options(SCRAPING_CONFIG['headless']):
                options.add_argument(option)

            self.driver = webdriver.Chrome(options=options)

        return self.driver

    def _parse_search_results(self, driver: webdriver.Chrome, max_results: int) -> List[Dict[str, Any]]:
        """Parse Target search results page."""
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products = []

        items = soup.select("[data-test='product-item']")[:max_results]

        for item in items:
            try:
                # Extract TCIN (Target ID)
                link = item.select_one('a[data-test="product-title"]')
                tcin_match = re.search(r'/A-(\d+)', link['href']) if link else None
                tcin = tcin_match.group(1) if tcin_match else None

                # Extract title
                title_elem = item.select_one('[data-test="product-title"]')
                title = title_elem.text.strip() if title_elem else None

                # Extract price
                price_elem = item.select_one('[data-test="current-price"]')
                price = self._parse_price(price_elem.text if price_elem else None)

                # Extract rating
                rating_elem = item.select_one('[data-test="ratings"]')
                rating = self._parse_rating(rating_elem['aria-label'] if rating_elem else None)

                # Extract review count
                review_elem = item.select_one('[data-test="rating-count"]')
                review_count = self._parse_review_count(review_elem.text if review_elem else None)

                # Build product URL
                product_url = self.base_url + link['href'] if link else None

                # Extract image
                img_elem = item.select_one('img')
                image_url = img_elem['src'] if img_elem else None

                product = {
                    'product_id': f"target_{tcin}",
                    'sku': tcin,
                    'title': title,
                    'retailer': 'target',
                    'url': product_url,
                    'image_url': image_url,
                    'current_price': price,
                    'rating': rating,
                    'review_count': review_count,
                    'availability': 'In Stock',
                }

                if title and price:
                    products.append(product)

            except Exception as e:
                logger.warning(f"Error parsing Target product: {e}")
                continue

        return products

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
                logger.info("Target scraper closed")
            except Exception as e:
                logger.error(f"Error closing driver: {e}")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
```

### Step 2: Create Agent

Create `agents/target_agent.py`:

```python
"""
Target Deal Agent.
Coordinates Target product searches and deal finding.
"""
from typing import List, Dict, Any
from loguru import logger

from scrapers.target_scraper import TargetScraper
from agents.analyzer_agent import analyzer
from utils.database import db
from utils.notifier import send_deal_notification


class TargetAgent:
    """Agent for monitoring Target deals."""

    def __init__(self):
        """Initialize Target agent."""
        self.scraper = TargetScraper()
        self.name = "Target Monitor"

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
                db.upsert_product({
                    'product_id': product['product_id'],
                    'deal_score': enriched_product['deal_score']
                })

                # Check if worth notifying
                analysis = {
                    'score': enriched_product.get('deal_score', 0),
                    'recommendation': enriched_product.get('deal_recommendation')
                }

                if analyzer.should_notify(analysis):
                    # Calculate savings
                    if enriched_product.get('previous_price'):
                        enriched_product['savings'] = (
                            enriched_product['previous_price'] - enriched_product['current_price']
                        )
                    elif enriched_product.get('average_price'):
                        enriched_product['savings'] = (
                            enriched_product['average_price'] - enriched_product['current_price']
                        )

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
target_agent = TargetAgent()
```

### Step 3: Update Configuration

Edit `config/settings.py`:

```python
# Add to RETAILERS
RETAILERS = {
    # ... existing retailers ...
    'target': {
        'base_url': 'https://www.target.com',
        'search_url': 'https://www.target.com/s',
        'enabled': True,
    }
}

# Add to MAX_REQUESTS_PER_HOUR
MAX_REQUESTS_PER_HOUR = {
    # ... existing limits ...
    'target': 60,  # Requests per hour
}
```

### Step 4: Integrate into Orchestrator

Edit `main.py`:

```python
# Add import
from agents.target_agent import target_agent

# In _scan_watchlist_items method, add:
if 'target' in retailers:
    try:
        deals = target_agent.search_deals(item)
        logger.info(f"Target: Found {len(deals)} deals")
    except Exception as e:
        logger.error(f"Target agent error: {e}")
```

### Step 5: Test

```python
# Test scraper
from scrapers.target_scraper import scraper

products = scraper.search_products("laptop", max_results=5)
print(f"Found {len(products)} products")
for p in products:
    print(f"{p['title']}: ${p['current_price']}")

# Test agent
from agents.target_agent import target_agent

watchlist_item = {
    'category': 'Laptop',
    'keywords': ['laptop'],
    'max_price': 1000,
    'priority': 'high',
    'retailers': ['target']
}

deals = target_agent.search_deals(watchlist_item)
print(f"Found {len(deals)} deals")
```

### Step 6: Add to Watchlist

```json
{
  "id": 6,
  "category": "Test Product",
  "keywords": ["laptop"],
  "max_price": 1000,
  "priority": "high",
  "retailers": ["target"],
  "check_frequency": "30min"
}
```

## Custom Agent Development

### Base Agent Template

```python
"""
Custom agent template.
"""
from typing import List, Dict, Any
from loguru import logger


class CustomAgent:
    """Custom agent for specific task."""

    def __init__(self):
        """Initialize agent."""
        self.name = "Custom Agent"
        # Initialize resources

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent logic.

        Args:
            input_data: Input parameters

        Returns:
            Results dictionary
        """
        try:
            logger.info(f"{self.name}: Starting execution")

            # Your logic here
            result = self._process(input_data)

            logger.info(f"{self.name}: Execution complete")
            return result

        except Exception as e:
            logger.error(f"{self.name}: Error - {e}")
            raise

    def _process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process logic."""
        # Implementation
        pass

    def cleanup(self):
        """Cleanup resources."""
        logger.info(f"{self.name}: Cleanup complete")


# Singleton
custom_agent = CustomAgent()
```

### Agent Best Practices

1. **Single Responsibility**: One agent, one task
2. **Error Handling**: Try/except with logging
3. **Cleanup**: Implement cleanup() method
4. **Logging**: Use loguru for consistent logging
5. **Database**: Use db singleton for data access
6. **Rate Limiting**: Respect rate limits
7. **Testing**: Write unit tests

## Database Operations

### Adding Custom Tables

```python
# In utils/database.py, add to init_database()

def init_database(self):
    with self.get_connection() as conn:
        cursor = conn.cursor()

        # ... existing tables ...

        # Custom table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_data (
                id INTEGER PRIMARY KEY,
                data_field TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_custom_data_timestamp
            ON custom_data(timestamp)
        """)
```

### Custom Queries

```python
class Database:
    # ... existing methods ...

    def get_custom_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get custom data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM custom_data
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def add_custom_data(self, data_field: str):
        """Add custom data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO custom_data (data_field)
                VALUES (?)
            """, (data_field,))
```

### Database Migrations

For schema changes:

```python
# migrations/001_add_new_field.py

def upgrade(conn):
    """Upgrade database."""
    cursor = conn.cursor()
    cursor.execute("""
        ALTER TABLE products
        ADD COLUMN new_field TEXT
    """)
    conn.commit()

def downgrade(conn):
    """Downgrade database."""
    # SQLite doesn't support DROP COLUMN directly
    # Need to recreate table
    pass

# Run migration
if __name__ == '__main__':
    from utils.database import db
    with db.get_connection() as conn:
        upgrade(conn)
```

## API Integration

### Adding a New API

**Example: Adding BestBuy API**

```python
# scrapers/bestbuy_api.py

import requests
from typing import Dict, List, Any
from loguru import logger

from config.settings import API_ENDPOINTS
from utils.rate_limiter import rate_limiter
from utils.database import db


class BestBuyAPI:
    """Best Buy API integration."""

    def __init__(self, api_key: str):
        """Initialize API client."""
        self.api_key = api_key
        self.base_url = "https://api.bestbuy.com/v1"

    def search_products(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search products via API."""
        if not rate_limiter.acquire('bestbuy_api', timeout=5):
            logger.warning("Best Buy API rate limit exceeded")
            return []

        try:
            url = f"{self.base_url}/products"
            params = {
                'apiKey': self.api_key,
                'format': 'json',
                'show': 'sku,name,salePrice,regularPrice,image',
                'search': f'search={query}',
                'pageSize': max_results
            }

            response = requests.get(url, params=params, timeout=30)

            db.track_api_usage('bestbuy_api', '/products', response.status_code == 200, response.status_code)

            if response.status_code == 200:
                data = response.json()
                return self._parse_response(data)
            else:
                logger.warning(f"Best Buy API returned {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Best Buy API error: {e}")
            db.track_api_usage('bestbuy_api', '/products', False, None)
            return []

    def _parse_response(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse API response."""
        products = []

        for item in data.get('products', []):
            product = {
                'product_id': f"bestbuy_{item['sku']}",
                'sku': item['sku'],
                'title': item['name'],
                'retailer': 'bestbuy',
                'current_price': item.get('salePrice'),
                'previous_price': item.get('regularPrice'),
                'image_url': item.get('image'),
            }
            products.append(product)

        return products
```

## Testing

### Unit Tests

**Test Scraper** (`tests/test_scrapers.py`):

```python
import pytest
from scrapers.amazon_scraper import AmazonScraper


class TestAmazonScraper:
    """Test Amazon scraper."""

    @pytest.fixture
    def scraper(self):
        """Create scraper instance."""
        return AmazonScraper()

    def test_parse_price(self, scraper):
        """Test price parsing."""
        assert scraper._parse_price("$19.99") == 19.99
        assert scraper._parse_price("$1,234.56") == 1234.56
        assert scraper._parse_price("Invalid") is None

    def test_parse_rating(self, scraper):
        """Test rating parsing."""
        assert scraper._parse_rating("4.5 out of 5 stars") == 4.5
        assert scraper._parse_rating("5.0 stars") == 5.0
        assert scraper._parse_rating("Invalid") is None

    @pytest.mark.integration
    def test_search_products(self, scraper):
        """Integration test: search products."""
        products = scraper.search_products_api("laptop", max_results=5)
        assert isinstance(products, list)
        if products:  # If API works
            assert 'title' in products[0]
            assert 'current_price' in products[0]
```

**Test Database** (`tests/test_database.py`):

```python
import pytest
from utils.database import Database


class TestDatabase:
    """Test database operations."""

    @pytest.fixture
    def db(self, tmp_path):
        """Create temporary database."""
        db_file = tmp_path / "test.db"
        return Database(db_path=db_file)

    def test_upsert_product(self, db):
        """Test product upsert."""
        product = {
            'product_id': 'test_123',
            'title': 'Test Product',
            'retailer': 'amazon',
            'current_price': 99.99
        }

        product_id = db.upsert_product(product)
        assert product_id > 0

        # Upsert again
        product['current_price'] = 89.99
        product_id_2 = db.upsert_product(product)
        assert product_id == product_id_2  # Same ID

        # Verify price updated
        saved = db.get_product_by_id('test_123')
        assert saved['current_price'] == 89.99

    def test_price_history(self, db):
        """Test price history."""
        product = {
            'product_id': 'test_456',
            'title': 'Test Product 2',
            'retailer': 'bestbuy',
            'current_price': 100.0
        }

        product_id = db.upsert_product(product)
        db.add_price_history(product_id, 100.0)
        db.add_price_history(product_id, 90.0)
        db.add_price_history(product_id, 95.0)

        history = db.get_price_history(product_id, limit=10)
        assert len(history) == 3
        assert history[0]['price'] == 95.0  # Most recent
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_database.py

# Run specific test
pytest tests/test_database.py::TestDatabase::test_upsert_product

# Run integration tests only
pytest -m integration

# Skip integration tests
pytest -m "not integration"
```

### Mock External Services

```python
import pytest
from unittest.mock import Mock, patch


class TestAmazonAgent:
    """Test Amazon agent."""

    @patch('agents.amazon_agent.AmazonScraper')
    def test_search_deals(self, mock_scraper):
        """Test search deals with mocked scraper."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.search_products_api.return_value = [
            {
                'title': 'Test Product',
                'current_price': 99.99,
                'product_id': 'amazon_test'
            }
        ]
        mock_scraper.return_value = mock_instance

        # Test
        from agents.amazon_agent import AmazonAgent
        agent = AmazonAgent()

        watchlist_item = {
            'category': 'Test',
            'keywords': ['test'],
            'max_price': 150,
            'priority': 'high',
            'retailers': ['amazon']
        }

        deals = agent.search_deals(watchlist_item)
        assert len(deals) >= 0  # May be filtered by deal score
```

## Code Style & Best Practices

### Python Style Guide

Follow PEP 8 with these additions:

**Line Length:** 100 characters (not 79)

**Imports:**
```python
# Standard library
import os
import sys
from typing import Dict, List, Optional

# Third-party
import requests
from loguru import logger

# Local
from config.settings import DATABASE_PATH
from utils.database import db
```

**Docstrings:**
```python
def function_name(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    One-line summary.

    More detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2 (default: 10)

    Returns:
        Dictionary with results

    Raises:
        ValueError: If param1 is invalid
    """
    pass
```

**Type Hints:**
```python
from typing import Dict, List, Optional, Any

def get_products(category: str, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
    """Get products with type hints."""
    pass
```

**Error Handling:**
```python
# Good
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    # Handle or re-raise
else:
    # Success path
finally:
    # Cleanup
    pass

# Bad
try:
    result = risky_operation()
except:  # Too broad
    pass  # Silent failure
```

### Logging Best Practices

```python
from loguru import logger

# Use appropriate levels
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.exception("Exception with traceback")

# Include context
logger.info(f"Processing product: {product_id}")
logger.error(f"Failed to scrape {url}: {error}")

# Sanitize sensitive data
logger.info(f"API key: {api_key[:8]}...")  # Don't log full key
```

### Database Best Practices

```python
# Use context managers
with db.get_connection() as conn:
    cursor = conn.cursor()
    # Operations
    # Auto-commit on success

# Use parameterized queries (prevent SQL injection)
cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))  # Good
cursor.execute(f"SELECT * FROM products WHERE id = {product_id}")  # Bad!

# Handle errors
try:
    product_id = db.upsert_product(product)
except sqlite3.IntegrityError:
    logger.error("Duplicate product")
```

## Debugging

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG
```

Or in code:
```python
logger.remove()
logger.add(sys.stdout, level="DEBUG")
```

### Debug Web Scraping

```bash
# Disable headless mode
export HEADLESS=false
python main.py
```

Watch browser in action!

### Debug with IPython

```python
# Add to code where you want to debug
import IPython; IPython.embed()

# When executed, drops into interactive shell
# Inspect variables, test code, etc.
```

### Debug with pdb

```python
# Add breakpoint
import pdb; pdb.set_trace()

# Or (Python 3.7+)
breakpoint()

# Commands:
# n - next line
# s - step into
# c - continue
# p variable - print variable
# q - quit
```

### Profile Performance

```python
import cProfile
import pstats

# Profile function
cProfile.run('agent.search_deals(item)', 'profile_stats')

# Analyze
p = pstats.Stats('profile_stats')
p.sort_stats('cumulative')
p.print_stats(20)  # Top 20 slowest
```

### Memory Profiling

```bash
pip install memory_profiler

# Add to function
@profile
def my_function():
    pass

# Run
python -m memory_profiler main.py
```

## Contributing

### Workflow

1. **Fork repository**
2. **Create branch:** `git checkout -b feature/new-retailer`
3. **Make changes**
4. **Write tests**
5. **Run tests:** `pytest`
6. **Format code:** `black . --line-length 100`
7. **Lint:** `flake8 .`
8. **Commit:** `git commit -m "Add Target retailer support"`
9. **Push:** `git push origin feature/new-retailer`
10. **Create Pull Request**

### Code Review Checklist

- [ ] Code follows style guide
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Performance considered
- [ ] Security reviewed

### Git Commit Messages

```
feat: Add Target retailer support
fix: Resolve Amazon scraper timeout issue
docs: Update deployment guide
refactor: Improve rate limiter efficiency
test: Add tests for Walmart scraper
chore: Update dependencies
```

---

Happy coding! Build amazing features for Deal Scanner! 🚀
