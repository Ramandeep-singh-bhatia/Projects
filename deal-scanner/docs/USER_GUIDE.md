# User Guide - Multi-Retail Deal Scanner

## Table of Contents
1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Scanner](#running-the-scanner)
5. [Understanding Notifications](#understanding-notifications)
6. [Managing Your Watchlist](#managing-your-watchlist)
7. [Monitoring & Logs](#monitoring--logs)
8. [Tips for Best Results](#tips-for-best-results)
9. [Common Tasks](#common-tasks)
10. [FAQ](#faq)

## Getting Started

### What is Deal Scanner?

Deal Scanner is an automated system that monitors online retailers 24/7 for deals on products you care about. When it finds a great deal (verified by AI), it sends you a Telegram message instantly.

### How It Works (Simple Version)

```
You set up watchlist → Scanner checks stores → AI analyzes deals → You get notified
```

### Prerequisites

Before you begin, you'll need:

1. **Computer Requirements:**
   - Windows 10+, macOS 10.14+, or Linux
   - 2GB free RAM
   - 500MB free disk space
   - Internet connection

2. **Accounts (Free):**
   - Telegram account
   - (Optional) OpenAI account for AI analysis
   - (Optional) RapidAPI account for faster Amazon searches

3. **Software:**
   - Python 3.11 or newer
   - Chrome or Chromium browser

## Installation

### Step 1: Install Python

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

**macOS:**
```bash
# Using Homebrew
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.11 python3.11-pip
```

**Verify Installation:**
```bash
python --version  # Should show Python 3.11 or higher
```

### Step 2: Install Chrome/Chromium

The scanner needs Chrome for web scraping.

**Windows/Mac:**
- Download from https://www.google.com/chrome/

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install chromium-browser

# Fedora
sudo dnf install chromium
```

### Step 3: Download Deal Scanner

```bash
# Clone the repository
git clone <repository-url>
cd deal-scanner

# Or download ZIP and extract
```

### Step 4: Install Dependencies

```bash
# Install all required Python packages
pip install -r requirements.txt
```

This will install:
- Selenium (web scraping)
- BeautifulSoup (HTML parsing)
- python-telegram-bot (notifications)
- OpenAI (AI analysis)
- And more...

**Troubleshooting:**
- If `pip` not found: Use `pip3` instead
- If permission errors: Use `pip install --user -r requirements.txt`

### Step 5: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your favorite text editor
nano .env    # or: vim .env, code .env, notepad .env
```

## Configuration

### Setting Up Telegram (REQUIRED)

Telegram is where you'll receive deal notifications.

#### Create a Telegram Bot

1. **Open Telegram** on your phone or computer

2. **Search for BotFather**
   - In the search bar, type: `@BotFather`
   - Click on the official BotFather account (verified checkmark)

3. **Create Your Bot**
   - Send: `/newbot`
   - BotFather asks for a name (e.g., "My Deal Scanner")
   - BotFather asks for a username (must end in 'bot', e.g., "mydeals_scanner_bot")

4. **Save Your Token**
   - BotFather gives you a token like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
   - Copy this entire token
   - Add to `.env`:
     ```
     TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
     ```

#### Get Your Chat ID

1. **Search for @userinfobot** in Telegram
2. **Send:** `/start`
3. **Copy your ID** (a number like `123456789`)
4. **Add to `.env`:**
   ```
   TELEGRAM_CHAT_ID=123456789
   ```

#### Activate Your Bot

1. **Search for your bot** in Telegram (the username you chose)
2. **Send:** `/start`
3. You should see a greeting message

### Setting Up OpenAI (OPTIONAL)

OpenAI powers the AI deal analysis. New accounts get $5 free credit.

1. **Create Account:**
   - Go to https://platform.openai.com/signup
   - Sign up with email or Google

2. **Get API Key:**
   - Visit https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it "Deal Scanner"
   - Copy the key (starts with `sk-`)

3. **Add to .env:**
   ```
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Without OpenAI:** The system uses rule-based analysis (still effective!). You'll save your $5 credit.

### Setting Up RapidAPI (OPTIONAL)

RapidAPI provides Amazon product data. Free tier: 500 requests/month.

1. **Create Account:**
   - Go to https://rapidapi.com/
   - Sign up (free)

2. **Subscribe to Amazon API:**
   - Search for "Real-Time Amazon Data"
   - Click "Subscribe to Test"
   - Select "Basic" plan (FREE)

3. **Get API Key:**
   - Go to your dashboard
   - Find your RapidAPI key

4. **Add to .env:**
   ```
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```

### Environment File Complete Example

```bash
# .env file

# REQUIRED
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# OPTIONAL - AI Analysis
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OPTIONAL - Faster Amazon searches
RAPIDAPI_KEY=your_rapidapi_key_here

# OPTIONAL - Alternative APIs
SERPAPI_KEY=
RAINFOREST_API_KEY=

# SETTINGS
NOTIFICATIONS_ENABLED=true
HEADLESS=true
LOG_LEVEL=INFO
```

### Configuring Your Watchlist

The watchlist tells the scanner what products to look for.

**Edit:** `config/products.json`

```json
{
  "watchlist": [
    {
      "id": 1,
      "category": "TV",
      "keywords": ["65 inch", "4K", "OLED", "QLED"],
      "max_price": 800,
      "priority": "high",
      "retailers": ["amazon", "bestbuy", "walmart"],
      "check_frequency": "30min"
    }
  ]
}
```

**Fields Explained:**

- **id**: Unique number (increment for each item)
- **category**: Product category (for organization)
- **keywords**: Words to search for (will match ANY keyword)
- **max_price**: Maximum price you're willing to pay (optional)
- **priority**:
  - `"high"` = Check every 30 minutes
  - `"medium"` = Check every 2 hours
  - `"low"` = Check once daily
- **retailers**: Which stores to check
  - Options: `"amazon"`, `"bestbuy"`, `"walmart"`
- **check_frequency**: For reference only

**Example Watchlist Items:**

```json
{
  "watchlist": [
    {
      "id": 1,
      "category": "Gaming Laptop",
      "keywords": ["RTX 4060", "gaming laptop", "RTX 4070"],
      "max_price": 1200,
      "priority": "high",
      "retailers": ["amazon", "bestbuy"],
      "check_frequency": "30min"
    },
    {
      "id": 2,
      "category": "Robot Vacuum",
      "keywords": ["robot vacuum", "roomba", "roborock"],
      "max_price": 400,
      "priority": "medium",
      "retailers": ["amazon", "walmart"],
      "check_frequency": "2hours"
    },
    {
      "id": 3,
      "category": "Air Fryer",
      "keywords": ["air fryer", "ninja air fryer"],
      "max_price": 100,
      "priority": "low",
      "retailers": ["walmart"],
      "check_frequency": "daily"
    }
  ]
}
```

## Running the Scanner

### First Run (Test Mode)

Before running 24/7, test your setup:

```bash
python main.py
```

You should see:
```
2025-01-17 10:00:00 | INFO     | __main__:main - Deal Scanner Orchestrator initialized
2025-01-17 10:00:00 | INFO     | __main__:main - Loaded 5 items from watchlist
2025-01-17 10:00:00 | INFO     | __main__:main - Running initial scan...
```

**What Happens:**
1. Scanner loads your watchlist
2. Runs an initial scan of all items
3. Starts the 24/7 scheduler
4. You should get a test notification

**Stop It:** Press `Ctrl+C`

### Running Continuously (24/7)

**Option 1: Terminal Window (Simple)**

Keep terminal open:
```bash
python main.py
```

**Option 2: Background Process (macOS/Linux)**

```bash
# Run in background
nohup python main.py > output.log 2>&1 &

# Save the process ID
echo $! > scanner.pid

# Check if running
ps -p $(cat scanner.pid)

# Stop it
kill $(cat scanner.pid)
```

**Option 3: System Service (Linux - Recommended)**

See [DEPLOYMENT.md](DEPLOYMENT.md) for full instructions.

**Option 4: Screen/Tmux (Server)**

```bash
# Using screen
screen -S deal-scanner
python main.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r deal-scanner

# Using tmux
tmux new -s deal-scanner
python main.py
# Press Ctrl+B, then D to detach

# Reattach later
tmux attach -t deal-scanner
```

## Understanding Notifications

### Notification Format

When a deal is found, you'll receive a message like this:

```
🔥 DEAL ALERT! 🔥

Samsung 65" QLED 4K Smart TV

🏪 Retailer: Best Buy

💰 Current Price: $699.99
📉 Was: $999.99
💵 You Save: $300.00 (30% off)

📊 Deal Score: 85/100
📈 Historical Low: $649.99

⭐⭐⭐⭐⭐ (4.7/5)
📝 Reviews: 1,234

✅ Status: In Stock

🔗 https://bestbuy.com/...

⚡ Act Fast! Deals expire quickly.
```

### Understanding Deal Score

The deal score (0-100) indicates how good the deal is:

| Score | Meaning | Action |
|-------|---------|--------|
| 90-100 | Exceptional deal | Buy immediately if you want it |
| 80-89 | Excellent deal | Very good price, act fast |
| 70-79 | Good deal | Worth buying if you need it |
| 60-69 | Fair price | Wait for better |
| Below 60 | Not a deal | Skip |

**You only get notified for scores ≥ 70** (configurable).

### What Affects the Score?

1. **Price vs History (40%)**
   - Is it the lowest price ever?
   - How much cheaper than average?
   - Bigger discount = higher score

2. **Product Quality (30%)**
   - Star rating (4.5+ stars = higher score)
   - Number of reviews (1000+ reviews = bonus)

3. **Timing (15%)**
   - Seasonal factors
   - Current market trends

4. **Retailer (15%)**
   - Amazon/Best Buy/Walmart = trusted
   - Return policies
   - Customer service

### Notification Frequency

To prevent spam:
- Same product: Max 1 notification per 30 minutes
- Daily status report: 8:00 PM
- System errors: Only critical

## Managing Your Watchlist

### Adding Products

1. **Edit** `config/products.json`
2. **Add new entry:**
   ```json
   {
     "id": 6,
     "category": "Wireless Earbuds",
     "keywords": ["wireless earbuds", "airpods", "galaxy buds"],
     "max_price": 150,
     "priority": "medium",
     "retailers": ["amazon", "bestbuy"],
     "check_frequency": "2hours"
   }
   ```
3. **Restart scanner:**
   ```bash
   # Stop: Ctrl+C
   # Start: python main.py
   ```

**OR** Add directly to database:

```python
from utils.database import db

db.add_watchlist_item({
    'category': 'Wireless Earbuds',
    'keywords': ['wireless earbuds', 'airpods'],
    'max_price': 150,
    'priority': 'medium',
    'retailers': ['amazon', 'bestbuy'],
    'check_frequency': '2hours'
})
```

### Removing Products

1. **Edit** `config/products.json`
2. **Delete the entry**
3. **Restart scanner**

**OR** Deactivate in database:

```python
from utils.database import db
import sqlite3

with db.get_connection() as conn:
    conn.execute("UPDATE watchlist SET active = 0 WHERE id = ?", (6,))
```

### Modifying Products

**Change price threshold:**
```json
{
  "id": 1,
  "max_price": 700  // Changed from 800
}
```

**Change priority:**
```json
{
  "id": 1,
  "priority": "medium"  // Changed from "high"
}
```

**Add/remove retailers:**
```json
{
  "id": 1,
  "retailers": ["amazon", "walmart"]  // Removed "bestbuy"
}
```

### Choosing Good Keywords

**❌ Too Broad:**
```json
"keywords": ["laptop"]  // Will match everything
```

**✅ More Specific:**
```json
"keywords": ["gaming laptop", "RTX 4060", "RTX 4070", "i7"]
```

**Tips:**
- Use specific model numbers (e.g., "RTX 4060")
- Include brand names (e.g., "Samsung", "LG")
- Add size/specs (e.g., "65 inch", "4K")
- Use variations (e.g., "airpods", "air pods")

**Examples by Category:**

```json
// TVs
"keywords": ["65 inch", "4K", "OLED", "QLED", "Samsung", "LG"]

// Laptops
"keywords": ["RTX 4060", "i7-13700H", "gaming laptop", "16GB RAM"]

// Kitchen
"keywords": ["instant pot", "air fryer", "ninja foodi", "8 quart"]

// Baby Products
"keywords": ["stroller", "chicco", "uppababy", "double stroller"]
```

## Monitoring & Logs

### Viewing Logs

**Real-time (while running):**
```bash
tail -f logs/scanner.log
```

**Last 100 lines:**
```bash
tail -n 100 logs/scanner.log
```

**Search for errors:**
```bash
grep ERROR logs/scanner.log
```

**Search for specific product:**
```bash
grep "Samsung" logs/scanner.log
```

### Understanding Log Messages

**INFO Messages (Normal):**
```
INFO | amazon_agent:search_deals - Searching for TV
INFO | amazon_agent:search_deals - Found 15 products
INFO | analyzer:analyze_deal - AI analysis complete: score=85
```

**WARNING Messages (Minor Issues):**
```
WARNING | rate_limiter:acquire - Rate limit exceeded for rapidapi
WARNING | amazon_scraper:search - Timeout waiting for results
```

**ERROR Messages (Problems):**
```
ERROR | amazon_agent:search_deals - Error processing product: ...
ERROR | notifier:send_message - Telegram error: ...
```

### Database Exploration

View stored data:

```python
from utils.database import db

# Get statistics
stats = db.get_statistics()
print(f"Total products: {stats['total_products']}")
print(f"Notifications sent: {stats['total_notifications']}")

# View top deals
for deal in stats['top_deals']:
    print(f"{deal['title']} - ${deal['current_price']} (Score: {deal['deal_score']})")

# Get product history
product = db.get_product_by_id('amazon_B08N5WRWNW')
history = db.get_price_history(product['id'], limit=30)

for entry in history:
    print(f"{entry['timestamp']}: ${entry['price']}")
```

**Using SQLite Browser:**

1. Install DB Browser: https://sqlitebrowser.org/
2. Open `deal_scanner.db`
3. Browse tables: products, price_history, notifications_sent

## Tips for Best Results

### 1. Set Realistic Price Expectations

**Research first:**
```bash
# Check historical prices on:
# - CamelCamelCamel (Amazon history)
# - Keepa (Amazon history)
# - Google Shopping
```

**Set max_price 10-20% below typical price:**
```json
{
  "category": "TV",
  // Typical price: $900
  "max_price": 750  // 15% below typical
}
```

### 2. Use Multiple Keywords

**Better matching:**
```json
"keywords": [
  "samsung 65",      // Exact match
  "65 inch samsung", // Variation
  "qled 65",         // Feature
  "QN65",           // Model prefix
  "65\" samsung"     // With quotes
]
```

### 3. Set Appropriate Priority

**High Priority (every 30min):**
- Limited stock items
- Price-volatile products
- Time-sensitive deals

**Medium Priority (every 2hr):**
- General electronics
- Seasonal items
- Regular monitoring

**Low Priority (daily):**
- Staples/consumables
- Non-urgent items
- Price-stable products

### 4. Monitor Multiple Retailers

```json
"retailers": ["amazon", "bestbuy", "walmart"]
```

Same product, different prices across stores!

### 5. Start Small, Expand Gradually

**Week 1:** 3-5 high-interest items
**Week 2:** Add 5 more
**Month 1:** Up to 20 items

Too many items → too many notifications → overwhelm

### 6. Review and Adjust

**Weekly:**
- Check if you're getting relevant notifications
- Adjust keywords if needed
- Remove items you're no longer interested in

**Monthly:**
- Review price thresholds
- Check deal scores
- Update priorities

## Common Tasks

### Task: Change Notification Threshold

Want only exceptional deals (score ≥ 80)?

**Edit:** `config/settings.py`

```python
DEAL_ANALYSIS_CONFIG = {
    'min_deal_score': 80,  # Changed from 70
    # ...
}
```

### Task: Disable Notifications Temporarily

**Option 1:** Edit `.env`
```
NOTIFICATIONS_ENABLED=false
```

**Option 2:** Comment out in code
```python
# In utils/notifier.py
NOTIFICATION_CONFIG = {
    'enabled': False,  # Temporarily disable
    # ...
}
```

### Task: Export Product Database

```python
from utils.database import db
import json

# Get all products
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = [dict(row) for row in cursor.fetchall()]

# Save to JSON
with open('products_backup.json', 'w') as f:
    json.dump(products, f, indent=2, default=str)
```

### Task: Clear Old Data

```python
from utils.database import db

with db.get_connection() as conn:
    cursor = conn.cursor()

    # Delete old price history (older than 90 days)
    cursor.execute("""
        DELETE FROM price_history
        WHERE timestamp < datetime('now', '-90 days')
    """)

    # Delete old notifications
    cursor.execute("""
        DELETE FROM notifications_sent
        WHERE timestamp < datetime('now', '-30 days')
    """)

    conn.commit()
    print("Old data cleared")
```

### Task: Add Custom Retailer

See [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) for instructions on adding new retailers.

### Task: Schedule Specific Scan Times

**Edit:** `main.py`

```python
# Add custom schedule
schedule.every().monday.at("10:00").do(run_high_priority_scan)
schedule.every().friday.at("15:00").do(run_aggregator_scan)
```

## FAQ

### Q: How much does this cost to run?

**A:** Free! All services have free tiers:
- Telegram: Free, unlimited
- OpenAI: $5 free credit
- RapidAPI: 500 requests/month free
- Electricity: ~$1/month for 24/7 operation

### Q: How many products can I monitor?

**A:** Recommended limits:
- **High priority:** 5-10 items
- **Medium priority:** 10-20 items
- **Low priority:** 20-50 items
- **Total:** Up to 100 items

Beyond this, you may hit API rate limits.

### Q: Do I need to keep my computer on 24/7?

**A:** For best results, yes. Alternatives:
- Run on a Raspberry Pi
- Use a cloud server (AWS free tier)
- Run on old laptop/desktop
- Use a VPS ($3-5/month)

### Q: Why am I not getting notifications?

**Check:**
1. Did you message your bot with `/start`?
2. Is `TELEGRAM_BOT_TOKEN` correct in `.env`?
3. Is `TELEGRAM_CHAT_ID` correct?
4. Check logs: `tail -f logs/scanner.log`
5. Test notification:
   ```python
   from utils.notifier import notifier
   import asyncio
   asyncio.run(notifier.send_message("Test"))
   ```

### Q: Can I get notifications on my phone?

**A:** Yes! Telegram works on all devices. Install Telegram on your phone and you'll get push notifications.

### Q: How accurate is the deal scoring?

**A:** Very accurate when:
- Product has price history (2+ weeks in database)
- Product has many reviews (100+)
- Using OpenAI for analysis

Less accurate for:
- Newly released products
- Products with few reviews
- First time seeing product

### Q: Can I run multiple instances?

**A:** Yes, with separate databases:
```bash
# Instance 1
export DATABASE_PATH=scanner_1.db
python main.py &

# Instance 2
export DATABASE_PATH=scanner_2.db
python main.py &
```

### Q: How do I update to the latest version?

```bash
# Stop scanner
Ctrl+C

# Pull latest code
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart
python main.py
```

### Q: What if a retailer blocks me?

**Happens rarely, but:**
1. System automatically backs off
2. Retries with different user agent
3. Waits longer between requests
4. Falls back to API if available

If persistent:
- Increase delays in `config/settings.py`
- Reduce priority of items from that retailer
- Use VPN to rotate IP address

### Q: Can I share this with friends?

**A:** Yes, but each person should run their own instance with their own API keys and database.

### Q: How do I report bugs?

1. Check logs for error messages
2. Open GitHub issue with:
   - Python version
   - OS (Windows/Mac/Linux)
   - Error message
   - Steps to reproduce

### Q: Can I customize notification format?

**A:** Yes! Edit `utils/notifier.py`:

```python
def format_deal_alert(self, product_data):
    # Customize this message format
    message = f"DEAL: {product_data['title']}\n"
    message += f"Price: ${product_data['current_price']}\n"
    # ...
    return message
```

---

## Next Steps

Now that you understand the basics:

1. **Read:** [DEPLOYMENT.md](DEPLOYMENT.md) for 24/7 hosting
2. **Read:** [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) to customize
3. **Read:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md) when issues arise

Happy deal hunting! 🎯💰
