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
# PORTFOLIO COMMANDS (Phase 2)
# ============================================================================

@cli.group()
def portfolio():
    """Portfolio management commands"""
    pass


@portfolio.command()
@click.argument('ticker')
@click.argument('shares', type=float)
@click.argument('price', type=float)
@click.option('--type', 'inv_type', type=click.Choice(['short_term', 'long_term']), default='long_term')
@click.option('--notes', default=None, help='Optional notes')
def add(ticker, shares, price, inv_type, notes):
    """Add a position to portfolio"""
    from src.portfolio.portfolio_manager import PortfolioManager

    ticker = ticker.upper()
    click.echo(f"Adding position: {ticker}, {shares} shares @ ${price:.2f}")

    manager = PortfolioManager()
    position = manager.add_position(
        ticker=ticker,
        shares=shares,
        purchase_price=price,
        investment_type=inv_type,
        notes=notes
    )

    click.secho(f"\n✓ Position added successfully!", fg='green')
    click.echo(f"Position ID: {position.id}")
    click.echo(f"Company: {position.company_name}")
    click.echo(f"Cost Basis: ${position.purchase_price * position.shares:.2f}")


@portfolio.command()
@click.argument('position_id', type=int)
@click.option('--price', type=float, help='Exit price (default: current market price)')
@click.option('--reason', default='Manual exit', help='Exit reason')
def remove(position_id, price, reason):
    """Remove/close a position"""
    from src.portfolio.portfolio_manager import PortfolioManager

    manager = PortfolioManager()

    click.echo(f"Closing position ID {position_id}...")

    position = manager.remove_position(
        position_id=position_id,
        exit_price=price,
        exit_reason=reason
    )

    click.secho(f"\n✓ Position closed!", fg='green')
    click.echo(f"Ticker: {position.ticker}")
    click.echo(f"Exit Price: ${position.exit_price:.2f}")

    if position.realized_gain_loss_pct:
        color = 'green' if position.realized_gain_loss_pct > 0 else 'red'
        click.secho(f"Realized P&L: ${position.realized_gain_loss_dollar:.2f} "
                   f"({position.realized_gain_loss_pct:+.2f}%)", fg=color)


@portfolio.command(name='list')
@click.option('--status', type=click.Choice(['active', 'closed']), default='active')
def list_positions(status):
    """List portfolio positions"""
    from src.portfolio.portfolio_manager import PortfolioManager
    from src.utils.helpers import format_currency, format_percentage

    manager = PortfolioManager()
    positions = manager.get_all_positions(status=status)

    if not positions:
        click.echo(f"No {status} positions")
        return

    # Update prices
    manager.update_position_prices(positions)

    click.echo(f"\n{status.upper()} POSITIONS ({len(positions)}):")
    click.echo("=" * 100)

    # Prepare table data
    headers = ['ID', 'Ticker', 'Shares', 'Entry', 'Current', 'P&L $', 'P&L %', 'Days', 'Risk']
    rows = []

    for p in positions:
        if status == 'active':
            pnl_dollar = p.unrealized_gain_loss_dollar or 0
            pnl_pct = p.unrealized_gain_loss_pct or 0
            current_price = p.current_price or p.purchase_price
            risk = p.current_risk_level.value if p.current_risk_level else '-'
        else:
            pnl_dollar = p.realized_gain_loss_dollar or 0
            pnl_pct = p.realized_gain_loss_pct or 0
            current_price = p.exit_price or p.purchase_price
            risk = '-'

        rows.append([
            p.id,
            p.ticker,
            f"{p.shares:.0f}",
            f"${p.purchase_price:.2f}",
            f"${current_price:.2f}",
            format_currency(pnl_dollar),
            format_percentage(pnl_pct),
            p.days_held or 0,
            risk
        ])

    click.echo(tabulate(rows, headers=headers, tablefmt='simple'))


