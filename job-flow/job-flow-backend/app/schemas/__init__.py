"""Pydantic schemas package"""
from .user import ProfileCreate, ProfileUpdate, ProfileResponse
from .question import (
    QuestionCreate, QuestionUpdate, QuestionResponse,
    QuestionMatchRequest, QuestionMatchResponse, QuestionLearnRequest
)
from .resume import (
    ResumeCreate, ResumeUpdate, ResumeResponse,
    ResumeUploadResponse, ResumeSelectionRequest, ResumeSelectionResponse
)
from .application import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    ApplicationAnswerCreate, ApplicationAnswerResponse,
    ApplicationStatistics, PreparedApplicationResponse
)
from .job import (
    JobListingCreate, JobListingUpdate, JobListingResponse,
    JobSearchCriteria, JobScanResponse, JobScoreRequest, JobScoreResponse
)

__all__ = [
    # User
    "ProfileCreate", "ProfileUpdate", "ProfileResponse",
    # Question
    "QuestionCreate", "QuestionUpdate", "QuestionResponse",
    "QuestionMatchRequest", "QuestionMatchResponse", "QuestionLearnRequest",
    # Resume
    "ResumeCreate", "ResumeUpdate", "ResumeResponse",
    "ResumeUploadResponse", "ResumeSelectionRequest", "ResumeSelectionResponse",
    # Application
    "ApplicationCreate", "ApplicationUpdate", "ApplicationResponse",
    "ApplicationAnswerCreate", "ApplicationAnswerResponse",
    "ApplicationStatistics", "PreparedApplicationResponse",
    # Job
    "JobListingCreate", "JobListingUpdate", "JobListingResponse",
    "JobSearchCriteria", "JobScanResponse", "JobScoreRequest", "JobScoreResponse"
]
