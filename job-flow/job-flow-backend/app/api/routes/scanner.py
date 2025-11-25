"""
Scanner API Routes - Job discovery and scanning endpoints

Endpoints for automated job scanning, manual triggers, and scan history.
"""

from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.database.database import get_db
from app.database.models import JobListing, UserProfile
from app.services.job_scanner import scan_jobs_for_user
from pydantic import BaseModel


router = APIRouter(prefix="/scanner", tags=["scanner"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class ScanRequest(BaseModel):
    """Request to start a job scan"""
    user_id: int
    max_jobs: int = 50
    platforms: Optional[list[str]] = None  # ['linkedin', 'indeed'] or None for all


class ScanResponse(BaseModel):
    """Response from job scan operation"""
    scan_id: Optional[int] = None
    status: str  # 'started', 'completed', 'failed'
    message: str
    jobs_found: Optional[dict[str, int]] = None  # {'linkedin': 25, 'indeed': 15}
    timestamp: datetime


class ScanHistoryItem(BaseModel):
    """Historical scan record"""
    scan_id: int
    user_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: str
    jobs_found: int
    platforms: list[str]
    error_message: Optional[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/scan", response_model=ScanResponse)
async def start_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start a job scan for a user.

    This endpoint triggers an async job scan that runs in the background.
    The scan will:
    1. Load user preferences
    2. Search job boards for matching opportunities
    3. Extract and score jobs
    4. Save to database for user review

    **Background Processing:**
    The scan runs asynchronously, so this endpoint returns immediately.
    Use GET /scanner/status/{scan_id} to check progress.

    **Rate Limiting:**
    To avoid being blocked by job boards, scans are rate-limited to:
    - 1 scan per user per 30 minutes
    - Maximum 50 jobs per platform per scan

    **Example:**
    ```python
    response = requests.post("http://localhost:8000/api/scanner/scan", json={
        "user_id": 1,
        "max_jobs": 50,
        "platforms": ["linkedin"]
    })
    print(response.json())
    # {"status": "started", "message": "Scan started for user 1", ...}
    ```
    """
    # Validate user exists
    user = db.query(UserProfile).filter(UserProfile.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")

    # Check if a recent scan is already in progress
    recent_scan_threshold = datetime.utcnow() - timedelta(minutes=30)
    recent_scan = db.query(JobListing).filter(
        and_(
            JobListing.user_id == request.user_id,
            JobListing.discovered_at >= recent_scan_threshold
        )
    ).first()

    if recent_scan:
        return ScanResponse(
            status="already_running",
            message=f"A scan was already performed in the last 30 minutes. Next scan available after {(recent_scan.discovered_at + timedelta(minutes=30)).isoformat()}",
            timestamp=datetime.utcnow()
        )

    # Start background scan
    background_tasks.add_task(
        _perform_scan,
        db=db,
        user_id=request.user_id,
        max_jobs=request.max_jobs,
        platforms=request.platforms
    )

    return ScanResponse(
        status="started",
        message=f"Job scan started for user {request.user_id}. Check status in a few minutes.",
        timestamp=datetime.utcnow()
    )


@router.post("/scan-sync", response_model=ScanResponse)
async def scan_sync(
    request: ScanRequest,
    db: Session = Depends(get_db)
):
    """
    Synchronous job scan (waits for completion).

    **Warning:** This endpoint will block until the scan completes,
    which can take 2-5 minutes depending on the number of jobs.

    Use POST /scanner/scan for asynchronous scanning (recommended).

    **Example:**
    ```python
    response = requests.post("http://localhost:8000/api/scanner/scan-sync", json={
        "user_id": 1,
        "max_jobs": 20
    })
    print(f"Found {response.json()['jobs_found']} new jobs")
    ```
    """
    # Validate user exists
    user = db.query(UserProfile).filter(UserProfile.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")

    try:
        # Perform sync scan
        results = await scan_jobs_for_user(
            db=db,
            user_id=request.user_id,
            max_jobs=request.max_jobs
        )

        return ScanResponse(
            status="completed",
            message=f"Scan completed successfully",
            jobs_found=results,
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        return ScanResponse(
            status="failed",
            message=f"Scan failed: {str(e)}",
            timestamp=datetime.utcnow()
        )


@router.get("/jobs/discovered", response_model=list[dict])
def get_discovered_jobs(
    user_id: int,
    min_score: float = 0.0,
    max_results: int = 50,
    status: Optional[str] = "discovered",
    platform: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get jobs discovered by the scanner for review.

    **Filtering:**
    - `user_id`: Required - jobs for this user
    - `min_score`: Minimum match score (0-100)
    - `max_results`: Maximum number of results to return
    - `status`: Job status ('discovered', 'saved', 'applied', 'rejected')
    - `platform`: Filter by platform ('linkedin', 'indeed', etc.)

    **Sorting:**
    Jobs are sorted by match score (highest first), then by date (newest first).

    **Example:**
    ```python
    # Get top 20 LinkedIn jobs with score >= 70
    response = requests.get("http://localhost:8000/api/scanner/jobs/discovered", params={
        "user_id": 1,
        "min_score": 70,
        "max_results": 20,
        "platform": "linkedin"
    })
    jobs = response.json()
    for job in jobs:
        print(f"{job['title']} at {job['company']} - Score: {job['match_score']}")
    ```
    """
    query = db.query(JobListing).filter(JobListing.user_id == user_id)

    # Apply filters
    if status:
        query = query.filter(JobListing.status == status)

    if platform:
        query = query.filter(JobListing.platform == platform)

    if min_score > 0:
        query = query.filter(JobListing.match_score >= min_score)

    # Sort by score and date
    query = query.order_by(
        desc(JobListing.match_score),
        desc(JobListing.discovered_at)
    )

    # Limit results
    jobs = query.limit(max_results).all()

    # Convert to dict
    return [
        {
            "id": job.id,
            "platform": job.platform,
            "external_job_id": job.external_job_id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description[:500] + "..." if len(job.description) > 500 else job.description,
            "job_url": job.job_url,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "easy_apply": job.easy_apply,
            "match_score": job.match_score,
            "status": job.status,
            "discovered_at": job.discovered_at.isoformat() if job.discovered_at else None,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
        }
        for job in jobs
    ]


@router.put("/jobs/{job_id}/status")
def update_job_status(
    job_id: int,
    status: str,
    db: Session = Depends(get_db)
):
    """
    Update status of a discovered job.

    **Allowed statuses:**
    - `discovered`: Initial state after scanning
    - `saved`: User saved for later
    - `applied`: User applied to this job
    - `rejected`: User not interested
    - `interview`: Interview scheduled
    - `offer`: Received offer
    - `archived`: Archived/no longer relevant

    **Example:**
    ```python
    # Mark job as saved
    requests.put(f"http://localhost:8000/api/scanner/jobs/{job_id}/status", params={
        "status": "saved"
    })

    # Mark as applied
    requests.put(f"http://localhost:8000/api/scanner/jobs/{job_id}/status", params={
        "status": "applied"
    })
    ```
    """
    valid_statuses = ['discovered', 'saved', 'applied', 'rejected', 'interview', 'offer', 'archived']

    if status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    job.status = status

    # Update applied_at timestamp if status is 'applied'
    if status == 'applied' and not job.applied_at:
        job.applied_at = datetime.utcnow()

    db.commit()
    db.refresh(job)

    return {
        "id": job.id,
        "status": job.status,
        "message": f"Job status updated to '{status}'"
    }


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a discovered job.

    This permanently removes the job from the database.
    Consider using PUT /jobs/{job_id}/status with status='rejected' instead.

    **Example:**
    ```python
    requests.delete(f"http://localhost:8000/api/scanner/jobs/{job_id}")
    ```
    """
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    db.delete(job)
    db.commit()

    return {"message": f"Job {job_id} deleted successfully"}


@router.get("/stats")
def get_scan_stats(
    user_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get scanning statistics for a user.

    Shows job discovery trends over the specified time period.

    **Example:**
    ```python
    response = requests.get("http://localhost:8000/api/scanner/stats", params={
        "user_id": 1,
        "days": 7
    })
    stats = response.json()
    print(f"Found {stats['total_discovered']} jobs in last 7 days")
    print(f"Average match score: {stats['avg_match_score']}")
    ```
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    jobs = db.query(JobListing).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.discovered_at >= cutoff_date
        )
    ).all()

    if not jobs:
        return {
            "user_id": user_id,
            "period_days": days,
            "total_discovered": 0,
            "avg_match_score": 0,
            "by_platform": {},
            "by_status": {},
            "top_companies": []
        }

    # Calculate stats
    total_discovered = len(jobs)
    avg_match_score = sum(job.match_score or 0 for job in jobs) / total_discovered

    # Group by platform
    by_platform = {}
    for job in jobs:
        by_platform[job.platform] = by_platform.get(job.platform, 0) + 1

    # Group by status
    by_status = {}
    for job in jobs:
        by_status[job.status] = by_status.get(job.status, 0) + 1

    # Top companies
    company_counts = {}
    for job in jobs:
        company_counts[job.company] = company_counts.get(job.company, 0) + 1

    top_companies = sorted(
        company_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    return {
        "user_id": user_id,
        "period_days": days,
        "total_discovered": total_discovered,
        "avg_match_score": round(avg_match_score, 2),
        "by_platform": by_platform,
        "by_status": by_status,
        "top_companies": [{"company": c, "count": n} for c, n in top_companies],
        "easy_apply_count": sum(1 for job in jobs if job.easy_apply),
        "easy_apply_percentage": round(sum(1 for job in jobs if job.easy_apply) / total_discovered * 100, 1)
    }


# ============================================================================
# Background Task Functions
# ============================================================================

async def _perform_scan(
    db: Session,
    user_id: int,
    max_jobs: int,
    platforms: Optional[list[str]]
):
    """
    Background task to perform job scan.

    This runs asynchronously and doesn't block the API response.
    """
    try:
        results = await scan_jobs_for_user(
            db=db,
            user_id=user_id,
            max_jobs=max_jobs
        )

        # Log results (in production, store in a scans history table)
        print(f"[Background Scan] Completed for user {user_id}: {results}")

    except Exception as e:
        print(f"[Background Scan] Failed for user {user_id}: {str(e)}")


# ============================================================================
# Scheduler Management Endpoints
# ============================================================================

@router.post("/schedule/enable")
def enable_scheduled_scans(
    user_id: int,
    interval_minutes: int = 30,
    max_jobs: int = 50,
    db: Session = Depends(get_db)
):
    """
    Enable scheduled scans for a user.

    This will automatically scan for jobs at the specified interval.

    **Default behavior:**
    - Scans every 30 minutes
    - Fetches up to 50 jobs per scan
    - Runs 24/7

    **Example:**
    ```python
    # Enable scans every hour
    requests.post("http://localhost:8000/api/scanner/schedule/enable", params={
        "user_id": 1,
        "interval_minutes": 60,
        "max_jobs": 50
    })
    ```
    """
    # Validate user exists
    user = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # Get scheduler and add user
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()

    scheduler.add_user_scan(
        user_id=user_id,
        interval_minutes=interval_minutes,
        max_jobs=max_jobs
    )

    next_run = scheduler.get_next_run(user_id)

    return {
        "message": f"Scheduled scans enabled for user {user_id}",
        "interval_minutes": interval_minutes,
        "max_jobs": max_jobs,
        "next_run": next_run.isoformat() if next_run else None
    }


@router.post("/schedule/disable")
def disable_scheduled_scans(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Disable scheduled scans for a user.

    **Example:**
    ```python
    requests.post("http://localhost:8000/api/scanner/schedule/disable", params={
        "user_id": 1
    })
    ```
    """
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()

    scheduler.remove_user_scan(user_id)

    return {
        "message": f"Scheduled scans disabled for user {user_id}"
    }


@router.post("/schedule/pause")
def pause_scheduled_scans(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Temporarily pause scheduled scans for a user.

    Use this when you want to temporarily stop scans without removing the schedule.
    Resume with POST /schedule/resume.

    **Example:**
    ```python
    # Pause scans
    requests.post("http://localhost:8000/api/scanner/schedule/pause", params={
        "user_id": 1
    })
    ```
    """
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()

    scheduler.pause_user_scan(user_id)

    return {
        "message": f"Scheduled scans paused for user {user_id}"
    }


@router.post("/schedule/resume")
def resume_scheduled_scans(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Resume paused scheduled scans for a user.

    **Example:**
    ```python
    # Resume scans
    requests.post("http://localhost:8000/api/scanner/schedule/resume", params={
        "user_id": 1
    })
    ```
    """
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()

    scheduler.resume_user_scan(user_id)

    next_run = scheduler.get_next_run(user_id)

    return {
        "message": f"Scheduled scans resumed for user {user_id}",
        "next_run": next_run.isoformat() if next_run else None
    }


@router.get("/schedule/status")
def get_schedule_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get schedule status for a user.

    Returns information about the user's scan schedule.

    **Example:**
    ```python
    response = requests.get("http://localhost:8000/api/scanner/schedule/status", params={
        "user_id": 1
    })
    status = response.json()
    print(f"Next scan: {status['next_run']}")
    ```
    """
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()

    next_run = scheduler.get_next_run(user_id)

    return {
        "user_id": user_id,
        "enabled": next_run is not None,
        "next_run": next_run.isoformat() if next_run else None
    }


@router.get("/schedule/all")
def get_all_schedules():
    """
    Get all active scan schedules.

    Admin endpoint to view all scheduled scans.

    **Example:**
    ```python
    response = requests.get("http://localhost:8000/api/scanner/schedule/all")
    schedules = response.json()
    print(f"Active schedules: {len(schedules)}")
    ```
    """
    from app.services.scheduler import get_scheduler
    scheduler = get_scheduler()

    jobs = scheduler.get_all_jobs()

    return {
        "total_schedules": len(jobs),
        "schedules": jobs
    }