@portfolio.command()
def summary():
    """Show portfolio summary"""
    from src.portfolio.portfolio_manager import PortfolioManager
    from src.utils.helpers import format_currency, format_percentage

    manager = PortfolioManager()
    summary_data = manager.get_portfolio_summary()

    if summary_data.get('total_positions', 0) == 0:
        click.echo("Portfolio is empty")
        click.echo("\nAdd a position:")
        click.echo("  python -m src.cli portfolio add AAPL 10 150.00")
        return

    click.echo("\nPORTFOLIO SUMMARY:")
    click.echo("=" * 60)

    click.echo(f"\nTotal Positions: {summary_data['total_positions']}")
    click.echo(f"  • Profitable: {summary_data['positions_profitable']}")
    click.echo(f"  • Losing: {summary_data['positions_losing']}")

    click.echo(f"\nInvestment:")
    click.echo(f"  Total Invested: {format_currency(summary_data['total_invested'])}")
    click.echo(f"  Current Value:  {format_currency(summary_data['current_value'])}")

    pnl = summary_data['total_gain_loss']
    pnl_pct = summary_data['total_gain_loss_pct']
    color = 'green' if pnl > 0 else 'red'
    click.echo(f"  Total P&L:      {click.style(format_currency(pnl), fg=color)} "
              f"({click.style(format_percentage(pnl_pct), fg=color)})")

    if summary_data.get('best_performer'):
        best = summary_data['best_performer']
        click.echo(f"\nBest Performer: {best['ticker']} "
                  f"({format_currency(best['gain_dollar'])}, {format_percentage(best['gain_pct'])})")

    if summary_data.get('worst_performer'):
        worst = summary_data['worst_performer']
        click.echo(f"Worst Performer: {worst['ticker']} "
                  f"({format_currency(worst['loss_dollar'])}, {format_percentage(worst['loss_pct'])})")


# ============================================================================
# SIGNAL COMMANDS (Phase 2)
# ============================================================================

@cli.group()
def signals():
    """Investment signal management commands"""
    pass


@signals.command()
@click.option('--max-signals', default=5, help='Maximum signals to generate')
@click.option('--use-newsapi', is_flag=True, help='Use NewsAPI (consumes quota)')
def scan(max_signals, use_newsapi):
    """Scan for new investment signals"""
    from src.signals.signal_generator import SignalGenerator
    from src.signals.signal_tracker import SignalTracker

    click.echo("Scanning for investment signals...")
    click.echo("(This may take a minute...)\n")

    generator = SignalGenerator()
    tracker = SignalTracker()

    # Generate signals
    signals = generator.scan_for_signals(
        max_signals=max_signals,
        use_newsapi=use_newsapi
    )

    if not signals:
        click.echo("No signals generated")
        click.echo("\nThis could mean:")
        click.echo("  • No strong catalysts in recent news")
        click.echo("  • All potential signals below confidence threshold")
        click.echo("  • Try again during market hours or after major news")
        return

    click.secho(f"\n✓ Generated {len(signals)} signal(s)!", fg='green')
    click.echo("=" * 80)

    # Save and display signals
    for i, signal in enumerate(signals, 1):
        # Save to database
        saved_signal = tracker.save_signal(signal)

        click.echo(f"\nSIGNAL #{i} (ID: {saved_signal.id})")
        click.echo("-" * 80)
        click.echo(f"Ticker: {signal['ticker']} ({signal['company_name']})")
        click.echo(f"Type: {signal['signal_type'].upper()} ({signal['timeframe_days']} days)")
        click.echo(f"Confidence: {signal['confidence']:.0f}%")
        click.echo()
        click.echo(f"Entry Price: ${signal['entry_price']:.2f}")
        click.echo(f"Target: ${signal['target_price']:.2f} ({signal['expected_gain_pct']:+.1f}%)")
        click.echo(f"Stop Loss: ${signal['stop_loss']:.2f}")
        click.echo()
        click.echo(f"Catalyst: {signal['news_title'][:70]}...")
        click.echo(f"Event Type: {signal.get('catalyst_type', 'N/A')}")

    click.echo("\n" + "=" * 80)
    click.echo("\nSignals saved to database. Track with:")
    click.echo("  python -m src.cli signals list --active")


