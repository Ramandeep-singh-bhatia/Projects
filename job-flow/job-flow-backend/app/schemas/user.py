"""
Pydantic schemas for user profile
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, List
from datetime import datetime


class ProfileBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "United States"
    work_authorized: bool = True
    requires_sponsorship: bool = False
    security_clearance: bool = False
    preferred_roles: Optional[List[str]] = None
    preferred_locations: Optional[List[str]] = None
    remote_preference: Optional[str] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    total_years_experience: Optional[int] = None
    current_title: Optional[str] = None
    tech_skills: Optional[Dict[str, int]] = None
    gender: Optional[str] = None
    ethnicity: Optional[str] = None
    veteran_status: Optional[str] = None
    disability_status: Optional[str] = None
    notice_period_weeks: int = 2
    available_start_date: Optional[datetime] = None
    professional_summary: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
