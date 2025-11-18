"""
CRUD operations for database models.
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from .db import (
    Document,
    DocumentChunk,
    Conversation,
    Message,
    Analytics,
    DocumentStatus,
    MessageRole
)


# ==================== Document Operations ====================

def create_document(
    db: Session,
    filename: str,
    content: str,
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    file_size: Optional[int] = None,
    file_type: Optional[str] = None
) -> Document:
    """Create a new document"""
    document = Document(
        filename=filename,
        content=content,
        source=source,
        metadata=metadata or {},
        file_size=file_size,
        file_type=file_type,
        status=DocumentStatus.PENDING
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document(db: Session, document_id: int) -> Optional[Document]:
    """Get a document by ID"""
    return db.query(Document).filter(Document.id == document_id).first()


def get_document_by_filename(db: Session, filename: str) -> Optional[Document]:
    """Get a document by filename"""
    return db.query(Document).filter(Document.filename == filename).first()


def get_all_documents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[DocumentStatus] = None
) -> List[Document]:
    """Get all documents with optional filtering"""
    query = db.query(Document)
    if status:
        query = query.filter(Document.status == status)
    return query.order_by(desc(Document.upload_date)).offset(skip).limit(limit).all()


def update_document_status(
    db: Session,
    document_id: int,
    status: DocumentStatus
) -> Optional[Document]:
    """Update document status"""
    document = get_document(db, document_id)
    if document:
        document.status = status
        db.commit()
        db.refresh(document)
    return document


def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document and its chunks"""
    document = get_document(db, document_id)
    if document:
        db.delete(document)
        db.commit()
        return True
    return False


def get_documents_count(db: Session, status: Optional[DocumentStatus] = None) -> int:
    """Get count of documents"""
    query = db.query(func.count(Document.id))
    if status:
        query = query.filter(Document.status == status)
    return query.scalar()


# ==================== Document Chunk Operations ====================

def create_document_chunk(
    db: Session,
    document_id: int,
    chunk_text: str,
    chunk_index: int,
    metadata: Optional[Dict[str, Any]] = None,
    embedding_id: Optional[str] = None
) -> DocumentChunk:
    """Create a new document chunk"""
    chunk = DocumentChunk(
        document_id=document_id,
        chunk_text=chunk_text,
        chunk_index=chunk_index,
        metadata=metadata or {},
        embedding_id=embedding_id
    )
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


def create_document_chunks_bulk(
    db: Session,
    chunks: List[Dict[str, Any]]
) -> List[DocumentChunk]:
    """Create multiple document chunks at once"""
    chunk_objects = [DocumentChunk(**chunk_data) for chunk_data in chunks]
    db.add_all(chunk_objects)
    db.commit()
    for chunk in chunk_objects:
        db.refresh(chunk)
    return chunk_objects


def get_document_chunks(db: Session, document_id: int) -> List[DocumentChunk]:
    """Get all chunks for a document"""
    return db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index).all()


def get_chunk_by_embedding_id(db: Session, embedding_id: str) -> Optional[DocumentChunk]:
    """Get chunk by embedding ID"""
    return db.query(DocumentChunk).filter(
        DocumentChunk.embedding_id == embedding_id
    ).first()


def delete_document_chunks(db: Session, document_id: int) -> int:
    """Delete all chunks for a document"""
    count = db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document_id
    ).delete()
    db.commit()
    return count


# ==================== Conversation Operations ====================

