"""
Application configuration
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "JobFlow API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./data/jobflow.db"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "chrome-extension://*"]

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RESUMES_DIR: Path = DATA_DIR / "resumes"
    COVER_LETTERS_DIR: Path = DATA_DIR / "cover_letters"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # Claude integration
    CLAUDE_SESSION_PATH: Path = BASE_DIR / "claude_session"

    # Job scanning
    JOB_SCAN_INTERVAL_MINUTES: int = 30
    JOB_SCAN_ENABLED: bool = False  # Disabled by default, enable after setup

    # Limits
    MAX_UPLOAD_SIZE_MB: int = 10
    MAX_RESUMES: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Create directories
        self.DATA_DIR.mkdir(exist_ok=True)
        self.RESUMES_DIR.mkdir(exist_ok=True)
        self.COVER_LETTERS_DIR.mkdir(exist_ok=True)
        self.LOGS_DIR.mkdir(exist_ok=True)


# Global settings instance
settings = Settings()
