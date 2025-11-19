# Multi-Retail Deal Scanner with AI Agents

A production-ready multi-agent deal scanning system that monitors Amazon, Best Buy, Walmart, and other retailers for deals on specific product categories using only **FREE** tools and APIs. Get real-time Telegram notifications when great deals are found!

## Features

- **Multi-Retailer Coverage**: Monitors Amazon, Best Buy, Walmart, and deal aggregators
- **AI-Powered Deal Analysis**: Uses OpenAI to evaluate deal quality (0-100 score)
- **Smart Notifications**: Only alerts you about genuinely good deals (score > 70)
- **Price History Tracking**: Stores historical prices to identify true deals
- **Automated Scheduling**: Runs 24/7 with priority-based scanning
- **Rate Limiting**: Stays within free API tier limits automatically
- **RSS Feed Monitoring**: Tracks Slickdeals, Reddit r/buildapcsales, and more
- **Customizable Watchlist**: Easy JSON configuration for products you want
- **Anti-Detection**: Rotating user agents and delays to avoid blocks

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Orchestrator                         │
│                    (main.py)                                 │
└─────────────┬───────────────────────────────────────────────┘
              │
         ┌────┴────┐
         │Scheduler│
         └────┬────┘
              │
    ┌─────────┼─────────────────────────────┐
    │         │                             │
┌───▼────┐ ┌──▼────┐ ┌────────┐ ┌─────────▼──────┐
│Amazon  │ │BestBuy│ │Walmart │ │  Aggregator    │
│ Agent  │ │ Agent │ │ Agent  │ │  Agent (RSS)   │
└───┬────┘ └──┬────┘ └───┬────┘ └─────────┬──────┘
    │         │           │               │
┌───▼─────────▼───────────▼───────────────▼──────┐
│          Deal Analyzer Agent (AI)               │
└───────────────────┬─────────────────────────────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
    ┌────▼───┐ ┌────▼────┐ ┌──▼──────┐
    │Database│ │Notifier │ │Rate     │
    │(SQLite)│ │(Telegram)│ │Limiter  │
    └────────┘ └─────────┘ └─────────┘
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Chrome/Chromium browser (for Selenium)
- Telegram account

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd deal-scanner
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys (see Setup Guide below)
```

4. **Configure your watchlist**
```bash
# Edit config/products.json to add products you want to track
```

5. **Run the scanner**
```bash
python main.py
```

That's it! The scanner will start monitoring deals and send Telegram notifications.

## Setup Guide

### 1. Telegram Bot Setup (REQUIRED)

Telegram is the only required service for notifications.

**Step 1: Create a Bot**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Add to `.env`: `TELEGRAM_BOT_TOKEN=your_token_here`

**Step 2: Get Your Chat ID**
1. Search for `@userinfobot` on Telegram
2. Send `/start`
3. Copy your chat ID (a number)
4. Add to `.env`: `TELEGRAM_CHAT_ID=your_chat_id`

**Step 3: Start Your Bot**
1. Find your bot in Telegram (search for the name you gave it)
2. Send `/start` to activate it

### 2. OpenAI API (OPTIONAL - for AI Analysis)

OpenAI provides $5 free credit for new accounts.

1. Go to https://platform.openai.com/api-keys
2. Create account (new users get $5 credit)
3. Click "Create new secret key"
4. Copy the key
5. Add to `.env`: `OPENAI_API_KEY=sk-...`

**Without OpenAI**: The system will use rule-based deal analysis (still effective!)

### 3. RapidAPI (OPTIONAL - for Amazon Data)

Free tier: 500 requests/month

1. Go to https://rapidapi.com/
2. Sign up for free account
3. Subscribe to "Real-Time Amazon Data" API (free tier)
4. Copy your RapidAPI key from dashboard
5. Add to `.env`: `RAPIDAPI_KEY=your_key`

### 4. Other Optional APIs

**SerpAPI** (100 searches/month free)
- Sign up at https://serpapi.com/
- Get API key from dashboard
- Add to `.env`: `SERPAPI_KEY=your_key`

**Rainforest API** (100 requests/month free)
- Sign up at https://www.rainforestapi.com/
- Get API key
- Add to `.env`: `RAINFOREST_API_KEY=your_key`

## Configuration

### Watchlist Configuration

Edit `config/products.json` to customize what deals you want:

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

**Parameters:**
- `category`: Product category name
- `keywords`: Search terms (will match any)
- `max_price`: Maximum price to consider (optional)
- `priority`: `high` (30min), `medium` (2hr), or `low` (daily)
- `retailers`: Which stores to check
- `check_frequency`: How often to scan (for reference)

### Scanning Schedule

Default schedule (configured in `config/settings.py`):
- **High Priority**: Every 30 minutes
- **Medium Priority**: Every 2 hours
- **Low Priority**: Daily at 9:00 AM
- **RSS Feeds**: Every hour
- **Best Buy Top Deals**: Every 2 hours
- **Status Report**: Daily at 8:00 PM

## Usage

### Run Continuously (Recommended)
```bash
python main.py
```

The scanner will run 24/7, checking for deals on schedule.

### Test Single Category
```python
from agents.amazon_agent import amazon_agent
from utils.database import db

