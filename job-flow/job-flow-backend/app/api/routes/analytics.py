"""
API routes for analytics and insights
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer
from typing import List, Dict
from datetime import datetime, timedelta

from ...database import get_db
from ...database.models import Application, Question, Resume, Session as AppSession

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics overview"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Applications stats
    total_apps = db.query(Application).filter(
        Application.applied_at >= cutoff_date
    ).count()

    responses = db.query(Application).filter(
        Application.applied_at >= cutoff_date,
        Application.got_response == True
    ).count()

    interviews = db.query(Application).filter(
        Application.applied_at >= cutoff_date,
        Application.response_type.in_(['phone_screen', 'technical', 'interview'])
    ).count()

    offers = db.query(Application).filter(
        Application.applied_at >= cutoff_date,
        Application.response_type == 'offer'
    ).count()

    response_rate = (responses / total_apps * 100) if total_apps > 0 else 0
    interview_rate = (interviews / total_apps * 100) if total_apps > 0 else 0
    offer_rate = (offers / total_apps * 100) if total_apps > 0 else 0

    # Time metrics
    avg_time_to_fill = db.query(
        func.avg(Application.time_to_fill)
    ).filter(
        Application.applied_at >= cutoff_date,
        Application.time_to_fill.isnot(None)
    ).scalar() or 0

    avg_time_to_review = db.query(
        func.avg(Application.time_to_review)
    ).filter(
        Application.applied_at >= cutoff_date,
        Application.time_to_review.isnot(None)
    ).scalar() or 0

    total_time_saved = (15 * 60 - (avg_time_to_fill + avg_time_to_review)) * total_apps

    return {
        "period_days": days,
        "applications": {
            "total": total_apps,
            "responses": responses,
            "interviews": interviews,
            "offers": offers
        },
        "rates": {
            "response_rate": round(response_rate, 2),
            "interview_rate": round(interview_rate, 2),
            "offer_rate": round(offer_rate, 2)
        },
        "time_metrics": {
            "avg_fill_time_seconds": round(avg_time_to_fill, 2),
            "avg_review_time_seconds": round(avg_time_to_review, 2),
            "avg_total_time_seconds": round(avg_time_to_fill + avg_time_to_review, 2),
            "total_time_saved_seconds": round(total_time_saved, 2),
            "total_time_saved_hours": round(total_time_saved / 3600, 2)
        }
    }


@router.get("/response-rate")
async def get_response_rate_breakdown(
    group_by: str = Query("match_score", regex="^(match_score|company_type|platform)$"),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get response rate breakdown by various dimensions"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    applications = db.query(Application).filter(
        Application.applied_at >= cutoff_date
    ).all()

    if group_by == "match_score":
        buckets = [
            (90, 100, "90-100%"),
            (80, 89, "80-89%"),
            (70, 79, "70-79%"),
            (0, 69, "0-69%")
        ]

        results = []
        for min_score, max_score, label in buckets:
            apps_in_bucket = [
                app for app in applications
                if app.match_score and min_score <= app.match_score <= max_score
            ]
            total = len(apps_in_bucket)
            responded = sum(1 for app in apps_in_bucket if app.got_response)

            results.append({
                "range": label,
                "applied": total,
                "responses": responded,
                "rate": round((responded / total * 100) if total > 0 else 0, 2)
            })

        return {"group_by": "match_score", "breakdown": results}

    elif group_by == "company_type":
        big_tech = ['microsoft', 'google', 'amazon', 'apple', 'meta', 'netflix', 'oracle']

        big_tech_apps = [
            app for app in applications
            if any(bt in app.company.lower() for bt in big_tech)
        ]
        other_apps = [
            app for app in applications
            if not any(bt in app.company.lower() for bt in big_tech)
        ]

        return {
            "group_by": "company_type",
            "breakdown": {
                "big_tech": {
                    "applied": len(big_tech_apps),
                    "responses": sum(1 for app in big_tech_apps if app.got_response),
                    "rate": round((sum(1 for app in big_tech_apps if app.got_response) / len(big_tech_apps) * 100) if big_tech_apps else 0, 2)
                },
                "others": {
                    "applied": len(other_apps),
                    "responses": sum(1 for app in other_apps if app.got_response),
                    "rate": round((sum(1 for app in other_apps if app.got_response) / len(other_apps) * 100) if other_apps else 0, 2)
                }
            }
        }

    elif group_by == "platform":
        platform_stats = {}

        for app in applications:
            platform = app.platform
            if platform not in platform_stats:
                platform_stats[platform] = {"applied": 0, "responses": 0}

            platform_stats[platform]["applied"] += 1
            if app.got_response:
                platform_stats[platform]["responses"] += 1

        # Calculate rates
        for platform in platform_stats:
            stats = platform_stats[platform]
            stats["rate"] = round(
                (stats["responses"] / stats["applied"] * 100) if stats["applied"] > 0 else 0,
                2
            )

        return {"group_by": "platform", "breakdown": platform_stats}


@router.get("/best-performing")
async def get_best_performing(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get best performing strategies and patterns"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    applications = db.query(Application).filter(
        Application.applied_at >= cutoff_date
    ).all()

    # Best resumes
    resume_performance = {}
    for app in applications:
        if app.resume_id:
            if app.resume_id not in resume_performance:
                resume_performance[app.resume_id] = {"used": 0, "responses": 0}

            resume_performance[app.resume_id]["used"] += 1
            if app.got_response:
                resume_performance[app.resume_id]["responses"] += 1

    # Calculate rates and get resume details
    best_resumes = []
    for resume_id, stats in resume_performance.items():
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            rate = (stats["responses"] / stats["used"] * 100) if stats["used"] > 0 else 0
            best_resumes.append({
                "resume_id": resume_id,
                "resume_name": resume.name,
                "times_used": stats["used"],
                "responses": stats["responses"],
                "response_rate": round(rate, 2)
            })

    best_resumes.sort(key=lambda x: x["response_rate"], reverse=True)

    # Best match score threshold
    high_match_apps = [app for app in applications if app.match_score and app.match_score >= 85]
    low_match_apps = [app for app in applications if app.match_score and app.match_score < 70]

    high_match_response_rate = (
        sum(1 for app in high_match_apps if app.got_response) / len(high_match_apps) * 100
    ) if high_match_apps else 0

    low_match_response_rate = (
        sum(1 for app in low_match_apps if app.got_response) / len(low_match_apps) * 100
    ) if low_match_apps else 0

    return {
        "best_resumes": best_resumes[:5],
        "match_score_insights": {
            "high_match_threshold": "85%+",
            "high_match_response_rate": round(high_match_response_rate, 2),
            "low_match_threshold": "< 70%",
            "low_match_response_rate": round(low_match_response_rate, 2),
            "recommendation": "Focus on jobs with 85%+ match score" if high_match_response_rate > low_match_response_rate * 1.5 else "Match score may not be strongly predictive"
        }
    }


@router.get("/timeline")
async def get_timeline(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Get application timeline data"""
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
                "responses": 0,
                "interviews": 0
            }

        timeline[date_key]["applications"] += 1
        if app.got_response:
            timeline[date_key]["responses"] += 1
        if app.response_type in ['phone_screen', 'technical', 'interview']:
            timeline[date_key]["interviews"] += 1

    # Fill in missing dates
    current_date = cutoff_date.date()
    end_date = datetime.utcnow().date()
    all_dates = []

    while current_date <= end_date:
        date_key = current_date.isoformat()
        if date_key in timeline:
            all_dates.append(timeline[date_key])
        else:
            all_dates.append({
                "date": date_key,
                "applications": 0,
                "responses": 0,
                "interviews": 0
            })
        current_date += timedelta(days=1)

    return {
        "period_days": days,
        "timeline": all_dates
    }


