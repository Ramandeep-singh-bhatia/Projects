# AI Stock Analysis Agent - Deployment Guide

Complete guide for deploying and running the AI Stock Analysis Agent.

---

## 📋 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] pip package manager
- [ ] Git (for cloning)
- [ ] Internet connection
- [ ] Terminal/command line access
- [ ] Text editor (for configuration)

### Verify Python Version

```bash
python --version
# Should show Python 3.11.x or higher

# If you have multiple Python versions:
python3.11 --version
```

---

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
# Navigate to your projects directory
cd ~/Projects

# Clone the repository
git clone <repository-url>
cd stock-analysis-agent

# Verify files
ls -la
```

You should see:
- `src/` directory
- `config/` directory
- `README.md`
- `requirements.txt`
- Phase documentation files

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

**Why use a virtual environment?**
- Isolates project dependencies
- Prevents conflicts with system Python
- Makes it easy to reproduce environment

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install core dependencies
pip install click sqlalchemy python-dotenv pyyaml yfinance \
            vaderSentiment nltk textblob feedparser requests \
            beautifulsoup4 tabulate apscheduler pandas numpy

# This will take a few minutes
```

**If installation fails:**

Try installing in smaller batches:

```bash
# Batch 1: CLI and database
pip install click tabulate sqlalchemy python-dotenv pyyaml

# Batch 2: Data sources
pip install yfinance feedparser requests beautifulsoup4

# Batch 3: NLP
pip install vaderSentiment nltk textblob

# Batch 4: Analysis
pip install pandas numpy apscheduler
```

### 4. Download NLTK Data

```bash
# Download required NLTK datasets
python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt'); nltk.download('averaged_perceptron_tagger')"
```

This downloads:
- `vader_lexicon`: For financial sentiment analysis
- `punkt`: For sentence tokenization
- `averaged_perceptron_tagger`: For part-of-speech tagging

---

## ⚙️ Configuration

### 1. Run Initial Setup

```bash
# This creates database and directories
python -m src.cli setup
```

You should see:
```
Setting up Stock Analysis Agent...

1. Checking configuration...
✓ Configuration loaded

2. Setting up database...
✓ Database created at data/stock_analysis.db

3. Setting up logging...
✓ Log directory: logs

4. Checking API keys...
⚠  Warning: No API keys configured!
   You can still use FREE unlimited sources

Setup complete!
```

### 2. Configure API Keys (Optional)

The system works perfectly without API keys using free sources. However, you can add NewsAPI for more news sources:

```bash
# Create config directory if it doesn't exist
mkdir -p config

# Create .env file
nano config/.env
# Or use your preferred editor: vi, vim, code, etc.
```

Add your keys (optional):

```bash
# NewsAPI (100 free requests/day)
# Get key from: https://newsapi.org/
NEWS_API_KEY=your_newsapi_key_here

# Alpha Vantage (optional, not needed)
ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
```

Save and exit (in nano: Ctrl+X, then Y, then Enter).

### 3. Customize Settings (Optional)

Edit `config/config.yaml` for custom settings:

```bash
nano config/config.yaml
```

Key settings to consider:

```yaml
# Minimum confidence for signal generation
signals:
  min_confidence: 60  # Range: 0-100

# Signal weights (must sum to 1.0)
  weights:
    catalyst: 0.4   # Catalyst events importance
    technical: 0.3  # Technical indicators importance
    sentiment: 0.3  # Sentiment analysis importance

# Risk thresholds
risk:
  max_position_size: 0.10      # Max 10% per position
  high_risk_threshold: 70      # Risk score 70+ is HIGH
  critical_risk_threshold: 85  # Risk score 85+ is CRITICAL

# Learning settings
learning:
  min_signals_for_learning: 20   # Need 20+ signals to optimize
  pattern_min_samples: 10        # Pattern needs 10+ samples
  weight_adjustment_rate: 0.10   # Adjust weights by 10% per update
```

---

## ✅ Verification

### 1. Run System Tests

```bash
python -m src.cli test
```

