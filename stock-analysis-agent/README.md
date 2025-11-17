# AI-Powered Stock Market Analysis Agent

**DISCLAIMER: This is an educational and experimental tool only. This system is NOT intended for actual trading decisions. All signals and predictions are for learning purposes only. This is not financial advice.**

## Overview

An intelligent stock market analysis system that:
- Continuously monitors financial news and market data
- Performs sentiment analysis and impact assessment
- Generates investment signals with confidence scoring
- Tracks prediction success/failure for learning
- Monitors portfolio positions for risk protection
- Provides comprehensive dashboard with analytics
- Learns and adapts from historical performance

## Purpose

This is a learning project designed to:
1. Understand market dynamics and catalyst-driven price movements
2. Learn how AI decision-making works in financial contexts
3. Develop systematic pattern recognition skills
4. Build disciplined analysis frameworks
5. Practice risk management with data-driven approaches
6. Continuously improve through iterative learning

## Features

### 1. Market Scanning & News Monitoring
- Multi-source news aggregation (Alpha Vantage, NewsAPI, RSS feeds)
- 15-30 minute scanning intervals
- Company/ticker extraction from articles
- Event classification (earnings, M&A, FDA, contracts, etc.)

### 2. Sentiment Analysis & Impact Assessment
- NLP-based sentiment classification
- Impact magnitude estimation
- Sector and market context consideration
- Sentiment velocity tracking

### 3. Investment Signal Generation
- **Short-term signals** (3-14 days): Momentum plays
- **Long-term signals** (30-180 days): Fundamental value plays
- Comprehensive signal details: entry/target/stop-loss
- Confidence scoring (0-100%)
- Detailed rationale with supporting data

### 4. Success Tracking & Validation
- Rigorous outcome classification
- Peak gain vs predicted tracking
- Sustainability analysis (24h, 48h, 7-day holds)
- Performance metrics by signal type and timeframe

### 5. Portfolio Monitoring & Protection
- Hourly deep analysis of holdings
- Early warning system for risk detection
- Multi-factor risk scoring
- EXIT signal generation with severity levels
- Real-time portfolio P&L tracking

### 6. Retrospective Learning System
- Pattern recognition from historical outcomes
- Success factor analysis
- Dynamic confidence calibration
- Adaptive weight adjustments
- Post-mortem report generation

### 7. Comprehensive Dashboard
- Real-time metrics and alerts
- Interactive performance charts
- Portfolio risk heat maps
- Signal tracking and outcomes
- Learning progress visualization

## Architecture

### Technology Stack
- **Language**: Python 3.11+
- **Database**: SQLite (upgradeable to PostgreSQL)
- **Backend**: FastAPI
- **Frontend**: React with Plotly.js charts
- **NLP**: transformers, nltk, spaCy
- **Data**: yfinance, Alpha Vantage, NewsAPI

### Core Modules
1. **News Scraper** (`src/scrapers/`) - Multi-source news aggregation
2. **Analysis Engine** (`src/analysis/`) - Sentiment and impact assessment
3. **Signal Generator** (`src/signals/`) - Investment opportunity identification
4. **Portfolio Monitor** (`src/portfolio/`) - Risk tracking and alerts
5. **Learning Engine** (`src/learning/`) - Pattern recognition and adaptation
6. **Dashboard** (`src/dashboard/`) - Web interface and visualization

## Installation

### Prerequisites
- Python 3.11 or higher
- pip package manager
- API keys for:
  - Alpha Vantage (free tier available)
  - NewsAPI (free tier available)

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd stock-analysis-agent
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp config/.env.example config/.env
# Edit config/.env with your API keys
```

5. Initialize database:
```bash
python -m src.database.init_db
```

6. Run initial setup:
```bash
python -m src.cli setup
```

## Configuration

Edit `config/settings.yaml` to customize:
- Scanning frequency (default: 30 minutes)
- Portfolio monitoring frequency (default: hourly)
- Risk thresholds
- Minimum confidence for signals (default: 60%)
- Success criteria thresholds
- Alert preferences

## Usage

### Starting the System

1. Start the news scanner:
```bash
python -m src.scrapers.news_scanner
```

2. Start the portfolio monitor:
```bash
python -m src.portfolio.monitor
```

3. Start the dashboard:
```bash
python -m src.dashboard.backend.app
```

4. Access dashboard at: `http://localhost:8000`

