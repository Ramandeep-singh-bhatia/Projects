"""
Database initialization script
Run this to create all tables
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.models import init_database, Base


def main():
    """Initialize the database"""
    print("=" * 60)
    print("Stock Analysis Agent - Database Initialization")
    print("=" * 60)

    # Ensure data directory exists
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Data directory: {data_dir}")

    # Database path
    db_path = data_dir / "stock_analysis.db"
    database_url = f"sqlite:///{db_path}"

    # Check if database already exists
    if db_path.exists():
        response = input(f"\nDatabase already exists at {db_path}\nRecreate? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return

        # Backup existing database
        backup_path = str(db_path) + ".backup"
        print(f"Creating backup at {backup_path}")
        import shutil
        shutil.copy2(db_path, backup_path)
        db_path.unlink()

    # Create database
    print(f"\nCreating database at: {db_path}")
    engine = init_database(database_url)

    # Print table information
    print("\n" + "=" * 60)
    print("Database Tables Created:")
    print("=" * 60)

    for table_name in Base.metadata.tables.keys():
        print(f"  ✓ {table_name}")

    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print(f"\nDatabase location: {db_path}")
    print(f"Size: {db_path.stat().st_size / 1024:.2f} KB")
    print("\nYou can now run the application.")


if __name__ == "__main__":
    main()
