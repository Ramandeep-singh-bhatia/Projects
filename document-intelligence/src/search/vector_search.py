"""
Vector search implementation using Pinecone.
Semantic similarity search with metadata filtering.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from src.core.vector_store import vector_store
from src.core.embeddings import embedding_service
from config.settings import settings
from src.utils.logger import app_logger as logger


@dataclass
class SearchResult:
    """Container for a search result."""
    id: str
    score: float
    content: str
    metadata: Dict[str, Any]
    document_id: Optional[int] = None
    chunk_index: Optional[int] = None


class VectorSearch:
    """Vector search engine using Pinecone."""

    def __init__(self):
        """Initialize vector search."""
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    def search(
        self,
        query: str,
        top_k: int = None,
        filter: Optional[Dict[str, Any]] = None,
        namespace: str = "",
        min_score: float = None
    ) -> List[SearchResult]:
        """
        Perform semantic vector search.

        Args:
            query: Search query text
            top_k: Number of results to return
            filter: Metadata filter
            namespace: Optional namespace
            min_score: Minimum similarity score threshold

        Returns:
            List of search results
        """
        top_k = top_k or settings.vector_search_top_k
        min_score = min_score or settings.similarity_threshold

        logger.info(f"Performing vector search: query='{query[:50]}...', top_k={top_k}")

        try:
            # Generate query embedding
            query_embedding = self.embedding_service.generate_embedding(query)

            # Search Pinecone
            results = self.vector_store.query(
                vector=query_embedding,
                top_k=top_k,
                filter=filter,
                namespace=namespace,
                include_metadata=True,
                include_values=False
            )

            # Convert to SearchResult objects
            search_results = []

            for match in results.matches:
                # Apply score threshold
                if match.score < min_score:
                    continue

                result = SearchResult(
                    id=match.id,
                    score=match.score,
                    content=match.metadata.get('content', ''),
                    metadata=match.metadata,
                    document_id=match.metadata.get('document_id'),
                    chunk_index=match.metadata.get('chunk_index')
                )

                search_results.append(result)

            logger.info(f"Vector search returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            raise

    def search_with_metadata_filters(
        self,
        query: str,
        document_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        user_id: Optional[int] = None,
        top_k: int = None
    ) -> List[SearchResult]:
        """
        Search with common metadata filters.

        Args:
            query: Search query
            document_type: Filter by document type
            date_from: Filter by date (from)
            date_to: Filter by date (to)
            user_id: Filter by user ID
            top_k: Number of results

        Returns:
            List of search results
        """
        # Build metadata filter
        filter_dict = {}

        if document_type:
            filter_dict['document_type'] = document_type

        if user_id:
            filter_dict['user_id'] = user_id

        if date_from or date_to:
            filter_dict['date'] = {}
            if date_from:
                filter_dict['date']['$gte'] = date_from
            if date_to:
                filter_dict['date']['$lte'] = date_to

        return self.search(
            query=query,
            top_k=top_k,
            filter=filter_dict if filter_dict else None
        )


# Global vector search instance
vector_search = VectorSearch()