@signals.command(name='list')
@click.option('--active', is_flag=True, help='Show only active signals')
@click.option('--limit', default=10, help='Number of signals to show')
def list_signals(active, limit):
    """List generated signals"""
    from src.signals.signal_tracker import SignalTracker
    from src.database.models import SignalGenerated, SignalStatus

    tracker = SignalTracker()

    query = tracker.session.query(SignalGenerated)

    if active:
        query = query.filter_by(status=SignalStatus.ACTIVE)

    signals = query.order_by(SignalGenerated.timestamp.desc()).limit(limit).all()

    if not signals:
        click.echo("No signals found")
        click.echo("\nGenerate signals:")
        click.echo("  python -m src.cli signals scan")
        return

    click.echo(f"\nSIGNALS ({len(signals)}):")
    click.echo("=" * 100)

    headers = ['ID', 'Date', 'Ticker', 'Type', 'Entry', 'Target', 'Exp. Gain', 'Conf.', 'Status']
    rows = []

    for s in signals:
        rows.append([
            s.id,
            s.timestamp.strftime('%m/%d'),
            s.ticker,
            s.signal_type.value[:5],
            f"${s.entry_price:.2f}",
            f"${s.target_price:.2f}",
            f"{s.expected_gain_pct:+.1f}%",
            f"{s.confidence:.0f}%",
            s.status.value
        ])

    click.echo(tabulate(rows, headers=headers, tablefmt='simple'))


@signals.command()
@click.option('--all', 'track_all', is_flag=True, help='Track all active signals')
@click.argument('signal_id', type=int, required=False)
def track(signal_id, track_all):
    """Track signal progress"""
    from src.signals.signal_tracker import SignalTracker

    tracker = SignalTracker()

    if track_all:
        results = tracker.track_all_active_signals()

        if not results:
            click.echo("No active signals to track")
            return

        click.echo(f"\nTRACKING {len(results)} ACTIVE SIGNAL(S):")
        click.echo("=" * 90)

        for r in results:
            status_symbol = "✓" if r['current_gain_pct'] > 0 else "✗"
            color = 'green' if r['current_gain_pct'] > 0 else 'red'

            click.echo(f"\n{status_symbol} Signal #{r['signal_id']}: {r['ticker']}")
            click.echo(f"  Entry: ${r['entry_price']:.2f} | Current: ${r['current_price']:.2f}")
            click.echo(f"  Target: ${r['target_price']:.2f}")
            click.secho(f"  Current Gain: {r['current_gain_pct']:+.1f}% (Expected: {r['expected_gain_pct']:.1f}%)", fg=color)
            click.echo(f"  Progress: Day {r['days_elapsed']} of {r['days_elapsed'] + r['days_remaining']}")

            if r['target_achieved']:
                click.secho("  🎯 TARGET ACHIEVED!", fg='green', bold=True)
            if r['stop_loss_hit']:
                click.secho("  ⚠️  STOP LOSS HIT!", fg='red', bold=True)

    elif signal_id:
        result = tracker.track_signal(signal_id)

        if not result:
            click.echo(f"Signal {signal_id} not found")
            return

        click.echo(f"\nSIGNAL #{result['signal_id']}: {result['ticker']}")
        click.echo("=" * 60)
        click.echo(f"Status: {result['status'].upper()}")
        click.echo(f"\nPrices:")
        click.echo(f"  Entry:   ${result['entry_price']:.2f}")
        click.echo(f"  Current: ${result['current_price']:.2f}")
        click.echo(f"  Target:  ${result['target_price']:.2f}")
        click.echo(f"  Stop:    ${result['stop_loss']:.2f}")

        color = 'green' if result['current_gain_pct'] > 0 else 'red'
        click.echo(f"\nPerformance:")
        click.secho(f"  Current Gain: {result['current_gain_pct']:+.1f}%", fg=color)
        click.echo(f"  Expected Gain: {result['expected_gain_pct']:.1f}%")
        click.echo(f"  Confidence: {result['confidence']:.0f}%")

        click.echo(f"\nTimeframe:")
        click.echo(f"  Elapsed: {result['days_elapsed']} days ({result['hours_elapsed']:.0f} hours)")
        click.echo(f"  Remaining: {result['days_remaining']} days")

        if result['target_achieved']:
            click.secho("\n✓ TARGET ACHIEVED!", fg='green', bold=True)
        if result['stop_loss_hit']:
            click.secho("\n✗ STOP LOSS HIT!", fg='red', bold=True)

    else:
        click.echo("Specify --all or provide a signal ID")
        click.echo("\nExamples:")
        click.echo("  python -m src.cli signals track --all")
        click.echo("  python -m src.cli signals track 1")


