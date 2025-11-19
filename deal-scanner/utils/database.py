"""
Database operations for the Deal Scanner system.
Uses SQLite for local storage of products, price history, and notifications.
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import json
from contextlib import contextmanager
from loguru import logger

from config.settings import DATABASE_PATH


class Database:
    """Handle all database operations for the deal scanner."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def init_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Products table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id TEXT UNIQUE,
                    asin TEXT,
                    sku TEXT,
                    title TEXT NOT NULL,
                    category TEXT,
                    retailer TEXT NOT NULL,
                    url TEXT,
                    image_url TEXT,
                    current_price REAL,
                    lowest_price REAL,
                    highest_price REAL,
                    average_price REAL,
                    rating REAL,
                    review_count INTEGER,
                    availability TEXT,
                    last_checked TIMESTAMP,
                    deal_score INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Price history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    availability TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)

            # Notifications sent table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications_sent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    deal_score INTEGER,
                    message TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
                )
            """)

            # Watchlist table (from products.json)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    keywords TEXT NOT NULL,
                    max_price REAL,
                    priority TEXT DEFAULT 'medium',
                    retailers TEXT NOT NULL,
                    check_frequency TEXT,
                    active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # API usage tracking table (for rate limiting)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    api_name TEXT NOT NULL,
                    endpoint TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    response_code INTEGER
                )
            """)

            # Create indices for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_retailer
                ON products(retailer)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_products_category
                ON products(category)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_price_history_product
                ON price_history(product_id, timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_api_usage_timestamp
                ON api_usage(api_name, timestamp)
            """)

            logger.info("Database initialized successfully")

    def upsert_product(self, product_data: Dict[str, Any]) -> int:
        """Insert or update a product."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if product exists
            cursor.execute(
                "SELECT id FROM products WHERE product_id = ?",
                (product_data.get('product_id'),)
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing product
                product_id = existing[0]
                self._update_product(cursor, product_id, product_data)
            else:
                # Insert new product
                product_id = self._insert_product(cursor, product_data)

            return product_id

    def _insert_product(self, cursor, product_data: Dict[str, Any]) -> int:
        """Insert a new product."""
        cursor.execute("""
            INSERT INTO products (
                product_id, asin, sku, title, category, retailer, url, image_url,
                current_price, lowest_price, highest_price, average_price,
                rating, review_count, availability, last_checked, deal_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            product_data.get('product_id'),
            product_data.get('asin'),
            product_data.get('sku'),
            product_data.get('title'),
            product_data.get('category'),
            product_data.get('retailer'),
            product_data.get('url'),
            product_data.get('image_url'),
            product_data.get('current_price'),
            product_data.get('current_price'),  # Initial lowest = current
            product_data.get('current_price'),  # Initial highest = current
            product_data.get('current_price'),  # Initial average = current
            product_data.get('rating'),
            product_data.get('review_count'),
            product_data.get('availability'),
            datetime.now(),
            product_data.get('deal_score'),
        ))
        return cursor.lastrowid

    def _update_product(self, cursor, product_id: int, product_data: Dict[str, Any]):
        """Update an existing product."""
        current_price = product_data.get('current_price')

        # Get current stats
        cursor.execute(
            "SELECT lowest_price, highest_price FROM products WHERE id = ?",
            (product_id,)
        )
        row = cursor.fetchone()
        lowest = min(row[0] or float('inf'), current_price) if current_price else row[0]
        highest = max(row[1] or 0, current_price) if current_price else row[1]

        cursor.execute("""
            UPDATE products SET
                title = COALESCE(?, title),
                url = COALESCE(?, url),
                image_url = COALESCE(?, image_url),
                current_price = COALESCE(?, current_price),
                lowest_price = ?,
                highest_price = ?,
                rating = COALESCE(?, rating),
                review_count = COALESCE(?, review_count),
                availability = COALESCE(?, availability),
                last_checked = ?,
                deal_score = COALESCE(?, deal_score),
                updated_at = ?
            WHERE id = ?
        """, (
            product_data.get('title'),
            product_data.get('url'),
            product_data.get('image_url'),
            current_price,
            lowest,
            highest,
            product_data.get('rating'),
            product_data.get('review_count'),
            product_data.get('availability'),
            datetime.now(),
            product_data.get('deal_score'),
            datetime.now(),
            product_id,
        ))

    def add_price_history(self, product_id: int, price: float, availability: str = None):
        """Add a price history entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO price_history (product_id, price, availability)
                VALUES (?, ?, ?)
            """, (product_id, price, availability))

            # Update average price
            cursor.execute("""
                SELECT AVG(price) FROM price_history WHERE product_id = ?
            """, (product_id,))
            avg_price = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE products SET average_price = ? WHERE id = ?
            """, (avg_price, product_id))

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by product_id."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE product_id = ?",
                (product_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all products in a category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM products WHERE category = ?",
                (category,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_price_history(self, product_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get price history for a product."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM price_history
                WHERE product_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (product_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def add_notification(self, product_id: int, price: float, deal_score: int, message: str):
        """Record a sent notification."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications_sent (product_id, price, deal_score, message)
                VALUES (?, ?, ?, ?)
            """, (product_id, price, deal_score, message))

    def was_notified_recently(self, product_id: int, minutes: int = 30) -> bool:
        """Check if notification was sent recently for this product."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM notifications_sent
                WHERE product_id = ?
                AND timestamp > datetime('now', '-' || ? || ' minutes')
            """, (product_id, minutes))
            count = cursor.fetchone()[0]
            return count > 0

    def track_api_usage(self, api_name: str, endpoint: str = None,
                        success: bool = True, response_code: int = None):
        """Track API usage for rate limiting."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_usage (api_name, endpoint, success, response_code)
                VALUES (?, ?, ?, ?)
            """, (api_name, endpoint, success, response_code))

    def get_api_usage_count(self, api_name: str, hours: int = 1) -> int:
        """Get API usage count in the last N hours."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM api_usage
                WHERE api_name = ?
                AND timestamp > datetime('now', '-' || ? || ' hours')
            """, (api_name, hours))
            return cursor.fetchone()[0]

    def add_watchlist_item(self, watchlist_data: Dict[str, Any]) -> int:
        """Add item to watchlist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO watchlist (
                    category, keywords, max_price, priority, retailers, check_frequency
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                watchlist_data['category'],
                json.dumps(watchlist_data['keywords']),
                watchlist_data.get('max_price'),
                watchlist_data.get('priority', 'medium'),
                json.dumps(watchlist_data['retailers']),
                watchlist_data.get('check_frequency'),
            ))
            return cursor.lastrowid

    def get_watchlist(self, priority: str = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get watchlist items."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM watchlist WHERE 1=1"
            params = []

            if active_only:
                query += " AND active = 1"

            if priority:
                query += " AND priority = ?"
                params.append(priority)

            cursor.execute(query, params)
            items = []
            for row in cursor.fetchall():
                item = dict(row)
                item['keywords'] = json.loads(item['keywords'])
                item['retailers'] = json.loads(item['retailers'])
                items.append(item)

            return items

    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Total products
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['total_products'] = cursor.fetchone()[0]

            # Products by retailer
            cursor.execute("""
                SELECT retailer, COUNT(*) as count
                FROM products
                GROUP BY retailer
            """)
            stats['products_by_retailer'] = dict(cursor.fetchall())

            # Total notifications sent
            cursor.execute("SELECT COUNT(*) FROM notifications_sent")
            stats['total_notifications'] = cursor.fetchone()[0]

            # Best deals (highest scores)
            cursor.execute("""
                SELECT title, retailer, current_price, deal_score
                FROM products
                WHERE deal_score IS NOT NULL
                ORDER BY deal_score DESC
                LIMIT 10
            """)
            stats['top_deals'] = [dict(row) for row in cursor.fetchall()]

            return stats


# Singleton instance
db = Database()
