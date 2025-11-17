# Configuration Reference

Complete guide to configuring the Multi-Retail Deal Scanner system.

## Table of Contents
1. [Environment Variables](#environment-variables)
2. [Settings File](#settings-file)
3. [Watchlist Configuration](#watchlist-configuration)
4. [Scraping Configuration](#scraping-configuration)
5. [Notification Configuration](#notification-configuration)
6. [Rate Limiting](#rate-limiting)
7. [Scheduling](#scheduling)
8. [Advanced Options](#advanced-options)

## Environment Variables

Location: `.env` file in root directory

### Required Variables

**TELEGRAM_BOT_TOKEN**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```
- **Description:** Telegram bot token from @BotFather
- **Format:** Numbers, colon, alphanumeric string
- **Required:** Yes
- **Get it:** Message @BotFather on Telegram → /newbot

**TELEGRAM_CHAT_ID**
```bash
TELEGRAM_CHAT_ID=123456789
```
- **Description:** Your Telegram chat ID
- **Format:** Number (positive or negative)
- **Required:** Yes
- **Get it:** Message @userinfobot on Telegram

### Optional API Keys

**OPENAI_API_KEY**
```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
- **Description:** OpenAI API key for AI deal analysis
- **Format:** Starts with `sk-`
- **Default Behavior:** Uses rule-based analysis if not provided
- **Free Tier:** $5 credit for new accounts
- **Get it:** https://platform.openai.com/api-keys

**RAPIDAPI_KEY**
```bash
RAPIDAPI_KEY=your_rapidapi_key_here
```
- **Description:** RapidAPI key for Amazon product data
- **Free Tier:** 500 requests/month
- **Get it:** https://rapidapi.com/

**SERPAPI_KEY**
```bash
SERPAPI_KEY=your_serpapi_key_here
```
- **Description:** SerpAPI key for Google Shopping
- **Free Tier:** 100 searches/month
- **Get it:** https://serpapi.com/

**RAINFOREST_API_KEY**
```bash
RAINFOREST_API_KEY=your_rainforest_api_key_here
```
- **Description:** Rainforest API key for Amazon data
- **Free Tier:** 100 requests/month
- **Get it:** https://www.rainforestapi.com/

### General Settings

**NOTIFICATIONS_ENABLED**
```bash
NOTIFICATIONS_ENABLED=true
```
- **Description:** Enable/disable Telegram notifications
- **Values:** `true` or `false`
- **Default:** `true`
- **Use Case:** Set to `false` for testing without spam

**HEADLESS**
```bash
HEADLESS=true
```
- **Description:** Run browsers in headless mode (no GUI)
- **Values:** `true` or `false`
- **Default:** `true`
- **Note:** Set to `false` for debugging to see browser

**LOG_LEVEL**
```bash
LOG_LEVEL=INFO
```
- **Description:** Logging verbosity
- **Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`
- **Default:** `INFO`
- **DEBUG:** Very verbose, for development
- **INFO:** Normal operation
- **WARNING:** Only warnings and errors
- **ERROR:** Only errors

### Complete Example

```bash
# .env file

# ============================================
# REQUIRED
# ============================================
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# ============================================
# OPTIONAL - APIs
# ============================================
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
RAPIDAPI_KEY=your_rapidapi_key_here
SERPAPI_KEY=
RAINFOREST_API_KEY=

# ============================================
# GENERAL SETTINGS
# ============================================
NOTIFICATIONS_ENABLED=true
HEADLESS=true
LOG_LEVEL=INFO
```

## Settings File

Location: `config/settings.py`

### Database Configuration

```python
# Database file path
DATABASE_PATH = BASE_DIR / 'deal_scanner.db'
```

**Custom Location:**
```python
import os
DATABASE_PATH = Path(os.getenv('DATABASE_PATH', BASE_DIR / 'deal_scanner.db'))
```

### Logging Configuration

```python
LOG_DIR = BASE_DIR / 'logs'
LOG_FILE = LOG_DIR / 'scanner.log'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

**Log Rotation:**
```python
# In main.py
logger.add(
    LOG_FILE,
    rotation="10 MB",      # Rotate when file reaches 10MB
    retention="7 days",    # Keep logs for 7 days
    compression="zip"      # Compress old logs
)
```

### Rate Limits

```python
MAX_REQUESTS_PER_HOUR = {
    'amazon': 50,        # Web scraping (self-imposed limit)
    'bestbuy': 100,      # More lenient
    'walmart': 80,       # Moderate
    'target': 60,        # If you add Target
    'rapidapi': 500,     # API monthly limit ÷ 30 days ÷ 24 hours
    'serpapi': 100,      # Same calculation
    'rainforest': 100,   # Same calculation
}
```

**Adjust Limits:**
- Increase for less restrictive scanning
- Decrease to be more cautious
- Consider retailer's robots.txt

### Scraping Configuration

```python
SCRAPING_CONFIG = {
    'user_agents': [
        # List of user agents to rotate
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
        # ... more user agents ...
    ],
    'delays': {
        'min': 5,              # Minimum delay between requests (seconds)
        'max': 15,             # Maximum delay
        'between_products': 3, # Delay when processing products
    },
    'retry_logic': {
        'max_retries': 3,      # Number of retries on failure
        'backoff_factor': 2,   # Exponential backoff multiplier
        'initial_wait': 1,     # Initial wait time (seconds)
    },
    'timeout': 30,             # Request timeout (seconds)
    'headless': os.getenv('HEADLESS', 'true').lower() == 'true',
}
```

**Customization Examples:**

**More Aggressive (Faster but riskier):**
```python
SCRAPING_CONFIG = {
    'delays': {
        'min': 2,
        'max': 5,
        'between_products': 1,
    },
    'retry_logic': {
        'max_retries': 2,
    },
    'timeout': 20,
}
```

**More Cautious (Slower but safer):**
```python
SCRAPING_CONFIG = {
    'delays': {
        'min': 10,
        'max': 20,
        'between_products': 5,
    },
    'retry_logic': {
        'max_retries': 5,
        'backoff_factor': 3,
    },
    'timeout': 60,
}
```

### Deal Analysis Configuration

```python
DEAL_ANALYSIS_CONFIG = {
    'min_deal_score': 70,              # Minimum score to notify
    'price_drop_threshold': 0.15,      # 15% minimum price drop
    'weights': {
        'price_vs_historical': 0.40,   # 40% weight
        'product_quality': 0.30,       # 30% weight
        'timing_seasonality': 0.15,    # 15% weight
        'retailer_reputation': 0.15,   # 15% weight
    }
}
```

**Adjustments:**

**Only Exceptional Deals:**
```python
DEAL_ANALYSIS_CONFIG = {
    'min_deal_score': 85,  # Raise threshold
    'price_drop_threshold': 0.25,  # Require 25% drop
}
```

**More Lenient:**
```python
DEAL_ANALYSIS_CONFIG = {
    'min_deal_score': 60,  # Lower threshold
    'price_drop_threshold': 0.10,  # 10% drop OK
}
```

**Prioritize Price Over Quality:**
```python
DEAL_ANALYSIS_CONFIG = {
    'weights': {
        'price_vs_historical': 0.60,   # Increase
        'product_quality': 0.20,       # Decrease
        'timing_seasonality': 0.10,
        'retailer_reputation': 0.10,
    }
}
```

### Notification Configuration

```python
NOTIFICATION_CONFIG = {
    'enabled': os.getenv('NOTIFICATIONS_ENABLED', 'true').lower() == 'true',
    'min_interval_minutes': 30,  # Don't spam same product
    'include_image': True,       # Send product images
}
```

**Adjustments:**

**More Frequent Updates:**
```python
NOTIFICATION_CONFIG = {
    'min_interval_minutes': 15,  # Every 15 minutes
}
```

**Text Only (Faster):**
```python
NOTIFICATION_CONFIG = {
    'include_image': False,  # No images, faster
}
```

### Scheduler Configuration

```python
SCHEDULER_CONFIG = {
    'high_priority_interval': 30,      # Minutes
    'medium_priority_interval': 120,   # Minutes (2 hours)
    'low_priority_interval': 1440,     # Minutes (24 hours)
    'low_priority_time': '09:00',      # Time for daily scan
}
```

**Customization:**

**More Frequent High Priority:**
```python
SCHEDULER_CONFIG = {
    'high_priority_interval': 15,  # Every 15 minutes
}
```

**Less Frequent (Save Resources):**
```python
SCHEDULER_CONFIG = {
    'high_priority_interval': 60,      # Every hour
    'medium_priority_interval': 240,   # Every 4 hours
}
```

### RSS Feeds

```python
RSS_FEEDS = {
    'slickdeals': 'https://slickdeals.net/newsearch.php?rss=1&searchin=first&forumid%5B%5D=9',
    'reddit_buildapcsales': 'https://www.reddit.com/r/buildapcsales/.rss',
    'bestbuy_deals': 'https://www.bestbuy.com/rss/deals',
}
```

**Add More Feeds:**
```python
RSS_FEEDS = {
    # ... existing ...
    'techbargains': 'https://www.techbargains.com/rss',
    'dealnews': 'https://www.dealnews.com/rss/',
    # Reddit categories
    'reddit_laptopdeals': 'https://www.reddit.com/r/LaptopDeals/.rss',
}
```

### Retailer Configuration

```python
RETAILERS = {
    'amazon': {
        'base_url': 'https://www.amazon.com',
        'search_url': 'https://www.amazon.com/s',
        'enabled': True,
    },
    'bestbuy': {
        'base_url': 'https://www.bestbuy.com',
        'top_deals_url': 'https://www.bestbuy.com/site/electronics/top-deals/pcmcat1563299784494.c',
        'deal_of_day_url': 'https://www.bestbuy.com/site/misc/deal-of-the-day/pcmcat248000050016.c',
        'enabled': True,
    },
    'walmart': {
        'base_url': 'https://www.walmart.com',
        'search_url': 'https://www.walmart.com/search',
        'enabled': True,
    },
}
```

**Disable Retailer:**
```python
RETAILERS = {
    'amazon': {
        # ...
        'enabled': False,  # Temporarily disable
    },
}
```

### OpenAI Configuration

```python
OPENAI_CONFIG = {
    'model': 'gpt-3.5-turbo',  # Model to use
    'temperature': 0.3,         # Lower = more consistent
    'max_tokens': 500,          # Response length limit
}
```

**Use GPT-4 (Better but more expensive):**
```python
OPENAI_CONFIG = {
    'model': 'gpt-4',  # More accurate analysis
    'temperature': 0.2,
    'max_tokens': 300,  # Shorter to save costs
}
```

**More Creative Analysis:**
```python
OPENAI_CONFIG = {
    'temperature': 0.7,  # More varied responses
}
```

## Watchlist Configuration

Location: `config/products.json`

### Basic Structure

```json
{
  "watchlist": [
    {
      "id": 1,
      "category": "Product Category",
      "keywords": ["keyword1", "keyword2"],
      "max_price": 500,
      "priority": "high",
      "retailers": ["amazon", "bestbuy"],
      "check_frequency": "30min"
    }
  ]
}
```

### Field Reference

**id** (Integer, Required)
- Unique identifier
- Increment for each item
- Used for tracking

**category** (String, Required)
- Product category name
- For organization and filtering
- Examples: "TV", "Laptop", "Baby Stroller"

**keywords** (Array of Strings, Required)
- Search terms
- Matches ANY keyword (OR logic)
- Case-insensitive
- Examples: `["65 inch", "4K", "OLED"]`

**max_price** (Number, Optional)
- Maximum price threshold
- Products above this are ignored
- Can be decimal: `999.99`
- Omit for no limit

**priority** (String, Required)
- Scan frequency
- Values:
  - `"high"` - Every 30 minutes
  - `"medium"` - Every 2 hours
  - `"low"` - Once daily
- Affects resource usage

**retailers** (Array of Strings, Required)
- Which stores to check
- Values: `"amazon"`, `"bestbuy"`, `"walmart"`
- Can include all or subset

**check_frequency** (String, Optional)
- For documentation only
- Actual frequency determined by priority
- Examples: `"30min"`, `"2hours"`, `"daily"`

### Examples by Use Case

**Time-Sensitive Deal (Stock Issues):**
```json
{
  "id": 1,
  "category": "PS5 Console",
  "keywords": ["playstation 5", "ps5", "playstation 5 console"],
  "max_price": 550,
  "priority": "high",
  "retailers": ["amazon", "bestbuy", "walmart"],
  "check_frequency": "30min"
}
```

**Regular Monitoring:**
```json
{
  "id": 2,
  "category": "Coffee Maker",
  "keywords": ["keurig", "coffee maker", "k-cup"],
  "max_price": 150,
  "priority": "medium",
  "retailers": ["amazon", "walmart"],
  "check_frequency": "2hours"
}
```

**Patient Search:**
```json
{
  "id": 3,
  "category": "Office Chair",
  "keywords": ["ergonomic chair", "office chair", "herman miller"],
  "max_price": 500,
  "priority": "low",
  "retailers": ["amazon"],
  "check_frequency": "daily"
}
```

**Specific Model:**
```json
{
  "id": 4,
  "category": "Laptop",
  "keywords": ["macbook pro m3", "macbook pro 14", "m3 pro"],
  "max_price": 1800,
  "priority": "high",
  "retailers": ["amazon", "bestbuy"],
  "check_frequency": "30min"
}
```

**Broad Category:**
```json
{
  "id": 5,
  "category": "Baby Products",
  "keywords": ["baby stroller", "crib", "car seat", "baby monitor"],
  "max_price": 300,
  "priority": "medium",
  "retailers": ["amazon", "walmart"],
  "check_frequency": "2hours"
}
```

### Keyword Strategy

**Good Keywords:**
- Specific model numbers: `"RTX 4060"`, `"i7-13700H"`
- Brand + product: `"Samsung QLED"`, `"LG OLED"`
- Size/specs: `"65 inch"`, `"16GB RAM"`

**Bad Keywords:**
- Too generic: `"laptop"`, `"tv"`
- Too many words: `"gaming laptop with RTX 4060 and 16GB RAM"`
- Overly specific: `"Samsung QN65Q80CAFXZA"` (use model series instead)

**Multiple Variations:**
```json
"keywords": [
  "airpods pro",
  "airpods pro 2",
  "apple airpods pro",
  "airpods pro 2nd generation"
]
```

### Priority Guidelines

**Use High Priority (30min) For:**
- Limited stock items
- Flash sales
- High-demand products
- Price-volatile items

**Use Medium Priority (2hr) For:**
- Regular electronics
- Seasonal items
- General monitoring
- Most products

**Use Low Priority (Daily) For:**
- Staples/consumables
- Non-urgent purchases
- Price-stable products
- "Nice to have" items

## Advanced Options

### Custom Scheduling

Edit `main.py` to add custom schedules:

```python
# Run specific scan on Mondays at 10 AM
schedule.every().monday.at("10:00").do(run_high_priority_scan)

# Run every Friday
schedule.every().friday.do(run_aggregator_scan)

# Run every N days
schedule.every(3).days.do(cleanup_old_data)
```

### Environment-Specific Configs

**Development:**
```bash
# .env.dev
NOTIFICATIONS_ENABLED=false
HEADLESS=false
LOG_LEVEL=DEBUG
```

**Production:**
```bash
# .env.prod
NOTIFICATIONS_ENABLED=true
HEADLESS=true
LOG_LEVEL=INFO
```

**Load specific environment:**
```bash
export ENV=dev
python main.py
```

```python
# In settings.py
import os
env = os.getenv('ENV', 'prod')
load_dotenv(f'.env.{env}')
```

### Multi-Instance Configuration

**Instance 1:**
```bash
export INSTANCE_ID=0
export TOTAL_INSTANCES=2
export DATABASE_PATH=scanner_1.db
python main.py
```

**Instance 2:**
```bash
export INSTANCE_ID=1
export TOTAL_INSTANCES=2
export DATABASE_PATH=scanner_2.db
python main.py
```

### Performance Tuning

**Low-Resource System (Raspberry Pi):**
```python
# config/settings.py
MAX_REQUESTS_PER_HOUR = {
    'amazon': 30,   # Reduce
    'bestbuy': 50,
    'walmart': 40,
}

SCRAPING_CONFIG = {
    'delays': {
        'min': 8,
        'max': 15,
    },
}

# Limit max results
# In agents:
products = scraper.search_products(keywords, max_results=5)
```

**High-Resource System:**
```python
MAX_REQUESTS_PER_HOUR = {
    'amazon': 100,   # Increase
    'bestbuy': 200,
    'walmart': 150,
}

SCRAPING_CONFIG = {
    'delays': {
        'min': 2,
        'max': 5,
    },
}

# More results
products = scraper.search_products(keywords, max_results=30)
```

### Logging Configuration

**Console and File:**
```python
# main.py
logger.add(sys.stdout, level="INFO")
logger.add(LOG_FILE, level="DEBUG", rotation="10 MB")
```

**JSON Logging (for parsing):**
```python
logger.add(
    "logs/scanner.json",
    format="{time} {level} {message}",
    serialize=True,  # JSON format
    rotation="10 MB"
)
```

**Separate Error Log:**
```python
logger.add(
    "logs/errors.log",
    level="ERROR",
    rotation="1 day"
)
```

### Database Configuration

**Custom Path:**
```python
# Environment variable
export DATABASE_PATH=/path/to/custom.db

# Or in code
DATABASE_PATH = Path('/path/to/custom.db')
```

**In-Memory (Testing):**
```python
DATABASE_PATH = ':memory:'
```

**Read-Only Mode:**
```python
conn = sqlite3.connect(f'file:{DATABASE_PATH}?mode=ro', uri=True)
```

---

## Configuration Checklist

Before running in production:

- [ ] Telegram credentials configured
- [ ] Watchlist customized
- [ ] Priorities set appropriately
- [ ] Rate limits reasonable
- [ ] Notifications enabled
- [ ] Log level appropriate
- [ ] Headless mode enabled
- [ ] API keys added (if using)
- [ ] Deal score threshold set
- [ ] Schedule reviewed

## Quick Reference

**Change Scan Frequency:**
→ Edit `config/settings.py` → `SCHEDULER_CONFIG`

**Add Product:**
→ Edit `config/products.json` → Add to `watchlist` array

**Change Notification Threshold:**
→ Edit `config/settings.py` → `DEAL_ANALYSIS_CONFIG['min_deal_score']`

**Disable Retailer:**
→ Edit `config/settings.py` → `RETAILERS[retailer]['enabled'] = False`

**Change Log Level:**
→ Edit `.env` → `LOG_LEVEL=DEBUG`

**Disable Notifications:**
→ Edit `.env` → `NOTIFICATIONS_ENABLED=false`

---

This configuration system is designed to be flexible. Start with defaults and adjust based on your needs!