@signals.command()
@click.argument('signal_id', type=int)
def validate(signal_id):
    """Validate a signal outcome"""
    from src.signals.signal_tracker import SignalTracker

    click.echo(f"Validating signal {signal_id}...")

    tracker = SignalTracker()
    outcome = tracker.validate_signal(signal_id)

    if not outcome:
        click.echo("Could not validate signal")
        return

    click.secho(f"\n✓ Signal validated!", fg='green')
    click.echo("=" * 60)

    click.echo(f"\nOutcome: {outcome.final_outcome.upper()}")

    if outcome.success_flag:
        click.secho("Result: SUCCESS", fg='green', bold=True)
    else:
        click.secho("Result: FAILURE", fg='red', bold=True)

    click.echo(f"\nPerformance:")
    click.echo(f"  Peak Gain: {outcome.peak_gain_pct:+.1f}%")
    click.echo(f"  Final Gain: {outcome.actual_gain_pct:+.1f}%")
    click.echo(f"  Time to Peak: {outcome.time_to_peak_hours:.1f} hours")
    click.echo(f"  Gain Sustained 24h: {'Yes' if outcome.gain_sustained_24h else 'No'}")

    click.echo(f"\nLessons Learned:")
    click.echo(outcome.lessons_learned)


@signals.command()
def performance():
    """Show signal performance summary"""
    from src.signals.signal_tracker import SignalTracker

    tracker = SignalTracker()
    summary = tracker.get_signal_performance_summary()

    if summary.get('total_signals', 0) == 0:
        click.echo("No completed signals yet")
        click.echo("\nGenerate and wait for signals to complete:")
        click.echo("  python -m src.cli signals scan")
        return

    click.echo("\nSIGNAL PERFORMANCE SUMMARY:")
    click.echo("=" * 60)

    click.echo(f"\nOverall:")
    click.echo(f"  Total Signals: {summary['total_signals']}")
    click.echo(f"  Successful: {summary['successful_signals']}")
    click.echo(f"  Unsuccessful: {summary['unsuccessful_signals']}")

    success_rate = summary['success_rate']
    color = 'green' if success_rate >= 60 else 'yellow' if success_rate >= 40 else 'red'
    click.secho(f"  Success Rate: {success_rate:.1f}%", fg=color, bold=True)

    click.echo(f"\nReturns:")
    click.echo(f"  Avg Gain (Winners): {summary['avg_gain_winners']:+.1f}%")
    click.echo(f"  Avg Loss (Losers): {summary['avg_loss_losers']:+.1f}%")

    click.echo(f"\nBy Timeframe:")
    click.echo(f"  Short-term: {summary['short_term']['success_rate']:.1f}% "
              f"({summary['short_term']['successful']}/{summary['short_term']['total']})")
    click.echo(f"  Long-term:  {summary['long_term']['success_rate']:.1f}% "
              f"({summary['long_term']['successful']}/{summary['long_term']['total']})")


# ============================================================================
# MONITORING COMMANDS (Phase 2)
# ============================================================================

@cli.group()
def monitor():
    """Portfolio monitoring and alerts"""
    pass


@monitor.command()
def run():
    """Run portfolio monitoring"""
    from src.portfolio.portfolio_monitor import PortfolioMonitor

    click.echo("Running portfolio monitoring...")
    click.echo()

    monitor = PortfolioMonitor()
    results = monitor.monitor_all_positions()

    if not results:
        click.echo("No positions to monitor")
        click.echo("\nAdd a position first:")
        click.echo("  python -m src.cli portfolio add AAPL 10 150.00")
        return

    click.echo(f"MONITORING RESULTS ({len(results)} positions):")
    click.echo("=" * 80)

    for r in results:
        risk_level = r['risk_level'].upper()

        if risk_level == 'CRITICAL':
            color = 'red'
            symbol = '🔴'
        elif risk_level == 'HIGH':
            color = 'red'
            symbol = '🟠'
        elif risk_level == 'MEDIUM':
            color = 'yellow'
            symbol = '🟡'
        else:
            color = 'green'
            symbol = '🟢'

        click.echo(f"\n{symbol} {r['ticker']} - {click.style(risk_level, fg=color)} RISK")
        click.echo(f"  Risk Score: {r['risk_score']:.0f}/100")
        click.echo(f"  Action: {r['action_recommended']}")

        if r['alert_generated']:
            click.secho(f"  ⚠️  ALERT GENERATED!", fg='yellow', bold=True)

        if r['risk_factors']:
            click.echo(f"  Top Risk Factors:")
            for factor in r['risk_factors'][:3]:
                click.echo(f"    • {factor}")

        if r['alternatives']:
            click.echo(f"  Suggested Alternatives: {', '.join(r['alternatives'])}")