# Load watchlist
watchlist = db.get_watchlist()
item = watchlist[0]  # First item

# Search for deals
deals = amazon_agent.search_deals(item)
print(f"Found {len(deals)} deals")
```

### Check Database Statistics
```python
from utils.database import db

stats = db.get_statistics()
print(f"Total products tracked: {stats['total_products']}")
print(f"Notifications sent: {stats['total_notifications']}")
print("Top deals:", stats['top_deals'])
```

## Free Tier Limitations

Understanding the constraints to avoid hitting limits:

| Service | Free Limit | Usage Strategy |
|---------|-----------|----------------|
| RapidAPI | 500/month | ~16/day - Use for high-priority items only |
| SerpAPI | 100/month | ~3/day - Backup search method |
| Rainforest | 100/month | ~3/day - Alternative Amazon source |
| OpenAI | $5 credit | ~250 analyses - Use wisely |
| Telegram | Unlimited | No limits! |
| Web Scraping | Self-limited | Rate limited to avoid blocks |

**Rate Limiting**: The system automatically tracks API usage and switches to web scraping when limits are approached.

## Deployment Options

### Local (Development)
```bash
python main.py
```

### Background Process (Linux/Mac)
```bash
nohup python main.py > output.log 2>&1 &
```

### Systemd Service (Linux)
Create `/etc/systemd/system/deal-scanner.service`:
```ini
[Unit]
Description=Deal Scanner Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/deal-scanner
ExecStart=/usr/bin/python3 /path/to/deal-scanner/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable deal-scanner
sudo systemctl start deal-scanner
sudo systemctl status deal-scanner
```

### Docker (Coming Soon)
```bash
# Build
docker build -t deal-scanner .

# Run
docker run -d --name deal-scanner \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  deal-scanner
```

### Cloud Options (24/7 Free Tiers)

1. **Google Cloud Run** (Free tier: 2M requests/month)
2. **AWS EC2 Free Tier** (t2.micro for 12 months)
3. **Oracle Cloud** (Always free tier available)
4. **Replit** (Can run continuously on paid plan)

## Troubleshooting

### Issue: No notifications received

**Solutions:**
1. Check Telegram bot token is correct
2. Make sure you messaged your bot with `/start`
3. Verify chat ID is correct
4. Check `.env` file is in the correct location
5. Look at logs: `tail -f logs/scanner.log`

### Issue: "Rate limit exceeded" errors

**Solutions:**
1. Check how many API calls you've made:
   ```python
   from utils.database import db
   print(db.get_api_usage_count('rapidapi', hours=24))
   ```
2. Wait for rate limit to reset (hourly/daily)
3. System will automatically fall back to web scraping

### Issue: Selenium WebDriver errors

**Solutions:**
1. Install Chrome/Chromium:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install chromium-browser

   # Mac
   brew install chromium
   ```
2. Update ChromeDriver:
   ```bash
   pip install --upgrade webdriver-manager
   ```
3. Check `HEADLESS` setting in `.env`

### Issue: Empty search results

**Solutions:**
1. Check your keywords are correct
2. Verify retailers are accessible
3. Try lowering `max_price` threshold
4. Check logs for specific errors
5. Test with a broader search:
   ```json
   {"keywords": ["laptop"], "max_price": 2000}
   ```

### Issue: Database locked errors

**Solutions:**
1. Only run one instance of the scanner
2. Check for zombie processes: `ps aux | grep main.py`
3. Delete lock if stuck: `rm deal_scanner.db-journal`

## Project Structure

