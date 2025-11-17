"""
Command Line Interface for Stock Analysis Agent
Allows testing and manual control of all components
"""

import click
import sys
from pathlib import Path
from datetime import datetime, timedelta
from tabulate import tabulate

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config.config_loader import get_config, reload_config
from src.database.models import init_database
from src.scrapers.news_scraper import NewsAggregator
from src.analysis.sentiment_analyzer import ArticleAnalyzer
from src.scrapers.market_data_collector import MarketDataService
from src.utils.logger import get_logger


logger = get_logger("cli")


# ============================================================================
# MAIN CLI GROUP
# ============================================================================

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    Stock Analysis Agent CLI

    Educational tool for learning market dynamics and AI decision-making.
    NOT for actual trading decisions.
    """
    # Show disclaimer
    click.echo("=" * 70)
    click.echo("Stock Analysis Agent - EDUCATIONAL TOOL ONLY")
    click.echo("=" * 70)
    click.echo("⚠  This is for learning purposes only")
    click.echo("⚠  NOT financial advice. NOT for actual trading decisions.")
    click.echo("=" * 70)
    click.echo()


# ============================================================================
# SETUP COMMANDS
# ============================================================================

@cli.command()
def setup():
    """Initial setup - create database and check configuration"""
    click.echo("Setting up Stock Analysis Agent...")
    click.echo()

    # 1. Check configuration
    click.echo("1. Checking configuration...")
    config = get_config()
    config.print_status()

    # 2. Create database
    click.echo("\n2. Setting up database...")
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    db_path = data_dir / "stock_analysis.db"
    database_url = f"sqlite:///{db_path}"

    if db_path.exists():
        if click.confirm(f"Database exists at {db_path}. Recreate?", default=False):
            db_path.unlink()
            init_database(database_url)
        else:
            click.echo("Keeping existing database.")
    else:
        init_database(database_url)

    # 3. Create log directory
    click.echo("\n3. Setting up logging...")
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    click.echo(f"✓ Log directory: {log_dir}")

    # 4. Check API keys
    click.echo("\n4. Checking API keys...")
    api_status = config.validate_api_keys()

    if not any(api_status.values()):
        click.echo("\n⚠  Warning: No API keys configured!")
        click.echo("   You can still use FREE unlimited sources (RSS feeds, yfinance)")
        click.echo(f"   To add API keys, edit: {project_root / 'config' / '.env'}")
    else:
        click.echo("✓ Some API keys configured")

    click.echo("\n" + "=" * 70)
    click.echo("Setup complete! You can now use the CLI commands.")
    click.echo("=" * 70)
    click.echo("\nNext steps:")
    click.echo("  • Test news scraper: python -m src.cli news scan")
    click.echo("  • Get stock quote: python -m src.cli market quote AAPL")
    click.echo("  • Analyze article: python -m src.cli analyze article")
    click.echo()


@cli.command()
def config():
    """Show current configuration"""
    cfg = get_config()
    cfg.print_status()


# ============================================================================
# NEWS COMMANDS
# ============================================================================

@cli.group()
def news():
    """News scraping and analysis commands"""
    pass


@news.command()
@click.option('--max-articles', default=20, help='Maximum articles to fetch')
@click.option('--use-newsapi', is_flag=True, help='Use NewsAPI (uses daily quota)')
def scan(max_articles, use_newsapi):
    """Scan for latest financial news"""
    click.echo(f"Scanning for news (max {max_articles} articles)...")
    click.echo()

    aggregator = NewsAggregator()

    # Fetch news
    with click.progressbar(length=max_articles, label='Fetching news') as bar:
        articles = aggregator.fetch_latest_news(
            max_articles=max_articles,
            use_newsapi=use_newsapi
        )
        bar.update(len(articles))

    if not articles:
        click.echo("No articles found.")
        return

    # Display articles
    click.echo(f"\nFound {len(articles)} articles:\n")

    for i, article in enumerate(articles, 1):
        click.echo(f"{i}. {article.title}")
        click.echo(f"   Source: {article.source_name}")
        click.echo(f"   Published: {article.published_date}")
        click.echo(f"   Tickers: {', '.join(article.tickers) if article.tickers else 'None'}")
        click.echo(f"   URL: {article.url}")
        click.echo()


@news.command()
@click.argument('ticker')
@click.option('--max-articles', default=10, help='Maximum articles to fetch')
def ticker(ticker, max_articles):
    """Get news for a specific ticker"""
    ticker = ticker.upper()
    click.echo(f"Fetching news for {ticker}...")
    click.echo()

    aggregator = NewsAggregator()
    articles = aggregator.fetch_ticker_news(ticker, max_articles=max_articles)

    if not articles:
        click.echo(f"No news found for {ticker}")
        return

    click.echo(f"Found {len(articles)} articles about {ticker}:\n")

    for i, article in enumerate(articles, 1):
        click.echo(f"{i}. {article.title}")
        click.echo(f"   {article.source_name} - {article.published_date}")
        click.echo()


# ============================================================================
# MARKET DATA COMMANDS
# ============================================================================

@cli.group()
def market():
    """Market data and stock information commands"""
    pass


@market.command()
@click.argument('ticker')
def quote(ticker):
    """Get current quote for a ticker"""
    ticker = ticker.upper()
    click.echo(f"Fetching quote for {ticker}...")
    click.echo()

    service = MarketDataService()
    quote_data = service.stock_collector.get_quote(ticker)

    if not quote_data:
        click.echo(f"Could not fetch quote for {ticker}")
        return

    # Display quote
    click.echo(f"{'='*60}")
    click.echo(f"{quote_data.get('company_name', ticker)} ({ticker})")
    click.echo(f"{'='*60}")
    click.echo()

    price = quote_data.get('current_price')
    change = quote_data.get('change')
    change_pct = quote_data.get('change_percent')

    if price:
        click.echo(f"Price: ${price:.2f}")

    if change and change_pct:
        color = 'green' if change > 0 else 'red'
        sign = '+' if change > 0 else ''
        click.secho(f"Change: {sign}${change:.2f} ({sign}{change_pct:.2f}%)", fg=color)

    click.echo()
    click.echo(f"Open: ${quote_data.get('open', 0):.2f}")
    click.echo(f"High: ${quote_data.get('high', 0):.2f}")
    click.echo(f"Low: ${quote_data.get('low', 0):.2f}")
    click.echo(f"Previous Close: ${quote_data.get('previous_close', 0):.2f}")
    click.echo()
    click.echo(f"Volume: {quote_data.get('volume', 0):,}")
    click.echo(f"Avg Volume: {quote_data.get('avg_volume', 0):,}")

    if quote_data.get('market_cap'):
        market_cap_b = quote_data['market_cap'] / 1_000_000_000
        click.echo(f"Market Cap: ${market_cap_b:.2f}B")

    if quote_data.get('sector'):
        click.echo(f"\nSector: {quote_data['sector']}")

    if quote_data.get('industry'):
        click.echo(f"Industry: {quote_data['industry']}")


@market.command()
@click.argument('ticker')
def indicators(ticker):
    """Get technical indicators for a ticker"""
    ticker = ticker.upper()
    click.echo(f"Calculating technical indicators for {ticker}...")
    click.echo()

    service = MarketDataService()
    indicators_data = service.indicator_calculator.get_latest_indicators(ticker)

    if not indicators_data:
        click.echo(f"Could not calculate indicators for {ticker}")
        return

    click.echo(f"Technical Indicators for {ticker}:")
    click.echo(f"{'='*60}")
    click.echo()

    # RSI
    rsi = indicators_data.get('rsi')
    if rsi:
        if rsi > 70:
            status = click.style("OVERBOUGHT", fg='red')
        elif rsi < 30:
            status = click.style("OVERSOLD", fg='green')
        else:
            status = "NEUTRAL"
        click.echo(f"RSI (14): {rsi:.2f} - {status}")

    # MACD
    macd = indicators_data.get('macd')
    macd_signal = indicators_data.get('macd_signal')
    if macd and macd_signal:
        trend = "BULLISH" if macd > macd_signal else "BEARISH"
        color = 'green' if macd > macd_signal else 'red'
        click.echo(f"MACD: {macd:.2f} | Signal: {macd_signal:.2f} - {click.style(trend, fg=color)}")

    # Moving Averages
    click.echo("\nMoving Averages:")
    if indicators_data.get('sma_20'):
        click.echo(f"  SMA 20:  ${indicators_data['sma_20']:.2f}")
    if indicators_data.get('sma_50'):
        click.echo(f"  SMA 50:  ${indicators_data['sma_50']:.2f}")
    if indicators_data.get('sma_200'):
        click.echo(f"  SMA 200: ${indicators_data['sma_200']:.2f}")

    # Bollinger Bands
    bb_upper = indicators_data.get('bb_upper')
    bb_lower = indicators_data.get('bb_lower')
    if bb_upper and bb_lower:
        click.echo(f"\nBollinger Bands:")
        click.echo(f"  Upper: ${bb_upper:.2f}")
        click.echo(f"  Lower: ${bb_lower:.2f}")


@market.command()
@click.argument('ticker')
@click.option('--hours', default=24, help='Hours to analyze')
def movement(ticker, hours):
    """Analyze price movement over recent period"""
    ticker = ticker.upper()
    click.echo(f"Analyzing {hours}h price movement for {ticker}...")
    click.echo()

    service = MarketDataService()
    movement_data = service.analyze_price_movement(ticker, hours_back=hours)

    if not movement_data:
        click.echo(f"Could not analyze movement for {ticker}")
        return

    click.echo(f"Price Movement Analysis ({hours}h):")
    click.echo(f"{'='*60}")
    click.echo()

    change_pct = movement_data.get('change_percent', 0)
    color = 'green' if change_pct > 0 else 'red'
    sign = '+' if change_pct > 0 else ''

    click.echo(f"Start Price: ${movement_data['start_price']:.2f}")
    click.echo(f"Current Price: ${movement_data['current_price']:.2f}")
    click.secho(f"Change: {sign}{change_pct:.2f}%", fg=color)
    click.echo()

    click.echo(f"Peak: ${movement_data['peak_price']:.2f}")
    click.echo(f"Trough: ${movement_data['trough_price']:.2f}")
    click.echo()

    click.echo(f"Volatility: {movement_data['volatility']:.2f}%")
    click.echo(f"Volume Ratio: {movement_data['volume_ratio']:.2f}x average")

    if movement_data.get('is_unusual_volume'):
        click.secho("\n⚠  UNUSUAL VOLUME DETECTED", fg='yellow', bold=True)


# ============================================================================
# ANALYSIS COMMANDS
# ============================================================================

@cli.group()
def analyze():
    """Analysis and sentiment commands"""
    pass


@analyze.command()
def article():
    """Analyze sentiment of a news article"""
    click.echo("Article Sentiment Analysis")
    click.echo("=" * 60)
    click.echo()

    # Get input
    title = click.prompt("Article title")
    content = click.prompt("Article content (or summary)")
    tickers_input = click.prompt("Tickers mentioned (comma-separated)", default="")

    tickers = [t.strip().upper() for t in tickers_input.split(",")] if tickers_input else []

    # Analyze
    click.echo("\nAnalyzing...")
    analyzer = ArticleAnalyzer()
    result = analyzer.analyze_article(title, content, tickers)

    # Display results
    click.echo("\nAnalysis Results:")
    click.echo("=" * 60)

    sentiment_type = result['sentiment_type']
    if sentiment_type == 'positive':
        color = 'green'
    elif sentiment_type == 'negative':
        color = 'red'
    else:
        color = 'yellow'

    click.echo(f"Sentiment: {click.style(sentiment_type.upper(), fg=color)}")
    click.echo(f"Score: {result['sentiment_score']:.3f}")
    click.echo(f"Confidence: {result['sentiment_confidence']:.3f}")
    click.echo()

    if result.get('event_type'):
        click.echo(f"Event Type: {result['event_type']}")

    click.echo(f"Impact: {result['impact_magnitude']}")
    click.echo(f"Relevance: {result['relevance_score']:.3f}")

    if result.get('tickers_mentioned'):
        click.echo(f"Tickers: {', '.join(result['tickers_mentioned'])}")


@analyze.command()
@click.argument('ticker')
def stock(ticker):
    """Complete analysis of a stock (news + market data)"""
    ticker = ticker.upper()
    click.echo(f"Complete Analysis for {ticker}")
    click.echo("=" * 60)
    click.echo()

    # 1. Get quote
    click.echo("1. Market Data:")
    click.echo("-" * 60)
    service = MarketDataService()
    quote_data = service.stock_collector.get_quote(ticker)

    if quote_data:
        price = quote_data.get('current_price')
        change_pct = quote_data.get('change_percent')
        click.echo(f"Price: ${price:.2f} ({change_pct:+.2f}%)")
    else:
        click.echo("Could not fetch market data")

    # 2. Get news
    click.echo("\n2. Recent News:")
    click.echo("-" * 60)
    aggregator = NewsAggregator()
    articles = aggregator.fetch_ticker_news(ticker, max_articles=5)

    if articles:
        analyzer = ArticleAnalyzer()
        for i, article in enumerate(articles, 1):
            click.echo(f"\n{i}. {article.title}")

            # Analyze sentiment
            result = analyzer.analyze_article(article.title, article.content, article.tickers)
            sentiment = result['sentiment_type']

            if sentiment == 'positive':
                color = 'green'
                symbol = '↑'
            elif sentiment == 'negative':
                color = 'red'
                symbol = '↓'
            else:
                color = 'yellow'
                symbol = '='

            click.echo(f"   Sentiment: {click.style(f'{symbol} {sentiment}', fg=color)} "
                      f"(score: {result['sentiment_score']:.2f})")
    else:
        click.echo("No recent news found")

    # 3. Get technical indicators
    click.echo("\n3. Technical Indicators:")
    click.echo("-" * 60)
    indicators_data = service.indicator_calculator.get_latest_indicators(ticker)

    if indicators_data:
        rsi = indicators_data.get('rsi')
        if rsi:
            click.echo(f"RSI: {rsi:.2f}")

        macd = indicators_data.get('macd')
        macd_signal = indicators_data.get('macd_signal')
        if macd and macd_signal:
            trend = "Bullish" if macd > macd_signal else "Bearish"
            click.echo(f"MACD Trend: {trend}")
    else:
        click.echo("Could not fetch indicators")

    # 4. Unusual activity check
    click.echo("\n4. Unusual Activity Check:")
    click.echo("-" * 60)
    unusual = service.detect_unusual_activity(ticker)

    if unusual.get('unusual_activity'):
        click.secho(f"⚠  UNUSUAL ACTIVITY DETECTED", fg='yellow', bold=True)
        for flag in unusual.get('flags', []):
            click.echo(f"   • {flag}")
    else:
        click.echo("No unusual activity detected")

    click.echo()


# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@cli.command()
def test():
    """Run system tests"""
    click.echo("Running system tests...")
    click.echo()

    # Test 1: Configuration
    click.echo("1. Testing configuration...")
    try:
        config = get_config()
        click.secho("   ✓ Configuration loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Configuration failed: {e}", fg='red')

    # Test 2: Database
    click.echo("\n2. Testing database...")
    try:
        from src.database.models import Base
        click.secho(f"   ✓ Database models loaded ({len(Base.metadata.tables)} tables)", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Database test failed: {e}", fg='red')

    # Test 3: News scraping
    click.echo("\n3. Testing news scraper...")
    try:
        aggregator = NewsAggregator()
        articles = aggregator.rss_scraper.scrape_all_feeds()
        click.secho(f"   ✓ News scraper working ({len(articles)} articles)", fg='green')
    except Exception as e:
        click.secho(f"   ✗ News scraper failed: {e}", fg='red')

    # Test 4: Market data
    click.echo("\n4. Testing market data...")
    try:
        service = MarketDataService()
        quote = service.stock_collector.get_quote("AAPL")
        if quote and quote.get('current_price'):
            click.secho(f"   ✓ Market data working (AAPL: ${quote['current_price']:.2f})", fg='green')
        else:
            click.secho("   ✗ Market data returned empty", fg='red')
    except Exception as e:
        click.secho(f"   ✗ Market data failed: {e}", fg='red')

    # Test 5: Sentiment analysis
    click.echo("\n5. Testing sentiment analysis...")
    try:
        analyzer = ArticleAnalyzer()
        result = analyzer.analyze_article(
            "Company beats earnings expectations",
            "Strong revenue growth reported",
            ["TEST"]
        )
        if result.get('sentiment_type'):
            click.secho(f"   ✓ Sentiment analysis working", fg='green')
        else:
            click.secho("   ✗ Sentiment analysis returned empty", fg='red')
    except Exception as e:
        click.secho(f"   ✗ Sentiment analysis failed: {e}", fg='red')

    click.echo("\nTest complete!")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    cli()