@monitor.command()
@click.option('--min-risk', type=click.Choice(['low', 'medium', 'high', 'critical']), default='medium')
def alerts(min_risk):
    """Show current portfolio alerts"""
    from src.portfolio.portfolio_monitor import PortfolioMonitor

    monitor = PortfolioMonitor()
    alerts_list = monitor.get_all_alerts(min_risk_level=min_risk)

    if not alerts_list:
        click.secho(f"\n✓ No {min_risk}+ risk alerts", fg='green')
        click.echo("All positions within acceptable risk levels")
        return

    click.echo(f"\nACTIVE ALERTS ({len(alerts_list)} positions):")
    click.echo("=" * 80)

    for alert in alerts_list:
        risk_level = alert['risk_level'].upper()

        if risk_level == 'CRITICAL':
            symbol = '🔴'
            color = 'red'
        elif risk_level == 'HIGH':
            symbol = '🟠'
            color = 'red'
        else:
            symbol = '🟡'
            color = 'yellow'

        click.echo(f"\n{symbol} {alert['ticker']} - {click.style(risk_level, fg=color, bold=True)}")
        click.echo(f"  Risk Score: {alert['risk_score']:.0f}/100")
        click.echo(f"  Action: {alert['action']}")
        click.echo(f"  Current Price: ${alert['current_price']:.2f}")

        if alert['unrealized_pnl']:
            pnl_color = 'green' if alert['unrealized_pnl'] > 0 else 'red'
            click.secho(f"  Current P&L: {alert['unrealized_pnl']:+.1f}%", fg=pnl_color)

        click.echo(f"\n  Summary:")
        for line in alert['summary'].split('\n')[:5]:
            click.echo(f"  {line}")


# ============================================================================
# LEARNING COMMANDS (PHASE 3)
# ============================================================================

@cli.group()
def learning():
    """Learning engine and adaptive system commands"""
    pass


@learning.command(name='analyze')
@click.option('--days', default=30, help='Days to analyze (default: 30)')
def learning_analyze(days):
    """Analyze system performance and learning metrics"""
    click.echo(f"Analyzing performance over last {days} days...")
    click.echo()

    from src.learning.learning_engine import LearningEngine

    try:
        engine = LearningEngine()
        analysis = engine.analyze_performance(days_back=days)

        # Overall performance
        click.echo("PERFORMANCE OVERVIEW:")
        click.echo("=" * 60)
        click.echo(f"Total Signals: {analysis['total_signals']}")
        click.echo(f"Success Rate: {analysis['success_rate']:.1f}%")
        click.echo(f"Average Gain: {analysis['avg_gain']:.2f}%")
        click.echo(f"Confidence Accuracy: {analysis['confidence_accuracy']:.1f}%")

        # By catalyst
        if analysis.get('by_catalyst'):
            click.echo("\nBY CATALYST TYPE:")
            click.echo("-" * 60)
            for catalyst, stats in analysis['by_catalyst'].items():
                click.echo(f"  {catalyst.upper()}: {stats['success_rate']:.1f}% "
                          f"({stats['successful']}/{stats['total']})")

        # By signal type
        if analysis.get('by_signal_type'):
            click.echo("\nBY SIGNAL TYPE:")
            click.echo("-" * 60)
            for sig_type, stats in analysis['by_signal_type'].items():
                click.echo(f"  {sig_type}: {stats['success_rate']:.1f}% "
                          f"({stats['successful']}/{stats['total']})")

        # Success factors
        if analysis.get('success_factors'):
            click.echo("\nTOP SUCCESS FACTORS:")
            click.echo("-" * 60)
            for factor in analysis['success_factors'][:5]:
                click.echo(f"  • {factor['factor']}: {factor['percentage']:.1f}%")

        click.secho("\n✓ Analysis complete", fg='green')

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red')


