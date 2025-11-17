# Getting Started with Stock Analysis Agent

This guide will help you set up and start using the Stock Analysis Agent in just a few minutes!

## Quick Start (5 Minutes)

### Step 1: Install Dependencies

```bash
cd stock-analysis-agent

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Initialize the System

```bash
# Run setup
python -m src.cli setup
```

This will:
- Create the database
- Set up logging directories
- Check your configuration
- Create .env file from template

### Step 3: Test the System

```bash
# Run system test
python -m src.cli test
```

All tests should pass with green checkmarks ✓

### Step 4: Try It Out!

```bash
# Get a stock quote
python -m src.cli market quote AAPL

# Scan for latest news
python -m src.cli news scan --max-articles 10

# Analyze a stock completely
python -m src.cli analyze stock TSLA
```

**That's it! You're ready to go!**

---

## Detailed Setup Guide

### Prerequisites

- **Python 3.11 or higher**
  ```bash
  python --version  # Should show 3.11+
  ```

- **pip** package manager
  ```bash
  pip --version
  ```

### Installation Steps

#### 1. Clone or Download the Project

```bash
cd stock-analysis-agent
```

#### 2. Create Virtual Environment (Highly Recommended)

```bash
# Create venv
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows
```

You should see `(venv)` in your terminal prompt.

#### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install all necessary libraries:
- **yfinance** - FREE unlimited stock data
- **feedparser** - FREE RSS feed parsing
- **vaderSentiment** - FREE sentiment analysis
- **textblob** - FREE NLP
- **pandas** - Data manipulation
- **sqlalchemy** - Database ORM
- **click** - CLI framework
- And more...

#### 4. Download NLTK Data (for sentiment analysis)

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
```

#### 5. Initialize the System

```bash
python -m src.cli setup
```

This interactive setup will:
1. Check your configuration
2. Create the SQLite database
3. Set up log directories
4. Create `.env` file if it doesn't exist
5. Validate API keys (optional)

### Configuration (Optional)

The system works **out of the box** with FREE sources, but you can add API keys for enhanced features.

#### Edit `.env` file:

```bash
cd config
nano .env  # or use any text editor
```

#### Free API Keys (Optional but Recommended):

1. **NewsAPI** (100 free requests/day)
   - Get key at: https://newsapi.org/register
   - Add to `.env`: `NEWS_API_KEY=your_key_here`

2. **Alpha Vantage** (25 free requests/day)
   - Get key at: https://www.alphavantage.co/support/#api-key
   - Add to `.env`: `ALPHA_VANTAGE_API_KEY=your_key_here`

3. **Financial Modeling Prep** (250 free requests/day)
   - Get key at: https://site.financialmodelingprep.com/developer
   - Add to `.env`: `FMP_API_KEY=your_key_here`

**Note:** Even without these keys, you still get:
- ✅ Unlimited stock data via yfinance
- ✅ Unlimited news via RSS feeds
- ✅ Local sentiment analysis
- ✅ Technical indicators
- ✅ Full system functionality

---

## Command Line Interface (CLI) Usage

The CLI is your main interface for testing and using the system.

### General Command Structure

```bash
python -m src.cli [COMMAND] [SUBCOMMAND] [OPTIONS]
```

### Available Commands

#### 1. Setup & Configuration

```bash
# Initial setup
python -m src.cli setup

# Show current configuration
python -m src.cli config

# Run system tests
python -m src.cli test
```

#### 2. Market Data Commands

```bash
# Get stock quote
python -m src.cli market quote AAPL

# Get technical indicators
python -m src.cli market indicators TSLA

# Analyze price movement (24h)
python -m src.cli market movement MSFT

# Analyze price movement (custom timeframe)
python -m src.cli market movement GOOGL --hours 48
```

Example output:
```
Price: $185.50
Change: +2.35 (+1.28%)
Volume: 52,345,678
RSI: 62.45
MACD Trend: Bullish
```

#### 3. News Commands

