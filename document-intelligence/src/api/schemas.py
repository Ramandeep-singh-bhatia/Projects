"""
Pydantic schemas for API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# Document schemas
class DocumentResponse(BaseModel):
    """Document response schema."""
    id: int
    filename: str
    file_size: int
    document_type: str
    status: str
    uploaded_at: datetime
    processing_completed_at: Optional[datetime] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Document upload response schema."""
    id: int
    filename: str
    status: str
    message: str


class DocumentListResponse(BaseModel):
    """Document list response schema."""
    total: int
    skip: int
    limit: int
    documents: List[DocumentResponse]


# Search schemas
class SearchRequest(BaseModel):
    """Search request schema."""
    query: str = Field(..., min_length=1, description="Search query")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results")
    strategy: str = Field(
        default="hybrid",
        description="Search strategy: hybrid, vector, keyword, multi_query, hyde"
    )
    document_type: Optional[str] = Field(None, description="Filter by document type")
    date_from: Optional[str] = Field(None, description="Filter by date (YYYY-MM-DD)")
    date_to: Optional[str] = Field(None, description="Filter by date (YYYY-MM-DD)")


class SearchResultItem(BaseModel):
    """Single search result."""
    id: str
    score: float
    content: str
    document_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    results: List[SearchResultItem]
    total_results: int
    strategy: str
    execution_time: float


# RAG schemas
class RAGQueryRequest(BaseModel):
    """RAG query request schema."""
    question: str = Field(..., min_length=1, description="Question to answer")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of sources")
    strategy: str = Field(
        default="hybrid",
        description="Retrieval strategy"
    )
    document_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class SourceItem(BaseModel):
    """Source document item."""
    number: int
    content: str
    score: float
    document_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RAGQueryResponse(BaseModel):
    """RAG query response schema."""
    answer: str
    sources: List[SourceItem]
    confidence: float
    num_sources: int
    retrieval_strategy: str
    execution_time: float


# Analytics schemas
class DocumentOverviewResponse(BaseModel):
    """Document overview analytics."""
    total_documents: int
    documents_by_type: Dict[str, int]
    documents_by_status: Dict[str, int]
    total_pages: int
    total_words: int
    avg_processing_time: Optional[float] = None


class SearchStatsResponse(BaseModel):
    """Search statistics."""
    total_searches: int
    avg_execution_time: float
    top_queries: List[Dict[str, Any]]
    searches_by_strategy: Dict[str, int]
    searches_over_time: List[Dict[str, Any]]


class ContentIntelligenceResponse(BaseModel):
    """Content intelligence analytics."""
    top_entities: List[Dict[str, Any]]
    top_topics: List[Dict[str, Any]]
    language_distribution: Dict[str, int]
    avg_document_length: float


# Auth schemas
class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None


class UserCreate(BaseModel):
    """User creation schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response schema."""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str
