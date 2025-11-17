"""
Market Data Collector
Uses FREE data sources:
- yfinance: Unlimited stock data (FREE)
- pandas_ta: Technical indicators calculated locally (FREE)
- Alpha Vantage: Only when necessary, respecting 25/day limit
"""

import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import pandas_ta as ta

from src.utils.logger import get_logger, get_api_logger
from src.utils.helpers import get_rate_limiter
from src.config.config_loader import get_config


logger = get_logger("market_data")
api_logger = get_api_logger()


# ============================================================================
# STOCK DATA COLLECTOR (yfinance - FREE, UNLIMITED)
# ============================================================================

class StockDataCollector:
    """
    Collect stock data using yfinance (Yahoo Finance)
    Completely free with no rate limits!
    """

    def __init__(self):
        self.logger = logger
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(minutes=10)

    def get_quote(self, ticker: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Get current quote for a ticker

        Args:
            ticker: Stock ticker symbol
            use_cache: Whether to use cached data

        Returns:
            Dictionary with quote data or None
        """
        # Check cache
        cache_key = f"quote_{ticker}"
        if use_cache and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                self.logger.debug(f"Using cached data for {ticker}")
                return cached_data

        try:
            self.logger.debug(f"Fetching quote for {ticker}")
            stock = yf.Ticker(ticker)
            info = stock.info

            # Extract relevant data
            quote = {
                "ticker": ticker,
                "timestamp": datetime.now(),
                "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "open": info.get("regularMarketOpen"),
                "high": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "low": info.get("dayLow") or info.get("regularMarketDayLow"),
                "previous_close": info.get("previousClose") or info.get("regularMarketPreviousClose"),
                "volume": info.get("volume") or info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "avg_volume": info.get("averageVolume"),
                "pe_ratio": info.get("trailingPE"),
                "company_name": info.get("longName") or info.get("shortName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
            }

            # Calculate change
            if quote["current_price"] and quote["previous_close"]:
                quote["change"] = quote["current_price"] - quote["previous_close"]
                quote["change_percent"] = (quote["change"] / quote["previous_close"]) * 100
            else:
                quote["change"] = None
                quote["change_percent"] = None

            # Cache result
            self.cache[cache_key] = (quote, datetime.now())

            self.logger.info(f"Quote for {ticker}: ${quote['current_price']}")
            return quote

        except Exception as e:
            self.logger.error(f"Error fetching quote for {ticker}: {e}")
            return None

    def get_historical_data(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Get historical price data

        Args:
            ticker: Stock ticker
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

        Returns:
            DataFrame with historical data
        """
        try:
            self.logger.debug(f"Fetching {period} historical data for {ticker}")
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)

            if df.empty:
                self.logger.warning(f"No historical data found for {ticker}")
                return None

            self.logger.info(f"Fetched {len(df)} historical data points for {ticker}")
            return df

        except Exception as e:
            self.logger.error(f"Error fetching historical data for {ticker}: {e}")
            return None

    def get_multiple_quotes(self, tickers: List[str]) -> Dict[str, Optional[Dict]]:
        """
        Get quotes for multiple tickers efficiently

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping tickers to quote data
        """
        results = {}

        try:
            # yfinance can handle multiple tickers at once
            tickers_str = " ".join(tickers)
            data = yf.download(
                tickers_str,
                period="1d",
                interval="1d",
                progress=False,
                show_errors=False
            )

            for ticker in tickers:
                try:
                    quote = self.get_quote(ticker)
                    results[ticker] = quote
                except Exception as e:
                    self.logger.error(f"Error getting quote for {ticker}: {e}")
                    results[ticker] = None

            self.logger.info(f"Fetched quotes for {len(results)} tickers")

        except Exception as e:
            self.logger.error(f"Error fetching multiple quotes: {e}")

        return results

    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """
        Get detailed company information

        Args:
            ticker: Stock ticker

        Returns:
            Company information dictionary
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            company_info = {
                "ticker": ticker,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "market_cap": info.get("marketCap"),
                "employees": info.get("fullTimeEmployees"),
                "description": info.get("longBusinessSummary"),
                "website": info.get("website"),
                "headquarters": {
                    "city": info.get("city"),
                    "state": info.get("state"),
                    "country": info.get("country")
                }
            }

            return company_info

        except Exception as e:
            self.logger.error(f"Error fetching company info for {ticker}: {e}")
            return None


# ============================================================================
# TECHNICAL INDICATORS (pandas_ta - FREE, LOCAL)
# ============================================================================

class TechnicalIndicatorCalculator:
    """
    Calculate technical indicators locally using pandas_ta
    No API calls needed - completely free!
    """

    def __init__(self):
        self.logger = logger

    def calculate_indicators(
        self,
        df: pd.DataFrame,
        indicators: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Calculate technical indicators on price data

        Args:
            df: DataFrame with OHLCV data
            indicators: List of indicators to calculate (None = all)

        Returns:
            DataFrame with indicators added
        """
        if df is None or df.empty:
            self.logger.warning("Empty dataframe provided")
            return df

        try:
            # Make a copy to avoid modifying original
            df_copy = df.copy()

            # Default indicators if none specified
            if indicators is None:
                indicators = ["RSI", "MACD", "SMA", "EMA", "BB", "VOLUME"]

            # RSI (Relative Strength Index)
            if "RSI" in indicators:
                df_copy.ta.rsi(length=14, append=True)

            # MACD (Moving Average Convergence Divergence)
            if "MACD" in indicators:
                df_copy.ta.macd(append=True)

            # Simple Moving Averages
            if "SMA" in indicators:
                df_copy.ta.sma(length=20, append=True)
                df_copy.ta.sma(length=50, append=True)
                df_copy.ta.sma(length=200, append=True)

            # Exponential Moving Averages
            if "EMA" in indicators:
                df_copy.ta.ema(length=12, append=True)
                df_copy.ta.ema(length=26, append=True)

            # Bollinger Bands
            if "BB" in indicators:
                df_copy.ta.bbands(length=20, append=True)

            # Volume indicators
            if "VOLUME" in indicators:
                # Average volume
                df_copy["Volume_SMA_20"] = df_copy["Volume"].rolling(window=20).mean()

            # ATR (Average True Range) - volatility
            if "ATR" in indicators:
                df_copy.ta.atr(length=14, append=True)

            # Stochastic
            if "STOCH" in indicators:
                df_copy.ta.stoch(append=True)

            self.logger.debug(f"Calculated {len(indicators)} indicators")
            return df_copy

        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            return df

    def get_latest_indicators(
        self,
        ticker: str,
        period: str = "3mo"
    ) -> Optional[Dict]:
        """
        Get latest technical indicator values for a ticker

        Args:
            ticker: Stock ticker
            period: Historical period for calculation

        Returns:
            Dictionary with latest indicator values
        """
        try:
            # Get historical data
            collector = StockDataCollector()
            df = collector.get_historical_data(ticker, period=period)

            if df is None or df.empty:
                return None

            # Calculate indicators
            df_with_indicators = self.calculate_indicators(df)

            # Extract latest values
            latest = df_with_indicators.iloc[-1]

            indicators = {
                "ticker": ticker,
                "timestamp": datetime.now(),
                "rsi": latest.get("RSI_14"),
                "macd": latest.get("MACD_12_26_9"),
                "macd_signal": latest.get("MACDs_12_26_9"),
                "macd_histogram": latest.get("MACDh_12_26_9"),
                "sma_20": latest.get("SMA_20"),
                "sma_50": latest.get("SMA_50"),
                "sma_200": latest.get("SMA_200"),
                "ema_12": latest.get("EMA_12"),
                "ema_26": latest.get("EMA_26"),
                "bb_upper": latest.get("BBU_20_2.0"),
                "bb_middle": latest.get("BBM_20_2.0"),
                "bb_lower": latest.get("BBL_20_2.0"),
                "atr": latest.get("ATR_14"),
                "volume_avg_20": latest.get("Volume_SMA_20"),
            }

            # Remove None values
            indicators = {k: v for k, v in indicators.items() if v is not None}

            self.logger.info(f"Calculated indicators for {ticker}")
            return indicators

        except Exception as e:
            self.logger.error(f"Error getting indicators for {ticker}: {e}")
            return None


