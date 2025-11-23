"""
Pydantic schemas for questions
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QuestionBase(BaseModel):
    question_text: str
    answer: str
    category: Optional[str] = None
    field_type: Optional[str] = "text"
    keywords: Optional[List[str]] = None
    variants: Optional[List[str]] = None
    platform_specific: Optional[str] = None


class QuestionCreate(QuestionBase):
    user_id: int = 1  # Default to single user for now


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    field_type: Optional[str] = None
    keywords: Optional[List[str]] = None
    variants: Optional[List[str]] = None
    user_verified: Optional[bool] = None


class QuestionResponse(QuestionBase):
    id: int
    user_id: int
    times_used: int
    last_used: Optional[datetime] = None
    confidence_score: int
    auto_learned: bool
    user_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionMatchRequest(BaseModel):
    question_text: str


class QuestionMatchResponse(BaseModel):
    answer: Optional[str] = None
    confidence: int
    matched_question: Optional[str] = None
    question_id: Optional[int] = None
    suggestions: List[dict]


class QuestionLearnRequest(BaseModel):
    question_text: str
    answer: str
    category: Optional[str] = None
