"""
API routes for AI Customer Support System.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import time
import uuid
from datetime import datetime, timedelta

from ..database import db_manager, crud
from ..database.db import DocumentStatus
from ..core import (
    DocumentIngestionPipeline,
    ChunkingStrategy,
    EmbeddingsManager,
    HybridRetriever,
    QueryProcessor,
    ConversationManager
)
from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    SourceCitation,
    DocumentUploadResponse,
    DocumentInfo,
    DocumentListResponse,
    DocumentDeleteResponse,
    ConversationHistoryResponse,
    ConversationInfo,
    ChatMessage,
    AnalyticsResponse,
    AnalyticsMetrics,
    QueryAnalytics,
    FeedbackRequest,
    FeedbackResponse
)
from ..utils.config import get_settings
from ..utils.logger import get_logger

router = APIRouter()
settings = get_settings()
logger = get_logger(__name__)


# ==================== Dependencies ====================

def get_db():
    """Get database session dependency"""
    if db_manager is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not initialized"
        )
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()


def get_conversation_manager(db: Session = Depends(get_db)) -> ConversationManager:
    """Get conversation manager dependency"""
    try:
        embeddings_manager = EmbeddingsManager()
        retriever = HybridRetriever(embeddings_manager=embeddings_manager)
        return ConversationManager(db=db, retriever=retriever)
    except Exception as e:
        logger.error(f"Failed to create conversation manager: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable"
        )


# ==================== Chat Endpoint ====================

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(
    request: ChatRequest,
    conversation_manager: ConversationManager = Depends(get_conversation_manager)
):
    """
    Process a chat message and return AI response.

    This endpoint:
    - Retrieves relevant context from the knowledge base
    - Generates an AI response using Claude/GPT
    - Maintains conversation history
    - Tracks analytics

    Args:
        request: Chat request with message and session info
        conversation_manager: Conversation manager dependency

    Returns:
        ChatResponse with AI response and metadata
    """
    try:
        start_time = time.time()

        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())

        logger.info(
            f"Processing chat message",
            session_id=session_id,
            message_length=len(request.message)
        )

        # Process message
        result = conversation_manager.process_message(
            session_id=session_id,
            query=request.message,
            user_id=request.user_id
        )

        # Format sources if requested
        sources = []
        if request.include_sources and result.get('sources'):
            for source in result['sources'][:5]:  # Limit to top 5 sources
                metadata = source.get('metadata', {})
                sources.append(SourceCitation(
                    document_id=metadata.get('document_id', 0),
                    filename=metadata.get('filename', 'Unknown'),
                    chunk_index=metadata.get('chunk_index', 0),
                    similarity_score=source.get('score', 0.0),
                    content=source.get('content', '')[:300],  # Limit content length
                    metadata=metadata
                ))

        # Prepare response
        response = ChatResponse(
            response=result['response'],
            session_id=session_id,
            confidence_score=result.get('confidence_score', 0.0),
            sources=sources,
            should_escalate=result.get('should_escalate', False),
            suggested_questions=result.get('suggested_questions', []),
            processing_time_ms=result.get('processing_time_ms', (time.time() - start_time) * 1000)
        )

        logger.info(
            f"Chat message processed successfully",
            session_id=session_id,
            confidence=response.confidence_score,
            should_escalate=response.should_escalate,
            processing_time_ms=response.processing_time_ms
        )

        return response

    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


# ==================== Document Management Endpoints ====================

async def process_document_upload(
    file_path: str,
    filename: str,
    db: Session
):
    """
    Background task to process uploaded document.

    Args:
        file_path: Path to uploaded file
        filename: Original filename
        db: Database session
    """
    try:
        # Get document from database
        document = crud.get_document_by_filename(db, filename)
        if not document:
            logger.error(f"Document not found in database: {filename}")
            return

        # Update status to processing
        crud.update_document_status(db, document.id, DocumentStatus.PROCESSING)

        # Process document
        pipeline = DocumentIngestionPipeline()
        result = pipeline.process_document(
            file_path=file_path,
            chunking_strategy=ChunkingStrategy.FIXED_SIZE,
            remove_duplicates=True
        )

        if result['success']:
            # Generate and store embeddings
            embeddings_manager = EmbeddingsManager()
            embedding_ids = embeddings_manager.store_embeddings(
                chunks=result['chunks'],
                document_id=document.id
            )

            # Store chunks in database
            chunk_data = []
            for chunk, embedding_id in zip(result['chunks'], embedding_ids):
                chunk_data.append({
                    'document_id': document.id,
                    'chunk_text': chunk['chunk_text'],
                    'chunk_index': chunk['chunk_index'],
                    'metadata': chunk.get('metadata', {}),
                    'embedding_id': embedding_id
                })

            crud.create_document_chunks_bulk(db, chunk_data)

            # Update status to completed
            crud.update_document_status(db, document.id, DocumentStatus.COMPLETED)

            logger.info(
                f"Document processed successfully",
                filename=filename,
                num_chunks=len(result['chunks'])
            )
        else:
            # Update status to failed
            crud.update_document_status(db, document.id, DocumentStatus.FAILED)
            logger.error(f"Document processing failed: {result.get('error')}")

    except Exception as e:
        logger.error(f"Background document processing failed: {e}", exc_info=True)
        if document:
            crud.update_document_status(db, document.id, DocumentStatus.FAILED)


@router.post("/documents/upload", response_model=DocumentUploadResponse, tags=["Documents"])
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a document to the knowledge base.

    Supported formats: PDF, DOCX, TXT, CSV, HTML

    The document will be:
    1. Validated for type and size
    2. Saved to disk
    3. Processed in the background (chunking + embedding)
    4. Indexed in the vector store

    Args:
        file: Uploaded file
        background_tasks: Background tasks manager
        db: Database session

    Returns:
        DocumentUploadResponse with upload status
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.txt', '.csv', '.html', '.htm']
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {allowed_extensions}"
            )

        # Read file
        content = await file.read()
        file_size = len(content)

        # Validate file size (max 50MB)
        max_size = 50 * 1024 * 1024
        if file_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large (max 50MB)"
            )

        # Save file
        upload_dir = settings.documents_dir
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename

        with open(file_path, 'wb') as f:
            f.write(content)

        # Create document record
        document = crud.create_document(
            db=db,
            filename=file.filename,
            content="",  # Will be populated during processing
            source=str(file_path),
            file_size=file_size,
            file_type=file_ext.replace('.', '')
        )

        # Schedule background processing
        background_tasks.add_task(
            process_document_upload,
            str(file_path),
            file.filename,
            db
        )

        logger.info(
            f"Document uploaded successfully",
            filename=file.filename,
            document_id=document.id,
            file_size=file_size
        )

        return DocumentUploadResponse(
            success=True,
            document_id=document.id,
            filename=file.filename,
            message="Document uploaded successfully. Processing in background.",
            num_chunks=None  # Will be populated after processing
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )


@router.get("/documents", response_model=DocumentListResponse, tags=["Documents"])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all documents in the knowledge base.

    Args:
        skip: Number of documents to skip
        limit: Maximum number of documents to return
        status_filter: Filter by status (pending, processing, completed, failed)
        db: Database session

    Returns:
        DocumentListResponse with list of documents
    """
    try:
        # Parse status filter
        doc_status = None
        if status_filter:
            try:
                doc_status = DocumentStatus(status_filter.lower())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status. Allowed: {[s.value for s in DocumentStatus]}"
                )

        # Get documents
        documents = crud.get_all_documents(
            db=db,
            skip=skip,
            limit=limit,
            status=doc_status
        )

        # Get total count
        total = crud.get_documents_count(db=db, status=doc_status)

        # Format documents
        document_list = []
        for doc in documents:
            # Get chunk count
            chunks = crud.get_document_chunks(db, doc.id)
            num_chunks = len(chunks)

            document_list.append(DocumentInfo(
                id=doc.id,
                filename=doc.filename,
                file_type=doc.file_type or '',
                file_size=doc.file_size or 0,
                upload_date=doc.upload_date,
                status=doc.status.value,
                num_chunks=num_chunks,
                metadata=doc.metadata or {}
            ))

        return DocumentListResponse(
            documents=document_list,
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            page_size=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list documents: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse, tags=["Documents"])
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document from the knowledge base.

    This will:
    1. Delete the document record from database
    2. Delete all associated chunks
    3. Remove embeddings from vector store (marked for deletion)
    4. Delete the file from disk

    Args:
        document_id: Document ID to delete
        db: Database session

    Returns:
        DocumentDeleteResponse with deletion status
    """
    try:
        # Get document
        document = crud.get_document(db, document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Delete embeddings from vector store
        try:
            embeddings_manager = EmbeddingsManager()
            embeddings_manager.delete_document_embeddings(document_id)
        except Exception as e:
            logger.warning(f"Failed to delete embeddings for document {document_id}: {e}")

        # Delete file from disk
        if document.source:
            try:
                file_path = Path(document.source)
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete file {document.source}: {e}")

        # Delete from database (cascade will delete chunks)
        success = crud.delete_document(db, document_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document"
            )

        logger.info(f"Document deleted successfully", document_id=document_id)

        return DocumentDeleteResponse(
            success=True,
            document_id=document_id,
            message="Document deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


# ==================== Conversation Endpoints ====================

@router.get("/conversations/{session_id}", response_model=ConversationHistoryResponse, tags=["Conversations"])
async def get_conversation(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a session.

    Args:
        session_id: Session ID
        db: Database session

    Returns:
        ConversationHistoryResponse with conversation and messages
    """
    try:
        # Get conversation
        conversation = crud.get_conversation_by_session_id(db, session_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages
        messages = crud.get_conversation_messages(db, conversation.id)

        # Format conversation info
        conversation_info = ConversationInfo(
            id=conversation.id,
            session_id=conversation.session_id,
            user_id=conversation.user_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            num_messages=len(messages),
            is_active=conversation.is_active == 1
        )

        # Format messages
        message_list = [
            ChatMessage(
                role=msg.role.value,
                content=msg.content,
                timestamp=msg.timestamp
            )
            for msg in messages
        ]

        return ConversationHistoryResponse(
            conversation=conversation_info,
            messages=message_list
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation"
        )


# ==================== Analytics Endpoints ====================

@router.get("/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_analytics(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get analytics metrics for the specified time period.

    Args:
        days: Number of days to include in analysis (default: 7)
        db: Database session

    Returns:
        AnalyticsResponse with metrics and insights
    """
    try:
        # Get aggregated metrics
        metrics_data = crud.get_analytics_metrics(db, days=days)

        metrics = AnalyticsMetrics(
            total_queries=metrics_data['total_queries'],
            avg_confidence_score=metrics_data['avg_confidence_score'],
            avg_resolution_time=metrics_data['avg_resolution_time'],
            autonomous_resolution_rate=metrics_data['autonomous_resolution_rate'],
            escalation_rate=metrics_data['escalation_rate'],
            avg_rating=metrics_data['avg_rating'],
            total_cost=metrics_data['total_cost'],
            period_days=metrics_data['period_days']
        )

        # Get recent queries
        recent_analytics = crud.get_analytics(
            db,
            limit=10,
            start_date=datetime.utcnow() - timedelta(days=days)
        )

        recent_queries = [
            QueryAnalytics(
                id=record.id,
                query=record.query,
                response=record.response,
                confidence_score=record.confidence_score,
                rating=record.rating,
                resolution_time=record.resolution_time,
                timestamp=record.timestamp,
                was_escalated=record.was_escalated == 1
            )
            for record in recent_analytics
        ]

        # Get low-rated queries
        low_rated = crud.get_low_rated_queries(db, rating_threshold=2, limit=10)

        low_rated_queries = [
            QueryAnalytics(
                id=record.id,
                query=record.query,
                response=record.response,
                confidence_score=record.confidence_score,
                rating=record.rating,
                resolution_time=record.resolution_time,
                timestamp=record.timestamp,
                was_escalated=record.was_escalated == 1
            )
            for record in low_rated
        ]

        return AnalyticsResponse(
            metrics=metrics,
            recent_queries=recent_queries,
            low_rated_queries=low_rated_queries
        )

    except Exception as e:
        logger.error(f"Failed to get analytics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )


# ==================== Feedback Endpoint ====================

@router.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """
    Submit feedback/rating for a response.

    Args:
        feedback: Feedback request with rating
        db: Database session

    Returns:
        FeedbackResponse with submission status
    """
    try:
        # If analytics_id provided, update that record
        if feedback.analytics_id:
            analytics = crud.update_analytics_rating(
                db,
                feedback.analytics_id,
                feedback.rating
            )

            if not analytics:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Analytics record not found"
                )

            logger.info(
                f"Feedback submitted",
                analytics_id=feedback.analytics_id,
                rating=feedback.rating
            )

            return FeedbackResponse(
                success=True,
                message="Feedback submitted successfully"
            )
        else:
            # If no analytics_id, we can still log the feedback
            logger.info(
                f"Feedback received without analytics_id",
                session_id=feedback.session_id,
                rating=feedback.rating
            )

            return FeedbackResponse(
                success=True,
                message="Feedback received"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )
