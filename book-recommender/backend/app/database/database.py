"""
Database connection and initialization module.
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Database file path
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "book_recommender.db"


def init_database(db_path: Optional[str] = None) -> None:
    """
    Initialize the database with schema.

    Args:
        db_path: Optional custom database path
    """
    if db_path is None:
        db_path = str(DB_PATH)

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Read schema file
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r') as f:
        schema_sql = f.read()

    # Execute schema
    conn = sqlite3.connect(db_path)
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()

    print(f"Database initialized at: {db_path}")


@contextmanager
def get_db_connection(db_path: Optional[str] = None):
    """
    Context manager for database connections.

    Args:
        db_path: Optional custom database path

    Yields:
        sqlite3.Connection: Database connection
    """
    if db_path is None:
        db_path = str(DB_PATH)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable column access by name

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def execute_query(query: str, params: tuple = (), db_path: Optional[str] = None):
    """
    Execute a query and return results.

    Args:
        query: SQL query to execute
        params: Query parameters
        db_path: Optional custom database path

    Returns:
        List of rows as dictionaries
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if query.strip().upper().startswith('SELECT'):
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            return cursor.lastrowid


def execute_many(query: str, params_list: list, db_path: Optional[str] = None):
    """
    Execute a query multiple times with different parameters.

    Args:
        query: SQL query to execute
        params_list: List of parameter tuples
        db_path: Optional custom database path
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
