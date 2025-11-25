"""
Review Dashboard API Routes - Batch job review and application queue

Endpoints for reviewing discovered jobs in batches and managing the application queue.
This enables workflows like:
- Review 20+ jobs at once with filtering and sorting
- Queue jobs for batch application
- Track review status and decisions
- Export review data
"""

from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, or_, func

from app.database.database import get_db
from app.database.models import JobListing, UserProfile, Application
from pydantic import BaseModel


router = APIRouter(prefix="/review", tags=["review"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class ReviewDecision(BaseModel):
    """User's decision on a job"""
    job_id: int
    decision: str  # 'apply', 'save', 'reject', 'maybe'
    notes: Optional[str] = None
    priority: Optional[int] = None  # 1-5, 1 = highest priority


class BatchReviewRequest(BaseModel):
    """Request to process batch review decisions"""
    user_id: int
    decisions: List[ReviewDecision]


class BatchReviewResponse(BaseModel):
    """Response from batch review processing"""
    processed: int
    queued_for_application: int
    saved: int
    rejected: int
    errors: List[str] = []


class QueueItem(BaseModel):
    """Item in the application queue"""
    job_id: int
    job_title: str
    company: str
    job_url: str
    platform: str
    easy_apply: bool
    match_score: float
    priority: int
    added_at: datetime
    notes: Optional[str] = None


class ReviewStats(BaseModel):
    """Review statistics for dashboard"""
    total_discovered: int
    pending_review: int
    queued_for_application: int
    applied: int
    rejected: int
    avg_review_time_seconds: Optional[float] = None
    high_priority_count: int


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/dashboard", response_model=ReviewStats)
def get_review_dashboard(
    user_id: int,
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get review dashboard statistics.

    Shows overview of jobs to review and decisions made.

    **Example:**
    ```python
    response = requests.get("http://localhost:8000/api/review/dashboard", params={
        "user_id": 1,
        "days": 7
    })
    stats = response.json()
    print(f"Pending review: {stats['pending_review']}")
    print(f"Queued for application: {stats['queued_for_application']}")
    ```
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Total discovered in period
    total_discovered = db.query(func.count(JobListing.id)).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.discovered_at >= cutoff_date
        )
    ).scalar()

    # Pending review (status = 'discovered')
    pending_review = db.query(func.count(JobListing.id)).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'discovered',
            JobListing.discovered_at >= cutoff_date
        )
    ).scalar()

    # Queued for application (status = 'queued')
    queued_count = db.query(func.count(JobListing.id)).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'queued'
        )
    ).scalar()

    # Applied
    applied_count = db.query(func.count(JobListing.id)).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'applied',
            JobListing.applied_at >= cutoff_date
        )
    ).scalar()

    # Rejected
    rejected_count = db.query(func.count(JobListing.id)).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'rejected',
            JobListing.discovered_at >= cutoff_date
        )
    ).scalar()

    # High priority in queue
    high_priority_count = db.query(func.count(JobListing.id)).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'queued',
            JobListing.priority.in_([1, 2])
        )
    ).scalar()

    return ReviewStats(
        total_discovered=total_discovered or 0,
        pending_review=pending_review or 0,
        queued_for_application=queued_count or 0,
        applied=applied_count or 0,
        rejected=rejected_count or 0,
        high_priority_count=high_priority_count or 0
    )


@router.get("/batch", response_model=List[dict])
def get_batch_for_review(
    user_id: int,
    batch_size: int = Query(20, ge=1, le=100),
    min_score: float = Query(0.0, ge=0, le=100),
    platform: Optional[str] = None,
    easy_apply_only: bool = False,
    sort_by: str = Query("score", regex="^(score|date|company)$"),
    db: Session = Depends(get_db)
):
    """
    Get a batch of jobs for review.

    Returns jobs that haven't been reviewed yet, sorted and filtered
    according to preferences.

    **Filtering:**
    - `batch_size`: Number of jobs to return (1-100)
    - `min_score`: Minimum match score (0-100)
    - `platform`: Filter by platform ('linkedin', etc.)
    - `easy_apply_only`: Only show Easy Apply jobs
    - `sort_by`: Sort order ('score', 'date', 'company')

    **Example:**
    ```python
    # Get top 20 unreviewed jobs with Easy Apply
    response = requests.get("http://localhost:8000/api/review/batch", params={
        "user_id": 1,
        "batch_size": 20,
        "min_score": 70,
        "easy_apply_only": True,
        "sort_by": "score"
    })
    jobs = response.json()
    for job in jobs:
        print(f"{job['title']} at {job['company']} - Score: {job['match_score']}")
    ```
    """
    # Query for unreviewed jobs
    query = db.query(JobListing).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'discovered'
        )
    )

    # Apply filters
    if min_score > 0:
        query = query.filter(JobListing.match_score >= min_score)

    if platform:
        query = query.filter(JobListing.platform == platform)

    if easy_apply_only:
        query = query.filter(JobListing.easy_apply == True)

    # Apply sorting
    if sort_by == 'score':
        query = query.order_by(desc(JobListing.match_score))
    elif sort_by == 'date':
        query = query.order_by(desc(JobListing.discovered_at))
    elif sort_by == 'company':
        query = query.order_by(JobListing.company)

    # Limit batch size
    jobs = query.limit(batch_size).all()

    # Convert to dict with extra fields for review
    return [
        {
            "id": job.id,
            "job_id": job.external_job_id,
            "platform": job.platform,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description[:300] + "..." if len(job.description) > 300 else job.description,
            "full_description": job.description,
            "job_url": job.job_url,
            "employment_type": job.employment_type,
            "experience_level": job.experience_level,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "easy_apply": job.easy_apply,
            "match_score": job.match_score,
            "discovered_at": job.discovered_at.isoformat() if job.discovered_at else None,
            "posted_date": job.posted_date.isoformat() if job.posted_date else None,
        }
        for job in jobs
    ]


