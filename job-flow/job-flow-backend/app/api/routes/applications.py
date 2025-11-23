"""
API routes for application tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta

from ...database import get_db
from ...database.models import Application, ApplicationAnswer
from ...schemas.application import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    ApplicationAnswerCreate, ApplicationAnswerResponse
)

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("/", response_model=List[ApplicationResponse])
async def list_applications(
    skip: int = 0,
    limit: int = Query(50, le=200),
    status_filter: Optional[str] = Query(None, alias="status"),
    company: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    platform: Optional[str] = None,
    min_match_score: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """List applications with filtering"""
    query = db.query(Application)

    if status_filter:
        query = query.filter(Application.status == status_filter)

    if company:
        query = query.filter(Application.company.ilike(f"%{company}%"))

    if platform:
        query = query.filter(Application.platform == platform)

    if min_match_score is not None:
        query = query.filter(Application.match_score >= min_match_score)

    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(Application.applied_at >= from_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use ISO format (YYYY-MM-DD)"
            )

    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(Application.applied_at <= to_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use ISO format (YYYY-MM-DD)"
            )

    applications = query.order_by(
        Application.applied_at.desc()
    ).offset(skip).limit(limit).all()

    return applications


@router.get("/{app_id}", response_model=ApplicationResponse)
async def get_application(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Get single application details"""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {app_id} not found"
        )
    return app


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    application: ApplicationCreate,
    db: Session = Depends(get_db)
):
    """Create new application record"""
    # Check for duplicate job URL
    existing = db.query(Application).filter(
        Application.job_url == application.job_url
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application for this job URL already exists"
        )

    db_app = Application(
        **application.model_dump(),
        applied_at=datetime.utcnow()
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app


@router.put("/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: int,
    update: ApplicationUpdate,
    db: Session = Depends(get_db)
):
    """Update application"""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {app_id} not found"
        )

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(app, key, value)

    # Track response
    if update.status and update.status in ["interview", "offer"]:
        app.got_response = True
        app.response_type = update.status
        if not app.response_at:
            app.response_at = datetime.utcnow()

    if update.status == "rejected":
        app.got_response = True
        app.response_type = "rejection"
        if not app.response_at:
            app.response_at = datetime.utcnow()

    app.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Delete application"""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {app_id} not found"
        )

    db.delete(app)
    db.commit()
    return None


@router.put("/{app_id}/status")
async def update_status(
    app_id: int,
    status_value: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update application status"""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {app_id} not found"
        )

    app.status = status_value
    if notes:
        app.notes = notes

    # Track response
    if status_value in ["interview", "offer"]:
        app.got_response = True
        app.response_type = status_value
        if not app.response_at:
            app.response_at = datetime.utcnow()

    if status_value == "rejected":
        app.got_response = True
        app.response_type = "rejection"
        if not app.response_at:
            app.response_at = datetime.utcnow()

    app.updated_at = datetime.utcnow()
    db.commit()

    return {"message": "Status updated", "status": app.status}


@router.get("/{app_id}/answers", response_model=List[ApplicationAnswerResponse])
async def get_application_answers(
    app_id: int,
    db: Session = Depends(get_db)
):
    """Get all answers for an application"""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {app_id} not found"
        )

    answers = db.query(ApplicationAnswer).filter(
        ApplicationAnswer.application_id == app_id
    ).all()

    return answers


@router.post("/{app_id}/answers", response_model=ApplicationAnswerResponse)
async def add_application_answer(
    app_id: int,
    answer: ApplicationAnswerCreate,
    db: Session = Depends(get_db)
):
    """Add answer to application"""
    app = db.query(Application).filter(Application.id == app_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {app_id} not found"
        )

    # Ensure app_id matches
    if answer.application_id != app_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application ID in path must match application_id in body"
        )

    db_answer = ApplicationAnswer(**answer.model_dump())
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer


@router.get("/stats/summary")
async def get_summary_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get summary statistics for applications"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Total applications
    total = db.query(Application).filter(
        Application.applied_at >= cutoff_date
    ).count()

    # Applications with responses
    responses = db.query(Application).filter(
        Application.applied_at >= cutoff_date,
        Application.got_response == True
    ).count()

    # By status
    status_counts = {}
    statuses = db.query(
        Application.status,
        db.func.count(Application.id).label('count')
    ).filter(
        Application.applied_at >= cutoff_date
    ).group_by(Application.status).all()

    for status_name, count in statuses:
        status_counts[status_name] = count

    # By platform
    platform_counts = {}
    platforms = db.query(
        Application.platform,
        db.func.count(Application.id).label('count')
    ).filter(
        Application.applied_at >= cutoff_date
    ).group_by(Application.platform).all()

    for platform_name, count in platforms:
        platform_counts[platform_name] = count

    # Average time metrics
    avg_fill_time = db.query(
        db.func.avg(Application.time_to_fill)
    ).filter(
        Application.applied_at >= cutoff_date,
        Application.time_to_fill.isnot(None)
    ).scalar() or 0

    avg_review_time = db.query(
        db.func.avg(Application.time_to_review)
    ).filter(
        Application.applied_at >= cutoff_date,
        Application.time_to_review.isnot(None)
    ).scalar() or 0

    response_rate = (responses / total * 100) if total > 0 else 0

    return {
        "period_days": days,
        "total_applications": total,
        "responses_received": responses,
        "response_rate": round(response_rate, 2),
        "status_breakdown": status_counts,
        "platform_breakdown": platform_counts,
        "avg_fill_time_seconds": round(avg_fill_time, 2),
        "avg_review_time_seconds": round(avg_review_time, 2),
        "avg_total_time_seconds": round(avg_fill_time + avg_review_time, 2)
    }


@router.get("/stats/timeline")
async def get_timeline_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get application timeline statistics"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    applications = db.query(Application).filter(
        Application.applied_at >= cutoff_date
    ).order_by(Application.applied_at).all()

    # Group by date
    timeline = {}
    for app in applications:
        date_key = app.applied_at.date().isoformat()
        if date_key not in timeline:
            timeline[date_key] = {
                "date": date_key,
                "applications": 0,
                "responses": 0
            }
        timeline[date_key]["applications"] += 1
        if app.got_response:
            timeline[date_key]["responses"] += 1

    return {
        "period_days": days,
        "timeline": list(timeline.values())
    }
