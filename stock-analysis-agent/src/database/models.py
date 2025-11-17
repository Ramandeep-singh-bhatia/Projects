"""
Database models for Stock Analysis Agent
Using SQLAlchemy ORM with SQLite (completely free, local)
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import enum

Base = declarative_base()


# ============================================================================
# ENUMS
# ============================================================================

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SignalType(str, enum.Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class SignalStatus(str, enum.Enum):
    ACTIVE = "active"
    SUCCESSFUL = "successful"
    UNSUCCESSFUL = "unsuccessful"
    PENDING = "pending"
    EXPIRED = "expired"


class RiskLevel(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InvestmentType(str, enum.Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class PositionStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    WATCHING = "watching"


class NewsSource(str, enum.Enum):
    RSS = "rss"
    NEWSAPI = "newsapi"
    SEC_EDGAR = "sec_edgar"
    ALPHA_VANTAGE = "alpha_vantage"
    FMP = "fmp"
    OTHER = "other"


# ============================================================================
# NEWS & DATA MODELS
# ============================================================================

class NewsArticle(Base):
    """Stores scraped news articles with sentiment analysis"""
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    source = Column(SQLEnum(NewsSource), nullable=False)
    source_name = Column(String(100))
    title = Column(String(500), nullable=False)
    content = Column(Text)
    url = Column(String(1000), unique=True, index=True)
    published_date = Column(DateTime, index=True)

    # Analysis fields
    tickers_mentioned = Column(JSON)  # List of ticker symbols
    sentiment_score = Column(Float)  # -1 to 1
    sentiment_type = Column(SQLEnum(SentimentType))
    relevance_score = Column(Float)  # 0 to 1
    impact_magnitude = Column(String(20))  # minor, moderate, major
    event_type = Column(String(50))  # earnings, m&a, fda, contract, etc.

    # Additional metadata
    keywords = Column(JSON)  # Extracted keywords
    entities = Column(JSON)  # Named entities (companies, people)
    summary = Column(Text)  # AI-generated summary

    # Processing flags
    processed = Column(Boolean, default=False)
    processing_timestamp = Column(DateTime)

    def __repr__(self):
        return f"<NewsArticle {self.id}: {self.title[:50]}...>"


class MarketData(Base):
    """Stores stock price and technical indicator data"""
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Price data
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    volume = Column(Integer)
    adjusted_close = Column(Float)

    # Technical indicators
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    sma_200 = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)

    # Additional metrics
    avg_volume_20d = Column(Float)
    volatility = Column(Float)
    market_cap = Column(Float)

    # Metadata
    data_source = Column(String(50))
    is_realtime = Column(Boolean, default=False)

    def __repr__(self):
        return f"<MarketData {self.ticker} @ {self.timestamp}: ${self.close}>"


# ============================================================================
# SIGNAL MODELS
# ============================================================================

class SignalGenerated(Base):
    """Stores all investment signals/predictions"""
    __tablename__ = "signals_generated"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Stock info
    ticker = Column(String(10), nullable=False, index=True)
    company_name = Column(String(200))

    # Signal details
    signal_type = Column(SQLEnum(SignalType), nullable=False)
    timeframe_days = Column(Integer, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price_at_signal = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)

    # Predictions
    expected_gain_pct = Column(Float, nullable=False)
    expected_gain_conservative = Column(Float)
    expected_gain_moderate = Column(Float)
    expected_gain_aggressive = Column(Float)

    # Confidence and risk
    confidence = Column(Float, nullable=False)  # 0-100
    risk_score = Column(Float)  # 0-100
    risk_factors = Column(JSON)  # List of risk factors

    # Rationale
    rationale = Column(Text, nullable=False)
    supporting_data = Column(JSON)  # Key data points
    catalyst_type = Column(String(50))  # What triggered this signal
    news_article_ids = Column(JSON)  # References to related news

    # Status tracking
    status = Column(SQLEnum(SignalStatus), default=SignalStatus.ACTIVE, index=True)
    expiry_date = Column(DateTime, index=True)
    last_checked = Column(DateTime)

    # Relationships
    outcome = relationship("SignalOutcome", back_populates="signal", uselist=False)

    def __repr__(self):
        return f"<Signal {self.id}: {self.ticker} {self.signal_type.value} {self.confidence}% conf>"


class SignalOutcome(Base):
    """Tracks actual outcomes of predictions for learning"""
    __tablename__ = "signal_outcomes"

    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals_generated.id"), unique=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Performance tracking
    peak_price = Column(Float)
    peak_timestamp = Column(DateTime)
    peak_gain_pct = Column(Float)
    time_to_peak_hours = Column(Float)

    # Sustainability checks
    price_24h_after_peak = Column(Float)
    price_48h_after_peak = Column(Float)
    price_7d_after_signal = Column(Float)
    gain_sustained_24h = Column(Boolean)
    gain_sustained_48h = Column(Boolean)

    # Final outcome
    final_outcome = Column(String(50))  # strong_success, moderate_success, weak_success, near_miss, failure
    success_flag = Column(Boolean, nullable=False)
    actual_gain_pct = Column(Float)
    holding_period_days = Column(Float)

    # Exit details
    exit_price = Column(Float)
    exit_timestamp = Column(DateTime)
    exit_reason = Column(String(100))  # target_reached, stop_loss, time_expired, manual

    # Analysis
    what_worked = Column(JSON)  # Factors that contributed to success
    what_failed = Column(JSON)  # Factors that contributed to failure
    lessons_learned = Column(Text)
    pattern_matched = Column(String(100))

    # Relationship
    signal = relationship("SignalGenerated", back_populates="outcome")

    def __repr__(self):
        return f"<SignalOutcome {self.id}: {'SUCCESS' if self.success_flag else 'FAILURE'} {self.actual_gain_pct:.1f}%>"


# ============================================================================
# PORTFOLIO MODELS
# ============================================================================

class PortfolioPosition(Base):
    """User's current stock holdings"""
    __tablename__ = "portfolio_positions"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(10), nullable=False, index=True)
    company_name = Column(String(200))

    # Position details
    shares = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    purchase_date = Column(DateTime, nullable=False)
    investment_type = Column(SQLEnum(InvestmentType), nullable=False)

    # Current status
    status = Column(SQLEnum(PositionStatus), default=PositionStatus.ACTIVE, index=True)
    current_price = Column(Float)
    last_price_update = Column(DateTime)

    # Performance
    unrealized_gain_loss_pct = Column(Float)
    unrealized_gain_loss_dollar = Column(Float)
    days_held = Column(Integer)

    # Risk tracking
    current_risk_level = Column(SQLEnum(RiskLevel))
    risk_score = Column(Float)
    last_risk_check = Column(DateTime)

    # Notes
    notes = Column(Text)
    tags = Column(JSON)

    # Exit tracking (if closed)
    exit_price = Column(Float)
    exit_date = Column(DateTime)
    exit_reason = Column(String(200))
    realized_gain_loss_pct = Column(Float)
    realized_gain_loss_dollar = Column(Float)

    # Relationships
    monitoring_records = relationship("PortfolioMonitoring", back_populates="position")

    def __repr__(self):
        return f"<Position {self.ticker}: {self.shares} shares @ ${self.purchase_price}>"