```
deal-scanner/
├── agents/              # AI agent implementations
│   ├── amazon_agent.py
│   ├── bestbuy_agent.py
│   ├── walmart_agent.py
│   ├── aggregator_agent.py
│   └── analyzer_agent.py
├── scrapers/           # Web scraping logic
│   ├── amazon_scraper.py
│   ├── bestbuy_scraper.py
│   └── walmart_scraper.py
├── utils/              # Utility modules
│   ├── database.py
│   ├── notifier.py
│   ├── rate_limiter.py
│   └── proxy_rotator.py
├── config/             # Configuration files
│   ├── settings.py
│   └── products.json
├── logs/               # Log files
├── main.py            # Main orchestrator
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
└── README.md         # This file
```

## How It Works

### 1. Watchlist Loading
System loads products from `config/products.json` and syncs with database.

### 2. Scheduled Scanning
Based on priority, agents are triggered to search for deals:
- **High Priority**: Scanned every 30 minutes
- **Medium Priority**: Every 2 hours
- **Low Priority**: Once daily

### 3. Multi-Source Search
For each watchlist item:
1. Try API first (if quota available)
2. Fall back to web scraping if needed
3. Extract: title, price, rating, availability

### 4. Deal Analysis
Each product is analyzed:
1. **Price Check** (40%): Compare to historical low/average
2. **Quality Check** (30%): Rating and review count
3. **Timing** (15%): Seasonality factors
4. **Retailer** (15%): Source reputation

Produces a 0-100 score.

### 5. Notification Decision
If deal score ≥ 70:
1. Format nice Telegram message
2. Check if already notified recently
3. Send notification with product details
4. Record in database

### 6. Database Tracking
- Store product info
- Track price history
- Log notifications sent
- Monitor API usage

## Advanced Features

### Custom Agent

Create a custom scraper/agent:

```python
# agents/target_agent.py
from agents.base_agent import BaseAgent

class TargetAgent(BaseAgent):
    def search_deals(self, watchlist_item):
        # Your custom logic
        pass
```

Register in `main.py`:
```python
from agents.target_agent import target_agent

# Add to scan loop
deals = target_agent.search_deals(item)
```

### Database Queries

```python
from utils.database import db

# Get all products for a retailer
products = db.get_products_by_category('TV')

# Get price history
history = db.get_price_history(product_id, limit=30)

# Check recent notifications
if not db.was_notified_recently(product_id, minutes=60):
    # Send notification
    pass
```

### Custom Notifications

```python
from utils.notifier import notifier
import asyncio

# Send custom message
asyncio.run(notifier.send_message("Hello from Deal Scanner!"))

# Send with image
asyncio.run(notifier.send_photo(
    "https://example.com/image.jpg",
    "Custom deal alert!"
))
```

## Best Practices

1. **Start Small**: Begin with 3-5 watchlist items, expand gradually
2. **Be Specific**: Use detailed keywords for better matches
3. **Set Realistic Prices**: Research typical prices before setting `max_price`
4. **Monitor Logs**: Check `logs/scanner.log` regularly
5. **Respect Rate Limits**: Don't modify rate limiters unless necessary
6. **Test Notifications**: Send test message before relying on alerts

## Legal & Ethical Considerations

This tool is for **personal use only**. Please follow these guidelines:

- Respect robots.txt files
- Use reasonable rate limits
- Don't resell data
- Follow retailer Terms of Service
- Attribute deal sources appropriately
- Don't overwhelm servers with requests

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional retailers (Target, Costco, etc.)
- [ ] Web dashboard for monitoring
- [ ] Price prediction ML model
- [ ] Browser extension for quick adds
- [ ] Multi-user support
- [ ] Docker deployment guide
- [ ] More deal sources (Twitter, Discord)

## License

MIT License - See LICENSE file

## Support

- **Issues**: Open a GitHub issue
- **Questions**: Check logs first, then open discussion
- **Feature Requests**: Submit via GitHub issues

## Changelog

### v1.0.0 (2025-01-17)
- Initial release
- Support for Amazon, Best Buy, Walmart
- AI-powered deal analysis
- Telegram notifications
- RSS feed aggregation
- Rate limiting
- Price history tracking

## Acknowledgments

- Built with LangChain/LangGraph for agent orchestration
- Uses Selenium for web scraping
- OpenAI for deal analysis
- Telegram for notifications

---

**Happy Deal Hunting!** 🎯💰

Found a great deal? Share it with the community!
