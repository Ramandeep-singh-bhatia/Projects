"""
Pydantic schemas for applications
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class ApplicationBase(BaseModel):
    company: str
    job_title: str
    job_url: str
    job_description: Optional[str] = None
    job_location: Optional[str] = None
    job_type: Optional[str] = None
    salary_range: Optional[str] = None
    platform: str
    match_score: Optional[int] = None
    match_reasons: Optional[Dict] = None
    resume_id: Optional[int] = None


class ApplicationCreate(ApplicationBase):
    user_id: int = 1
    session_id: Optional[str] = None
    time_to_fill: Optional[int] = None
    time_to_review: Optional[int] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    response_type: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int
    status: str
    discovered_at: Optional[datetime] = None
    prepared_at: Optional[datetime] = None
    applied_at: Optional[datetime] = None
    response_at: Optional[datetime] = None
    got_response: bool
    response_type: Optional[str] = None
    session_id: Optional[str] = None
    time_to_fill: Optional[int] = None
    time_to_review: Optional[int] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationAnswerCreate(BaseModel):
    application_id: int
    question_text: str
    answer: str
    question_id: Optional[int] = None
    confidence: Optional[int] = None


class ApplicationAnswerResponse(BaseModel):
    id: int
    application_id: int
    question_text: str
    answer: str
    question_id: Optional[int] = None
    confidence: Optional[int] = None
    manually_edited: bool

    class Config:
        from_attributes = True


class ApplicationStatistics(BaseModel):
    period_days: int
    total_applications: int
    responses_received: int
    response_rate: float
    avg_time_per_application_seconds: float
    by_match_score: List[Dict]
    by_company_type: Dict
    by_platform: List[Dict]
    top_questions: List[Dict]


class PreparedApplicationResponse(BaseModel):
    job: Dict
    resume: Dict
    answers: Dict[str, str]
    ready_for_review: bool
    estimated_time: str
    match_score: int
