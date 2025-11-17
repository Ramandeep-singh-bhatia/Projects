# AI Stock Analysis Agent

**Educational Tool for Learning Market Dynamics and AI Decision-Making**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Educational-green.svg)]()
[![Status](https://img.shields.io/badge/status-Complete-success.svg)]()

---

## ⚠️ IMPORTANT DISCLAIMER

**THIS IS AN EDUCATIONAL TOOL ONLY**

- ❌ **NOT** financial advice
- ❌ **NOT** for actual trading
- ❌ **NOT** a guarantee of profits
- ✅ **FOR** learning market dynamics
- ✅ **FOR** understanding AI/ML techniques
- ✅ **FOR** educational purposes only

Always consult qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [CLI Commands](#cli-commands)
- [How It Works](#how-it-works)
- [Data Sources](#data-sources)
- [Learning System](#learning-system)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Educational Learning Points](#educational-learning-points)
- [Project Structure](#project-structure)

---

## Overview

The AI Stock Analysis Agent is a comprehensive educational system that demonstrates how AI can analyze market news, generate investment signals, manage portfolios, and learn from outcomes. It's built in three phases:

- **Phase 1**: Foundation (news scraping, sentiment analysis, market data)
- **Phase 2**: Signal generation, portfolio management, tracking
- **Phase 3**: Learning engine, pattern recognition, adaptive optimization

### What This Tool Does

1. **Monitors News**: Scrapes financial news from RSS feeds and NewsAPI
2. **Analyzes Sentiment**: Uses NLP (VADER, TextBlob) to gauge market sentiment
3. **Identifies Catalysts**: Detects FDA approvals, M&A, earnings beats, etc.
4. **Generates Signals**: Creates investment signals with confidence scores
5. **Tracks Performance**: Monitors signal outcomes and P&L
6. **Learns & Adapts**: Discovers patterns and optimizes strategy
7. **Generates Reports**: Creates comprehensive learning reports

### What Makes It Unique

- ✅ **100% Free Data Sources**: No paid APIs required (optional NewsAPI with free tier)
- ✅ **Educational Focus**: Designed for learning, not trading
- ✅ **Self-Improving**: Learns from outcomes and adapts
- ✅ **Comprehensive CLI**: Full control via command-line interface
- ✅ **Production-Ready**: SQLite database, proper logging, error handling
- ✅ **Well-Documented**: Extensive documentation and examples

---

## Features

### 📰 News Collection (Phase 1)
- RSS feed aggregation from major financial sources
- NewsAPI integration (100 free requests/day)
- Multi-ticker article tracking
- Duplicate detection
- Automatic categorization

### 🧠 Sentiment Analysis (Phase 1)
- VADER sentiment (finance-optimized)
- TextBlob sentiment analysis
- Ensemble scoring (combined approach)
- Magnitude and confidence metrics
- Historical sentiment tracking

### 💹 Market Data (Phase 1)
- Real-time quotes via yfinance (free, unlimited)
- Historical price data
- Technical indicators (RSI, MACD, volume)
- Market cap and sector information
- Multi-ticker support

### 🎯 Signal Generation (Phase 2)
- Catalyst identification (FDA, M&A, earnings, etc.)
- Multi-factor scoring:
  - Catalyst score (40% weight)
  - Technical analysis (30% weight)
  - Sentiment analysis (30% weight)
- Confidence scoring (0-100)
- Signal types (short-term, long-term)
- Automatic signal expiry

### 📊 Portfolio Management (Phase 2)
- Virtual portfolio tracking
- Position management (add/remove)
- P&L calculation (realized/unrealized)
- Cost basis tracking
- Portfolio value monitoring

### 🔍 Portfolio Monitoring (Phase 2)
- Risk assessment (4 levels: CRITICAL/HIGH/MEDIUM/LOW)
- Multi-factor risk scoring
- Early warning system
- Automated alerts
- Daily monitoring reports

### 🎓 Learning Engine (Phase 3)
- Performance analysis with comprehensive metrics
- Success/failure factor extraction
- Correlation-based weight optimization
- Confidence calibration
- Trend detection
- Weekly learning reports

### 🔍 Pattern Recognition (Phase 3)
- Discovers 6 pattern types
- Statistical validation (Wilson score)
- Pattern matching for new signals
- Confidence boosting

### ⚙️ Adaptive Optimization (Phase 3)
- Dynamic weight adjustment
- Catalyst multiplier tuning
- Confidence threshold optimization
- Pattern-based boosting
- Version tracking

### 📈 Backtesting (Phase 3)
- Historical signal validation
- Strategy testing
- Parameter optimization
- Walk-forward analysis
- Risk metrics (Sharpe ratio, drawdown)

### 📑 Reporting (Phase 3)
- Weekly/monthly learning reports
- Trend analysis
- Actionable recommendations
- JSON and Markdown export

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Interface                            │
│  (User commands, status display, interactive control)       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Core Services Layer                         │
├─────────────────────────────────────────────────────────────┤
│  News Scraper  │  Sentiment  │  Market Data  │  Signals    │
│  (RSS + API)   │  (NLP)      │  (yfinance)   │  (Generator)│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Portfolio Management Layer                      │
├─────────────────────────────────────────────────────────────┤
│  Portfolio     │  Signal      │  Risk         │  Position   │
│  Manager       │  Tracker     │  Monitor      │  Tracker    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               Learning & Optimization Layer                  │
├─────────────────────────────────────────────────────────────┤
│  Learning   │  Pattern    │  Adaptive   │  Backtest  │ Report│
│  Engine     │  Recognizer │  Weights    │  System    │  Gen  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│  SQLite Database (12 tables)                                │
│  - Articles, Sentiment, Signals, Outcomes, Portfolio, etc.  │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- **Python 3.11+** (3.11 or higher required)
- **pip** (Python package manager)
- **Git** (for cloning repository)
- **Internet connection** (for data fetching)

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd stock-analysis-agent
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install click sqlalchemy python-dotenv pyyaml yfinance \
            vaderSentiment nltk textblob feedparser requests \
            beautifulsoup4 tabulate apscheduler pandas
```

### Step 4: Download NLTK Data

```bash
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
```

---

## Configuration

### Step 1: Initial Setup

```bash
python -m src.cli setup
```

This creates:
- SQLite database at `data/stock_analysis.db`
- `logs/` directory
- `reports/` directory

### Step 2: Configure API Keys (Optional)

```bash
mkdir -p config
nano config/.env
```

Add optional API keys:

```bash
# NewsAPI (optional - 100 free requests/day)
NEWS_API_KEY=your_key_here
```

**Note**: The system works with just free RSS feeds and yfinance. API keys are optional.

### Step 3: Configure Settings

Edit `config/config.yaml`:

```yaml
# Signal generation
signals:
  min_confidence: 60
  weights:
    catalyst: 0.4
    technical: 0.3
    sentiment: 0.3

# Risk management
risk:
  max_position_size: 0.10  # 10% per position
  high_risk_threshold: 70
```

---

## Quick Start

### 1. Setup System

```bash
python -m src.cli setup
python -m src.cli test
```

### 2. Collect Initial Data

```bash
# Scrape news
python -m src.cli news scrape

# Analyze sentiment
python -m src.cli news analyze

# Show recent news
python -m src.cli news list --limit 10
```

### 3. Generate Signals

```bash
# Generate signals
python -m src.cli signals generate --days 7

# View signals
python -m src.cli signals list --status active
```

### 4. Track Performance

```bash
# Track outcomes
python -m src.cli signals track

# View results
python -m src.cli signals outcomes --days 30
```

### 5. Manage Portfolio

```bash
# Add position
python -m src.cli portfolio add AAPL 10 150.00

# View portfolio
python -m src.cli portfolio view

# Monitor risks
python -m src.cli portfolio monitor
```

### 6. Learn and Optimize

```bash
# Analyze performance
python -m src.cli learning analyze --days 30

# Discover patterns
python -m src.cli learning patterns

# Generate report
python -m src.cli learning report --type weekly
```

---

## Usage Guide

### Daily Workflow

**Morning:**

```bash
# 1. Scrape overnight news
python -m src.cli news scrape

# 2. Analyze sentiment
python -m src.cli news analyze

# 3. Generate new signals
python -m src.cli signals generate --days 1

# 4. Check portfolio
python -m src.cli portfolio view
python -m src.cli portfolio monitor

# 5. Track existing signals
python -m src.cli signals track
```

**Evening:**

```bash
# 1. Check outcomes
python -m src.cli signals outcomes --days 7

# 2. View portfolio changes
python -m src.cli portfolio history

# 3. Check alerts
python -m src.cli portfolio alerts
```

### Weekly Workflow

```bash
# 1. Analyze performance
python -m src.cli learning analyze --days 7

# 2. Check patterns
python -m src.cli learning patterns

# 3. Get recommendations
python -m src.cli learning recommendations

# 4. Generate report
python -m src.cli learning report --type weekly --export

# 5. Update weights
python -m src.cli learning weights --update
```

---

## CLI Commands

### News Commands

```bash
python -m src.cli news scrape              # Scrape news
python -m src.cli news analyze             # Analyze sentiment
python -m src.cli news list [--limit 20]   # List articles
python -m src.cli news stats               # News statistics
```

### Market Data Commands

```bash
python -m src.cli market update <ticker>   # Update data
python -m src.cli market quote <ticker>    # Get quote
python -m src.cli market technicals <ticker> # View indicators
```

### Signal Commands

```bash
python -m src.cli signals generate [--days 7]  # Generate signals
python -m src.cli signals list                 # List signals
python -m src.cli signals track                # Track outcomes
python -m src.cli signals outcomes [--days 30] # View results
python -m src.cli signals stats                # Statistics
```

### Portfolio Commands

```bash
python -m src.cli portfolio view                        # View portfolio
python -m src.cli portfolio add <ticker> <shares> <price>  # Add position
python -m src.cli portfolio remove <ticker>             # Remove position
python -m src.cli portfolio monitor                     # Monitor risks
python -m src.cli portfolio alerts                      # View alerts
python -m src.cli portfolio history                     # View history
```

### Learning Commands

```bash
python -m src.cli learning analyze [--days 30]          # Analyze performance
python -m src.cli learning patterns                     # View patterns
python -m src.cli learning weights [--update]           # Manage weights
python -m src.cli learning report --type weekly         # Generate report
python -m src.cli learning backtest [--days 30]         # Run backtest
python -m src.cli learning recommendations              # Get suggestions
```

### Utility Commands

```bash
python -m src.cli setup    # Initial setup
python -m src.cli test     # Run tests
```

---

## How It Works

### Phase 1: Data Collection

**News Scraping:**
- RSS feeds (free, unlimited)
- NewsAPI (100 requests/day free)
- Articles parsed and stored
- Tickers extracted

**Sentiment Analysis:**
- VADER: Finance-optimized (-1 to +1)
- TextBlob: Polarity and subjectivity
- Combined: Averaged with confidence

**Market Data:**
- yfinance: Real-time quotes (free)
- Technical indicators (RSI, MACD)
- Historical price data

### Phase 2: Signal Generation

**Catalyst Detection:**
- FDA: Drug approvals
- M&A: Mergers, acquisitions
- Earnings: Revenue beats
- Contract: Major wins
- Product: Launches
- Analyst: Upgrades

**Multi-Factor Scoring:**

```python
final_score = (
    catalyst_score * 0.4 +
    technical_score * 0.3 +
    sentiment_score * 0.3
)
```

**Signal Tracking:**
- Monitors price movements
- Tracks peak gains
- Validates success/failure
- Stores outcomes

**Portfolio Management:**
- Position tracking
- P&L calculation
- Risk assessment (0-100)
- Alert generation

### Phase 3: Learning

**Performance Analysis:**
- Calculate success rates
- Extract winning characteristics
- Identify success factors
- Track trends

**Pattern Discovery:**
- Group signals by features
- Calculate success rates
- Statistical validation (Wilson score)
- Save validated patterns

**Weight Optimization:**

```python
# Calculate correlations
catalyst_corr = correlation(catalyst_scores, outcomes)

# Optimize weights
new_weight = correlation / total_correlation

# Gradual adjustment (10%)
adjusted = current + (new - current) * 0.10
```

**Backtesting:**
- Test on historical data
- Calculate performance metrics
- Validate strategies
- Optimize parameters

---

## Data Sources

### Free (Unlimited)

**RSS Feeds:**
- Yahoo Finance, CNBC, MarketWatch
- FREE, unlimited
- Good for headlines

**yfinance:**
- Real-time stock quotes
- Historical data
- Technical indicators
- FREE, unlimited
- Excellent quality

**VADER & TextBlob:**
- Local NLP libraries
- No API calls
- FREE, unlimited

### Optional (Free Tier)

**NewsAPI:**
- 80,000+ sources
- 100 requests/day FREE
- Good supplement

---

## Learning System

### Learning Cycle

```
Signals Generated → Outcomes Tracked → Data Stored →
Analyze Outcomes → Extract Factors → Optimize Weights →
Apply New Weights → Generate Better Signals
```

### Expected Performance

| Signals | Success Rate | Weight Stability | Patterns |
|---------|--------------|------------------|----------|
| 0-50    | 50-60%       | Unstable         | 0-3      |
| 50-100  | 60-65%       | Moderate         | 3-8      |
| 100-500 | 65-70%       | Stable           | 8-15     |
| 500+    | 70-75%       | Very Stable      | 15-25    |

---

## Examples

### Example 1: Signal Analysis

```bash
$ python -m src.cli signals generate --days 7

SIGNALS GENERATED (3):
1. AAPL - FDA Approval Signal
   Confidence: 78%
   Expected Move: +8.5%

2. MSFT - Earnings Beat Signal
   Confidence: 72%
   Expected Move: +6.2%

3. NVDA - Product Launch Signal
   Confidence: 65%
   Expected Move: +5.8%
```

### Example 2: Portfolio Management

```bash
$ python -m src.cli portfolio view

PORTFOLIO SUMMARY:
Total Value: $3,045.00
Unrealized P&L: +$45.00 (+1.50%)

POSITIONS:
1. AAPL: 10 shares @ $150.00
   Current: $152.00
   P&L: +$20.00 (+1.33%)
   Risk: MEDIUM (62)
```

### Example 3: Learning

```bash
$ python -m src.cli learning analyze --days 30

PERFORMANCE OVERVIEW:
Total Signals: 45
Success Rate: 62.2%
Average Gain: 7.3%

BY CATALYST TYPE:
  FDA: 75.0% (6/8)
  M&A: 66.7% (4/6)
  EARNINGS: 58.3% (7/12)
```

---

## Troubleshooting

### Common Issues

**"No module named 'click'"**
```bash
pip install click tabulate sqlalchemy
```

**"Database not found"**
```bash
python -m src.cli setup
```

**"No news articles found"**
```bash
python -m src.cli news scrape
```

**"Not enough signals for learning"**
```bash
# Need 20+ signals
python -m src.cli signals generate --days 30
```

### Debug Mode

```bash
export LOG_LEVEL=DEBUG
python -m src.cli <command>
tail -f logs/stock_analysis.log
```

---

## Development

### Project Structure

```
stock-analysis-agent/
├── config/              # Configuration files
├── data/                # SQLite database
├── logs/                # Application logs
├── reports/             # Generated reports
├── src/
│   ├── analysis/        # Sentiment analysis
│   ├── config/          # Config loader
│   ├── database/        # SQLAlchemy models
│   ├── learning/        # Phase 3 - Learning engine
│   ├── portfolio/       # Phase 2 - Portfolio management
│   ├── scrapers/        # News and market data
│   ├── signals/         # Phase 2 - Signal generation
│   ├── utils/           # Utilities
│   └── cli.py           # CLI interface
├── PHASE1_COMPLETE.md
├── PHASE2_COMPLETE.md
├── PHASE3_COMPLETE.md
└── README.md
```

### Technology Stack

- **Language**: Python 3.11+
- **CLI**: Click
- **Database**: SQLite + SQLAlchemy
- **NLP**: VADER, TextBlob, NLTK
- **Market Data**: yfinance
- **News**: feedparser, requests
- **Technical Analysis**: pandas, numpy

---

## Educational Learning Points

### AI/ML Concepts
- Supervised learning from outcomes
- Feature engineering from news
- Ensemble methods
- Pattern recognition
- Online learning
- Overfitting prevention

### NLP Techniques
- Sentiment analysis
- Named entity recognition
- Text classification
- Confidence scoring

### Financial Concepts
- Catalyst events
- Technical analysis
- Risk management
- P&L calculation
- Performance metrics

### Software Engineering
- Clean architecture
- Database design
- CLI development
- Logging and monitoring
- Error handling

---

## Version History

- **v1.0.0**: Phase 1 - Foundation
- **v2.0.0**: Phase 2 - Signals & Portfolio
- **v3.0.0**: Phase 3 - Learning Engine

---

## Roadmap

- [ ] Web UI dashboard
- [ ] Real-time streaming
- [ ] Deep learning models
- [ ] Multi-asset support
- [ ] Social media sentiment
- [ ] Advanced visualization

---

**Remember: This is an educational tool. Always do your own research and consult financial advisors.**

**Happy Learning! 📚🎓**
