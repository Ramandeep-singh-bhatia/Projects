"""
Configuration management using Pydantic Settings.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Keys
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")

    # Model Configuration
    embedding_model: str = Field(
        default="text-embedding-ada-002",
        env="EMBEDDING_MODEL"
    )
    llm_model: str = Field(
        default="claude-sonnet-4-20250514",
        env="LLM_MODEL"
    )
    fallback_llm_model: str = Field(
        default="gpt-4",
        env="FALLBACK_LLM_MODEL"
    )
    llm_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        env="LLM_TEMPERATURE"
    )
    llm_max_tokens: int = Field(
        default=1000,
        gt=0,
        env="LLM_MAX_TOKENS"
    )

    # Document Processing
    chunk_size: int = Field(
        default=500,
        gt=0,
        env="CHUNK_SIZE"
    )
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        env="CHUNK_OVERLAP"
    )
    max_chunk_size: int = Field(
        default=1000,
        gt=0,
        env="MAX_CHUNK_SIZE"
    )

    # Retrieval Configuration
    top_k_retrieval: int = Field(
        default=5,
        gt=0,
        env="TOP_K_RETRIEVAL"
    )
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        env="CONFIDENCE_THRESHOLD"
    )
    hybrid_search_alpha: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        env="HYBRID_SEARCH_ALPHA",
        description="Weight for vector search vs keyword search (0=keyword only, 1=vector only)"
    )

    # Database
    database_url: str = Field(
        default="sqlite:///./data/database/customer_support.db",
        env="DATABASE_URL"
    )

    # Vector Store
    vector_store_path: str = Field(
        default="./data/vector_store",
        env="VECTOR_STORE_PATH"
    )
    faiss_index_name: str = Field(
        default="customer_support_index",
        env="FAISS_INDEX_NAME"
    )

    # API Configuration
    api_host: str = Field(
        default="0.0.0.0",
        env="API_HOST"
    )
    api_port: int = Field(
        default=8000,
        gt=0,
        le=65535,
        env="API_PORT"
    )
    rate_limit_per_minute: int = Field(
        default=10,
        gt=0,
        env="RATE_LIMIT_PER_MINUTE"
    )

    # Streamlit Configuration
    streamlit_port: int = Field(
        default=8501,
        gt=0,
        le=65535,
        env="STREAMLIT_PORT"
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL"
    )
    log_format: str = Field(
        default="json",
        env="LOG_FORMAT"
    )

    # Performance
    max_conversation_history: int = Field(
        default=5,
        gt=0,
        env="MAX_CONVERSATION_HISTORY"
    )
    max_tokens_per_request: int = Field(
        default=8000,
        gt=0,
        env="MAX_TOKENS_PER_REQUEST"
    )
    request_timeout: int = Field(
        default=30,
        gt=0,
        env="REQUEST_TIMEOUT"
    )

    # Analytics
    enable_analytics: bool = Field(
        default=True,
        env="ENABLE_ANALYTICS"
    )
    track_costs: bool = Field(
        default=True,
        env="TRACK_COSTS"
    )

    # Escalation
    escalation_confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        env="ESCALATION_CONFIDENCE_THRESHOLD"
    )
    max_retry_attempts: int = Field(
        default=3,
        gt=0,
        env="MAX_RETRY_ATTEMPTS"
    )

    # Project paths (computed)
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default=None)
    documents_dir: Path = Field(default=None)
    vector_store_dir: Path = Field(default=None)
    database_dir: Path = Field(default=None)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set computed paths after initialization
        self.data_dir = self.project_root / "data"
        self.documents_dir = self.data_dir / "documents"
        self.vector_store_dir = self.data_dir / "vector_store"
        self.database_dir = self.data_dir / "database"

    @validator("chunk_overlap")
    def validate_chunk_overlap(cls, v, values):
        """Ensure chunk overlap is less than chunk size"""
        if "chunk_size" in values and v >= values["chunk_size"]:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper

    @validator("log_format")
    def validate_log_format(cls, v):
        """Validate log format"""
        valid_formats = ["json", "text"]
        v_lower = v.lower()
        if v_lower not in valid_formats:
            raise ValueError(f"log_format must be one of {valid_formats}")
        return v_lower

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.data_dir,
            self.documents_dir,
            self.vector_store_dir,
            self.database_dir
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def get_database_url(self) -> str:
        """Get the properly formatted database URL"""
        if self.database_url.startswith("sqlite"):
            # Ensure the database directory exists
            self.database_dir.mkdir(parents=True, exist_ok=True)
            return self.database_url
        return self.database_url

    def get_vector_store_path(self) -> Path:
        """Get the vector store path and ensure it exists"""
        path = Path(self.vector_store_path)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_faiss_index_path(self) -> Path:
        """Get the full path to the FAISS index"""
        return self.get_vector_store_path() / self.faiss_index_name

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return not self.is_production

    def __repr__(self):
        """Safe representation without exposing API keys"""
        return (
            f"Settings("
            f"llm_model='{self.llm_model}', "
            f"embedding_model='{self.embedding_model}', "
            f"database_url='{self.database_url}', "
            f"log_level='{self.log_level}'"
            f")"
        )


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get or create the global settings instance.

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.create_directories()
    return _settings


def reload_settings() -> Settings:
    """
    Reload settings from environment.

    Returns:
        New Settings instance
    """
    global _settings
    _settings = Settings()
    _settings.create_directories()
    return _settings


# LLM Pricing Configuration (tokens per dollar)
LLM_PRICING = {
    "claude-sonnet-4-20250514": {
        "input": 0.003,  # per 1K tokens
        "output": 0.015,  # per 1K tokens
    },
    "gpt-4": {
        "input": 0.03,  # per 1K tokens
        "output": 0.06,  # per 1K tokens
    },
    "text-embedding-ada-002": {
        "input": 0.0001,  # per 1K tokens
        "output": 0.0,
    }
}


def calculate_cost(model: str, input_tokens: int, output_tokens: int = 0) -> float:
    """
    Calculate cost for LLM usage.

    Args:
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in dollars
    """
    if model not in LLM_PRICING:
        return 0.0

    pricing = LLM_PRICING[model]
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]

    return input_cost + output_cost