class PortfolioMonitoring(Base):
    """Hourly monitoring and risk assessment of portfolio positions"""
    __tablename__ = "portfolio_monitoring"

    id = Column(Integer, primary_key=True)
    position_id = Column(Integer, ForeignKey("portfolio_positions.id"), index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Current snapshot
    current_price = Column(Float, nullable=False)
    price_change_1h = Column(Float)
    price_change_24h = Column(Float)
    volume_vs_avg = Column(Float)

    # Risk assessment
    risk_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    risk_factors = Column(JSON)  # List of identified risks

    # Alert information
    alert_level = Column(SQLEnum(RiskLevel))
    alert_generated = Column(Boolean, default=False)
    action_recommended = Column(String(100))  # exit_now, exit_24h, monitor, hold
    alternative_stocks = Column(JSON)  # Suggested alternatives if exiting

    # Analysis
    negative_news_count = Column(Integer, default=0)
    sentiment_shift = Column(Float)  # Change in sentiment
    technical_signals = Column(JSON)  # Technical indicator warnings
    sector_performance = Column(Float)
    insider_activity = Column(String(50))

    # Summary
    analysis_summary = Column(Text)
    confidence = Column(Float)  # Confidence in the risk assessment

    # Relationship
    position = relationship("PortfolioPosition", back_populates="monitoring_records")

    def __repr__(self):
        return f"<Monitoring {self.position_id} @ {self.timestamp}: {self.risk_level.value}>"


# ============================================================================
# LEARNING MODELS
# ============================================================================

class LearningPattern(Base):
    """Discovered patterns from historical analysis"""
    __tablename__ = "learning_patterns"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Pattern identification
    pattern_type = Column(String(100), nullable=False, index=True)
    pattern_name = Column(String(200))
    description = Column(Text, nullable=False)

    # Pattern characteristics
    conditions = Column(JSON)  # What conditions define this pattern
    indicators = Column(JSON)  # Which indicators are involved

    # Performance
    success_rate = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=False)  # Statistical confidence

    # Context
    market_cap_range = Column(String(50))  # small, mid, large
    sector = Column(String(100))
    timeframe = Column(String(50))
    market_conditions = Column(JSON)

    # Impact on future signals
    weight_adjustment = Column(Float)  # How much to adjust signal weights
    active = Column(Boolean, default=True)
    last_validated = Column(DateTime)

    # Examples
    example_signals = Column(JSON)  # IDs of signals that match this pattern
    avg_gain_on_success = Column(Float)
    avg_loss_on_failure = Column(Float)

    def __repr__(self):
        return f"<Pattern {self.pattern_name}: {self.success_rate:.1f}% ({self.sample_size} samples)>"