Expected output:

```
Running system tests...

1. Testing configuration...
   ✓ Configuration loaded

2. Testing database...
   ✓ Database models loaded (12 tables)

3. Testing news scraper...
   ✓ News scraper working

4. Testing market data...
   ✓ Market data working (AAPL: $150.25)

5. Testing sentiment analysis...
   ✓ Sentiment analysis working

6. Testing signal generator...
   ✓ Signal generator loaded

7. Testing portfolio manager...
   ✓ Portfolio manager loaded

8. Testing portfolio monitor...
   ✓ Portfolio monitor loaded

9. Testing learning engine...
   ✓ Learning engine loaded

10. Testing pattern recognizer...
   ✓ Pattern recognizer loaded

11. Testing adaptive weights...
   ✓ Adaptive weights system loaded

12. Testing backtester...
   ✓ Backtester loaded

13. Testing report generator...
   ✓ Report generator loaded

Phase 1, 2 & 3 tests complete!
```

If all tests pass ✓, your installation is successful!

### 2. Test Each Component

**Test news scraping:**

```bash
python -m src.cli news scrape
python -m src.cli news list --limit 5
```

**Test market data:**

```bash
python -m src.cli market quote AAPL
```

**Test signal generation:**

```bash
python -m src.cli signals generate --days 7
python -m src.cli signals list
```

---

## 🎯 First Run Guide

### Step 1: Collect Initial Data

```bash
# Scrape news (takes 1-2 minutes)
python -m src.cli news scrape

# Analyze sentiment for scraped articles
python -m src.cli news analyze

# View what was collected
python -m src.cli news list --limit 10
```

### Step 2: Generate Your First Signals

```bash
# Generate signals from recent news
python -m src.cli signals generate --days 7

# View generated signals
python -m src.cli signals list --status active
```

Example output:

```
ACTIVE SIGNALS (3):

1. AAPL - FDA Approval
   Confidence: 78%
   Expected Move: +8.5%
   Expires: 2025-01-24

2. MSFT - Earnings Beat
   Confidence: 72%
   Expected Move: +6.2%
   Expires: 2025-01-25
```

### Step 3: Start Paper Trading (Virtual Portfolio)

```bash
# Add a position based on a signal
python -m src.cli portfolio add AAPL 10 150.00

# View your portfolio
python -m src.cli portfolio view

# Monitor risks
python -m src.cli portfolio monitor
```

### Step 4: Track Signal Performance

```bash
# Track outcomes (run this daily)
python -m src.cli signals track

# View outcomes after a week
python -m src.cli signals outcomes --days 7
```

### Step 5: Enable Learning (After 20+ Signals)

```bash
# Analyze performance
python -m src.cli learning analyze --days 30

# Discover patterns
python -m src.cli learning patterns

# Get recommendations
python -m src.cli learning recommendations

# Generate weekly report
python -m src.cli learning report --type weekly
```

---

## 📅 Daily Operations

### Morning Routine (5 minutes)

```bash
# 1. Scrape overnight news
python -m src.cli news scrape

# 2. Analyze sentiment
python -m src.cli news analyze

# 3. Generate signals
python -m src.cli signals generate --days 1

# 4. Check portfolio
python -m src.cli portfolio view
python -m src.cli portfolio monitor

# 5. Track existing signals
python -m src.cli signals track
```

**Automation tip:** Create a shell script:

```bash
# Create morning_routine.sh
nano morning_routine.sh
```

Add:

```bash
#!/bin/bash
echo "=== Stock Analysis Agent - Morning Routine ==="
echo "1. Scraping news..."
python -m src.cli news scrape

echo "2. Analyzing sentiment..."
python -m src.cli news analyze

echo "3. Generating signals..."
python -m src.cli signals generate --days 1

echo "4. Checking portfolio..."
python -m src.cli portfolio view

echo "5. Tracking signals..."
python -m src.cli signals track

echo "=== Morning routine complete ==="
```

Make executable and run:

```bash
chmod +x morning_routine.sh
./morning_routine.sh
```

