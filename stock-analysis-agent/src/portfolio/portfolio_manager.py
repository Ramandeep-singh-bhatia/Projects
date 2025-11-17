"""
Portfolio Management System
Allows users to track their stock holdings and calculate performance
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.models import (
    PortfolioPosition,
    PositionStatus,
    InvestmentType,
    create_engine_and_session
)
from src.scrapers.market_data_collector import MarketDataService
from src.utils.logger import get_logger
from src.utils.helpers import format_currency, format_percentage
from src.config.config_loader import get_config


logger = get_logger("portfolio_manager")


# ============================================================================
# PORTFOLIO MANAGER
# ============================================================================

class PortfolioManager:
    """
    Manage portfolio positions - add, remove, track performance
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.logger = logger
        self.config = get_config()
        self.market_service = MarketDataService()

        # Database session
        if db_session:
            self.session = db_session
        else:
            _, SessionLocal = create_engine_and_session(self.config.database.url)
            self.session = SessionLocal()

    def add_position(
        self,
        ticker: str,
        shares: float,
        purchase_price: float,
        purchase_date: Optional[datetime] = None,
        investment_type: str = "long_term",
        notes: Optional[str] = None
    ) -> PortfolioPosition:
        """
        Add a new position to the portfolio

        Args:
            ticker: Stock ticker symbol
            shares: Number of shares
            purchase_price: Price per share at purchase
            purchase_date: Date of purchase (default: today)
            investment_type: 'short_term' or 'long_term'
            notes: Optional notes

        Returns:
            Created PortfolioPosition object
        """
        try:
            ticker = ticker.upper()

            # Get company name
            quote = self.market_service.stock_collector.get_quote(ticker)
            company_name = quote.get('company_name', ticker) if quote else ticker

            # Create position
            position = PortfolioPosition(
                ticker=ticker,
                company_name=company_name,
                shares=shares,
                purchase_price=purchase_price,
                purchase_date=purchase_date or datetime.now(),
                investment_type=InvestmentType(investment_type),
                status=PositionStatus.ACTIVE,
                notes=notes,
                tags=[]
            )

            self.session.add(position)
            self.session.commit()

            self.logger.info(f"Added position: {ticker} - {shares} shares @ ${purchase_price}")

            # Update with current price
            self.update_position_prices([position])

            return position

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error adding position: {e}")
            raise

    def remove_position(
        self,
        position_id: int,
        exit_price: Optional[float] = None,
        exit_reason: Optional[str] = None
    ) -> PortfolioPosition:
        """
        Close/remove a position from portfolio

        Args:
            position_id: Position ID
            exit_price: Exit price (default: current market price)
            exit_reason: Reason for exit

        Returns:
            Updated PortfolioPosition object
        """
        try:
            position = self.session.query(PortfolioPosition).get(position_id)

            if not position:
                raise ValueError(f"Position {position_id} not found")

            # Get exit price
            if exit_price is None:
                quote = self.market_service.stock_collector.get_quote(position.ticker)
                exit_price = quote.get('current_price') if quote else position.purchase_price

            # Calculate realized gain/loss
            cost_basis = position.purchase_price * position.shares
            exit_value = exit_price * position.shares
            realized_gain_loss = exit_value - cost_basis
            realized_gain_loss_pct = (realized_gain_loss / cost_basis) * 100

            # Update position
            position.status = PositionStatus.CLOSED
            position.exit_price = exit_price
            position.exit_date = datetime.now()
            position.exit_reason = exit_reason or "Manual exit"
            position.realized_gain_loss_pct = realized_gain_loss_pct
            position.realized_gain_loss_dollar = realized_gain_loss

            self.session.commit()

            self.logger.info(f"Closed position: {position.ticker} - "
                           f"P&L: {format_currency(realized_gain_loss)} "
                           f"({format_percentage(realized_gain_loss_pct)})")

            return position

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error removing position: {e}")
            raise

    def get_all_positions(
        self,
        status: Optional[str] = None
    ) -> List[PortfolioPosition]:
        """
        Get all portfolio positions

        Args:
            status: Filter by status ('active', 'closed', 'watching')

        Returns:
            List of PortfolioPosition objects
        """
        try:
            query = self.session.query(PortfolioPosition)

            if status:
                query = query.filter(PortfolioPosition.status == PositionStatus(status))

            positions = query.order_by(PortfolioPosition.purchase_date.desc()).all()

            return positions

        except Exception as e:
            self.logger.error(f"Error getting positions: {e}")
            return []

    def get_position(self, position_id: int) -> Optional[PortfolioPosition]:
        """Get a specific position by ID"""
        try:
            return self.session.query(PortfolioPosition).get(position_id)
        except Exception as e:
            self.logger.error(f"Error getting position {position_id}: {e}")
            return None

    def update_position_prices(
        self,
        positions: Optional[List[PortfolioPosition]] = None
    ):
        """
        Update current prices for positions

        Args:
            positions: List of positions to update (default: all active)
        """
        try:
            if positions is None:
                positions = self.get_all_positions(status='active')

            if not positions:
                return

            # Get unique tickers
            tickers = list(set(p.ticker for p in positions))

            # Fetch current prices
            quotes = self.market_service.stock_collector.get_multiple_quotes(tickers)

            # Update each position
            for position in positions:
                quote = quotes.get(position.ticker)

                if quote and quote.get('current_price'):
                    current_price = quote['current_price']

                    # Calculate unrealized gain/loss
                    cost_basis = position.purchase_price * position.shares
                    current_value = current_price * position.shares
                    unrealized_gain_loss = current_value - cost_basis
                    unrealized_gain_loss_pct = (unrealized_gain_loss / cost_basis) * 100

                    # Calculate days held
                    days_held = (datetime.now() - position.purchase_date).days

                    # Update position
                    position.current_price = current_price
                    position.last_price_update = datetime.now()
                    position.unrealized_gain_loss_pct = unrealized_gain_loss_pct
                    position.unrealized_gain_loss_dollar = unrealized_gain_loss
                    position.days_held = days_held

            self.session.commit()
            self.logger.debug(f"Updated prices for {len(positions)} positions")

        except Exception as e:
            self.session.rollback()
            self.logger.error(f"Error updating position prices: {e}")

    def get_portfolio_summary(self) -> Dict:
        """
        Get overall portfolio summary statistics

        Returns:
            Dictionary with portfolio metrics
        """
        try:
            # Get active positions
            active_positions = self.get_all_positions(status='active')

            # Update prices first
            self.update_position_prices(active_positions)

            if not active_positions:
                return {
                    'total_positions': 0,
                    'total_invested': 0.0,
                    'current_value': 0.0,
                    'total_gain_loss': 0.0,
                    'total_gain_loss_pct': 0.0,
                    'positions_profitable': 0,
                    'positions_losing': 0,
                    'best_performer': None,
                    'worst_performer': None,
                }

            # Calculate totals
            total_invested = sum(p.purchase_price * p.shares for p in active_positions)
            current_value = sum(
                (p.current_price or p.purchase_price) * p.shares
                for p in active_positions
            )
            total_gain_loss = current_value - total_invested
            total_gain_loss_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0.0

            # Count profitable vs losing
            profitable = sum(1 for p in active_positions if (p.unrealized_gain_loss_pct or 0) > 0)
            losing = sum(1 for p in active_positions if (p.unrealized_gain_loss_pct or 0) < 0)

            # Best and worst performers
            sorted_by_performance = sorted(
                active_positions,
                key=lambda p: p.unrealized_gain_loss_pct or 0,
                reverse=True
            )
            best = sorted_by_performance[0] if sorted_by_performance else None
            worst = sorted_by_performance[-1] if sorted_by_performance else None

            # Position concentration
            position_sizes = [
                (p.current_price or p.purchase_price) * p.shares
                for p in active_positions
            ]
            largest_position_pct = (max(position_sizes) / current_value * 100) if current_value > 0 else 0

            return {
                'total_positions': len(active_positions),
                'total_invested': total_invested,
                'current_value': current_value,
                'total_gain_loss': total_gain_loss,
                'total_gain_loss_pct': total_gain_loss_pct,
                'positions_profitable': profitable,
                'positions_losing': losing,
                'best_performer': {
                    'ticker': best.ticker,
                    'gain_pct': best.unrealized_gain_loss_pct,
                    'gain_dollar': best.unrealized_gain_loss_dollar
                } if best else None,
                'worst_performer': {
                    'ticker': worst.ticker,
                    'loss_pct': worst.unrealized_gain_loss_pct,
                    'loss_dollar': worst.unrealized_gain_loss_dollar
                } if worst else None,
                'largest_position_pct': largest_position_pct,
                'positions_breakdown': {
                    'short_term': sum(1 for p in active_positions if p.investment_type == InvestmentType.SHORT_TERM),
                    'long_term': sum(1 for p in active_positions if p.investment_type == InvestmentType.LONG_TERM),
                }
            }

        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return {}

    def get_position_details(self, position_id: int) -> Optional[Dict]:
        """
        Get detailed information about a specific position

        Args:
            position_id: Position ID

        Returns:
            Dictionary with position details
        """
        try:
            position = self.get_position(position_id)

            if not position:
                return None

            # Update price
            self.update_position_prices([position])

            # Get recent price movement
            movement = self.market_service.analyze_price_movement(
                position.ticker,
                hours_back=24
            )

            # Calculate metrics
            cost_basis = position.purchase_price * position.shares
            current_value = (position.current_price or position.purchase_price) * position.shares
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

            return {
                'id': position.id,
                'ticker': position.ticker,
                'company_name': position.company_name,
                'shares': position.shares,
                'purchase_price': position.purchase_price,
                'purchase_date': position.purchase_date,
                'current_price': position.current_price,
                'cost_basis': cost_basis,
                'current_value': current_value,
                'unrealized_gain_loss': gain_loss,
                'unrealized_gain_loss_pct': gain_loss_pct,
                'days_held': position.days_held,
                'investment_type': position.investment_type.value,
                'status': position.status.value,
                'notes': position.notes,
                'price_movement_24h': movement.get('change_percent') if movement else None,
                'risk_level': position.current_risk_level.value if position.current_risk_level else None,
                'risk_score': position.risk_score,
            }

        except Exception as e:
            self.logger.error(f"Error getting position details: {e}")
            return None

    def __del__(self):
        """Cleanup database session"""
        if hasattr(self, 'session'):
            self.session.close()