# ============================================================================
# MARKET DATA SERVICE (Combined)
# ============================================================================

class MarketDataService:
    """
    Complete market data service combining all sources
    """

    def __init__(self):
        self.stock_collector = StockDataCollector()
        self.indicator_calculator = TechnicalIndicatorCalculator()
        self.logger = logger

    def get_complete_data(self, ticker: str) -> Optional[Dict]:
        """
        Get complete market data for a ticker including technical indicators

        Args:
            ticker: Stock ticker symbol

        Returns:
            Complete data dictionary
        """
        try:
            # Get quote
            quote = self.stock_collector.get_quote(ticker)
            if not quote:
                return None

            # Get technical indicators
            indicators = self.indicator_calculator.get_latest_indicators(ticker)

            # Combine
            complete_data = {
                **quote,
                "technical_indicators": indicators or {}
            }

            return complete_data

        except Exception as e:
            self.logger.error(f"Error getting complete data for {ticker}: {e}")
            return None

    def analyze_price_movement(
        self,
        ticker: str,
        hours_back: int = 24
    ) -> Optional[Dict]:
        """
        Analyze price movement over recent period

        Args:
            ticker: Stock ticker
            hours_back: Hours to look back

        Returns:
            Price movement analysis
        """
        try:
            # Determine period and interval
            if hours_back <= 24:
                period = "5d"
                interval = "1h"
            elif hours_back <= 168:  # 1 week
                period = "1mo"
                interval = "1d"
            else:
                period = "3mo"
                interval = "1d"

            # Get historical data
            df = self.stock_collector.get_historical_data(
                ticker,
                period=period,
                interval=interval
            )

            if df is None or len(df) < 2:
                return None

            # Calculate changes
            latest_price = df['Close'].iloc[-1]
            start_price = df['Close'].iloc[0]
            change = latest_price - start_price
            change_pct = (change / start_price) * 100

            # Find peak and trough
            peak_price = df['High'].max()
            trough_price = df['Low'].min()
            peak_time = df['High'].idxmax()
            trough_time = df['Low'].idxmin()

            # Volume analysis
            avg_volume = df['Volume'].mean()
            latest_volume = df['Volume'].iloc[-1]
            volume_ratio = latest_volume / avg_volume if avg_volume > 0 else 1.0

            # Volatility
            volatility = df['Close'].pct_change().std() * 100

            analysis = {
                "ticker": ticker,
                "period_analyzed": f"{hours_back}h",
                "start_price": float(start_price),
                "current_price": float(latest_price),
                "change": float(change),
                "change_percent": float(change_pct),
                "peak_price": float(peak_price),
                "trough_price": float(trough_price),
                "peak_time": peak_time,
                "trough_time": trough_time,
                "volatility": float(volatility),
                "avg_volume": float(avg_volume),
                "latest_volume": float(latest_volume),
                "volume_ratio": float(volume_ratio),
                "is_unusual_volume": volume_ratio > 1.5,
            }

            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing price movement for {ticker}: {e}")
            return None

    def detect_unusual_activity(self, ticker: str) -> Dict:
        """
        Detect unusual trading activity

        Args:
            ticker: Stock ticker

        Returns:
            Dictionary with unusual activity flags
        """
        try:
            # Get recent movement
            movement = self.analyze_price_movement(ticker, hours_back=24)
            if not movement:
                return {"unusual_activity": False}

            # Get technical indicators
            indicators = self.indicator_calculator.get_latest_indicators(ticker)

            unusual = {
                "unusual_activity": False,
                "flags": []
            }

            # Check for unusual volume
            if movement.get("is_unusual_volume"):
                unusual["unusual_activity"] = True
                unusual["flags"].append("unusual_volume")

            # Check for large price move
            if abs(movement.get("change_percent", 0)) > 5:
                unusual["unusual_activity"] = True
                unusual["flags"].append("large_price_move")

            # Check for high volatility
            if movement.get("volatility", 0) > 5:
                unusual["unusual_activity"] = True
                unusual["flags"].append("high_volatility")

            # Check RSI extremes
            if indicators:
                rsi = indicators.get("rsi")
                if rsi:
                    if rsi > 70:
                        unusual["flags"].append("overbought")
                    elif rsi < 30:
                        unusual["flags"].append("oversold")

            return unusual

        except Exception as e:
            self.logger.error(f"Error detecting unusual activity for {ticker}: {e}")
            return {"unusual_activity": False}


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test market data collection"""
    print("=" * 60)
    print("Market Data Collector Test (FREE - yfinance + pandas_ta)")
    print("=" * 60)

    service = MarketDataService()

    # Test ticker
    ticker = "AAPL"

    print(f"\n1. Getting quote for {ticker}...")
    quote = service.stock_collector.get_quote(ticker)
    if quote:
        print(f"   Price: ${quote['current_price']:.2f}")
        print(f"   Change: {quote['change_percent']:.2f}%")
        print(f"   Volume: {quote['volume']:,}")

    print(f"\n2. Getting technical indicators for {ticker}...")
    indicators = service.indicator_calculator.get_latest_indicators(ticker)
    if indicators:
        print(f"   RSI: {indicators.get('rsi', 'N/A')}")
        print(f"   MACD: {indicators.get('macd', 'N/A')}")
        print(f"   SMA 50: {indicators.get('sma_50', 'N/A')}")

    print(f"\n3. Analyzing price movement for {ticker}...")
    movement = service.analyze_price_movement(ticker, hours_back=24)
    if movement:
        print(f"   24h Change: {movement['change_percent']:.2f}%")
        print(f"   Volatility: {movement['volatility']:.2f}%")
        print(f"   Volume Ratio: {movement['volume_ratio']:.2f}x")

    print(f"\n4. Detecting unusual activity for {ticker}...")
    unusual = service.detect_unusual_activity(ticker)
    print(f"   Unusual Activity: {unusual['unusual_activity']}")
    if unusual.get("flags"):
        print(f"   Flags: {', '.join(unusual['flags'])}")

    print("\n" + "=" * 60)
    print("Test complete!")


if __name__ == "__main__":
    main()