### Evening Review (3 minutes)

```bash
# Check signal outcomes
python -m src.cli signals outcomes --days 7

# View portfolio changes
python -m src.cli portfolio history

# Check for alerts
python -m src.cli portfolio alerts
```

### Weekly Learning (10 minutes)

```bash
# Analyze weekly performance
python -m src.cli learning analyze --days 7

# Check for new patterns
python -m src.cli learning patterns

# Get recommendations
python -m src.cli learning recommendations

# Generate and export report
python -m src.cli learning report --type weekly --export

# Update weights if enough data
python -m src.cli learning weights --update
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue: "No module named 'click'"

**Solution:**

```bash
# Activate virtual environment first
source venv/bin/activate

# Then install
pip install click tabulate sqlalchemy
```

#### Issue: "Database not found"

**Solution:**

```bash
python -m src.cli setup
```

#### Issue: "No news articles found"

**Solution:**

```bash
# Scrape news first
python -m src.cli news scrape

# Then list
python -m src.cli news list
```

#### Issue: "yfinance connection error"

**Solution:**

- Check internet connection
- Try again in a few minutes (yfinance rate limits)
- Some tickers may not have data

```bash
# Test with a common ticker
python -m src.cli market quote AAPL
```

#### Issue: "Not enough signals for learning"

**Solution:**

The learning system needs at least 20 signals. Generate more:

```bash
# Generate signals from more days
python -m src.cli signals generate --days 30

# Check count
python -m src.cli signals stats
```

#### Issue: Virtual environment not activating

**Solution:**

```bash
# Deactivate if already in one
deactivate

# Recreate virtual environment
rm -rf venv
python -m venv venv

# Activate
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
```

### Enable Debug Logging

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run command
python -m src.cli <command>

# View logs
tail -f logs/stock_analysis.log
```

### Database Issues

```bash
# Backup existing database
cp data/stock_analysis.db data/stock_analysis.db.backup

# Recreate database
rm data/stock_analysis.db
python -m src.cli setup

# Restore backup if needed
cp data/stock_analysis.db.backup data/stock_analysis.db
```

---

## 🔄 Updates and Maintenance

### Update Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Update all packages
pip install --upgrade click sqlalchemy python-dotenv pyyaml yfinance \
            vaderSentiment nltk textblob feedparser requests \
            beautifulsoup4 tabulate apscheduler pandas
```

### Clean Old Data

```bash
# Remove old signals (keeps last 90 days)
python -m src.cli signals cleanup --days 90

# Check database size
du -h data/stock_analysis.db
```

### Backup Data

```bash
# Create backups directory
mkdir -p backups

# Backup database
cp data/stock_analysis.db backups/stock_analysis_$(date +%Y%m%d).db

# Backup configuration
cp config/config.yaml backups/config_$(date +%Y%m%d).yaml
cp config/.env backups/env_$(date +%Y%m%d).backup
```

---

## 📊 Monitoring

### Check System Health

```bash
# View logs
tail -n 50 logs/stock_analysis.log

# Check database size
du -h data/stock_analysis.db

# Check disk space
df -h
```

### Performance Metrics

```bash
# Signal statistics
python -m src.cli signals stats --days 30

# Learning performance
python -m src.cli learning analyze --days 30

# Portfolio performance
python -m src.cli portfolio view
```

---

## 🎓 Best Practices

### 1. Data Collection

- **Scrape news daily**: Run morning routine every trading day
- **Don't over-scrape**: Once per day is sufficient (respects rate limits)
- **Use free sources**: RSS feeds + yfinance are enough

### 2. Signal Generation

- **Start conservative**: Use min_confidence: 60 initially
- **Review manually**: Signals are suggestions, not commands
- **Track outcomes**: Essential for learning

### 3. Portfolio Management

- **Paper trade first**: Don't use real money while learning
- **Diversify**: Max 10% per position
- **Monitor risks**: Check daily for alerts

### 4. Learning

- **Be patient**: Need 20+ signals before optimization
- **Review patterns**: Check weekly for insights
- **Trust the process**: Learning takes 4-8 weeks to converge

### 5. Maintenance

- **Backup regularly**: Weekly database backups
- **Clean old data**: Monthly cleanup of expired signals
- **Update dependencies**: Monthly package updates
- **Review logs**: Check for errors weekly

---

## 🔒 Security Considerations

### Protect Your API Keys

```bash
# Never commit .env file to git
echo "config/.env" >> .gitignore

