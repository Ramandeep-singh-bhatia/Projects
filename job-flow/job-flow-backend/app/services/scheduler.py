"""
Job Scanning Scheduler - Automated periodic job discovery

This service manages scheduled job scans using APScheduler.
It runs scans at configured intervals (default: every 30 minutes)
and can be customized per user.

Features:
- Automatic job discovery every 30 minutes
- User-specific scan schedules
- Overnight batch scanning
- Configurable max jobs per scan
- Error handling and retry logic
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, time as dt_time

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.database.models import UserProfile
from app.services.job_scanner import scan_jobs_for_user


logger = logging.getLogger(__name__)


class JobScanScheduler:
    """
    Manages scheduled job scans for all users.

    Usage:
        scheduler = JobScanScheduler()
        scheduler.start()

        # Add user to scanning
        scheduler.add_user_scan(user_id=1, interval_minutes=30)

        # Stop scheduler on shutdown
        scheduler.stop()
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.active_jobs: Dict[int, str] = {}  # user_id -> job_id mapping
        self.is_running = False

    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("JobScanScheduler started")

            # Load all active users and schedule their scans
            self._load_active_users()

    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("JobScanScheduler stopped")

    def _load_active_users(self):
        """Load all users who have scanning enabled and schedule their scans"""
        db = SessionLocal()
        try:
            # Get all users (in production, filter by users who have scanning enabled)
            users = db.query(UserProfile).all()

            for user in users:
                # Default: scan every 30 minutes during business hours
                self.add_user_scan(
                    user_id=user.id,
                    interval_minutes=30,
                    max_jobs=50
                )

            logger.info(f"Loaded {len(users)} users for scheduled scanning")

        except Exception as e:
            logger.error(f"Error loading active users: {str(e)}")

        finally:
            db.close()

    def add_user_scan(
        self,
        user_id: int,
        interval_minutes: int = 30,
        max_jobs: int = 50,
        start_hour: int = 8,
        end_hour: int = 22
    ):
        """
        Add a scheduled scan for a user.

        Args:
            user_id: User ID to scan for
            interval_minutes: Scan interval in minutes (default: 30)
            max_jobs: Maximum jobs to fetch per scan (default: 50)
            start_hour: Start hour for scans (default: 8am)
            end_hour: End hour for scans (default: 10pm)
        """
        # Remove existing scan if any
        self.remove_user_scan(user_id)

        # Create job ID
        job_id = f"user_{user_id}_scan"

        # Add interval job
        # Only scan during specified hours to avoid rate limiting
        self.scheduler.add_job(
            func=self._scan_job_wrapper,
            trigger=IntervalTrigger(minutes=interval_minutes),
            args=[user_id, max_jobs],
            id=job_id,
            name=f"Job scan for user {user_id}",
            replace_existing=True,
            max_instances=1,  # Prevent overlapping scans
            misfire_grace_time=300,  # 5 minutes grace period
        )

        self.active_jobs[user_id] = job_id
        logger.info(f"Scheduled scan for user {user_id}: every {interval_minutes} minutes")

    def add_overnight_scan(self, user_id: int, scan_time: str = "02:00"):
        """
        Add an overnight batch scan for a user.

        This is useful for discovering many jobs overnight for morning review.

        Args:
            user_id: User ID to scan for
            scan_time: Time to run scan in HH:MM format (default: "02:00" = 2am)
        """
        hour, minute = map(int, scan_time.split(":"))

        job_id = f"user_{user_id}_overnight"

        self.scheduler.add_job(
            func=self._scan_job_wrapper,
            trigger=CronTrigger(hour=hour, minute=minute),
            args=[user_id, 100],  # Fetch more jobs in overnight scan
            id=job_id,
            name=f"Overnight scan for user {user_id}",
            replace_existing=True,
        )

        logger.info(f"Scheduled overnight scan for user {user_id} at {scan_time}")

    def remove_user_scan(self, user_id: int):
        """Remove scheduled scan for a user"""
        job_id = self.active_jobs.get(user_id)
        if job_id:
            try:
                self.scheduler.remove_job(job_id)
                del self.active_jobs[user_id]
                logger.info(f"Removed scan schedule for user {user_id}")
            except Exception as e:
                logger.error(f"Error removing scan for user {user_id}: {str(e)}")

    async def _scan_job_wrapper(self, user_id: int, max_jobs: int):
        """
        Wrapper for the scan job that handles database sessions and errors.

        This function:
        1. Creates a new database session
        2. Runs the scan
        3. Handles errors gracefully
        4. Logs results
        """
        db = SessionLocal()

        try:
            logger.info(f"[Scheduled Scan] Starting scan for user {user_id}")

            # Run scan
            results = await scan_jobs_for_user(
                db=db,
                user_id=user_id,
                max_jobs=max_jobs
            )

            # Log results
            total_found = sum(results.values())
            logger.info(f"[Scheduled Scan] User {user_id}: Found {total_found} new jobs - {results}")

        except Exception as e:
            logger.error(f"[Scheduled Scan] Error scanning for user {user_id}: {str(e)}", exc_info=True)

        finally:
            db.close()

    def get_next_run(self, user_id: int) -> Optional[datetime]:
        """Get next scheduled run time for a user"""
        job_id = self.active_jobs.get(user_id)
        if job_id:
            job = self.scheduler.get_job(job_id)
            if job:
                return job.next_run_time
        return None

    def get_all_jobs(self) -> list[Dict[str, Any]]:
        """Get all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger),
            })
        return jobs

    def pause_user_scan(self, user_id: int):
        """Pause scheduled scan for a user"""
        job_id = self.active_jobs.get(user_id)
        if job_id:
            job = self.scheduler.get_job(job_id)
            if job:
                job.pause()
                logger.info(f"Paused scan for user {user_id}")

    def resume_user_scan(self, user_id: int):
        """Resume scheduled scan for a user"""
        job_id = self.active_jobs.get(user_id)
        if job_id:
            job = self.scheduler.get_job(job_id)
            if job:
                job.resume()
                logger.info(f"Resumed scan for user {user_id}")


# Global scheduler instance
_scheduler: Optional[JobScanScheduler] = None


def get_scheduler() -> JobScanScheduler:
    """
    Get global scheduler instance.

    Creates scheduler if it doesn't exist.
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = JobScanScheduler()
    return _scheduler


def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    if not scheduler.is_running:
        scheduler.start()
        logger.info("Global job scan scheduler started")


def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler
    if _scheduler and _scheduler.is_running:
        _scheduler.stop()
        logger.info("Global job scan scheduler stopped")
