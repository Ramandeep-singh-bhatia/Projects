"""
Configuration settings for the Multi-Agent Business Automation System.
Loads environment variables and provides typed configuration objects.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Main application settings."""

    # Application
    app_name: str = Field(default="Multi-Agent Business Automation System")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_workers: int = Field(default=4)
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8501")

    # Security
    secret_key: str = Field(default="change-this-secret-key-in-production")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)

    # LLM Configuration
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    reasoning_model: str = Field(default="gpt-4-turbo-preview")
    execution_model: str = Field(default="gpt-3.5-turbo")
    default_temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=4096)

    # Database - PostgreSQL
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="multi_agent_system")
    postgres_user: str = Field(default="agent_user")
    postgres_password: str = Field(default="changeme")

    # Database - Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_password: str = Field(default="changeme")
    redis_db: int = Field(default=0)

    # CRM Integration
    salesforce_username: Optional[str] = None
    salesforce_password: Optional[str] = None
    salesforce_security_token: Optional[str] = None
    salesforce_domain: str = Field(default="login")

    hubspot_api_key: Optional[str] = None
    hubspot_portal_id: Optional[str] = None

    # Email & Calendar
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_refresh_token: Optional[str] = None

    outlook_client_id: Optional[str] = None
    outlook_client_secret: Optional[str] = None
    outlook_tenant_id: Optional[str] = None

    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # Project Management
    jira_server: Optional[str] = None
    jira_email: Optional[str] = None
    jira_api_token: Optional[str] = None

    asana_access_token: Optional[str] = None
    asana_workspace_id: Optional[str] = None

    # Web Search
    serper_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    brave_search_api_key: Optional[str] = None

    # Browser Automation
    playwright_headless: bool = Field(default=True)
    playwright_timeout: int = Field(default=30000)

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60)
    rate_limit_per_hour: int = Field(default=1000)

    # Monitoring
    prometheus_port: int = Field(default=9090)
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/multi_agent_system.log")

    # Celery
    celery_broker_url: Optional[str] = None
    celery_result_backend: Optional[str] = None

    # Agent Configuration
    max_agent_iterations: int = Field(default=25)
    agent_timeout_seconds: int = Field(default=300)
    enable_human_in_loop: bool = Field(default=True)
    confidence_threshold: float = Field(default=0.85)

    # Memory Settings
    enable_long_term_memory: bool = Field(default=True)
    enable_semantic_memory: bool = Field(default=True)
    memory_ttl_hours: int = Field(default=24)

    # Workflow Settings
    max_workflow_duration_minutes: int = Field(default=60)
    enable_workflow_checkpointing: bool = Field(default=True)
    checkpoint_interval_seconds: int = Field(default=30)

    # Retry Configuration
    max_retries: int = Field(default=3)
    retry_delay_seconds: int = Field(default=5)

    # Feature Flags
    enable_agent_metrics: bool = Field(default=True)
    enable_performance_tracking: bool = Field(default=True)
    enable_ab_testing: bool = Field(default=False)
    enable_audit_trail: bool = Field(default=True)

    # Frontend
    react_app_api_url: str = Field(default="http://localhost:8000")
    streamlit_server_port: int = Field(default=8501)
    streamlit_server_address: str = Field(default="localhost")

    # Development
    reload: bool = Field(default=True)
    enable_swagger_ui: bool = Field(default=True)
    enable_redoc: bool = Field(default=True)

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL database URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @validator("confidence_threshold")
    def validate_confidence_threshold(cls, v):
        """Ensure confidence threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("confidence_threshold must be between 0 and 1")
        return v

    @validator("default_temperature")
    def validate_temperature(cls, v):
        """Ensure temperature is between 0 and 2."""
        if not 0 <= v <= 2:
            raise ValueError("default_temperature must be between 0 and 2")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
