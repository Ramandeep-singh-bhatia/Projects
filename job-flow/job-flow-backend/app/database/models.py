"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=False)

    # Professional Links
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))

    # Location
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    country = Column(String(100), default="United States")

    # Work Authorization
    work_authorized = Column(Boolean, default=True)
    requires_sponsorship = Column(Boolean, default=False)
    security_clearance = Column(Boolean, default=False)

    # Job Preferences
    preferred_roles = Column(JSON)  # ["Senior Software Engineer", "Backend Engineer"]
    preferred_locations = Column(JSON)  # ["Seattle", "Remote", "Bellevue"]
    remote_preference = Column(String(50))  # "remote", "hybrid", "onsite", "any"
    min_salary = Column(Integer)
    max_salary = Column(Integer)

    # Experience
    total_years_experience = Column(Integer)
    current_title = Column(String(255))
    tech_skills = Column(JSON)  # {"Python": 6, "Java": 4, "AWS": 4, ...}

    # Demographics (optional, for EEO)
    gender = Column(String(50))
    ethnicity = Column(String(100))
    veteran_status = Column(String(100))
    disability_status = Column(String(100))

    # Notice Period
    notice_period_weeks = Column(Integer, default=2)
    available_start_date = Column(DateTime)

    # Additional
    professional_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="user", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    name = Column(String(255), nullable=False)  # "Backend-Focus", "ML-Systems"
    file_path = Column(String(500), nullable=False)
    file_format = Column(String(10), nullable=False)  # "pdf", "docx"
    file_size = Column(Integer)  # Size in bytes

    is_master = Column(Boolean, default=False)  # Master template

    # Auto-selection metadata
    focus_areas = Column(JSON)  # ["distributed systems", "backend", "search"]
    keywords = Column(JSON)  # Extracted keywords for matching
    technologies = Column(JSON)  # ["Java", "Python", "AWS", "Elasticsearch"]

    # Usage statistics
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # % of applications that got responses

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserProfile", back_populates="resumes")
    applications = relationship("Application", back_populates="resume")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Categorization
    category = Column(String(100))  # "experience_years", "skills", "work_auth", "personal"
    field_type = Column(String(50))  # "text", "number", "boolean", "select", "textarea"

    # Matching
    keywords = Column(JSON)  # For fuzzy matching
    variants = Column(JSON)  # Known question variations

    # Metadata
    times_used = Column(Integer, default=0)
    last_used = Column(DateTime)
    confidence_score = Column(Integer, default=100)  # 0-100
    platform_specific = Column(String(50))  # If specific to a platform

    # Learning
    auto_learned = Column(Boolean, default=False)  # Was this auto-learned or manually added?
    user_verified = Column(Boolean, default=True)  # Has user verified this answer?

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserProfile", back_populates="questions")


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    # Job details
    company = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_url = Column(String(500), nullable=False, unique=True)
    job_description = Column(Text)
    job_location = Column(String(255))
    job_type = Column(String(50))  # "Full-time", "Contract", etc.
    salary_range = Column(String(100))

    # Application details
    platform = Column(String(50), nullable=False)  # "linkedin_easy_apply", "workday", etc.
    status = Column(String(50), default="submitted")  # "draft", "submitted", "reviewing", "rejected", "interview", "offer"

    # Match score
    match_score = Column(Integer)  # 0-100
    match_reasons = Column(JSON)  # Why it matched

    # Resume used
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    resume_customizations = Column(JSON)  # What was changed for this application
    cover_letter_used = Column(Boolean, default=False)
    cover_letter_path = Column(String(500))

    # Tracking
    discovered_at = Column(DateTime)  # When job was found
    prepared_at = Column(DateTime)  # When application was prepared
    applied_at = Column(DateTime)  # When user submitted
    response_at = Column(DateTime)  # When company responded

    # Response tracking
    got_response = Column(Boolean, default=False)
    response_type = Column(String(50))  # "rejection", "phone_screen", "technical", "offer"

    # Metadata
    session_id = Column(String(100))  # Group applications by session
    time_to_fill = Column(Integer)  # Seconds to fill form
    time_to_review = Column(Integer)  # Seconds user spent reviewing
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("UserProfile", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
    answers = relationship("ApplicationAnswer", back_populates="application", cascade="all, delete-orphan")


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), nullable=False)

    question_text = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"))  # If matched to known question

    # Metadata
    confidence = Column(Integer)  # How confident was the match (0-100)
    manually_edited = Column(Boolean, default=False)  # Did user edit this?

    # Relationships
    application = relationship("Application", back_populates="answers")


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)

    # Job details
    company = Column(String(255), nullable=False)
    job_title = Column(String(255), nullable=False)
    job_url = Column(String(500), nullable=False, unique=True)
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String(255))
    job_type = Column(String(50))
    salary_range = Column(String(100))

    # Platform info
    platform = Column(String(50))  # "linkedin", "indeed", etc.
    platform_job_id = Column(String(100))
    easy_apply = Column(Boolean, default=False)

    # Dates
    posted_date = Column(DateTime)
    expires_date = Column(DateTime)

    # Matching
    match_score = Column(Integer)  # 0-100
    match_details = Column(JSON)  # Detailed matching breakdown

    # Status
    reviewed = Column(Boolean, default=False)
    applied = Column(Boolean, default=False)
    skipped = Column(Boolean, default=False)
    skip_reason = Column(String(255))

    # Tracking
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime, default=datetime.utcnow)

    # Relationships
    application_id = Column(Integer, ForeignKey("applications.id"))


class PlatformPattern(Base):
    """Store learned patterns for unknown platforms"""
    __tablename__ = "platform_patterns"

    id = Column(Integer, primary_key=True, index=True)

    # Platform identification
    platform_identifier = Column(String(255), unique=True)  # Domain or signature
    platform_name = Column(String(255))
    platform_url_pattern = Column(String(500))

    # Field mappings (learned from AI analysis + user corrections)
    field_selectors = Column(JSON)  # CSS selectors or XPath for each field
    field_mappings = Column(JSON)  # Field type mappings
    field_labels = Column(JSON)  # Expected labels

    # Form characteristics
    is_multi_step = Column(Boolean, default=False)
    step_count = Column(Integer)
    requires_cover_letter = Column(Boolean)
    requires_resume_upload = Column(Boolean)

    # Performance metrics
    times_used = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # % of successful auto-fills
    last_success_rate = Column(Float)  # Success rate in last 10 uses

    # Learning metadata
    last_updated = Column(DateTime)
    needs_review = Column(Boolean, default=False)  # Flag if success rate drops

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Session(Base):
    """Track application sessions for analytics"""
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)

    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

    applications_submitted = Column(Integer, default=0)
    applications_skipped = Column(Integer, default=0)

    total_time_seconds = Column(Integer)
    avg_time_per_app = Column(Integer)

    session_type = Column(String(50))  # "manual", "batch_review"