# ============================================================================
# MAIN FUNCTION FOR TESTING
# ============================================================================

def main():
    """Test portfolio manager"""
    print("=" * 70)
    print("Portfolio Manager Test")
    print("=" * 70)
    print()

    manager = PortfolioManager()

    # Add a test position
    print("Adding test position: AAPL, 10 shares @ $150...")
    position = manager.add_position(
        ticker="AAPL",
        shares=10,
        purchase_price=150.00,
        investment_type="long_term",
        notes="Test position"
    )
    print(f"✓ Position added: ID {position.id}")
    print()

    # Get portfolio summary
    print("Portfolio Summary:")
    print("-" * 70)
    summary = manager.get_portfolio_summary()
    print(f"Total Positions: {summary['total_positions']}")
    print(f"Total Invested: {format_currency(summary['total_invested'])}")
    print(f"Current Value: {format_currency(summary['current_value'])}")
    print(f"Total Gain/Loss: {format_currency(summary['total_gain_loss'])} "
          f"({format_percentage(summary['total_gain_loss_pct'])})")
    print()

    # Get position details
    print("Position Details:")
    print("-" * 70)
    details = manager.get_position_details(position.id)
    if details:
        print(f"Ticker: {details['ticker']}")
        print(f"Shares: {details['shares']}")
        print(f"Purchase Price: {format_currency(details['purchase_price'])}")
        print(f"Current Price: {format_currency(details['current_price'])}")
        print(f"Unrealized P&L: {format_currency(details['unrealized_gain_loss'])} "
              f"({format_percentage(details['unrealized_gain_loss_pct'])})")
        print(f"Days Held: {details['days_held']}")


if __name__ == "__main__":
    main()