@learning.command(name='patterns')
@click.option('--min-samples', default=5, help='Minimum sample size (default: 5)')
def learning_patterns(min_samples):
    """Show discovered patterns from historical data"""
    click.echo(f"Analyzing patterns (min samples: {min_samples})...")
    click.echo()

    from src.learning.pattern_recognizer import PatternRecognizer

    try:
        recognizer = PatternRecognizer()
        patterns = recognizer.analyze_all_patterns()

        # Filter by sample size
        validated_patterns = [p for p in patterns if p['sample_size'] >= min_samples]

        if not validated_patterns:
            click.echo("No patterns discovered yet with sufficient samples.")
            click.echo(f"Need at least {min_samples} samples per pattern.")
            return

        # Sort by success rate
        validated_patterns.sort(key=lambda x: x['success_rate'], reverse=True)

        click.echo(f"DISCOVERED PATTERNS ({len(validated_patterns)}):")
        click.echo("=" * 70)

        for i, pattern in enumerate(validated_patterns[:15], 1):
            click.echo(f"\n{i}. {pattern['description']}")
            click.echo(f"   Type: {pattern['pattern_type']}")
            click.echo(f"   Success Rate: {pattern['success_rate']:.1f}%")
            click.echo(f"   Sample Size: {pattern['sample_size']}")
            click.echo(f"   Statistical Confidence: {pattern['statistical_confidence']:.1f}%")

            # Show characteristics
            if pattern.get('characteristics'):
                chars = pattern['characteristics']
                if isinstance(chars, dict):
                    click.echo(f"   Characteristics:")
                    for key, value in chars.items():
                        click.echo(f"     - {key}: {value}")

        click.secho(f"\n✓ Found {len(validated_patterns)} validated patterns", fg='green')

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red')


@learning.command(name='weights')
@click.option('--update', is_flag=True, help='Update weights based on recent performance')
@click.option('--history', is_flag=True, help='Show weight adjustment history')
def learning_weights(update, history):
    """View or update adaptive weights"""
    from src.learning.adaptive_weights import AdaptiveWeightsSystem

    try:
        system = AdaptiveWeightsSystem()

        if update:
            # Update weights
            click.echo("Updating adaptive weights...")
            click.echo()

            result = system.update_weights(min_signals=20)

            if result['updated']:
                click.secho("✓ Weights updated successfully!", fg='green')
                click.echo(f"Version: {result['version']}")
                click.echo("\nChanges:")
                for key, change in result['changes'].items():
                    symbol = '+' if change > 0 else ''
                    color = 'green' if change > 0 else 'red' if change < 0 else 'white'
                    click.secho(f"  {key}: {symbol}{change:.3f}", fg=color)
            else:
                click.secho(f"✗ Weights not updated: {result['reason']}", fg='yellow')

        elif history:
            # Show history
            click.echo("WEIGHT ADJUSTMENT HISTORY:")
            click.echo("=" * 70)

            hist = system.get_weight_history(last_n=10)

            if not hist:
                click.echo("No weight adjustments yet.")
            else:
                for i, adj in enumerate(reversed(hist), 1):
                    click.echo(f"\n{i}. {adj['timestamp']}")
                    click.echo(f"   Reason: {adj['reason']}")
                    click.echo(f"   Performance: {adj['performance_data']['success_rate']:.1f}% "
                              f"({adj['performance_data']['total_signals']} signals)")

        else:
            # Show current weights
            weights = system.get_adjusted_weights()

            click.echo("CURRENT ADAPTIVE WEIGHTS:")
            click.echo("=" * 70)
            click.echo(f"Version: {weights['version']}")
            click.echo(f"Last Updated: {weights['last_updated'] or 'Never'}")

            click.echo("\nSignal Generation Weights:")
            for key, value in weights['signal_generation'].items():
                click.echo(f"  {key}: {value:.3f}")

            click.echo("\nConfidence Thresholds:")
            for key, value in weights['confidence_thresholds'].items():
                click.echo(f"  {key}: {value}")

            click.echo("\nCatalyst Multipliers:")
            for key, value in weights['catalyst_multipliers'].items():
                click.echo(f"  {key}: {value:.2f}x")

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red')


@learning.command(name='report')
@click.option('--type', 'report_type', default='weekly',
              type=click.Choice(['weekly', 'monthly', 'performance']),
              help='Report type (default: weekly)')