@router.post("/batch/decide", response_model=BatchReviewResponse)
def process_batch_decisions(
    request: BatchReviewRequest,
    db: Session = Depends(get_db)
):
    """
    Process batch review decisions.

    Accept a list of decisions for multiple jobs and update their statuses.

    **Allowed decisions:**
    - `apply`: Queue for application (status = 'queued')
    - `save`: Save for later (status = 'saved')
    - `reject`: Not interested (status = 'rejected')
    - `maybe`: Mark as maybe (status = 'maybe')

    **Priority levels (for 'apply' decision):**
    - 1: Highest priority
    - 2: High priority
    - 3: Medium priority
    - 4: Low priority
    - 5: Lowest priority

    **Example:**
    ```python
    decisions = [
        {"job_id": 1, "decision": "apply", "priority": 1, "notes": "Great fit!"},
        {"job_id": 2, "decision": "apply", "priority": 2},
        {"job_id": 3, "decision": "save", "notes": "Maybe later"},
        {"job_id": 4, "decision": "reject", "notes": "Not interested"},
    ]

    response = requests.post("http://localhost:8000/api/review/batch/decide", json={
        "user_id": 1,
        "decisions": decisions
    })
    result = response.json()
    print(f"Queued {result['queued_for_application']} jobs for application")
    ```
    """
    valid_decisions = ['apply', 'save', 'reject', 'maybe']
    errors = []
    processed = 0
    queued_for_application = 0
    saved = 0
    rejected = 0

    for decision in request.decisions:
        try:
            # Validate decision
            if decision.decision not in valid_decisions:
                errors.append(f"Job {decision.job_id}: Invalid decision '{decision.decision}'")
                continue

            # Get job
            job = db.query(JobListing).filter(
                and_(
                    JobListing.id == decision.job_id,
                    JobListing.user_id == request.user_id
                )
            ).first()

            if not job:
                errors.append(f"Job {decision.job_id}: Not found or wrong user")
                continue

            # Update status based on decision
            if decision.decision == 'apply':
                job.status = 'queued'
                job.priority = decision.priority or 3  # Default to medium priority
                job.notes = decision.notes
                queued_for_application += 1
            elif decision.decision == 'save':
                job.status = 'saved'
                job.notes = decision.notes
                saved += 1
            elif decision.decision == 'reject':
                job.status = 'rejected'
                job.notes = decision.notes
                rejected += 1
            elif decision.decision == 'maybe':
                job.status = 'maybe'
                job.notes = decision.notes

            processed += 1

        except Exception as e:
            errors.append(f"Job {decision.job_id}: {str(e)}")

    # Commit all changes
    db.commit()

    return BatchReviewResponse(
        processed=processed,
        queued_for_application=queued_for_application,
        saved=saved,
        rejected=rejected,
        errors=errors
    )