### CLI Commands

```bash
# Add portfolio position
python -m src.cli portfolio add --ticker AAPL --shares 100 --price 150.00

# View active signals
python -m src.cli signals list --active

# Run backtest
python -m src.cli backtest --start-date 2023-01-01 --end-date 2024-01-01

# View performance metrics
python -m src.cli metrics --period 30d

# Generate report
python -m src.cli report --type weekly
```

## Database Schema

### Core Tables
- `news_articles` - Scraped and analyzed news
- `market_data` - Price and technical indicators
- `signals_generated` - All prediction signals
- `signal_outcomes` - Validation results
- `portfolio_positions` - User holdings
- `portfolio_monitoring` - Hourly risk analysis
- `learning_patterns` - Discovered patterns
- `performance_metrics` - Aggregated statistics

## Dashboard Features

### Pages
1. **Home** - Overview with key metrics and recent alerts
2. **Signals** - Active and historical predictions
3. **Portfolio** - Holdings with risk analysis
4. **Performance** - Success rate analytics
5. **News Feed** - Recent articles and analysis
6. **Backtest** - Historical performance simulation

### Key Metrics
- Overall success rate
- Success rate by timeframe and signal type
- Average gain on winners vs losses
- Risk-adjusted returns
- Confidence calibration
- Learning progress over time

## Safety Features

- Prominent educational disclaimers
- No automatic trade execution
- All signals require manual review
- Comprehensive risk warnings
- Hypothetical vs actual tracking
- Decision logging for auditing

## Learning System

The agent continuously learns from:
- Prediction outcomes (success/failure)
- Pattern effectiveness over time
- Market condition correlations
- Signal quality by news type
- Optimal entry/exit timing
- Sector-specific behaviors

### Feedback Loop
1. Generate prediction
2. Monitor actual outcome
3. Classify success/failure
4. Extract success factors
5. Adjust model weights
6. Improve future predictions

## Development Phases

- **Phase 1** (Weeks 1-2): Foundation - Structure, DB, basic scraping
- **Phase 2** (Weeks 3-4): Core Intelligence - Signal generation, tracking
- **Phase 3** (Weeks 5-6): Learning System - Pattern recognition, backtesting
- **Phase 4** (Weeks 7-8): Dashboard & Alerts - Full web interface
- **Phase 5** (Weeks 9-10): Refinement - Advanced features, optimization
- **Phase 6** (Ongoing): Continuous learning and adaptation

## Testing

Run tests:
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=src tests/
```

## Contributing

This is a personal learning project, but suggestions and improvements are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## Logging

Logs are stored in `logs/` directory:
- `logs/scanner.log` - News scraping activity
- `logs/signals.log` - Signal generation
- `logs/portfolio.log` - Portfolio monitoring
- `logs/learning.log` - Learning system updates
- `logs/errors.log` - Error tracking

## Troubleshooting

Common issues:

1. **API Rate Limits**: Free tier APIs have limits. Configure longer intervals.
2. **Missing Data**: Some tickers may not have complete data.
3. **Network Errors**: Scrapers include retry logic with exponential backoff.
4. **Database Locks**: Use connection pooling if concurrent access issues occur.

## Roadmap

Future enhancements:
- [ ] Machine learning models for sentiment analysis
- [ ] Options chain analysis
- [ ] Crypto market support
- [ ] Multi-portfolio management
- [ ] Mobile app for alerts
- [ ] Advanced technical indicators
- [ ] Social media sentiment integration
- [ ] Institutional flow tracking

## License

MIT License - See LICENSE file

## Disclaimer

**THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL PURPOSES ONLY.**

The creators and contributors of this software:
- Make NO warranties about accuracy or reliability
- Accept NO liability for financial losses
- Do NOT provide investment advice
- Do NOT recommend this for actual trading decisions

Stock market investing carries substantial risk of loss. Past performance does not guarantee future results. Always consult with qualified financial advisors before making investment decisions.

## Contact

For questions or issues, please open a GitHub issue.

---

**Remember: This is a learning tool. Learn, experiment, and understand - but always make real investment decisions with professional guidance.**
