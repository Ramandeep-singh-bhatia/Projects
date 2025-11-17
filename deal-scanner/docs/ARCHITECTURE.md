# Architecture & Design Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Patterns](#architecture-patterns)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [Agent System](#agent-system)
7. [Scalability Considerations](#scalability-considerations)
8. [Security & Privacy](#security--privacy)

## System Overview

### Purpose
The Multi-Retail Deal Scanner is an autonomous AI-agent system designed to continuously monitor multiple e-commerce retailers for product deals, analyze deal quality using AI, and notify users via Telegram when significant deals are found.

### Design Goals
1. **Automation**: Run 24/7 without human intervention
2. **Cost Efficiency**: Use only free APIs and tools
3. **Reliability**: Handle errors gracefully and continue operation
4. **Scalability**: Support multiple users and products
5. **Intelligence**: AI-powered deal quality assessment
6. **Modularity**: Easy to add new retailers or features

### Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Language: Python 3.11+                                      │
│  Framework: LangChain/LangGraph (Agent Orchestration)        │
│  Scheduler: schedule library                                 │
│  Logging: loguru                                             │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│  Database: SQLite3 (local)                                   │
│  ORM: Native sqlite3 with context managers                   │
│  Caching: In-memory rate limiter buckets                     │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Web Scraping: Selenium + BeautifulSoup4                     │
│  HTTP Clients: requests, httpx, aiohttp                      │
│  APIs: OpenAI, RapidAPI, SerpAPI, Rainforest API             │
│  Notifications: python-telegram-bot                          │
│  RSS Parsing: feedparser                                     │
└─────────────────────────────────────────────────────────────┘
```

## Architecture Patterns

### 1. Multi-Agent Architecture

The system follows a **Multi-Agent System (MAS)** design pattern where autonomous agents work independently but coordinate through a central orchestrator.

```
┌──────────────────────────────────────────────────────────────┐
│                     Orchestrator                              │
│                     (main.py)                                 │
│  - Manages agent lifecycle                                    │
│  - Schedules tasks                                            │
│  - Coordinates inter-agent communication                      │
└────────┬─────────────────────────────────────────────────────┘
         │
         ├─────────────┬──────────────┬──────────────┬─────────
         ▼             ▼              ▼              ▼
    ┌────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐
    │Amazon  │   │Best Buy  │   │Walmart  │   │Aggregator│
    │Agent   │   │Agent     │   │Agent    │   │Agent     │
    └───┬────┘   └────┬─────┘   └────┬────┘   └─────┬────┘
        │             │              │              │
        └─────────────┴──────────────┴──────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │  Analyzer    │
                   │  Agent (AI)  │
                   └──────┬───────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
       ┌────────┐   ┌─────────┐   ┌─────────┐
       │Database│   │Notifier │   │Rate     │
       │        │   │         │   │Limiter  │
       └────────┘   └─────────┘   └─────────┘
```

**Agent Responsibilities:**

- **Amazon Agent**: Searches Amazon using APIs + scraping, extracts product data
- **Best Buy Agent**: Scrapes Best Buy product pages and deals
- **Walmart Agent**: Monitors Walmart products and clearance
- **Aggregator Agent**: Parses RSS feeds from deal aggregators
- **Analyzer Agent**: Evaluates deal quality using AI and rules

### 2. Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation Layer (Telegram Bot)                           │
│  - Formats and sends notifications                           │
│  - User interaction interface                                │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Business Logic Layer (Agents)                               │
│  - Deal discovery logic                                      │
│  - Deal analysis and scoring                                 │
│  - Decision making (notify/skip)                             │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Data Access Layer (Scrapers)                                │
│  - Web scraping implementation                               │
│  - API integration                                           │
│  - Data extraction and parsing                               │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  Infrastructure Layer (Utils)                                │
│  - Database operations                                       │
│  - Rate limiting                                             │
│  - Logging and monitoring                                    │
└─────────────────────────────────────────────────────────────┘
```

### 3. Repository Pattern

Database operations are abstracted through a repository pattern with context managers:

```python
# Context manager ensures proper connection handling
with db.get_connection() as conn:
    cursor = conn.cursor()
    # Operations
    cursor.execute(...)
    # Auto-commit on success, rollback on error
```

### 4. Strategy Pattern

Scraping strategies are interchangeable:

```python
# Try API first
products = scraper.search_products_api(keywords)

# Fallback to scraping strategy
if not products:
    products = scraper.search_products_scrape(keywords)
```

## Component Design

### Main Orchestrator (`main.py`)

**Responsibilities:**
- Initialize all agents
- Load watchlist configuration
- Schedule periodic tasks
- Handle graceful shutdown
- Coordinate agent execution
- Send status reports

**Key Methods:**
```python
class DealScannerOrchestrator:
    def __init__(self)
    def _load_watchlist() -> List[Dict]
    def setup_scheduler() -> None
    def run_high_priority_scan() -> None
    def run_medium_priority_scan() -> None
    def run_low_priority_scan() -> None
    def run_aggregator_scan() -> None
    def run() -> None  # Main loop
```

**Scheduling Logic:**
```python
# Priority-based scheduling
schedule.every(30).minutes.do(run_high_priority_scan)    # High
schedule.every(120).minutes.do(run_medium_priority_scan) # Medium
schedule.every().day.at("09:00").do(run_low_priority_scan) # Low

# Specialized scans
schedule.every(60).minutes.do(run_aggregator_scan)       # RSS
schedule.every().day.at("20:00").do(send_status_report)  # Reports
```

### Agents Layer

#### Amazon Agent (`agents/amazon_agent.py`)

**Purpose:** Discover deals on Amazon using multiple data sources

**Data Sources:**
1. RapidAPI (Real-Time Amazon Data API) - Primary
2. Rainforest API - Backup
3. Web Scraping (Selenium) - Fallback

**Algorithm:**
```
FOR each watchlist item:
    1. Try RapidAPI search
    2. IF quota exceeded OR no results:
        Try web scraping
    3. FOR each product found:
        a. Filter by max_price
        b. Save to database
        c. Update price history
        d. Get historical data
        e. Analyze deal quality (AI)
        f. IF deal_score >= 70:
            Send notification
```

**Error Handling:**
- API failures → fallback to scraping
- Scraping failures → log and continue
- CAPTCHA detection → skip and retry later
- Rate limiting → automatic backoff

#### Best Buy Agent (`agents/bestbuy_agent.py`)

**Purpose:** Monitor Best Buy deals and products

**Capabilities:**
- Search by keywords
- Scrape "Top Deals" page
- Scrape "Deal of the Day" page
- Detect open-box deals

**Scraping Strategy:**
```
1. Load page with Selenium
2. Wait for dynamic content (JavaScript)
3. Scroll page to trigger lazy loading
4. Parse with BeautifulSoup
5. Extract: SKU, title, price, savings, rating
6. Detect special conditions (open-box)
```

#### Walmart Agent (`agents/walmart_agent.py`)

**Purpose:** Track Walmart products and clearance items

**Special Features:**
- Rollback detection (special Walmart promotion)
- Clearance section monitoring
- Deal score boost for clearance (+15) and rollback (+10)

**Selectors Used:**
```python
# Product items
items = soup.select("[data-item-id]")

# Rollback badge
rollback = item.select_one('[data-automation-id="product-badge-rollback"]')

# Price
price = item.select_one('[data-automation-id="product-price"]')
```

#### Aggregator Agent (`agents/aggregator_agent.py`)

**Purpose:** Monitor curated deal sources

**RSS Feeds:**
1. Slickdeals (electronics)
2. Reddit r/buildapcsales
3. Best Buy deals RSS (if available)

**Processing:**
```
FOR each RSS feed:
    1. Parse feed with feedparser
    2. Extract: title, link, description
    3. Extract price from text (regex)
    4. Match against watchlist keywords
    5. IF matches AND price <= max_price:
        Save and analyze
    6. Add 5-point boost (curated source)
```

#### Analyzer Agent (`agents/analyzer_agent.py`)

**Purpose:** Evaluate deal quality using AI and rules

**Scoring Algorithm:**

**AI-Powered (OpenAI):**
```python
prompt = f"""
Analyze this deal and score 0-100:
Product: {title}
Current: ${current_price}
Average: ${avg_price}
Low: ${lowest_price}
Rating: {rating}/5 ({review_count} reviews)

Weights:
- Price vs history: 40%
- Quality/reviews: 30%
- Timing: 15%
- Retailer: 15%

Return JSON: {{"score": X, "reasoning": "...", "recommendation": "BUY_NOW|WAIT"}}
"""
```

**Rule-Based (Fallback):**
```python
score = 0

# 1. Price Analysis (40 points)
if current_price <= lowest_price:
    score += 40  # Historical low
elif current_price <= avg_price * 0.70:
    score += 35  # 30%+ discount

# 2. Quality (30 points)
if rating >= 4.5:
    score += 30
elif rating >= 4.0:
    score += 25

# Adjust for review count
if review_count >= 1000:
    score += 5

# 3. Timing (15 points)
score += 10  # Base score

# 4. Retailer (15 points)
if retailer in ['amazon', 'bestbuy', 'walmart']:
    score += 15

# Recommendation
if score >= 80: return "BUY_NOW"
elif score >= 70: return "GOOD_DEAL"
elif score >= 50: return "CONSIDER"
else: return "WAIT"
```

### Scrapers Layer

#### Amazon Scraper (`scrapers/amazon_scraper.py`)

**API Integration:**
```python
# RapidAPI request
headers = {
    'X-RapidAPI-Key': RAPIDAPI_KEY,
    'X-RapidAPI-Host': 'real-time-amazon-data.p.rapidapi.com'
}

response = requests.get(
    'https://real-time-amazon-data.p.rapidapi.com/search',
    headers=headers,
    params={'query': keywords, 'country': 'US'}
)
```

**Web Scraping:**
```python
# Selenium setup
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f'user-agent={random_user_agent}')

driver = webdriver.Chrome(options=options)

# Anti-detection
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": ua_rotator.get_random_user_agent()
})
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)
```

**Data Extraction:**
```python
# Search results
items = soup.select("[data-component-type='s-search-result']")

for item in items:
    asin = item.get('data-asin')
    title = item.select_one('h2 a span').text
    price = item.select_one('.a-price .a-offscreen').text
    rating = item.select_one('.a-icon-star-small .a-icon-alt').text
```

#### Best Buy Scraper (`scrapers/bestbuy_scraper.py`)

**Page Loading Strategy:**
```python
# Wait for dynamic content
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CLASS_NAME, "sku-item"))
)

# Scroll to load lazy content
for i in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
```

**Selectors:**
```python
items = soup.select(".sku-item")

for item in items:
    sku = item.get('data-sku-id')
    title = item.select_one('.sku-title a').text
    price = item.select_one('.priceView-customer-price span').text
    original = item.select_one('.pricing-price__regular-price').text
    condition = 'Open Box' if item.select_one('.open-box-option') else 'New'
```

#### Walmart Scraper (`scrapers/walmart_scraper.py`)

**Challenges:**
- Heavy JavaScript rendering
- Anti-bot protection
- Dynamic element IDs

**Solutions:**
```python
# Longer wait times for JS
time.sleep(3)

# Multiple scroll passes
for i in range(3):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1.5)

# Flexible selectors
price_elem = item.select_one('[data-automation-id="product-price"]')
if not price_elem:
    price_elem = item.select_one('.price-characteristic')
```

### Utilities Layer

#### Database (`utils/database.py`)

**Schema Design:**

```sql
-- Products table
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    product_id TEXT UNIQUE,          -- Composite: "retailer_sku"
    asin TEXT,                       -- Amazon-specific
    sku TEXT,                        -- Retailer SKU
    title TEXT NOT NULL,
    category TEXT,
    retailer TEXT NOT NULL,
    url TEXT,
    image_url TEXT,
    current_price REAL,
    lowest_price REAL,               -- Historical low
    highest_price REAL,              -- Historical high
    average_price REAL,              -- Rolling average
    rating REAL,
    review_count INTEGER,
    availability TEXT,
    last_checked TIMESTAMP,
    deal_score INTEGER,              -- 0-100
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Price history
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    price REAL NOT NULL,
    availability TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Notifications log
CREATE TABLE notifications_sent (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    price REAL NOT NULL,
    deal_score INTEGER,
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Watchlist
CREATE TABLE watchlist (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,
    keywords TEXT NOT NULL,          -- JSON array
    max_price REAL,
    priority TEXT DEFAULT 'medium',  -- high/medium/low
    retailers TEXT NOT NULL,         -- JSON array
    check_frequency TEXT,
    active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking
CREATE TABLE api_usage (
    id INTEGER PRIMARY KEY,
    api_name TEXT NOT NULL,
    endpoint TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN,
    response_code INTEGER
);
```

**Indices:**
```sql
CREATE INDEX idx_products_retailer ON products(retailer);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_price_history_product ON price_history(product_id, timestamp);
CREATE INDEX idx_api_usage_timestamp ON api_usage(api_name, timestamp);
```

**Key Operations:**
```python
# Upsert pattern
def upsert_product(product_data):
    existing = cursor.execute("SELECT id FROM products WHERE product_id = ?",
                              (product_data['product_id'],)).fetchone()
    if existing:
        _update_product(existing[0], product_data)
    else:
        _insert_product(product_data)

# Price history aggregation
avg_price = cursor.execute(
    "SELECT AVG(price) FROM price_history WHERE product_id = ?",
    (product_id,)
).fetchone()[0]
```

#### Rate Limiter (`utils/rate_limiter.py`)

**Token Bucket Algorithm:**

```
┌─────────────────────────────────────┐
│  Bucket Capacity: max_requests/hour │
│                                     │
│  Tokens: ████████░░░░░░░░░░         │  (40/100)
│                                     │
│  Refill Rate: max_requests/3600 s   │
└─────────────────────────────────────┘

On Request:
  IF tokens >= 1:
    tokens -= 1
    return True (allow)
  ELSE:
    wait OR return False (deny)

Every Second:
  tokens += refill_rate
  tokens = min(tokens, max_capacity)
```

**Implementation:**
```python
class RateLimiter:
    def _refill_bucket(self, bucket):
        now = datetime.now()
        elapsed = (now - bucket['last_refill']).total_seconds()
        new_tokens = elapsed * bucket['refill_rate']
        bucket['tokens'] = min(bucket['max_tokens'],
                              bucket['tokens'] + new_tokens)
        bucket['last_refill'] = now

    def acquire(self, api_name, timeout=60):
        # Check database for hard limit
        usage = db.get_api_usage_count(api_name, hours=1)
        if usage >= MAX_REQUESTS_PER_HOUR[api_name]:
            return False

        # Try to get token from bucket
        return self.wait_for_token(api_name, timeout)
```

**Rate Limits:**
```python
MAX_REQUESTS_PER_HOUR = {
    'amazon': 50,        # Web scraping limit
    'bestbuy': 100,      # More lenient
    'walmart': 80,
    'rapidapi': 500,     # Monthly / 30 / 24 ≈ 0.7/hour
    'serpapi': 100,      # Monthly / 30 / 24 ≈ 0.14/hour
    'rainforest': 100,
}
```

#### Notifier (`utils/notifier.py`)

**Telegram Integration:**

```python
import asyncio
from telegram import Bot

class TelegramNotifier:
    async def send_deal_alert(self, product_data, product_id):
        # Check recent notifications
        if db.was_notified_recently(product_id, minutes=30):
            return False

        # Format message
        message = self.format_deal_alert(product_data)

        # Send with image
        if product_data.get('image_url'):
            await self.bot.send_photo(
                chat_id=self.chat_id,
                photo=product_data['image_url'],
                caption=message,
                parse_mode='HTML'
            )
        else:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='HTML'
            )

        # Log notification
        db.add_notification(product_id, price, deal_score, message)
```

**Message Format:**
```html
<b>DEAL ALERT!</b>

<b>Samsung 65" QLED 4K Smart TV</b>

<b>Retailer:</b> Best Buy
<b>Current Price:</b> $699.99
<b>Was:</b> $999.99
<b>You Save:</b> $300.00 (30% off)

<b>Deal Score:</b> 85/100
<b>Historical Low:</b> $649.99

<b>Rating:</b> ⭐⭐⭐⭐⭐ (4.7/5)
<b>Reviews:</b> 1,234

<b>Status:</b> ✅ In Stock

<a href='https://bestbuy.com/...'>View Deal</a>

⚡ <i>Act Fast! Deals expire quickly.</i>
```

#### Proxy Rotator (`utils/proxy_rotator.py`)

**User Agent Management:**

```python
class UserAgentRotator:
    def __init__(self):
        self.custom_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...',
            # ... 10+ user agents
        ]

    def get_random_user_agent(self):
        return random.choice(self.custom_agents)

    def get_headers(self, retailer=None):
        headers = {
            'User-Agent': self.get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,...',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            # ... more headers
        }

        # Customize per retailer
        if retailer == 'amazon':
            headers.update({
                'Sec-Fetch-User': '?1',
            })

        return headers
```

**Selenium Anti-Detection:**
```python
def get_selenium_options(self, headless=True):
    options = [
        '--disable-blink-features=AutomationControlled',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--no-sandbox',
        f'user-agent={self.get_random_user_agent()}',
        '--disable-infobars',
        '--disable-notifications',
    ]

    if headless:
        options.append('--headless=new')

    return options

# In scraper
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)
```

## Data Flow

### Complete Deal Discovery Flow

```
1. SCHEDULER TRIGGERS
   ↓
2. ORCHESTRATOR selects watchlist items by priority
   ↓
3. FOR EACH RETAILER in watchlist_item.retailers:
   ↓
4. AGENT searches for products
   ├─ Try API (if quota available)
   │  ├─ Check rate limiter
   │  ├─ Make API request
   │  └─ Track usage in DB
   └─ Fallback to web scraping
      ├─ Get user agent
      ├─ Apply rate limiting
      ├─ Load page with Selenium
      └─ Parse with BeautifulSoup
   ↓
5. FOR EACH PRODUCT found:
   ↓
6. FILTER by max_price
   ↓
7. DATABASE upsert
   ├─ Insert if new
   └─ Update if exists
       └─ Recalculate lowest/highest/average
   ↓
8. ADD PRICE HISTORY entry
   ↓
9. RETRIEVE historical data
   ↓
10. ANALYZER evaluates deal
    ├─ Calculate price score (40%)
    ├─ Calculate quality score (30%)
    ├─ Calculate timing score (15%)
    └─ Calculate retailer score (15%)
    ↓
11. IF deal_score >= 70:
    ↓
12. CHECK if notified recently
    ↓
13. IF NOT notified:
    ↓
14. FORMAT notification message
    ↓
15. SEND via Telegram
    ↓
16. LOG notification in DB
    ↓
17. RETURN to step 5 (next product) or step 3 (next retailer)
```

### RSS Feed Flow

```
1. SCHEDULER triggers hourly
   ↓
2. AGGREGATOR AGENT starts
   ↓
3. FOR EACH RSS feed:
   ↓
4. PARSE feed with feedparser
   ↓
5. FOR EACH entry (limit 50):
   ↓
6. EXTRACT price from title/description (regex)
   ↓
7. MATCH against watchlist keywords
   ↓
8. IF matches AND price <= max_price:
   ↓
9. CREATE product object
   ├─ product_id: "feed_hash(url)"
   ├─ title: from feed
   ├─ price: extracted
   ├─ url: from feed
   └─ retailer: detected from text
   ↓
10. SAVE to database
    ↓
11. ANALYZE deal (+ 5 point curated bonus)
    ↓
12. IF deal_score >= 70:
    └─ NOTIFY user
```

## Database Schema

### Entity Relationship Diagram

```
┌──────────────────┐
│    watchlist     │
└────────┬─────────┘
         │ 1
         │
         │ N
         ▼
┌──────────────────┐        ┌──────────────────┐
│    products      │───────▶│  price_history   │
└────────┬─────────┘ 1    N └──────────────────┘
         │ 1
         │
         │ N
         ▼
┌──────────────────┐
│notifications_sent│
└──────────────────┘

┌──────────────────┐
│   api_usage      │  (Independent tracking table)
└──────────────────┘
```

### Data Relationships

**Products ← Price History** (One-to-Many)
- One product has many price history entries
- Used for: trending, average calculation, deal detection

**Products ← Notifications** (One-to-Many)
- One product can trigger many notifications
- Used for: preventing spam, tracking user engagement

**Watchlist → Products** (Logical, not enforced)
- Watchlist items guide product discovery
- No foreign key (products can exist without watchlist)

## Agent System

### Agent Communication Pattern

**Direct Communication:**
```
Retailer Agents → Analyzer Agent → Notifier
```

**Shared State:**
```
All Agents → Database ← All Agents
```

**No Inter-Agent Communication:**
- Agents don't communicate directly with each other
- All coordination through orchestrator
- Shared state only via database
- This allows parallel execution

### Agent Lifecycle

```
INIT Phase:
  1. Orchestrator creates agent instances
  2. Agents initialize scrapers
  3. Database connection established

RUN Phase:
  1. Orchestrator calls agent.search_deals(watchlist_item)
  2. Agent executes search
  3. Agent processes each product
  4. Agent calls analyzer for each product
  5. Agent triggers notifications
  6. Agent returns results

CLEANUP Phase:
  1. Signal handler catches SIGTERM/SIGINT
  2. Orchestrator calls agent.cleanup()
  3. Agents close WebDriver sessions
  4. Database connections closed
```

### Error Recovery

**Agent-Level:**
```python
try:
    deals = amazon_agent.search_deals(item)
except Exception as e:
    logger.error(f"Amazon agent error: {e}")
    # Continue to next agent
```

**Product-Level:**
```python
for product in products:
    try:
        # Process product
    except Exception as e:
        logger.error(f"Error processing product: {e}")
        continue  # Skip to next product
```

**Request-Level:**
```python
@retry(stop=stop_after_attempt(3),
       wait=wait_exponential(multiplier=1, min=2, max=10))
def search_products_scrape(keywords):
    # Automatic retry with backoff
```

## Scalability Considerations

### Current Limitations

1. **Single Instance**: Designed to run on one machine
2. **SQLite**: Not suitable for concurrent writes from multiple processes
3. **Sequential Processing**: Products processed one at a time per agent
4. **Memory**: All watchlist items loaded into memory

### Scaling Strategies

**Horizontal Scaling (Multi-Instance):**

```python
# Partition watchlist by hash
instance_id = int(os.getenv('INSTANCE_ID', 0))
total_instances = int(os.getenv('TOTAL_INSTANCES', 1))

watchlist_partition = [
    item for i, item in enumerate(watchlist)
    if i % total_instances == instance_id
]
```

**Database Scaling:**

```python
# Option 1: PostgreSQL
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@localhost/dealdb')

# Option 2: Distributed SQLite (litefs)
# Run multiple read-only replicas

# Option 3: Redis cache
import redis
cache = redis.Redis(host='localhost', port=6379)
cache.set(f'product:{product_id}', json.dumps(product), ex=3600)
```

**Parallel Processing:**

```python
from concurrent.futures import ThreadPoolExecutor

def scan_retailer(retailer, item):
    agent = AGENT_MAP[retailer]
    return agent.search_deals(item)

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [
        executor.submit(scan_retailer, retailer, item)
        for retailer in item['retailers']
    ]
    results = [f.result() for f in futures]
```

**Queue-Based Architecture:**

```
┌──────────┐      ┌───────┐      ┌────────────┐
│Scheduler │─────▶│ Queue │─────▶│   Workers  │
└──────────┘      │(Redis)│      │  (N instances)│
                  └───────┘      └────────────┘
                                       │
                                       ▼
                                 ┌──────────┐
                                 │PostgreSQL│
                                 └──────────┘
```

**Caching Strategy:**

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_product_cached(product_id):
    return db.get_product_by_id(product_id)

# Or use Redis
def get_product_cached(product_id):
    cached = redis.get(f'product:{product_id}')
    if cached:
        return json.loads(cached)

    product = db.get_product_by_id(product_id)
    redis.setex(f'product:{product_id}', 3600, json.dumps(product))
    return product
```

## Security & Privacy

### API Key Management

**Environment Variables:**
```bash
# Never commit .env file
# Use .env.example as template
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
TELEGRAM_BOT_TOKEN=1234567890:ABCdefgh...
```

**Key Rotation:**
```python
# Support multiple keys for rotation
OPENAI_KEYS = os.getenv('OPENAI_API_KEYS', '').split(',')
current_key_index = 0

def get_api_key():
    global current_key_index
    key = OPENAI_KEYS[current_key_index]
    current_key_index = (current_key_index + 1) % len(OPENAI_KEYS)
    return key
```

### Data Privacy

**PII Handling:**
- No user data stored (single-user system)
- Telegram chat ID in env vars only
- No logging of sensitive data

**Database Security:**
```python
# File permissions
os.chmod(DATABASE_PATH, 0o600)  # Owner read/write only

# Encryption at rest (optional)
from sqlcipher3 import dbapi2 as sqlite
conn = sqlite.connect('deal_scanner.db')
conn.execute("PRAGMA key='your-secret-key'")
```

### Web Scraping Ethics

**Rate Limiting:**
- Respect robots.txt
- Delay between requests (5-15s)
- Max requests per hour enforced
- Randomized delays to appear human

**User Agent:**
- Identify as browser, not bot
- Rotate user agents
- Don't overwhelm servers

**Legal Compliance:**
- Personal use only
- Don't redistribute data
- Follow retailer ToS
- Public data only

### Error Logging

**Sanitize Logs:**
```python
def sanitize_for_log(data):
    sensitive_keys = ['api_key', 'token', 'password', 'chat_id']
    if isinstance(data, dict):
        return {
            k: '***REDACTED***' if k in sensitive_keys else v
            for k, v in data.items()
        }
    return data

logger.info(f"Config: {sanitize_for_log(config)}")
```

**Log Rotation:**
```python
logger.add(
    LOG_FILE,
    rotation="10 MB",      # Rotate at 10MB
    retention="7 days",    # Keep for 7 days
    compression="zip"      # Compress old logs
)
```

---

## Performance Considerations

### Memory Usage

**Current Profile:**
- Watchlist: ~5KB (100 items)
- Product cache: ~1MB (1000 products)
- WebDriver: ~100-200MB per instance
- Total: ~300MB typical

**Optimization:**
```python
# Process in batches
for batch in chunks(products, 10):
    process_batch(batch)
    # Clear memory
    del batch
    gc.collect()
```

### CPU Usage

**Bottlenecks:**
- BeautifulSoup parsing
- Selenium page loads
- AI analysis (OpenAI API calls)

**Solutions:**
- Parse only necessary elements
- Reuse WebDriver sessions
- Batch AI analysis
- Use faster parsers (lxml vs html.parser)

### Network Usage

**Bandwidth:**
- ~1MB per product page
- ~50KB per API request
- ~10KB per Telegram message

**Monthly Estimate:**
- 20 products × 3 retailers × 48 checks/day × 30 days = 86,400 requests
- At 1MB avg: ~86GB/month (if all scraping)
- At 50KB avg: ~4.3GB/month (if all API)

---

This architecture document provides the complete technical foundation for understanding, maintaining, and extending the Deal Scanner system.
