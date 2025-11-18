"""
Analytics API endpoints.
Provides insights into documents, searches, and content.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta

from src.core.database import get_db
from src.core.models import Document, SearchHistory, DocumentType, ProcessingStatus
from src.api.schemas import (
    DocumentOverviewResponse,
    SearchStatsResponse,
    ContentIntelligenceResponse
)
from src.utils.logger import app_logger as logger

router = APIRouter()


@router.get("/overview", response_model=DocumentOverviewResponse)
async def get_document_overview(
    db: Session = Depends(get_db)
):
    """
    Get document overview analytics.

    Args:
        db: Database session

    Returns:
        Document overview statistics
    """
    logger.info("Getting document overview analytics")

    try:
        # Total documents
        total_documents = db.query(Document).count()

        # Documents by type
        type_counts = db.query(
            Document.document_type,
            func.count(Document.id)
        ).group_by(Document.document_type).all()

        documents_by_type = {
            doc_type.value: count
            for doc_type, count in type_counts
        }

        # Documents by status
        status_counts = db.query(
            Document.status,
            func.count(Document.id)
        ).group_by(Document.status).all()

        documents_by_status = {
            status.value: count
            for status, count in status_counts
        }

        # Total pages and words
        total_pages = db.query(func.sum(Document.page_count)).scalar() or 0
        total_words = db.query(func.sum(Document.word_count)).scalar() or 0

        # Average processing time
        avg_time_result = db.query(
            func.avg(
                func.extract(
                    'epoch',
                    Document.processing_completed_at - Document.processing_started_at
                )
            )
        ).filter(
            Document.processing_completed_at.isnot(None),
            Document.processing_started_at.isnot(None)
        ).scalar()

        avg_processing_time = float(avg_time_result) if avg_time_result else None

        return DocumentOverviewResponse(
            total_documents=total_documents,
            documents_by_type=documents_by_type,
            documents_by_status=documents_by_status,
            total_pages=int(total_pages),
            total_words=int(total_words),
            avg_processing_time=avg_processing_time
        )

    except Exception as e:
        logger.error(f"Failed to get document overview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get document overview: {str(e)}"
        )


@router.get("/search-stats", response_model=SearchStatsResponse)
async def get_search_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get search analytics.

    Args:
        days: Number of days to analyze
        db: Database session

    Returns:
        Search statistics
    """
    logger.info(f"Getting search statistics for last {days} days")

    try:
        # Date threshold
        date_threshold = datetime.utcnow() - timedelta(days=days)

        # Total searches
        total_searches = db.query(SearchHistory).filter(
            SearchHistory.created_at >= date_threshold
        ).count()

        # Average execution time
        avg_time = db.query(
            func.avg(SearchHistory.execution_time_ms)
        ).filter(
            SearchHistory.created_at >= date_threshold
        ).scalar() or 0.0

        # Top queries
        top_queries_result = db.query(
            SearchHistory.query,
            func.count(SearchHistory.id).label('count'),
            func.avg(SearchHistory.top_result_score).label('avg_score')
        ).filter(
            SearchHistory.created_at >= date_threshold
        ).group_by(
            SearchHistory.query
        ).order_by(
            func.count(SearchHistory.id).desc()
        ).limit(10).all()

        top_queries = [
            {
                "query": query,
                "count": count,
                "avg_score": float(avg_score) if avg_score else 0.0
            }
            for query, count, avg_score in top_queries_result
        ]

        # Searches by strategy
        strategy_counts = db.query(
            SearchHistory.query_type,
            func.count(SearchHistory.id)
        ).filter(
            SearchHistory.created_at >= date_threshold
        ).group_by(
            SearchHistory.query_type
        ).all()

        searches_by_strategy = {
            query_type: count
            for query_type, count in strategy_counts
        }

        # Searches over time (daily)
        searches_over_time_result = db.query(
            func.date(SearchHistory.created_at).label('date'),
            func.count(SearchHistory.id).label('count')
        ).filter(
            SearchHistory.created_at >= date_threshold
        ).group_by(
            func.date(SearchHistory.created_at)
        ).order_by(
            func.date(SearchHistory.created_at)
        ).all()

        searches_over_time = [
            {
                "date": str(date),
                "count": count
            }
            for date, count in searches_over_time_result
        ]

        return SearchStatsResponse(
            total_searches=total_searches,
            avg_execution_time=float(avg_time),
            top_queries=top_queries,
            searches_by_strategy=searches_by_strategy,
            searches_over_time=searches_over_time
        )

    except Exception as e:
        logger.error(f"Failed to get search stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get search stats: {str(e)}"
        )


@router.get("/content-intelligence", response_model=ContentIntelligenceResponse)
async def get_content_intelligence(
    db: Session = Depends(get_db)
):
    """
    Get content intelligence analytics.

    Args:
        db: Database session

    Returns:
        Content intelligence insights
    """
    logger.info("Getting content intelligence analytics")

    try:
        # Language distribution
        language_counts = db.query(
            Document.language,
            func.count(Document.id)
        ).filter(
            Document.language.isnot(None)
        ).group_by(
            Document.language
        ).all()

        language_distribution = {
            lang: count
            for lang, count in language_counts
            if lang
        }

        # Average document length
        avg_length = db.query(
            func.avg(Document.word_count)
        ).filter(
            Document.word_count.isnot(None)
        ).scalar() or 0.0

        # Placeholder for entities and topics
        # TODO: Implement proper entity and topic extraction
        top_entities = []
        top_topics = []

        return ContentIntelligenceResponse(
            top_entities=top_entities,
            top_topics=top_topics,
            language_distribution=language_distribution,
            avg_document_length=float(avg_length)
        )

    except Exception as e:
        logger.error(f"Failed to get content intelligence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content intelligence: {str(e)}"
        )