```bash
# Scan for latest financial news (RSS only - FREE)
python -m src.cli news scan

# Scan with more articles
python -m src.cli news scan --max-articles 50

# Get news for specific ticker
python -m src.cli news ticker AAPL

# Use NewsAPI (consumes daily quota)
python -m src.cli news scan --use-newsapi
```

Example output:
```
Found 20 articles:

1. Apple beats earnings expectations with strong iPhone sales
   Source: Bloomberg Markets
   Published: 2024-01-15 14:30:00
   Tickers: AAPL
   URL: https://...
```

#### 4. Analysis Commands

```bash
# Analyze sentiment of a news article (interactive)
python -m src.cli analyze article

# Complete stock analysis (news + market data + indicators)
python -m src.cli analyze stock NVDA
```

Complete analysis output includes:
- Current price and change
- Recent news with sentiment analysis
- Technical indicators (RSI, MACD, etc.)
- Unusual activity detection

#### 5. Help

```bash
# Show all commands
python -m src.cli --help

# Show help for specific command
python -m src.cli market --help
python -m src.cli news --help
```

---

## Example Workflows

### Workflow 1: Morning Market Scan

```bash
# 1. Scan for overnight news
python -m src.cli news scan --max-articles 20

# 2. Check your watchlist stocks
python -m src.cli market quote AAPL
python -m src.cli market quote TSLA
python -m src.cli market quote NVDA

# 3. Get complete analysis for interesting stocks
python -m src.cli analyze stock AAPL
```

### Workflow 2: Research a Specific Stock

```bash
# 1. Get current quote and technical indicators
python -m src.cli market quote MSFT
python -m src.cli market indicators MSFT

# 2. Check recent news
python -m src.cli news ticker MSFT

# 3. Analyze price movement
python -m src.cli market movement MSFT --hours 72

# 4. Complete analysis
python -m src.cli analyze stock MSFT
```

### Workflow 3: Sentiment Analysis Practice

```bash
# Interactive sentiment analysis
python -m src.cli analyze article

# Then enter:
Title: Tesla announces new Gigafactory in Texas
Content: Tesla Inc. announced plans to build a new manufacturing facility...
Tickers: TSLA

# System will output:
# - Sentiment score and type
# - Confidence level
# - Event type detected
# - Impact magnitude
# - Relevance score
```

---

## Testing Individual Components

### Test News Scraper

```python
# test_news.py
from src.scrapers.news_scraper import NewsAggregator

aggregator = NewsAggregator()
articles = aggregator.fetch_latest_news(max_articles=10)

for article in articles:
    print(f"{article.title} - {article.source_name}")
```

```bash
python test_news.py
```

### Test Sentiment Analysis

```python
# test_sentiment.py
from src.analysis.sentiment_analyzer import ArticleAnalyzer

analyzer = ArticleAnalyzer()
result = analyzer.analyze_article(
    title="Apple beats earnings expectations",
    content="Strong iPhone sales drive revenue growth",
    tickers=["AAPL"]
)

print(f"Sentiment: {result['sentiment_type']}")
print(f"Score: {result['sentiment_score']}")
print(f"Impact: {result['impact_magnitude']}")
```

```bash
python test_sentiment.py
```

### Test Market Data

```python
# test_market.py
from src.scrapers.market_data_collector import MarketDataService

service = MarketDataService()
quote = service.stock_collector.get_quote("AAPL")

print(f"Price: ${quote['current_price']}")
print(f"Change: {quote['change_percent']}%")

indicators = service.indicator_calculator.get_latest_indicators("AAPL")
print(f"RSI: {indicators['rsi']}")
```

```bash
python test_market.py
```

---

## Understanding the System

### What Data Sources Are Used?

1. **Stock Prices** (yfinance)
   - ✅ FREE, unlimited
   - 15-minute delayed data (acceptable for learning)
   - Historical data available

