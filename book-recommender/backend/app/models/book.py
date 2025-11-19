"""
Pydantic models for books and reading tracking.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ReadingStatus(str, Enum):
    """Reading status enum."""
    TO_READ = "to_read"
    READING = "reading"
    COMPLETED = "completed"
    DNF = "dnf"


class BookBase(BaseModel):
    """Base book model."""
    title: str
    author: str
    isbn: Optional[str] = None
    genre: str
    page_count: Optional[int] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    publication_year: Optional[int] = None
    snoisle_available: bool = False
    format_available: Optional[str] = None


class BookCreate(BookBase):
    """Model for creating a new book."""
    pass


class Book(BookBase):
    """Complete book model with ID."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReadingLogBase(BaseModel):
    """Base reading log model."""
    book_id: int
    status: ReadingStatus
    date_started: Optional[datetime] = None
    date_completed: Optional[datetime] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    reading_duration_days: Optional[int] = None
    format_used: Optional[str] = None
    personal_notes: Optional[str] = None
    ai_summary: Optional[str] = None


class ReadingLogCreate(ReadingLogBase):
    """Model for creating a reading log entry."""
    pass


class ReadingLogUpdate(BaseModel):
    """Model for updating a reading log entry."""
    status: Optional[ReadingStatus] = None
    date_started: Optional[datetime] = None
    date_completed: Optional[datetime] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    reading_duration_days: Optional[int] = None
    format_used: Optional[str] = None
    personal_notes: Optional[str] = None
    ai_summary: Optional[str] = None


class ReadingLog(ReadingLogBase):
    """Complete reading log model with ID."""
    id: int
    date_added: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecommendationBase(BaseModel):
    """Base recommendation model."""
    book_id: int
    genre: str
    reason: Optional[str] = None
    score: Optional[float] = None
    shown_to_user: bool = False
    is_active: bool = True


class RecommendationCreate(RecommendationBase):
    """Model for creating a recommendation."""
    pass


class Recommendation(RecommendationBase):
    """Complete recommendation model with ID."""
    id: int
    recommendation_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class BookWithReadingStatus(Book):
    """Book model with reading status information."""
    reading_status: Optional[ReadingStatus] = None
    rating: Optional[int] = None
    date_started: Optional[datetime] = None
    date_completed: Optional[datetime] = None
    reading_log_id: Optional[int] = None


class RecommendationWithBook(Recommendation):
    """Recommendation model with complete book information."""
    book: Book
