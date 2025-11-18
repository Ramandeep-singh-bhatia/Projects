"""
Configuration management for Document Intelligence Platform.
Loads and validates settings from environment variables.
"""

from typing import List, Optional
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-3-large",
        env="OPENAI_EMBEDDING_MODEL"
    )
    openai_chat_model: str = Field(
        default="gpt-4-turbo-preview",
        env="OPENAI_CHAT_MODEL"
    )
    openai_cheap_model: str = Field(
        default="gpt-3.5-turbo",
        env="OPENAI_CHEAP_MODEL"
    )

    # Pinecone Configuration
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(..., env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(
        default="document-intelligence",
        env="PINECONE_INDEX_NAME"
    )
    pinecone_dimension: int = Field(default=3072, env="PINECONE_DIMENSION")

    # Database Configuration
    database_url: str = Field(..., env="DATABASE_URL")
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")

    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    redis_max_connections: int = Field(default=50, env="REDIS_MAX_CONNECTIONS")

    # Celery Configuration
    celery_broker_url: str = Field(
        default="redis://localhost:6379/0",
        env="CELERY_BROKER_URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_RESULT_BACKEND"
    )

    # Application Settings
    app_name: str = Field(
        default="Document Intelligence Platform",
        env="APP_NAME"
    )
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    secret_key: str = Field(..., env="SECRET_KEY")

    # File Upload Settings
    max_file_size_mb: int = Field(default=50, env="MAX_FILE_SIZE_MB")
    allowed_extensions: str = Field(
        default="pdf,docx,xlsx,pptx,png,jpg,jpeg,eml,msg,html,md,txt",
        env="ALLOWED_EXTENSIONS"
    )
    upload_dir: Path = Field(default=Path("data/uploads"), env="UPLOAD_DIR")
    processed_dir: Path = Field(
        default=Path("data/processed"),
        env="PROCESSED_DIR"
    )

    # Document Processing Settings
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    min_chunk_size: int = Field(default=100, env="MIN_CHUNK_SIZE")
    max_chunks_per_document: int = Field(
        default=1000,
        env="MAX_CHUNKS_PER_DOCUMENT"
    )

    # Search Configuration
    vector_search_top_k: int = Field(default=10, env="VECTOR_SEARCH_TOP_K")
    keyword_search_top_k: int = Field(default=10, env="KEYWORD_SEARCH_TOP_K")
    hybrid_vector_weight: float = Field(default=0.7, env="HYBRID_VECTOR_WEIGHT")
    hybrid_keyword_weight: float = Field(
        default=0.3,
        env="HYBRID_KEYWORD_WEIGHT"
    )
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    rerank_top_k: int = Field(default=5, env="RERANK_TOP_K")

    # RAG Configuration
    multi_query_num_queries: int = Field(
        default=3,
        env="MULTI_QUERY_NUM_QUERIES"
    )
    hyde_enabled: bool = Field(default=True, env="HYDE_ENABLED")
    parent_chunk_enabled: bool = Field(default=True, env="PARENT_CHUNK_ENABLED")
    max_context_length: int = Field(default=4000, env="MAX_CONTEXT_LENGTH")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8501"],
        env="CORS_ORIGINS"
    )

    # Streamlit Configuration
    streamlit_port: int = Field(default=8501, env="STREAMLIT_PORT")
    streamlit_theme: str = Field(default="light", env="STREAMLIT_THEME")

    # Security
    jwt_secret_key: str = Field(..., env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    # Monitoring
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")

    # OCR Settings
    tesseract_path: str = Field(
        default="/usr/bin/tesseract",
        env="TESSERACT_PATH"
    )
    ocr_languages: str = Field(default="eng", env="OCR_LANGUAGES")

    @validator("upload_dir", "processed_dir", pre=True)
    def create_directories(cls, v):
        """Ensure directories exist."""
        path = Path(v) if isinstance(v, str) else v
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get allowed extensions as a list."""
        return [ext.strip() for ext in self.allowed_extensions.split(",")]

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
