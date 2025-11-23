"""
Pydantic schemas for job listings
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class JobListingBase(BaseModel):
    company: str
    job_title: str
    job_url: str
    description: Optional[str] = None
    requirements: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    platform: Optional[str] = None
    easy_apply: bool = False


class JobListingCreate(JobListingBase):
    platform_job_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    match_score: Optional[int] = None
    match_details: Optional[Dict] = None


class JobListingUpdate(BaseModel):
    reviewed: Optional[bool] = None
    applied: Optional[bool] = None
    skipped: Optional[bool] = None
    skip_reason: Optional[str] = None


class JobListingResponse(JobListingBase):
    id: int
    platform_job_id: Optional[str] = None
    posted_date: Optional[datetime] = None
    expires_date: Optional[datetime] = None
    match_score: Optional[int] = None
    match_details: Optional[Dict] = None
    reviewed: bool
    applied: bool
    skipped: bool
    skip_reason: Optional[str] = None
    discovered_at: datetime
    last_checked: datetime

    class Config:
        from_attributes = True


class JobSearchCriteria(BaseModel):
    keywords: List[str]
    locations: List[str]
    experience_level: Optional[List[str]] = ["Mid-Senior level"]
    posted_within: str = "24h"
    easy_apply_only: bool = True
    tech_skills: Optional[List[str]] = None
    remote_only: bool = False


class JobScanResponse(BaseModel):
    found: int
    jobs: List[Dict]
    message: str


class JobScoreRequest(BaseModel):
    job_url: str


class JobScoreResponse(BaseModel):
    score: int
    breakdown: Dict[str, int]
    reasons: List[str]