2. **News** (RSS Feeds)
   - ✅ FREE, unlimited
   - Bloomberg, CNBC, MarketWatch, etc.
   - Real-time news feeds

3. **News** (NewsAPI - optional)
   - 100 requests/day free
   - More targeted news search
   - 1-month historical data

4. **Technical Indicators** (pandas_ta)
   - ✅ FREE, calculated locally
   - RSI, MACD, Bollinger Bands, SMAs, etc.
   - No API calls needed

### How Does Sentiment Analysis Work?

The system uses **multiple free NLP libraries**:

1. **VADER** (Valence Aware Dictionary and sEntiment Reasoner)
   - Specifically designed for social media and news
   - Excellent for financial sentiment
   - Completely free and local

2. **TextBlob**
   - Backup sentiment validation
   - Pattern-based analysis
   - Free and local

3. **Keyword Analysis**
   - Custom financial keyword dictionary
   - Positive/negative indicators
   - Event type detection

Combined, these give highly accurate sentiment scores for financial news!

### What Gets Stored in the Database?

The SQLite database stores:
- News articles and their sentiment scores
- Market data snapshots
- Technical indicator calculations
- (Future) Generated signals and their outcomes
- (Future) Portfolio positions and monitoring
- (Future) Learning patterns

You can view the database using any SQLite browser or:

```bash
sqlite3 data/stock_analysis.db
```

---

## Troubleshooting

### "Module not found" errors

```bash
# Make sure you activated the virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Reinstall requirements
pip install -r requirements.txt
```

### "No articles found"

This usually means:
1. Network connectivity issue
2. RSS feeds are temporarily down
3. Try using NewsAPI: `--use-newsapi` flag

```bash
python -m src.cli news scan --use-newsapi
```

### "Could not fetch quote for [TICKER]"

This means:
1. Ticker symbol might be invalid
2. Network issue
3. yfinance temporarily unavailable

Try a common ticker like AAPL to test:
```bash
python -m src.cli market quote AAPL
```

### Rate Limiting Issues

If you see rate limit errors:
1. Check `logs/api_calls.log` to see usage
2. The system automatically respects limits
3. Rely more on free sources (RSS, yfinance)

### NLTK Data Not Found

```bash
python -c "import nltk; nltk.download('all')"
```

### Permission Errors

On Linux/Mac, you might need:
```bash
chmod +x src/cli.py
```

---

## Next Steps

Now that you have the system running, you can:

1. **Explore the CLI** - Try all the commands
2. **Study the Code** - Look at how sentiment analysis works
3. **Customize** - Add your own keywords, modify thresholds
4. **Extend** - Add new data sources or analysis methods

### Coming Soon (Future Phases):

- ✨ Signal generation system
- 📊 Portfolio monitoring and risk alerts
- 🧠 Learning engine with pattern recognition
- 🌐 Web dashboard
- 📱 Mobile-friendly interface
- 📈 Backtesting system
- 📧 Alert notifications

---

## Learning Resources

### Understanding Sentiment Analysis
- VADER Paper: http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf
- Financial NLP: https://arxiv.org/abs/1908.10063

### Technical Analysis
- RSI: https://www.investopedia.com/terms/r/rsi.asp
- MACD: https://www.investopedia.com/terms/m/macd.asp
- Bollinger Bands: https://www.investopedia.com/terms/b/bollingerbands.asp

### Python Libraries Used
- yfinance: https://github.com/ranaroussi/yfinance
- pandas_ta: https://github.com/twopirllc/pandas-ta
- VADER: https://github.com/cjhutto/vaderSentiment

---

## Support & Feedback

- **Issues**: Open an issue on GitHub
- **Questions**: Check the docs/ folder
- **Contributions**: Pull requests welcome!

---

## Disclaimer

**THIS IS AN EDUCATIONAL TOOL ONLY**

- Not financial advice
- Not for actual trading decisions
- No guarantees of accuracy
- Past performance ≠ future results
- Always consult qualified financial advisors

Happy learning! 📚📈
