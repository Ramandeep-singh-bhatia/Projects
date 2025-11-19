"""
Main orchestrator for the Deal Scanner system.
Coordinates all agents and schedules regular scans.
"""
import sys
import json
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import schedule
from loguru import logger

# Configure logging
from config.settings import LOG_FILE, LOG_LEVEL, SCHEDULER_CONFIG, BASE_DIR

logger.remove()
logger.add(sys.stdout, level=LOG_LEVEL, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")
logger.add(LOG_FILE, rotation="10 MB", retention="7 days", level=LOG_LEVEL)

# Import agents
from agents.amazon_agent import amazon_agent
from agents.bestbuy_agent import bestbuy_agent
from agents.walmart_agent import walmart_agent
from agents.aggregator_agent import aggregator_agent
from utils.database import db
from utils.notifier import notifier


class DealScannerOrchestrator:
    """Main orchestrator for the deal scanner system."""

    def __init__(self):
        """Initialize orchestrator."""
        self.watchlist = self._load_watchlist()
        self.running = True
        logger.info("Deal Scanner Orchestrator initialized")

    def _load_watchlist(self) -> List[Dict[str, Any]]:
        """Load watchlist from products.json."""
        watchlist_file = BASE_DIR / 'config' / 'products.json'

        try:
            with open(watchlist_file, 'r') as f:
                data = json.load(f)
                watchlist = data.get('watchlist', [])

            # Also load from database
            db_watchlist = db.get_watchlist(active_only=True)

            # Merge watchlists (database takes precedence)
            if not db_watchlist:
                # Seed database from JSON file
                for item in watchlist:
                    db.add_watchlist_item(item)

            logger.info(f"Loaded {len(watchlist)} items from watchlist")
            return watchlist

        except FileNotFoundError:
            logger.warning(f"Watchlist file not found: {watchlist_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing watchlist JSON: {e}")
            return []

    def run_high_priority_scan(self):
        """Scan high-priority items (every 30 min)."""
        logger.info("=" * 80)
        logger.info("Starting HIGH PRIORITY scan")
        logger.info("=" * 80)

        high_priority_items = [item for item in self.watchlist if item.get('priority') == 'high']

        if not high_priority_items:
            logger.info("No high priority items in watchlist")
            return

        self._scan_watchlist_items(high_priority_items)

        logger.info("HIGH PRIORITY scan completed")
        logger.info("=" * 80)

    def run_medium_priority_scan(self):
        """Scan medium-priority items (every 2 hours)."""
        logger.info("=" * 80)
        logger.info("Starting MEDIUM PRIORITY scan")
        logger.info("=" * 80)

        medium_priority_items = [item for item in self.watchlist if item.get('priority') == 'medium']

        if not medium_priority_items:
            logger.info("No medium priority items in watchlist")
            return

        self._scan_watchlist_items(medium_priority_items)

        logger.info("MEDIUM PRIORITY scan completed")
        logger.info("=" * 80)

    def run_low_priority_scan(self):
        """Scan low-priority items (daily)."""
        logger.info("=" * 80)
        logger.info("Starting LOW PRIORITY scan")
        logger.info("=" * 80)

        low_priority_items = [item for item in self.watchlist if item.get('priority') == 'low']

        if not low_priority_items:
            logger.info("No low priority items in watchlist")
            return

        self._scan_watchlist_items(low_priority_items)

        logger.info("LOW PRIORITY scan completed")
        logger.info("=" * 80)

    def run_aggregator_scan(self):
        """Scan RSS feeds (hourly)."""
        logger.info("=" * 80)
        logger.info("Starting AGGREGATOR scan")
        logger.info("=" * 80)

        try:
            deals = aggregator_agent.scan_feeds(self.watchlist)
            logger.info(f"Aggregator found {len(deals)} deals")

        except Exception as e:
            logger.error(f"Error in aggregator scan: {e}")

        logger.info("AGGREGATOR scan completed")
        logger.info("=" * 80)

    def run_bestbuy_top_deals_scan(self):
        """Scan Best Buy top deals (every 2 hours)."""
        logger.info("Scanning Best Buy top deals")

        try:
            deals = bestbuy_agent.scan_top_deals()
            logger.info(f"Found {len(deals)} Best Buy top deals")

        except Exception as e:
            logger.error(f"Error scanning Best Buy top deals: {e}")

    def _scan_watchlist_items(self, items: List[Dict[str, Any]]):
        """
        Scan a list of watchlist items.

        Args:
            items: List of watchlist items to scan
        """
        for item in items:
            try:
                logger.info(f"Scanning for: {item['category']}")

                retailers = item.get('retailers', [])

                # Scan each retailer
                if 'amazon' in retailers:
                    try:
                        deals = amazon_agent.search_deals(item)
                        logger.info(f"Amazon: Found {len(deals)} deals")
                    except Exception as e:
                        logger.error(f"Amazon agent error: {e}")

                if 'bestbuy' in retailers:
                    try:
                        deals = bestbuy_agent.search_deals(item)
                        logger.info(f"Best Buy: Found {len(deals)} deals")
                    except Exception as e:
                        logger.error(f"Best Buy agent error: {e}")

                if 'walmart' in retailers:
                    try:
                        deals = walmart_agent.search_deals(item)
                        logger.info(f"Walmart: Found {len(deals)} deals")
                    except Exception as e:
                        logger.error(f"Walmart agent error: {e}")

                # Small delay between items
                time.sleep(5)

            except Exception as e:
                logger.error(f"Error scanning watchlist item {item.get('category')}: {e}")
                continue

    def send_status_report(self):
        """Send daily status report."""
        logger.info("Generating status report")

        try:
            stats = db.get_statistics()
            import asyncio
            asyncio.run(notifier.send_system_status(stats))

        except Exception as e:
            logger.error(f"Error sending status report: {e}")

    def run_initial_scan(self):
        """Run an initial scan of all watchlist items."""
        logger.info("Running initial scan of all watchlist items")

        self._scan_watchlist_items(self.watchlist)

        # Also scan aggregator
        self.run_aggregator_scan()

        # Scan Best Buy top deals
        self.run_bestbuy_top_deals_scan()

        logger.info("Initial scan completed")

    def setup_scheduler(self):
        """Set up the task scheduler."""
        logger.info("Setting up scheduler")

        # High priority scans (every 30 minutes)
        schedule.every(SCHEDULER_CONFIG['high_priority_interval']).minutes.do(
            self.run_high_priority_scan
        )

        # Medium priority scans (every 2 hours)
        schedule.every(SCHEDULER_CONFIG['medium_priority_interval']).minutes.do(
            self.run_medium_priority_scan
        )

        # Low priority scans (daily at 9 AM)
        schedule.every().day.at(SCHEDULER_CONFIG['low_priority_time']).do(
            self.run_low_priority_scan
        )

        # RSS feed aggregator (hourly)
        schedule.every(60).minutes.do(self.run_aggregator_scan)

        # Best Buy top deals (every 2 hours)
        schedule.every(120).minutes.do(self.run_bestbuy_top_deals_scan)

        # Daily status report (at 8 PM)
        schedule.every().day.at("20:00").do(self.send_status_report)

        logger.info("Scheduler configured:")
        logger.info(f"  - High priority: every {SCHEDULER_CONFIG['high_priority_interval']} minutes")
        logger.info(f"  - Medium priority: every {SCHEDULER_CONFIG['medium_priority_interval']} minutes")
        logger.info(f"  - Low priority: daily at {SCHEDULER_CONFIG['low_priority_time']}")
        logger.info(f"  - Aggregator: hourly")
        logger.info(f"  - Status report: daily at 20:00")

    def run(self):
        """Run the main orchestrator loop."""
        logger.info("Deal Scanner System starting...")

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Setup scheduler
        self.setup_scheduler()

        # Run initial scan
        logger.info("Running initial scan...")
        self.run_initial_scan()

        # Main loop
        logger.info("Entering main scheduler loop. Press Ctrl+C to stop.")

        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Continue after error

        logger.info("Deal Scanner System stopped")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received. Cleaning up...")
        self.running = False

        # Cleanup agents
        try:
            amazon_agent.cleanup()
            bestbuy_agent.cleanup()
            walmart_agent.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

        logger.info("Cleanup completed")


def main():
    """Main entry point."""
    logger.info("=" * 80)
    logger.info("MULTI-RETAIL DEAL SCANNER WITH AI AGENTS")
    logger.info("=" * 80)

    orchestrator = DealScannerOrchestrator()

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
