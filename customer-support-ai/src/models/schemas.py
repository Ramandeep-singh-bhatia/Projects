"""
Pydantic models for request/response validation.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ==================== Chat Schemas ====================

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Role of the message sender (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")

    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant', 'system']:
            raise ValueError("Role must be 'user', 'assistant', or 'system'")
        return v


class ChatRequest(BaseModel):
    """Request for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation continuity")
    user_id: Optional[str] = Field(default=None, description="User ID")
    include_sources: bool = Field(default=True, description="Include source citations in response")
    max_history: int = Field(default=5, ge=0, le=20, description="Number of previous messages to include")


class SourceCitation(BaseModel):
    """Source citation for response"""
    document_id: int = Field(..., description="Document ID")
    filename: str = Field(..., description="Source filename")
    chunk_index: int = Field(..., description="Chunk index in document")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Similarity score")
    content: str = Field(..., description="Relevant content snippet")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    response: str = Field(..., description="Assistant's response")
    session_id: str = Field(..., description="Session ID")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    sources: List[SourceCitation] = Field(default=[], description="Source citations")
    should_escalate: bool = Field(default=False, description="Whether to escalate to human agent")
    suggested_questions: List[str] = Field(default=[], description="Suggested follow-up questions")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


# ==================== Document Schemas ====================

class DocumentUploadRequest(BaseModel):
    """Request for document upload"""
    filename: str = Field(..., description="Original filename")
    category: Optional[str] = Field(default=None, description="Document category")
    tags: List[str] = Field(default=[], description="Document tags")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata")


class DocumentUploadResponse(BaseModel):
    """Response from document upload"""
    success: bool = Field(..., description="Upload success status")
    document_id: Optional[int] = Field(default=None, description="Created document ID")
    filename: str = Field(..., description="Filename")
    num_chunks: Optional[int] = Field(default=None, description="Number of chunks created")
    message: str = Field(..., description="Status message")
    processing_time: Optional[float] = Field(default=None, description="Processing time in seconds")


class DocumentInfo(BaseModel):
    """Document information"""
    id: int = Field(..., description="Document ID")
    filename: str = Field(..., description="Filename")
    file_type: str = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    upload_date: datetime = Field(..., description="Upload date")
    status: str = Field(..., description="Processing status")
    num_chunks: int = Field(default=0, description="Number of chunks")
    metadata: Dict[str, Any] = Field(default={}, description="Metadata")


class DocumentListResponse(BaseModel):
    """Response for document list"""
    documents: List[DocumentInfo] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=100, description="Page size")


class DocumentDeleteResponse(BaseModel):
    """Response from document deletion"""
    success: bool = Field(..., description="Deletion success status")
    document_id: int = Field(..., description="Deleted document ID")
    message: str = Field(..., description="Status message")


# ==================== Conversation Schemas ====================

class ConversationInfo(BaseModel):
    """Conversation information"""
    id: int = Field(..., description="Conversation ID")
    session_id: str = Field(..., description="Session ID")
    user_id: Optional[str] = Field(default=None, description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    num_messages: int = Field(default=0, description="Number of messages")
    is_active: bool = Field(default=True, description="Whether conversation is active")


class ConversationHistoryResponse(BaseModel):
    """Response for conversation history"""
    conversation: ConversationInfo = Field(..., description="Conversation info")
    messages: List[ChatMessage] = Field(..., description="Message history")


# ==================== Analytics Schemas ====================

class AnalyticsMetrics(BaseModel):
    """Analytics metrics"""
    total_queries: int = Field(..., description="Total number of queries")
    avg_confidence_score: float = Field(..., ge=0.0, le=1.0, description="Average confidence score")
    avg_resolution_time: float = Field(..., description="Average resolution time in seconds")
    autonomous_resolution_rate: float = Field(..., ge=0.0, le=100.0, description="Autonomous resolution rate %")
    escalation_rate: float = Field(..., ge=0.0, le=100.0, description="Escalation rate %")
    avg_rating: float = Field(..., ge=0.0, le=5.0, description="Average customer rating")
    total_cost: float = Field(..., description="Total cost in dollars")
    period_days: int = Field(..., description="Period in days")


class QueryAnalytics(BaseModel):
    """Individual query analytics"""
    id: int = Field(..., description="Analytics ID")
    query: str = Field(..., description="Customer query")
    response: str = Field(..., description="Assistant response")
    confidence_score: Optional[float] = Field(default=None, description="Confidence score")
    rating: Optional[int] = Field(default=None, ge=1, le=5, description="Customer rating")
    resolution_time: Optional[float] = Field(default=None, description="Resolution time in seconds")
    timestamp: datetime = Field(..., description="Query timestamp")
    was_escalated: bool = Field(default=False, description="Whether query was escalated")


class AnalyticsResponse(BaseModel):
    """Response for analytics endpoint"""
    metrics: AnalyticsMetrics = Field(..., description="Aggregated metrics")
    recent_queries: List[QueryAnalytics] = Field(default=[], description="Recent queries")
    low_rated_queries: List[QueryAnalytics] = Field(default=[], description="Low rated queries")


class HourlyVolume(BaseModel):
    """Hourly query volume"""
    hour: int = Field(..., ge=0, le=23, description="Hour of day (0-23)")
    count: int = Field(..., description="Query count")


class CategoryBreakdown(BaseModel):
    """Query category breakdown"""
    category: str = Field(..., description="Category name")
    count: int = Field(..., description="Query count")


class AnalyticsDetailResponse(BaseModel):
    """Detailed analytics response"""
    metrics: AnalyticsMetrics = Field(..., description="Aggregated metrics")
    hourly_volume: List[HourlyVolume] = Field(default=[], description="Hourly query volume")
    category_breakdown: List[CategoryBreakdown] = Field(default=[], description="Category breakdown")
    confidence_distribution: Dict[str, int] = Field(default={}, description="Confidence score distribution")


# ==================== Feedback Schemas ====================

class FeedbackRequest(BaseModel):
    """Request for submitting feedback"""
    analytics_id: Optional[int] = Field(default=None, description="Analytics record ID")
    session_id: str = Field(..., description="Session ID")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    comment: Optional[str] = Field(default=None, max_length=1000, description="Optional comment")


class FeedbackResponse(BaseModel):
    """Response from feedback submission"""
    success: bool = Field(..., description="Submission success status")
    message: str = Field(..., description="Status message")


# ==================== Health Check Schema ====================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(default="1.0.0", description="API version")
    database: str = Field(..., description="Database status")
    vector_store: str = Field(..., description="Vector store status")
    num_documents: int = Field(default=0, description="Number of documents indexed")


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request ID for tracking")


# ==================== Utility Schemas ====================

class ProcessingStatus(BaseModel):
    """Processing status for long-running operations"""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Status (pending/processing/completed/failed)")
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    message: Optional[str] = Field(default=None, description="Status message")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Result data if completed")


class BulkUploadRequest(BaseModel):
    """Request for bulk document upload"""
    files: List[str] = Field(..., description="List of file paths")
    category: Optional[str] = Field(default=None, description="Category for all documents")
    chunking_strategy: str = Field(default="fixed_size", description="Chunking strategy to use")


class BulkUploadResponse(BaseModel):
    """Response from bulk upload"""
    task_id: str = Field(..., description="Task ID for tracking progress")
    num_files: int = Field(..., description="Number of files to process")
    message: str = Field(..., description="Status message")


# ==================== Configuration ====================

class Config:
    """Pydantic configuration"""
    json_encoders = {
        datetime: lambda v: v.isoformat()
    }
    schema_extra = {
        "example": {}
    }
