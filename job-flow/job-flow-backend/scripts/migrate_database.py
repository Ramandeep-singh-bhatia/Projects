"""
Database Migration Script for Phase 4 Updates

This script migrates the existing database schema to support the new
scanner, scheduler, and review dashboard features.

Changes:
- Add new fields to job_listings table
- Add new fields to user_profiles table
- Update constraints and indexes

Usage:
    python scripts/migrate_database.py

IMPORTANT: Backup your database before running this script!
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, inspect
from app.database.database import engine, SessionLocal
from app.database.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backup_database():
    """Create a backup of the database"""
    db_path = Path(__file__).parent.parent / 'data' / 'jobflow.db'

    if not db_path.exists():
        logger.info("No existing database found. Will create new one.")
        return None

    import shutil
    from datetime import datetime

    backup_path = db_path.parent / f'jobflow_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backed up to: {backup_path}")
    return backup_path


def column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns


def table_exists(table_name: str) -> bool:
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_user_profiles():
    """Add new fields to user_profiles table"""
    logger.info("Migrating user_profiles table...")

    with engine.connect() as conn:
        # Add willing_to_relocate if it doesn't exist
        if not column_exists('user_profiles', 'willing_to_relocate'):
            logger.info("  Adding willing_to_relocate column...")
            conn.execute(text(
                "ALTER TABLE user_profiles ADD COLUMN willing_to_relocate BOOLEAN DEFAULT 0"
            ))
            conn.commit()
        else:
            logger.info("  willing_to_relocate column already exists")


def migrate_job_listings():
    """Add new fields to job_listings table"""
    logger.info("Migrating job_listings table...")

    if not table_exists('job_listings'):
        logger.info("  job_listings table doesn't exist yet, skipping migration")
        return

    with engine.connect() as conn:
        # Add user_id if it doesn't exist
        if not column_exists('job_listings', 'user_id'):
            logger.info("  Adding user_id column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN user_id INTEGER"
            ))
            # Set default user_id to 1 for existing records
            conn.execute(text(
                "UPDATE job_listings SET user_id = 1 WHERE user_id IS NULL"
            ))
            conn.commit()

        # Add status if it doesn't exist
        if not column_exists('job_listings', 'status'):
            logger.info("  Adding status column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN status VARCHAR(50) DEFAULT 'discovered'"
            ))
            # Update existing records
            conn.execute(text(
                "UPDATE job_listings SET status = CASE "
                "WHEN applied = 1 THEN 'applied' "
                "WHEN skipped = 1 THEN 'rejected' "
                "WHEN reviewed = 1 THEN 'saved' "
                "ELSE 'discovered' END"
            ))
            conn.commit()

        # Add priority if it doesn't exist
        if not column_exists('job_listings', 'priority'):
            logger.info("  Adding priority column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN priority INTEGER"
            ))
            conn.commit()

        # Add notes if it doesn't exist
        if not column_exists('job_listings', 'notes'):
            logger.info("  Adding notes column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN notes TEXT"
            ))
            conn.commit()

        # Add applied_at if it doesn't exist
        if not column_exists('job_listings', 'applied_at'):
            logger.info("  Adding applied_at column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN applied_at DATETIME"
            ))
            conn.commit()

        # Add salary_min if it doesn't exist
        if not column_exists('job_listings', 'salary_min'):
            logger.info("  Adding salary_min column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN salary_min INTEGER"
            ))
            conn.commit()

        # Add salary_max if it doesn't exist
        if not column_exists('job_listings', 'salary_max'):
            logger.info("  Adding salary_max column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN salary_max INTEGER"
            ))
            conn.commit()

        # Add experience_level if it doesn't exist
        if not column_exists('job_listings', 'experience_level'):
            logger.info("  Adding experience_level column...")
            conn.execute(text(
                "ALTER TABLE job_listings ADD COLUMN experience_level VARCHAR(100)"
            ))
            conn.commit()

        # Change match_score to FLOAT if it's INTEGER
        columns = inspect(engine).get_columns('job_listings')
        match_score_col = next((col for col in columns if col['name'] == 'match_score'), None)
        if match_score_col and str(match_score_col['type']) != 'FLOAT':
            logger.info("  Updating match_score column type to FLOAT...")
            # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
            # For now, just note that new inserts will use FLOAT
            logger.info("    Note: SQLite limitation - existing match_score values remain as INTEGER")
            logger.info("    New values will be stored as FLOAT")

        logger.info("  job_listings table migration complete")


def create_missing_tables():
    """Create any missing tables"""
    logger.info("Creating missing tables...")

    # This will create all tables defined in models.py that don't exist yet
    Base.metadata.create_all(bind=engine)

    logger.info("  All tables created")


def verify_migration():
    """Verify that migration was successful"""
    logger.info("\nVerifying migration...")

    inspector = inspect(engine)

    # Check user_profiles
    if table_exists('user_profiles'):
        columns = [col['name'] for col in inspector.get_columns('user_profiles')]
        logger.info(f"  user_profiles columns: {len(columns)}")
        required = ['willing_to_relocate']
        for col in required:
            if col in columns:
                logger.info(f"    ✓ {col}")
            else:
                logger.warning(f"    ✗ {col} MISSING")

    # Check job_listings
    if table_exists('job_listings'):
        columns = [col['name'] for col in inspector.get_columns('job_listings')]
        logger.info(f"  job_listings columns: {len(columns)}")
        required = ['user_id', 'status', 'priority', 'notes', 'applied_at',
                   'salary_min', 'salary_max', 'experience_level']
        for col in required:
            if col in columns:
                logger.info(f"    ✓ {col}")
            else:
                logger.warning(f"    ✗ {col} MISSING")

    logger.info("\nMigration verification complete!")


def main():
    """Run database migration"""
    logger.info("=" * 60)
    logger.info("JobFlow Database Migration")
    logger.info("Phase 4: Scanner, Scheduler, and Review Dashboard")
    logger.info("=" * 60)

    # Step 1: Backup
    logger.info("\nStep 1: Creating backup...")
    backup_path = backup_database()

    # Step 2: Create missing tables
    logger.info("\nStep 2: Creating missing tables...")
    try:
        create_missing_tables()
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        logger.error("Migration failed!")
        return

    # Step 3: Migrate user_profiles
    logger.info("\nStep 3: Migrating user_profiles...")
    try:
        migrate_user_profiles()
    except Exception as e:
        logger.error(f"Error migrating user_profiles: {e}")
        logger.error("Migration failed!")
        if backup_path:
            logger.info(f"Restore from backup: {backup_path}")
        return

    # Step 4: Migrate job_listings
    logger.info("\nStep 4: Migrating job_listings...")
    try:
        migrate_job_listings()
    except Exception as e:
        logger.error(f"Error migrating job_listings: {e}")
        logger.error("Migration failed!")
        if backup_path:
            logger.info(f"Restore from backup: {backup_path}")
        return

    # Step 5: Verify
    verify_migration()

    logger.info("\n" + "=" * 60)
    logger.info("✓ Migration completed successfully!")
    logger.info("=" * 60)
    if backup_path:
        logger.info(f"\nBackup saved at: {backup_path}")
    logger.info("\nYou can now start the backend server:")
    logger.info("  uvicorn app.main:app --reload")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nUnexpected error: {e}", exc_info=True)
        sys.exit(1)
