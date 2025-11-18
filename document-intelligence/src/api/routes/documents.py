"""
Document management API endpoints.
Handles upload, retrieval, and deletion of documents.
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from src.core.database import get_db
from src.core.models import Document, DocumentType, ProcessingStatus, User
from src.api.schemas import (
    DocumentResponse,
    DocumentListResponse,
    DocumentUploadResponse
)
from src.utils.logger import app_logger as logger
from config.settings import settings

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a single document for processing.

    Args:
        file: Uploaded file
        db: Database session

    Returns:
        Upload response with document ID
    """
    logger.info(f"Uploading document: {file.filename}")

    try:
        # Validate file size
        if file.size and file.size > settings.max_file_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )

        # Validate file extension
        file_ext = Path(file.filename).suffix.lower().lstrip('.')
        if file_ext not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type .{file_ext} is not allowed. Allowed types: {', '.join(settings.allowed_extensions_list)}"
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = settings.upload_dir / unique_filename

        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Determine document type
        doc_type = _get_document_type(file_ext)

        # Create document record
        document = Document(
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=file.size or 0,
            document_type=doc_type,
            status=ProcessingStatus.PENDING,
            user_id=1  # TODO: Get from auth
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        logger.info(f"Document uploaded successfully: ID={document.id}")

        # TODO: Trigger async processing task

        return DocumentUploadResponse(
            id=document.id,
            filename=file.filename,
            status=document.status.value,
            message="Document uploaded successfully. Processing will begin shortly."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    type_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all documents with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by processing status
        type_filter: Filter by document type
        db: Database session

    Returns:
        List of documents
    """
    logger.info(f"Listing documents: skip={skip}, limit={limit}")

    try:
        query = db.query(Document)

        # Apply filters
        if status_filter:
            query = query.filter(Document.status == status_filter)

        if type_filter:
            query = query.filter(Document.document_type == type_filter)

        # Get total count
        total = query.count()

        # Get documents
        documents = query.order_by(Document.uploaded_at.desc()).offset(skip).limit(limit).all()

        return DocumentListResponse(
            total=total,
            skip=skip,
            limit=limit,
            documents=[_document_to_response(doc) for doc in documents]
        )

    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Get document details by ID.

    Args:
        document_id: Document ID
        db: Database session

    Returns:
        Document details
    """
    logger.info(f"Getting document: ID={document_id}")

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )

        return _document_to_response(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a document.

    Args:
        document_id: Document ID
        db: Database session

    Returns:
        Success message
    """
    logger.info(f"Deleting document: ID={document_id}")

    try:
        document = db.query(Document).filter(Document.id == document_id).first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )

        # Delete file
        try:
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to delete file: {str(e)}")

        # Delete from database
        db.delete(document)
        db.commit()

        logger.info(f"Document deleted successfully: ID={document_id}")

        return {"message": f"Document {document_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


def _get_document_type(extension: str) -> DocumentType:
    """Map file extension to DocumentType enum."""
    type_map = {
        'pdf': DocumentType.PDF,
        'docx': DocumentType.DOCX,
        'xlsx': DocumentType.XLSX,
        'xls': DocumentType.XLSX,
        'pptx': DocumentType.PPTX,
        'png': DocumentType.IMAGE,
        'jpg': DocumentType.IMAGE,
        'jpeg': DocumentType.IMAGE,
        'eml': DocumentType.EMAIL,
        'msg': DocumentType.EMAIL,
        'html': DocumentType.HTML,
        'htm': DocumentType.HTML,
        'md': DocumentType.MARKDOWN,
        'markdown': DocumentType.MARKDOWN,
        'txt': DocumentType.TEXT,
    }

    return type_map.get(extension, DocumentType.OTHER)


def _document_to_response(document: Document) -> DocumentResponse:
    """Convert Document model to response schema."""
    return DocumentResponse(
        id=document.id,
        filename=document.original_filename,
        file_size=document.file_size,
        document_type=document.document_type.value,
        status=document.status.value,
        uploaded_at=document.uploaded_at,
        processing_completed_at=document.processing_completed_at,
        page_count=document.page_count,
        word_count=document.word_count,
        metadata=document.metadata or {}
    )