@router.get("/question-insights")
async def get_question_insights(db: Session = Depends(get_db)):
    """Get insights about question database"""
    total_questions = db.query(Question).count()

    # Most used questions
    most_used = db.query(Question).order_by(
        Question.times_used.desc()
    ).limit(20).all()

    # Least confident questions (auto-learned but not verified)
    needs_review = db.query(Question).filter(
        Question.auto_learned == True,
        Question.user_verified == False
    ).count()

    # By category
    by_category = {}
    categories = db.query(
        Question.category,
        func.count(Question.id).label('count')
    ).group_by(Question.category).all()

    for category, count in categories:
        by_category[category or "uncategorized"] = count

    return {
        "total_questions": total_questions,
        "needs_review": needs_review,
        "by_category": by_category,
        "most_used_questions": [
            {
                "question": q.question_text,
                "times_used": q.times_used,
                "category": q.category,
                "verified": q.user_verified
            }
            for q in most_used
        ]
    }


@router.get("/recommendations")
async def get_recommendations(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get personalized recommendations"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    applications = db.query(Application).filter(
        Application.applied_at >= cutoff_date
    ).all()

    recommendations = []

    if not applications:
        recommendations.append({
            "type": "action",
            "priority": "high",
            "message": "No applications yet. Start applying to build data for insights!"
        })
        return {"recommendations": recommendations}

    # Check application volume
    apps_per_day = len(applications) / days
    if apps_per_day < 5:
        recommendations.append({
            "type": "volume",
            "priority": "medium",
            "message": f"Current rate: {apps_per_day:.1f} apps/day. Target: 10+ apps/day for better results."
        })

    # Check match score distribution
    high_match = [app for app in applications if app.match_score and app.match_score >= 85]
    if len(high_match) / len(applications) < 0.3:
        recommendations.append({
            "type": "quality",
            "priority": "high",
            "message": "Only {:.0%} of applications have high match scores (85%+). Refine job search criteria.".format(len(high_match) / len(applications))
        })

    # Check response rate
    responses = sum(1 for app in applications if app.got_response)
    response_rate = (responses / len(applications)) * 100
    if response_rate < 5:
        recommendations.append({
            "type": "response_rate",
            "priority": "high",
            "message": f"Response rate is {response_rate:.1f}%. Consider: tailoring applications, improving resume, or adjusting target companies."
        })

    # Check time efficiency
    avg_time = db.query(
        func.avg(Application.time_to_fill + Application.time_to_review)
    ).filter(
        Application.applied_at >= cutoff_date,
        Application.time_to_fill.isnot(None)
    ).scalar() or 0

    if avg_time > 300:  # > 5 minutes
        recommendations.append({
            "type": "efficiency",
            "priority": "medium",
            "message": f"Average time per application: {avg_time/60:.1f} minutes. Add more questions to database to speed up."
        })

    # Check unverified questions
    unverified = db.query(Question).filter(
        Question.user_verified == False
    ).count()

    if unverified > 10:
        recommendations.append({
            "type": "maintenance",
            "priority": "low",
            "message": f"{unverified} auto-learned questions need verification. Review them for accuracy."
        })

    if not recommendations:
        recommendations.append({
            "type": "success",
            "priority": "low",
            "message": "Great job! Your application strategy is working well. Keep it up!"
        })

    return {"recommendations": recommendations}