@click.option('--export', is_flag=True, help='Export as markdown')
def learning_report(report_type, export):
    """Generate learning and performance reports"""
    click.echo(f"Generating {report_type} report...")
    click.echo()

    from src.learning.report_generator import ReportGenerator

    try:
        generator = ReportGenerator()

        # Generate report
        if report_type == 'weekly':
            report = generator.generate_weekly_report(save_to_file=True)
        elif report_type == 'monthly':
            report = generator.generate_monthly_report(save_to_file=True)
        else:
            report = generator.generate_performance_report(save_to_file=True)

        # Show summary
        click.echo("REPORT SUMMARY:")
        click.echo("=" * 70)

        if 'summary' in report:
            summary = report['summary']
            click.echo(f"Overall Assessment: {summary['overall_assessment'].upper()}")
            click.echo(f"\nKey Metrics:")
            for key, value in summary['key_metrics'].items():
                click.echo(f"  {key.replace('_', ' ').title()}: {value}")
            click.echo(f"\nRecommendation: {summary['recommendation']}")

        # Show sections
        sections = report.get('sections', {})
        click.echo(f"\nSections Included: {len(sections)}")
        for section_name in sections.keys():
            click.echo(f"  • {section_name.title()}")

        # Export markdown
        if export:
            md = generator.export_markdown(report)
            md_file = generator.reports_dir / f"{report_type}_report.md"
            with open(md_file, 'w') as f:
                f.write(md)
            click.secho(f"\n✓ Markdown exported to {md_file}", fg='green')

        click.secho(f"\n✓ Report generated and saved to reports/ directory", fg='green')

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red')


@learning.command(name='backtest')
@click.option('--days', default=30, help='Days to backtest (default: 30)')
@click.option('--strategy', is_flag=True, help='Test with custom strategy')
def learning_backtest(days, strategy):
    """Run backtesting on historical data"""
    click.echo(f"Backtesting last {days} days...")
    click.echo()

    from src.learning.backtester import Backtester

    try:
        backtester = Backtester()

        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Run backtest
        if strategy:
            click.echo("Testing custom strategy...")
            result = backtester.backtest_strategy(start_date, end_date)
        else:
            click.echo("Testing historical signals...")
            result = backtester.backtest_historical_signals(start_date, end_date)

        # Display results
        click.echo("BACKTEST RESULTS:")
        click.echo("=" * 70)
        click.echo(f"Period: {start_date.date()} to {end_date.date()}")
        click.echo(f"\nPerformance:")
        click.echo(f"  Total Signals: {result.total_signals}")
        click.echo(f"  Successful: {result.successful_signals}")
        click.echo(f"  Failed: {result.failed_signals}")
        click.echo(f"  Success Rate: {result.success_rate:.1f}%")

        click.echo(f"\nReturns:")
        click.echo(f"  Total Return: {result.total_return:.2f}%")
        click.echo(f"  Average Gain: {result.avg_gain:.2f}%")
        click.echo(f"  Average Loss: {result.avg_loss:.2f}%")

        click.echo(f"\nRisk Metrics:")
        click.echo(f"  Sharpe Ratio: {result.sharpe_ratio:.2f}")
        click.echo(f"  Max Drawdown: {result.max_drawdown:.2f}%")
        click.echo(f"  Win/Loss Ratio: {result.win_loss_ratio:.2f}")

        if result.best_trade:
            click.echo(f"\nBest Trade: {result.best_trade['ticker']} "
                      f"(+{result.best_trade['gain']:.2f}%)")

        if result.worst_trade:
            click.echo(f"Worst Trade: {result.worst_trade['ticker']} "
                      f"({result.worst_trade['loss']:.2f}%)")

        # By catalyst
        if result.by_catalyst:
            click.echo(f"\nBy Catalyst Type:")
            for catalyst, stats in result.by_catalyst.items():
                click.echo(f"  {catalyst}: {stats['success_rate']:.1f}% "
                          f"({stats['successful']}/{stats['total']})")

        click.secho("\n✓ Backtest complete", fg='green')

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red')


