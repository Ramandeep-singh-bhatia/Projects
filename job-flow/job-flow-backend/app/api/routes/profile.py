"""
API routes for user profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict

from ...database import get_db
from ...database.models import UserProfile
from ...schemas.user import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/", response_model=ProfileResponse)
async def get_profile(db: Session = Depends(get_db)):
    """Get user profile with all details"""
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )
    return profile


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate, db: Session = Depends(get_db)):
    """Create initial user profile"""
    # Check if profile already exists
    existing_profile = db.query(UserProfile).first()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists. Use PUT to update."
        )

    db_profile = UserProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.put("/", response_model=ProfileResponse)
async def update_profile(profile: ProfileUpdate, db: Session = Depends(get_db)):
    """Update user profile"""
    db_profile = db.query(UserProfile).first()
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create a profile first."
        )

    # Update only provided fields
    update_data = profile.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)

    db.commit()
    db.refresh(db_profile)
    return db_profile


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(db: Session = Depends(get_db)):
    """Delete user profile (warning: cascades to all related data)"""
    db_profile = db.query(UserProfile).first()
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    db.delete(db_profile)
    db.commit()
    return None


@router.post("/tech-skills")
async def update_tech_skills(
    skills: Dict[str, int],
    db: Session = Depends(get_db)
):
    """Update technology skills and years of experience"""
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    profile.tech_skills = skills
    db.commit()
    return {"tech_skills": profile.tech_skills, "message": "Tech skills updated successfully"}


@router.get("/preferences")
async def get_preferences(db: Session = Depends(get_db)):
    """Get just job preferences"""
    profile = db.query(UserProfile).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return {
        "preferred_roles": profile.preferred_roles,
        "preferred_locations": profile.preferred_locations,
        "remote_preference": profile.remote_preference,
        "min_salary": profile.min_salary,
        "max_salary": profile.max_salary
    }