@router.get("/queue", response_model=List[QueueItem])
def get_application_queue(
    user_id: int,
    priority: Optional[int] = None,
    platform: Optional[str] = None,
    easy_apply_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Get jobs queued for application.

    Returns jobs that have been marked for application, sorted by priority.

    **Filtering:**
    - `priority`: Filter by priority (1-5)
    - `platform`: Filter by platform
    - `easy_apply_only`: Only show Easy Apply jobs

    **Example:**
    ```python
    # Get high-priority jobs in queue
    response = requests.get("http://localhost:8000/api/review/queue", params={
        "user_id": 1,
        "priority": 1,
        "easy_apply_only": True
    })
    queue = response.json()
    print(f"Found {len(queue)} high-priority Easy Apply jobs")
    ```
    """
    query = db.query(JobListing).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'queued'
        )
    )

    # Apply filters
    if priority:
        query = query.filter(JobListing.priority == priority)

    if platform:
        query = query.filter(JobListing.platform == platform)

    if easy_apply_only:
        query = query.filter(JobListing.easy_apply == True)

    # Sort by priority (1 = highest), then by score
    query = query.order_by(
        JobListing.priority.asc(),
        desc(JobListing.match_score)
    )

    jobs = query.all()

    return [
        QueueItem(
            job_id=job.id,
            job_title=job.title,
            company=job.company,
            job_url=job.job_url,
            platform=job.platform,
            easy_apply=job.easy_apply,
            match_score=job.match_score,
            priority=job.priority or 3,
            added_at=job.discovered_at,
            notes=job.notes
        )
        for job in jobs
    ]


@router.delete("/queue/{job_id}")
def remove_from_queue(
    job_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Remove a job from the application queue.

    Changes status back to 'saved'.

    **Example:**
    ```python
    requests.delete(f"http://localhost:8000/api/review/queue/{job_id}", params={
        "user_id": 1
    })
    ```
    """
    job = db.query(JobListing).filter(
        and_(
            JobListing.id == job_id,
            JobListing.user_id == user_id,
            JobListing.status == 'queued'
        )
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found in queue or wrong user"
        )

    job.status = 'saved'
    job.priority = None
    db.commit()

    return {
        "message": f"Job {job_id} removed from queue",
        "new_status": "saved"
    }


@router.put("/queue/{job_id}/priority")
def update_queue_priority(
    job_id: int,
    user_id: int,
    priority: int = Query(..., ge=1, le=5),
    db: Session = Depends(get_db)
):
    """
    Update priority of a queued job.

    **Priority levels:**
    - 1: Highest priority (apply first)
    - 2: High priority
    - 3: Medium priority
    - 4: Low priority
    - 5: Lowest priority

    **Example:**
    ```python
    # Set to highest priority
    requests.put(f"http://localhost:8000/api/review/queue/{job_id}/priority", params={
        "user_id": 1,
        "priority": 1
    })
    ```
    """
    job = db.query(JobListing).filter(
        and_(
            JobListing.id == job_id,
            JobListing.user_id == user_id,
            JobListing.status == 'queued'
        )
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail=f"Job {job_id} not found in queue or wrong user"
        )

    job.priority = priority
    db.commit()

    return {
        "job_id": job_id,
        "new_priority": priority,
        "message": f"Priority updated to {priority}"
    }


@router.post("/queue/clear-applied")
def clear_applied_from_queue(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Clear jobs marked as applied from the queue.

    Updates status from 'queued' to 'applied' for jobs that have been applied to.
    This is useful after a batch application session.

    **Example:**
    ```python
    # After applying to 10 jobs manually
    requests.post("http://localhost:8000/api/review/queue/clear-applied", params={
        "user_id": 1
    })
    ```
    """
    # This would typically be used in conjunction with the extension
    # marking jobs as applied. For now, this is a placeholder.

    return {
        "message": "Feature placeholder - integrate with extension to mark applied jobs"
    }


@router.get("/history")
def get_review_history(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get review history for analytics.

    Shows all review decisions made in the specified period.

    **Example:**
    ```python
    response = requests.get("http://localhost:8000/api/review/history", params={
        "user_id": 1,
        "days": 30
    })
    history = response.json()
    print(f"Reviewed {history['total_reviewed']} jobs in last 30 days")
    print(f"Application rate: {history['application_rate']}%")
    ```
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Get all jobs discovered in period
    all_jobs = db.query(JobListing).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.discovered_at >= cutoff_date
        )
    ).all()

    # Count by status
    status_counts = {}
    for job in all_jobs:
        status_counts[job.status] = status_counts.get(job.status, 0) + 1

    total_reviewed = sum(
        count for status, count in status_counts.items()
        if status != 'discovered'
    )

    total_discovered = len(all_jobs)
    application_rate = (status_counts.get('applied', 0) / total_discovered * 100) if total_discovered > 0 else 0

    return {
        "period_days": days,
        "total_discovered": total_discovered,
        "total_reviewed": total_reviewed,
        "by_status": status_counts,
        "application_rate": round(application_rate, 1),
        "avg_match_score": round(sum(job.match_score for job in all_jobs) / len(all_jobs), 1) if all_jobs else 0,
        "easy_apply_percentage": round(sum(1 for job in all_jobs if job.easy_apply) / len(all_jobs) * 100, 1) if all_jobs else 0
    }


@router.get("/saved")
def get_saved_jobs(
    user_id: int,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get jobs saved for later review.

    **Example:**
    ```python
    response = requests.get("http://localhost:8000/api/review/saved", params={
        "user_id": 1,
        "limit": 50
    })
    saved_jobs = response.json()
    ```
    """
    jobs = db.query(JobListing).filter(
        and_(
            JobListing.user_id == user_id,
            JobListing.status == 'saved'
        )
    ).order_by(desc(JobListing.match_score)).limit(limit).all()

    return [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "job_url": job.job_url,
            "platform": job.platform,
            "match_score": job.match_score,
            "easy_apply": job.easy_apply,
            "notes": job.notes,
            "saved_at": job.discovered_at.isoformat() if job.discovered_at else None
        }
        for job in jobs
    ]