class PerformanceMetrics(Base):
    """Daily/weekly aggregated performance metrics"""
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    period_type = Column(String(20))  # daily, weekly, monthly

    # Overall metrics
    total_signals = Column(Integer, default=0)
    successful_signals = Column(Integer, default=0)
    unsuccessful_signals = Column(Integer, default=0)
    pending_signals = Column(Integer, default=0)

    # Success rates
    overall_success_rate = Column(Float)
    success_rate_short_term = Column(Float)
    success_rate_long_term = Column(Float)

    # By signal type
    success_rate_earnings = Column(Float)
    success_rate_ma = Column(Float)
    success_rate_fda = Column(Float)
    success_rate_contract = Column(Float)
    success_rate_technical = Column(Float)

    # Financial metrics
    avg_gain_winners = Column(Float)
    avg_loss_losers = Column(Float)
    max_gain = Column(Float)
    max_loss = Column(Float)
    total_gain_pct = Column(Float)

    # Risk-adjusted metrics
    sharpe_ratio = Column(Float)
    win_loss_ratio = Column(Float)
    profit_factor = Column(Float)

    # Confidence calibration
    confidence_accuracy = Column(Float)  # How well confidence predicts success
    avg_confidence = Column(Float)

    # Portfolio metrics (if applicable)
    portfolio_value = Column(Float)
    portfolio_gain_loss_pct = Column(Float)
    positions_at_risk = Column(Integer)

    # Learning progress
    patterns_discovered = Column(Integer)
    patterns_validated = Column(Integer)
    model_adjustments_made = Column(Integer)

    # API usage (to track free tier limits)
    api_calls_newsapi = Column(Integer, default=0)
    api_calls_alpha_vantage = Column(Integer, default=0)
    api_calls_fmp = Column(Integer, default=0)

    def __repr__(self):
        return f"<Metrics {self.date.date()}: {self.overall_success_rate:.1f}% success>"


# ============================================================================
# UTILITY MODELS
# ============================================================================

class APIUsageLog(Base):
    """Track API usage to stay within free tier limits"""
    __tablename__ = "api_usage_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    api_name = Column(String(50), nullable=False, index=True)
    endpoint = Column(String(200))
    success = Column(Boolean, default=True)
    response_time_ms = Column(Integer)
    error_message = Column(Text)

    def __repr__(self):
        return f"<APICall {self.api_name} @ {self.timestamp}>"


class SystemLog(Base):
    """General system events and errors"""
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    module = Column(String(100), index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON)
    traceback = Column(Text)

    def __repr__(self):
        return f"<SystemLog {self.level}: {self.message[:50]}...>"


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def create_engine_and_session(database_url: str = "sqlite:///data/stock_analysis.db"):
    """Create database engine and session"""
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def init_database(database_url: str = "sqlite:///data/stock_analysis.db"):
    """Initialize database with all tables"""
    engine, _ = create_engine_and_session(database_url)
    Base.metadata.create_all(bind=engine)
    print(f"✓ Database initialized at: {database_url}")
    print(f"✓ Created {len(Base.metadata.tables)} tables")
    return engine


if __name__ == "__main__":
    # Create database if running this file directly
    init_database()