@learning.command(name='recommendations')
def learning_recommendations():
    """Get AI recommendations for system improvements"""
    click.echo("Analyzing system and generating recommendations...")
    click.echo()

    from src.learning.adaptive_weights import AdaptiveWeightsSystem

    try:
        system = AdaptiveWeightsSystem()
        recs = system.get_recommended_adjustments()

        if not recs:
            click.echo("No recommendations at this time.")
            click.echo("System is performing within expected parameters.")
            return

        click.echo(f"RECOMMENDATIONS ({len(recs)}):")
        click.echo("=" * 70)

        # Group by type
        by_type = {}
        for rec in recs:
            rec_type = rec.get('type', 'info')
            if rec_type not in by_type:
                by_type[rec_type] = []
            by_type[rec_type].append(rec)

        # Display by priority
        for rec_type in ['warning', 'insight', 'success', 'info']:
            if rec_type not in by_type:
                continue

            symbol = {
                'warning': '⚠️',
                'success': '✓',
                'insight': '💡',
                'info': 'ℹ️'
            }.get(rec_type, '•')

            color = {
                'warning': 'yellow',
                'success': 'green',
                'insight': 'cyan',
                'info': 'white'
            }.get(rec_type, 'white')

            for rec in by_type[rec_type]:
                click.echo()
                click.secho(f"{symbol} {rec['message']}", fg=color)
                if 'action' in rec:
                    click.echo(f"   Action: {rec['action']}")
                if 'category' in rec:
                    click.echo(f"   Category: {rec['category']}")

        click.secho(f"\n✓ Generated {len(recs)} recommendations", fg='green')

    except Exception as e:
        click.secho(f"\n✗ Error: {e}", fg='red')


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

    # Test 6: Signal generator (Phase 2)
    click.echo("\n6. Testing signal generator...")
    try:
        from src.signals.signal_generator import SignalGenerator
        generator = SignalGenerator()
        click.secho(f"   ✓ Signal generator loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Signal generator failed: {e}", fg='red')

    # Test 7: Portfolio manager (Phase 2)
    click.echo("\n7. Testing portfolio manager...")
    try:
        from src.portfolio.portfolio_manager import PortfolioManager
        manager = PortfolioManager()
        click.secho(f"   ✓ Portfolio manager loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Portfolio manager failed: {e}", fg='red')

    # Test 8: Portfolio monitor (Phase 2)
    click.echo("\n8. Testing portfolio monitor...")
    try:
        from src.portfolio.portfolio_monitor import PortfolioMonitor
        monitor = PortfolioMonitor()
        click.secho(f"   ✓ Portfolio monitor loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Portfolio monitor failed: {e}", fg='red')

    # Test 9: Learning engine (Phase 3)
    click.echo("\n9. Testing learning engine...")
    try:
        from src.learning.learning_engine import LearningEngine
        engine = LearningEngine()
        click.secho(f"   ✓ Learning engine loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Learning engine failed: {e}", fg='red')

    # Test 10: Pattern recognizer (Phase 3)
    click.echo("\n10. Testing pattern recognizer...")
    try:
        from src.learning.pattern_recognizer import PatternRecognizer
        recognizer = PatternRecognizer()
        click.secho(f"   ✓ Pattern recognizer loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Pattern recognizer failed: {e}", fg='red')

    # Test 11: Adaptive weights (Phase 3)
    click.echo("\n11. Testing adaptive weights system...")
    try:
        from src.learning.adaptive_weights import AdaptiveWeightsSystem
        weights_system = AdaptiveWeightsSystem()
        click.secho(f"   ✓ Adaptive weights system loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Adaptive weights failed: {e}", fg='red')

    # Test 12: Backtester (Phase 3)
    click.echo("\n12. Testing backtester...")
    try:
        from src.learning.backtester import Backtester
        backtester = Backtester()
        click.secho(f"   ✓ Backtester loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Backtester failed: {e}", fg='red')

    # Test 13: Report generator (Phase 3)
    click.echo("\n13. Testing report generator...")
    try:
        from src.learning.report_generator import ReportGenerator
        report_gen = ReportGenerator()
        click.secho(f"   ✓ Report generator loaded", fg='green')
    except Exception as e:
        click.secho(f"   ✗ Report generator failed: {e}", fg='red')

    click.echo("\n" + "=" * 60)
    click.echo("Phase 1, 2 & 3 tests complete!")
    click.echo("=" * 60)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    cli()
