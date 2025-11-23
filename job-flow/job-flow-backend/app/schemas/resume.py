"""
Pydantic schemas for resumes
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ResumeBase(BaseModel):
    name: str
    focus_areas: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    is_master: bool = False


class ResumeCreate(ResumeBase):
    user_id: int = 1


class ResumeUpdate(BaseModel):
    name: Optional[str] = None
    focus_areas: Optional[List[str]] = None
    technologies: Optional[List[str]] = None
    is_master: Optional[bool] = None


class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_path: str
    file_format: str
    file_size: int
    keywords: Optional[List[str]] = None
    times_used: int
    success_rate: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeUploadResponse(BaseModel):
    id: int
    name: str
    file_path: str
    file_format: str
    message: str


class ResumeSelectionRequest(BaseModel):
    job_description: str


class ResumeSelectionResponse(BaseModel):
    resume_id: Optional[int] = None
    resume_name: Optional[str] = None
    match_score: int
    reasons: List[str]