# Set proper permissions
chmod 600 config/.env
```

### Database Security

```bash
# Set proper permissions
chmod 600 data/stock_analysis.db

# Only you can read/write
ls -la data/stock_analysis.db
# Should show: -rw------- (600)
```

### Safe Shutdown

```bash
# Always deactivate virtual environment when done
deactivate

# Stop any running processes
# (No background processes in current version)
```

---

## 📈 Scaling Considerations

### Running Multiple Instances

Each instance needs its own:
- Virtual environment
- Database file
- Configuration
- Log directory

```bash
# Create instance 2
mkdir instance2
cd instance2
python -m venv venv
# ... install dependencies ...

# Use different database
# Edit config/config.yaml:
database:
  url: "sqlite:///data/stock_analysis_2.db"
```

### Scheduled Automation

Use cron (Linux/Mac) or Task Scheduler (Windows):

```bash
# Edit crontab
crontab -e

# Add morning routine (8 AM on weekdays)
0 8 * * 1-5 cd /path/to/stock-analysis-agent && ./morning_routine.sh

# Add evening review (5 PM on weekdays)
0 17 * * 1-5 cd /path/to/stock-analysis-agent && ./evening_review.sh

# Add weekly report (Sunday 6 PM)
0 18 * * 0 cd /path/to/stock-analysis-agent && ./weekly_report.sh
```

---

## 🎯 Success Metrics

After successful deployment, you should see:

**Week 1:**
- [ ] Daily news scraping working
- [ ] 5-10 signals generated
- [ ] Portfolio tracking setup
- [ ] Basic outcomes tracked

**Week 4:**
- [ ] 20+ signals tracked
- [ ] First learning insights
- [ ] Pattern discovery beginning
- [ ] Weekly reports generated

**Week 8:**
- [ ] 50+ signals tracked
- [ ] Weight optimization active
- [ ] 5-10 patterns discovered
- [ ] Success rate improving

**Week 12:**
- [ ] 100+ signals tracked
- [ ] Stable weight adjustments
- [ ] 10-15 validated patterns
- [ ] Consistent 60-70% success rate

---

## 📞 Getting Help

### Documentation

- **README.md**: Overview and quick start
- **PHASE1_COMPLETE.md**: Data collection details
- **PHASE2_COMPLETE.md**: Signal generation details
- **PHASE3_COMPLETE.md**: Learning system details

### Command Help

```bash
# General help
python -m src.cli --help

# Command-specific help
python -m src.cli news --help
python -m src.cli signals --help
python -m src.cli portfolio --help
python -m src.cli learning --help
```

### Logs

```bash
# View recent logs
tail -f logs/stock_analysis.log

# Search for errors
grep -i error logs/stock_analysis.log

# View specific date
grep "2025-01-17" logs/stock_analysis.log
```

---

## ✅ Deployment Checklist

Before going live, ensure:

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed
- [ ] NLTK data downloaded
- [ ] Initial setup completed (`python -m src.cli setup`)
- [ ] All tests passing (`python -m src.cli test`)
- [ ] News scraping working
- [ ] First signals generated
- [ ] Portfolio created
- [ ] Backups configured
- [ ] Morning/evening routines scripted
- [ ] Documentation reviewed

---

## 🎉 You're Ready!

Your AI Stock Analysis Agent is now deployed and ready for educational use. Remember:

- This is a **learning tool**, not financial advice
- Start with paper trading
- Be patient with the learning system
- Review and understand all signals manually
- Always consult financial advisors for real trading

**Happy Learning! 📚🚀**
