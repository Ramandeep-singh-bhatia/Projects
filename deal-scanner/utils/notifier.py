"""
Telegram notification system for deal alerts.
Sends formatted messages with deal information to users.
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. Notifications disabled.")

from config.settings import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    NOTIFICATION_CONFIG
)
from utils.database import db


class TelegramNotifier:
    """Send deal notifications via Telegram."""

    def __init__(self, bot_token: str = None, chat_id: str = None):
        """
        Initialize Telegram notifier.

        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.enabled = (
            NOTIFICATION_CONFIG['enabled']
            and TELEGRAM_AVAILABLE
            and self.bot_token
            and self.chat_id
        )

        if self.enabled:
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram notifier initialized")
        else:
            self.bot = None
            logger.warning("Telegram notifier disabled")

    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Send a message via Telegram.

        Args:
            message: Message text
            parse_mode: Parse mode ('HTML', 'Markdown', or None)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Notification disabled. Would send: {message[:100]}...")
            return False

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode,
                disable_web_page_preview=False
            )
            logger.info("Telegram message sent successfully")
            return True

        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False

    async def send_photo(self, photo_url: str, caption: str) -> bool:
        """
        Send a photo with caption via Telegram.

        Args:
            photo_url: URL of the photo
            caption: Photo caption

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Notification disabled. Would send photo: {photo_url}")
            return False

        try:
            await self.bot.send_photo(
                chat_id=self.chat_id,
                photo=photo_url,
                caption=caption,
                parse_mode='HTML'
            )
            logger.info("Telegram photo sent successfully")
            return True

        except TelegramError as e:
            logger.error(f"Telegram error sending photo: {e}")
            # Fallback to text message
            return await self.send_message(caption)
        except Exception as e:
            logger.error(f"Error sending Telegram photo: {e}")
            return False

    def format_deal_alert(self, product_data: Dict[str, Any]) -> str:
        """
        Format a deal alert message.

        Args:
            product_data: Product information

        Returns:
            Formatted message string
        """
        title = product_data.get('title', 'Unknown Product')
        retailer = product_data.get('retailer', 'Unknown').title()
        current_price = product_data.get('current_price', 0)
        previous_price = product_data.get('previous_price') or product_data.get('average_price')
        deal_score = product_data.get('deal_score', 0)
        url = product_data.get('url', '')
        historical_low = product_data.get('lowest_price')

        # Calculate savings
        savings = 0
        discount_percent = 0
        if previous_price and previous_price > current_price:
            savings = previous_price - current_price
            discount_percent = (savings / previous_price) * 100

        # Build message
        message = f"<b>DEAL ALERT!</b>\n\n"
        message += f"<b>{title[:100]}</b>\n\n"
        message += f"<b>Retailer:</b> {retailer}\n"
        message += f"<b>Current Price:</b> ${current_price:.2f}\n"

        if previous_price:
            message += f"<b>Was:</b> ${previous_price:.2f}\n"
            message += f"<b>You Save:</b> ${savings:.2f} ({discount_percent:.1f}% off)\n"

        message += f"\n<b>Deal Score:</b> {deal_score}/100\n"

        if historical_low:
            message += f"<b>Historical Low:</b> ${historical_low:.2f}\n"

        # Add rating if available
        if product_data.get('rating'):
            rating = product_data['rating']
            stars = '⭐' * int(rating)
            message += f"<b>Rating:</b> {stars} ({rating}/5)\n"

        if product_data.get('review_count'):
            message += f"<b>Reviews:</b> {product_data['review_count']:,}\n"

        # Add availability
        if product_data.get('availability'):
            availability = product_data['availability']
            if availability.lower() == 'in stock':
                message += f"\n<b>Status:</b> ✅ In Stock\n"
            else:
                message += f"\n<b>Status:</b> {availability}\n"

        message += f"\n<a href='{url}'>View Deal</a>\n"
        message += f"\n⚡ <i>Act Fast! Deals expire quickly.</i>"

        return message

    async def send_deal_alert(self, product_data: Dict[str, Any], product_id: int = None) -> bool:
        """
        Send a deal alert notification.

        Args:
            product_data: Product information
            product_id: Database product ID

        Returns:
            True if sent successfully, False otherwise
        """
        # Check if already notified recently
        if product_id:
            min_interval = NOTIFICATION_CONFIG['min_interval_minutes']
            if db.was_notified_recently(product_id, minutes=min_interval):
                logger.info(f"Skipping notification - already sent recently for product {product_id}")
                return False

        # Format and send message
        message = self.format_deal_alert(product_data)

        # Send with image if available and enabled
        if NOTIFICATION_CONFIG['include_image'] and product_data.get('image_url'):
            success = await self.send_photo(
                product_data['image_url'],
                message
            )
        else:
            success = await self.send_message(message)

        # Record notification in database
        if success and product_id:
            db.add_notification(
                product_id=product_id,
                price=product_data.get('current_price', 0),
                deal_score=product_data.get('deal_score', 0),
                message=message
            )

        return success

    async def send_error_alert(self, error_message: str):
        """
        Send an error alert to admin.

        Args:
            error_message: Error description
        """
        message = f"<b>⚠️ Deal Scanner Error</b>\n\n{error_message}"
        await self.send_message(message)

    async def send_system_status(self, stats: Dict[str, Any]):
        """
        Send system status report.

        Args:
            stats: System statistics
        """
        message = "<b>📊 Deal Scanner Status Report</b>\n\n"

        if 'total_products' in stats:
            message += f"<b>Total Products Tracked:</b> {stats['total_products']}\n"

        if 'total_notifications' in stats:
            message += f"<b>Notifications Sent:</b> {stats['total_notifications']}\n"

        if 'products_by_retailer' in stats:
            message += f"\n<b>Products by Retailer:</b>\n"
            for retailer, count in stats['products_by_retailer'].items():
                message += f"  • {retailer.title()}: {count}\n"

        if 'top_deals' in stats and stats['top_deals']:
            message += f"\n<b>Top Deals:</b>\n"
            for deal in stats['top_deals'][:5]:
                message += f"  • {deal['title'][:40]}... (${deal['current_price']:.2f}, Score: {deal['deal_score']})\n"

        await self.send_message(message)

    def send_sync(self, message: str) -> bool:
        """
        Synchronous wrapper for sending messages.

        Args:
            message: Message to send

        Returns:
            True if sent successfully
        """
        return asyncio.run(self.send_message(message))

    def send_deal_alert_sync(self, product_data: Dict[str, Any], product_id: int = None) -> bool:
        """
        Synchronous wrapper for sending deal alerts.

        Args:
            product_data: Product information
            product_id: Database product ID

        Returns:
            True if sent successfully
        """
        return asyncio.run(self.send_deal_alert(product_data, product_id))


# Singleton instance
notifier = TelegramNotifier()


def send_deal_notification(product_data: Dict[str, Any], product_id: int = None) -> bool:
    """
    Convenience function to send a deal notification.

    Args:
        product_data: Product information
        product_id: Database product ID

    Returns:
        True if sent successfully
    """
    return notifier.send_deal_alert_sync(product_data, product_id)


def send_error_notification(error_message: str):
    """
    Convenience function to send an error notification.

    Args:
        error_message: Error description
    """
    asyncio.run(notifier.send_error_alert(error_message))
