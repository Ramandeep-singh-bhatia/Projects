"""
Database models for Document Intelligence Platform.
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey,
    Text, JSON, Float, Boolean, Enum, Index
)
from sqlalchemy.orm import relationship
from src.core.database import Base


class ProcessingStatus(PyEnum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(PyEnum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    PPTX = "pptx"
    IMAGE = "image"
    EMAIL = "email"
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"
    OTHER = "other"


class UserRole(PyEnum):
    """User roles for RBAC."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class User(Base):
    """User model for authentication and RBAC."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("Document", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Document(Base):
    """Document metadata model."""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    document_type = Column(Enum(DocumentType), nullable=False, index=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING, index=True)

    # Metadata
    title = Column(String(500))
    author = Column(String(255))
    created_date = Column(DateTime)
    modified_date = Column(DateTime)
    language = Column(String(10))
    page_count = Column(Integer)
    word_count = Column(Integer)

    # Processing info
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    processing_error = Column(Text)

    # Additional metadata (JSON)
    metadata = Column(JSON)

    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_doc_user_status", "user_id", "status"),
        Index("idx_doc_type_status", "document_type", "status"),
    )


class DocumentChunk(Base):
    """Document chunk model for storing text chunks and embeddings."""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)

    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Position in document

    # Chunk metadata
    start_char = Column(Integer)
    end_char = Column(Integer)
    token_count = Column(Integer)

    # Parent-child relationships for hierarchical chunking
    parent_chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=True)

    # Vector database reference
    vector_id = Column(String(100), unique=True, index=True)  # Pinecone ID

    # Additional metadata (JSON)
    metadata = Column(JSON)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    parent_chunk = relationship("DocumentChunk", remote_side=[id])

    # Indexes
    __table_args__ = (
        Index("idx_chunk_doc_index", "document_id", "chunk_index"),
    )


class SearchHistory(Base):
    """Search query history for analytics."""
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Query details
    query = Column(Text, nullable=False)
    query_type = Column(String(50))  # hybrid, vector, keyword, rag

    # Search parameters
    search_params = Column(JSON)

    # Results
    results_count = Column(Integer)
    top_result_score = Column(Float)

    # Performance metrics
    execution_time_ms = Column(Float)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="search_history")

    # Indexes
    __table_args__ = (
        Index("idx_search_user_date", "user_id", "created_at"),
    )


class AuditLog(Base):
    """Audit log for tracking user actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))  # document, search, user, etc.
    resource_id = Column(Integer)

    # Additional details
    details = Column(JSON)
    ip_address = Column(String(45))  # Support IPv6
    user_agent = Column(String(500))

    # Status
    status = Column(String(20))  # success, failure
    error_message = Column(Text)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_action_date", "action", "created_at"),
        Index("idx_audit_user_date", "user_id", "created_at"),
    )
