"""
API routes for job listings and discovery
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ...database import get_db
from ...database.models import JobListing, UserProfile
from ...schemas.job import (
    JobListingCreate, JobListingUpdate, JobListingResponse,
    JobSearchCriteria, JobScanResponse, JobScoreRequest, JobScoreResponse
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/", response_model=List[JobListingResponse])
async def list_jobs(
    skip: int = 0,
    limit: int = Query(50, le=200),
    reviewed: Optional[bool] = None,
    applied: Optional[bool] = None,
    skipped: Optional[bool] = None,
    min_score: int = Query(0, ge=0, le=100),
    platform: Optional[str] = None,
    easy_apply_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get discovered jobs with filtering"""
    query = db.query(JobListing)

    if reviewed is not None:
        query = query.filter(JobListing.reviewed == reviewed)

    if applied is not None:
        query = query.filter(JobListing.applied == applied)

    if skipped is not None:
        query = query.filter(JobListing.skipped == skipped)

    if min_score > 0:
        query = query.filter(JobListing.match_score >= min_score)

    if platform:
        query = query.filter(JobListing.platform == platform)

    if easy_apply_only:
        query = query.filter(JobListing.easy_apply == True)

    jobs = query.order_by(
        JobListing.match_score.desc(),
        JobListing.discovered_at.desc()
    ).offset(skip).limit(limit).all()

    return jobs


@router.get("/{job_id}", response_model=JobListingResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Get specific job listing"""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job listing with ID {job_id} not found"
        )
    return job


@router.post("/", response_model=JobListingResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobListingCreate,
    db: Session = Depends(get_db)
):
    """Create new job listing"""
    # Check for duplicate
    existing = db.query(JobListing).filter(
        JobListing.job_url == job.job_url
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job listing with this URL already exists"
        )

    db_job = JobListing(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.put("/{job_id}", response_model=JobListingResponse)
async def update_job(
    job_id: int,
    update: JobListingUpdate,
    db: Session = Depends(get_db)
):
    """Update job listing"""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job listing with ID {job_id} not found"
        )

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Delete job listing"""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job listing with ID {job_id} not found"
        )

    db.delete(job)
    db.commit()
    return None


@router.post("/scan", response_model=JobScanResponse)
async def trigger_job_scan(
    criteria: Optional[JobSearchCriteria] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Manually trigger job scan"""
    # Get user profile for default criteria
    profile = db.query(UserProfile).first()

    if not profile and not criteria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user profile found and no criteria provided"
        )

    # Use profile preferences if no criteria provided
    if not criteria:
        criteria = JobSearchCriteria(
            keywords=profile.preferred_roles or ["Software Engineer"],
            locations=profile.preferred_locations or ["Remote"],
            tech_skills=list(profile.tech_skills.keys()) if profile.tech_skills else []
        )

    # For now, return a placeholder response
    # In production, this would trigger the job scanner service
    return JobScanResponse(
        found=0,
        jobs=[],
        message="Job scanning functionality will be implemented in the job scanner service. " +
                "This endpoint will trigger background job discovery."
    )


@router.post("/score", response_model=JobScoreResponse)
async def score_job(
    request: JobScoreRequest,
    db: Session = Depends(get_db)
):
    """Score a job posting against user profile"""
    # Find job
    job = db.query(JobListing).filter(JobListing.job_url == request.job_url).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found in database"
        )

    # Get user profile
    profile = db.query(UserProfile).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user profile found. Create a profile first."
        )

    # Calculate score
    score = 0
    breakdown = {}
    reasons = []

    # Title match (30 points)
    if profile.preferred_roles:
        title_lower = job.job_title.lower()
        role_matches = [role for role in profile.preferred_roles if role.lower() in title_lower]
        if role_matches:
            title_score = 30
            score += title_score
            breakdown["title_match"] = title_score
            reasons.append(f"Title matches preferred roles: {', '.join(role_matches)}")

    # Location match (20 points)
    if profile.preferred_locations:
        location_lower = job.location.lower() if job.location else ""
        location_matches = [loc for loc in profile.preferred_locations if loc.lower() in location_lower]
        if location_matches or "remote" in location_lower:
            location_score = 20
            score += location_score
            breakdown["location_match"] = location_score
            reasons.append(f"Location matches: {job.location}")

    # Tech skills match (40 points)
    if profile.tech_skills and job.description:
        desc_lower = job.description.lower()
        matched_skills = [skill for skill in profile.tech_skills.keys() if skill.lower() in desc_lower]
        if matched_skills:
            skills_score = min(40, len(matched_skills) * 10)
            score += skills_score
            breakdown["skills_match"] = skills_score
            reasons.append(f"Required skills match: {', '.join(matched_skills[:5])}")

    # Easy Apply bonus (10 points)
    if job.easy_apply:
        easy_score = 10
        score += easy_score
        breakdown["easy_apply"] = easy_score
        reasons.append("Easy Apply available")

    # Update job score in database
    job.match_score = min(100, score)
    job.match_details = breakdown
    db.commit()

    return JobScoreResponse(
        score=min(100, score),
        breakdown=breakdown,
        reasons=reasons if reasons else ["Low match - consider customizing search criteria"]
    )


@router.get("/stats/summary")
async def get_job_stats(db: Session = Depends(get_db)):
    """Get job discovery statistics"""
    total_jobs = db.query(JobListing).count()
    reviewed_jobs = db.query(JobListing).filter(JobListing.reviewed == True).count()
    applied_jobs = db.query(JobListing).filter(JobListing.applied == True).count()
    skipped_jobs = db.query(JobListing).filter(JobListing.skipped == True).count()
    pending_review = total_jobs - reviewed_jobs

    # Average match score
    avg_score = db.query(db.func.avg(JobListing.match_score)).scalar() or 0

    # By platform
    by_platform = {}
    platforms = db.query(
        JobListing.platform,
        db.func.count(JobListing.id).label('count')
    ).group_by(JobListing.platform).all()

    for platform_name, count in platforms:
        by_platform[platform_name] = count

    return {
        "total_jobs_discovered": total_jobs,
        "pending_review": pending_review,
        "reviewed": reviewed_jobs,
        "applied": applied_jobs,
        "skipped": skipped_jobs,
        "avg_match_score": round(avg_score, 2),
        "by_platform": by_platform
    }


@router.post("/{job_id}/skip")
async def skip_job(
    job_id: int,
    reason: str,
    db: Session = Depends(get_db)
):
    """Mark job as skipped"""
    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job listing with ID {job_id} not found"
        )

    job.skipped = True
    job.skip_reason = reason
    job.reviewed = True
    db.commit()

    return {"message": "Job marked as skipped", "job_id": job_id}


@router.post("/{job_id}/prepare")
async def prepare_application(
    job_id: int,
    db: Session = Depends(get_db)
):
    """Prepare application for a job"""
    from ...schemas.application import PreparedApplicationResponse

    job = db.query(JobListing).filter(JobListing.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job listing with ID {job_id} not found"
        )

    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No user profile found"
        )

    # This would call the application preparer service
    # For now, return a placeholder
    return PreparedApplicationResponse(
        job={
            "id": job.id,
            "title": job.job_title,
            "company": job.company,
            "url": job.job_url,
            "description": job.description
        },
        resume={
            "id": None,
            "name": "Will be auto-selected",
            "path": None
        },
        answers={},
        ready_for_review=False,
        estimated_time="2-3 minutes",
        match_score=job.match_score or 0
    )
