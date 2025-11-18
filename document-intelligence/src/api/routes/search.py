"""
Search and RAG API endpoints.
Handles hybrid search and question answering.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
import time

from src.core.database import get_db
from src.core.models import SearchHistory
from src.api.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    RAGQueryRequest,
    RAGQueryResponse,
    SourceItem
)
from src.search.hybrid_search import hybrid_search
from src.search.vector_search import vector_search
from src.search.keyword_search import keyword_search
from src.rag.multi_query import multi_query_retriever
from src.rag.hyde import hyde_retriever
from src.rag.rag_chain import rag_chain
from src.utils.logger import app_logger as logger

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Perform document search using various strategies.

    Args:
        request: Search request parameters
        db: Database session

    Returns:
        Search results
    """
    logger.info(f"Search request: query='{request.query[:50]}...', strategy={request.strategy}")

    start_time = time.time()

    try:
        # Build metadata filter
        filter_dict = None
        if request.document_type or request.date_from or request.date_to:
            filter_dict = {}
            if request.document_type:
                filter_dict['document_type'] = request.document_type
            if request.date_from or request.date_to:
                filter_dict['date'] = {}
                if request.date_from:
                    filter_dict['date']['$gte'] = request.date_from
                if request.date_to:
                    filter_dict['date']['$lte'] = request.date_to

        # Perform search based on strategy
        if request.strategy == "vector":
            results = vector_search.search(
                query=request.query,
                top_k=request.top_k,
                filter=filter_dict
            )
        elif request.strategy == "keyword":
            results = keyword_search.search(
                query=request.query,
                top_k=request.top_k
            )
        elif request.strategy == "multi_query":
            results = multi_query_retriever.retrieve(
                query=request.query,
                top_k=request.top_k
            )
        elif request.strategy == "hyde":
            results = hyde_retriever.retrieve(
                query=request.query,
                top_k=request.top_k
            )
        else:  # hybrid (default)
            results = hybrid_search.search(
                query=request.query,
                top_k=request.top_k,
                filter=filter_dict
            )

        execution_time = time.time() - start_time

        # Log search to history
        try:
            search_history = SearchHistory(
                user_id=1,  # TODO: Get from auth
                query=request.query,
                query_type=request.strategy,
                search_params={
                    "top_k": request.top_k,
                    "filters": filter_dict
                },
                results_count=len(results),
                top_result_score=results[0].score if results else 0.0,
                execution_time_ms=execution_time * 1000
            )
            db.add(search_history)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log search history: {str(e)}")

        # Convert results to response format
        result_items = [
            SearchResultItem(
                id=r.id,
                score=r.score,
                content=r.content,
                document_id=r.document_id,
                metadata=r.metadata
            )
            for r in results
        ]

        return SearchResponse(
            query=request.query,
            results=result_items,
            total_results=len(results),
            strategy=request.strategy,
            execution_time=execution_time
        )

    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/query", response_model=RAGQueryResponse)
async def rag_query(
    request: RAGQueryRequest,
    db: Session = Depends(get_db)
):
    """
    Answer questions using RAG.

    Args:
        request: RAG query request
        db: Database session

    Returns:
        Answer with sources
    """
    logger.info(f"RAG query: question='{request.question[:50]}...', strategy={request.strategy}")

    try:
        # Build metadata filter
        filter_dict = None
        if request.document_type or request.date_from or request.date_to:
            filter_dict = {}
            if request.document_type:
                filter_dict['document_type'] = request.document_type
            if request.date_from or request.date_to:
                filter_dict['date'] = {}
                if request.date_from:
                    filter_dict['date']['$gte'] = request.date_from
                if request.date_to:
                    filter_dict['date']['$lte'] = request.date_to

        # Perform RAG query
        result = rag_chain.query(
            question=request.question,
            retrieval_strategy=request.strategy,
            top_k=request.top_k,
            filter=filter_dict
        )

        # Log query to history
        try:
            search_history = SearchHistory(
                user_id=1,  # TODO: Get from auth
                query=request.question,
                query_type=f"rag_{request.strategy}",
                search_params={
                    "top_k": request.top_k,
                    "filters": filter_dict
                },
                results_count=result['num_sources'],
                top_result_score=result['confidence'],
                execution_time_ms=result['execution_time'] * 1000
            )
            db.add(search_history)
            db.commit()
        except Exception as e:
            logger.warning(f"Failed to log query history: {str(e)}")

        # Convert sources to response format
        source_items = [
            SourceItem(
                number=s['number'],
                content=s['content'],
                score=s['score'],
                document_id=s.get('document_id'),
                metadata=s['metadata']
            )
            for s in result['sources']
        ]

        return RAGQueryResponse(
            answer=result['answer'],
            sources=source_items,
            confidence=result['confidence'],
            num_sources=result['num_sources'],
            retrieval_strategy=result['retrieval_strategy'],
            execution_time=result['execution_time']
        )

    except Exception as e:
        logger.error(f"RAG query failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG query failed: {str(e)}"
        )
