"""
Database models and connection management for the Customer Support AI system.
"""
from datetime import datetime
from typing import Optional
import json

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    JSON,
    Enum as SQLEnum,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool
import enum

Base = declarative_base()


class DocumentStatus(str, enum.Enum):
    """Status of document processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    """Role of message sender"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Document(Base):
    """Documents uploaded to the knowledge base"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, default={})
    source = Column(String(255), nullable=True)
    upload_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(50), nullable=True)

    # Relationships
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_document_status', 'status'),
        Index('idx_document_upload_date', 'upload_date'),
    )

    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"


class DocumentChunk(Base):
    """Chunks of documents for embedding and retrieval"""
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    metadata = Column(JSON, default={})
    embedding_id = Column(String(255), nullable=True)  # Reference to vector store

    # Relationships
    document = relationship("Document", back_populates="chunks")

    # Indexes
    __table_args__ = (
        Index('idx_chunk_document_id', 'document_id'),
        Index('idx_chunk_embedding_id', 'embedding_id'),
    )

    def __repr__(self):
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, chunk_index={self.chunk_index})>"


class Conversation(Base):
    """Conversation sessions with users"""
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    metadata = Column(JSON, default={})
    is_active = Column(Integer, default=1)  # Using Integer for SQLite compatibility

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_conversation_session_id', 'session_id'),
        Index('idx_conversation_user_id', 'user_id'),
        Index('idx_conversation_created_at', 'created_at'),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, session_id='{self.session_id}')>"


class Message(Base):
    """Messages within conversations"""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    metadata = Column(JSON, default={})
    confidence_score = Column(Float, nullable=True)
    sources_used = Column(JSON, default=[])

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index('idx_message_conversation_id', 'conversation_id'),
        Index('idx_message_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, role='{self.role}')>"


class Analytics(Base):
    """Analytics and metrics for queries and responses"""
    __tablename__ = "analytics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), nullable=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=True)
    rating = Column(Integer, nullable=True)  # 1-5 rating or thumbs up/down
    resolution_time = Column(Float, nullable=True)  # in seconds
    sources_used = Column(JSON, default=[])
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    was_escalated = Column(Integer, default=0)  # Using Integer for SQLite compatibility
    query_category = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    metadata = Column(JSON, default={})

    # Indexes
    __table_args__ = (
        Index('idx_analytics_timestamp', 'timestamp'),
        Index('idx_analytics_session_id', 'session_id'),
        Index('idx_analytics_rating', 'rating'),
        Index('idx_analytics_confidence_score', 'confidence_score'),
    )

    def __repr__(self):
        return f"<Analytics(id={self.id}, session_id='{self.session_id}', rating={self.rating})>"


class DatabaseManager:
    """Manager class for database operations"""

    def __init__(self, database_url: str):
        """
        Initialize database connection.

        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url

        # Create engine with proper configuration
        if database_url.startswith('sqlite'):
            # SQLite specific configuration
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # PostgreSQL configuration
            self.engine = create_engine(
                database_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                echo=False
            )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables in the database"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()

    def get_db(self):
        """
        Dependency for FastAPI to get database session.
        Use with Depends() in route functions.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


# Global database manager instance (to be initialized in main app)
db_manager: Optional[DatabaseManager] = None


def init_database(database_url: str) -> DatabaseManager:
    """
    Initialize the database manager and create tables.

    Args:
        database_url: SQLAlchemy database URL

    Returns:
        DatabaseManager instance
    """
    global db_manager
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    return db_manager


def get_db_session() -> Session:
    """
    Get a database session from the global manager.

    Returns:
        Database session
    """
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    return db_manager.get_session()