def create_conversation(
    db: Session,
    session_id: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Conversation:
    """Create a new conversation"""
    conversation = Conversation(
        session_id=session_id,
        user_id=user_id,
        metadata=metadata or {},
        is_active=1
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_conversation(db: Session, conversation_id: int) -> Optional[Conversation]:
    """Get a conversation by ID"""
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_conversation_by_session_id(db: Session, session_id: str) -> Optional[Conversation]:
    """Get a conversation by session ID"""
    return db.query(Conversation).filter(Conversation.session_id == session_id).first()


def get_or_create_conversation(
    db: Session,
    session_id: str,
    user_id: Optional[str] = None
) -> Conversation:
    """Get existing conversation or create new one"""
    conversation = get_conversation_by_session_id(db, session_id)
    if not conversation:
        conversation = create_conversation(db, session_id, user_id)
    return conversation


def update_conversation(
    db: Session,
    conversation_id: int,
    is_active: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[Conversation]:
    """Update conversation"""
    conversation = get_conversation(db, conversation_id)
    if conversation:
        if is_active is not None:
            conversation.is_active = is_active
        if metadata is not None:
            conversation.metadata = metadata
        conversation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(conversation)
    return conversation


def get_active_conversations(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Conversation]:
    """Get all active conversations"""
    return db.query(Conversation).filter(
        Conversation.is_active == 1
    ).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()


# ==================== Message Operations ====================

def create_message(
    db: Session,
    conversation_id: int,
    role: MessageRole,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    confidence_score: Optional[float] = None,
    sources_used: Optional[List[Dict[str, Any]]] = None
) -> Message:
    """Create a new message"""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        metadata=metadata or {},
        confidence_score=confidence_score,
        sources_used=sources_used or []
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_message(db: Session, message_id: int) -> Optional[Message]:
    """Get a message by ID"""
    return db.query(Message).filter(Message.id == message_id).first()


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    limit: Optional[int] = None
) -> List[Message]:
    """Get all messages for a conversation"""
    query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp)

    if limit:
        # Get the last N messages
        query = query.order_by(desc(Message.timestamp)).limit(limit)
        messages = query.all()
        messages.reverse()  # Return in chronological order
        return messages

    return query.all()


def get_recent_messages(
    db: Session,
    conversation_id: int,
    last_n: int = 5
) -> List[Message]:
    """Get the N most recent messages for a conversation"""
    return get_conversation_messages(db, conversation_id, limit=last_n)


def update_message_metadata(
    db: Session,
    message_id: int,
    metadata: Dict[str, Any]
) -> Optional[Message]:
    """Update message metadata"""
    message = get_message(db, message_id)
    if message:
        message.metadata = {**message.metadata, **metadata}
        db.commit()
        db.refresh(message)
    return message


# ==================== Analytics Operations ====================

def create_analytics_record(
    db: Session,
    session_id: str,
    query: str,
    response: str,
    confidence_score: Optional[float] = None,
    resolution_time: Optional[float] = None,
    sources_used: Optional[List[Dict[str, Any]]] = None,
    was_escalated: bool = False,
    query_category: Optional[str] = None,
    tokens_used: Optional[int] = None,
    cost: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Analytics:
    """Create a new analytics record"""
    analytics = Analytics(
        session_id=session_id,
        query=query,
        response=response,
        confidence_score=confidence_score,
        resolution_time=resolution_time,
        sources_used=sources_used or [],
        was_escalated=1 if was_escalated else 0,
        query_category=query_category,
        tokens_used=tokens_used,
        cost=cost,
        metadata=metadata or {}
    )
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics


def update_analytics_rating(
    db: Session,
    analytics_id: int,
    rating: int
) -> Optional[Analytics]:
    """Update analytics rating"""
    analytics = db.query(Analytics).filter(Analytics.id == analytics_id).first()
    if analytics:
        analytics.rating = rating
        db.commit()
        db.refresh(analytics)
    return analytics


def get_analytics(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Analytics]:
    """Get analytics records with optional date filtering"""
    query = db.query(Analytics)

    if start_date:
        query = query.filter(Analytics.timestamp >= start_date)
    if end_date:
        query = query.filter(Analytics.timestamp <= end_date)

    return query.order_by(desc(Analytics.timestamp)).offset(skip).limit(limit).all()


def get_analytics_metrics(
    db: Session,
    days: int = 7
) -> Dict[str, Any]:
    """Get aggregated analytics metrics"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Total queries
    total_queries = db.query(func.count(Analytics.id)).filter(
        Analytics.timestamp >= start_date
    ).scalar()

    # Average confidence score
    avg_confidence = db.query(func.avg(Analytics.confidence_score)).filter(
        and_(
            Analytics.timestamp >= start_date,
            Analytics.confidence_score.isnot(None)
        )
    ).scalar()

    # Average resolution time
    avg_resolution_time = db.query(func.avg(Analytics.resolution_time)).filter(
        and_(
            Analytics.timestamp >= start_date,
            Analytics.resolution_time.isnot(None)
        )
    ).scalar()

    # Escalation rate
    escalated_count = db.query(func.count(Analytics.id)).filter(
        and_(
            Analytics.timestamp >= start_date,
            Analytics.was_escalated == 1
        )
    ).scalar()

    escalation_rate = (escalated_count / total_queries * 100) if total_queries > 0 else 0
    autonomous_resolution_rate = 100 - escalation_rate

    # Average rating
    avg_rating = db.query(func.avg(Analytics.rating)).filter(
        and_(
            Analytics.timestamp >= start_date,
            Analytics.rating.isnot(None)
        )
    ).scalar()

    # Total cost
    total_cost = db.query(func.sum(Analytics.cost)).filter(
        and_(
            Analytics.timestamp >= start_date,
            Analytics.cost.isnot(None)
        )
    ).scalar()

    return {
        "total_queries": total_queries or 0,
        "avg_confidence_score": round(avg_confidence, 3) if avg_confidence else 0,
        "avg_resolution_time": round(avg_resolution_time, 2) if avg_resolution_time else 0,
        "autonomous_resolution_rate": round(autonomous_resolution_rate, 2),
        "escalation_rate": round(escalation_rate, 2),
        "avg_rating": round(avg_rating, 2) if avg_rating else 0,
        "total_cost": round(total_cost, 4) if total_cost else 0,
        "period_days": days
    }


def get_low_rated_queries(
    db: Session,
    rating_threshold: int = 2,
    limit: int = 50
) -> List[Analytics]:
    """Get queries with low ratings"""
    return db.query(Analytics).filter(
        and_(
            Analytics.rating.isnot(None),
            Analytics.rating <= rating_threshold
        )
    ).order_by(desc(Analytics.timestamp)).limit(limit).all()


def get_queries_by_category(
    db: Session,
    days: int = 7
) -> Dict[str, int]:
    """Get query counts by category"""
    start_date = datetime.utcnow() - timedelta(days=days)

    results = db.query(
        Analytics.query_category,
        func.count(Analytics.id).label('count')
    ).filter(
        and_(
            Analytics.timestamp >= start_date,
            Analytics.query_category.isnot(None)
        )
    ).group_by(Analytics.query_category).all()

    return {category: count for category, count in results}


def get_hourly_query_volume(
    db: Session,
    days: int = 7
) -> List[Dict[str, Any]]:
    """Get query volume by hour of day"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # This is simplified - actual implementation may vary by database
    results = db.query(
        func.strftime('%H', Analytics.timestamp).label('hour'),
        func.count(Analytics.id).label('count')
    ).filter(
        Analytics.timestamp >= start_date
    ).group_by('hour').all()

    return [{"hour": int(hour), "count": count} for hour, count in results]
