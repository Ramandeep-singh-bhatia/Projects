"""
Pydantic models for reading statistics and analytics.
"""
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date, datetime
from enum import Enum


class GoalType(str, Enum):
    """Reading goal type enum."""
    ANNUAL = "annual"
    MONTHLY = "monthly"
    GENRE_DIVERSITY = "genre_diversity"
    CUSTOM = "custom"


class ReadingStatsBase(BaseModel):
    """Base reading stats model."""
    date: date
    pages_read: int = 0
    minutes_read: int = 0
    books_completed_count: int = 0


class ReadingStatsCreate(ReadingStatsBase):
    """Model for creating reading stats."""
    pass


class ReadingStats(ReadingStatsBase):
    """Complete reading stats model with ID."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ReadingGoalBase(BaseModel):
    """Base reading goal model."""
    goal_type: GoalType
    target_value: int
    current_value: int = 0
    year: Optional[int] = None
    month: Optional[int] = None
    description: Optional[str] = None
    is_active: bool = True


class ReadingGoalCreate(ReadingGoalBase):
    """Model for creating a reading goal."""
    pass


class ReadingGoalUpdate(BaseModel):
    """Model for updating a reading goal."""
    target_value: Optional[int] = None
    current_value: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ReadingGoal(ReadingGoalBase):
    """Complete reading goal model with ID."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    """Comprehensive dashboard statistics."""
    books_read_year: int
    books_read_all_time: int
    pages_read_total: int
    average_reading_speed: float  # pages per day
    completion_rate: float  # percentage
    current_streak_days: int
    books_this_month: int
    genre_distribution: Dict[str, int]
    monthly_trends: List[Dict[str, any]]
    top_rated_books: List[Dict[str, any]]
    currently_reading: List[Dict[str, any]]
    active_goals: List[ReadingGoal]


class GenreStats(BaseModel):
    """Statistics for a specific genre."""
    genre: str
    books_read: int
    average_rating: float
    total_pages: int
    completion_rate: float


class ReadingPatterns(BaseModel):
    """Analysis of user's reading patterns."""
    favorite_genres: List[str]
    avoided_genres: List[str]
    average_book_length: int
    reading_consistency_score: float  # 0-100
    genre_diversity_score: float  # 0-100
    most_productive_month: str
    reading_velocity_trend: str  # "increasing", "decreasing", "stable"
