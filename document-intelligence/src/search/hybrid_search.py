"""
Hybrid search combining vector and keyword search.
Uses Reciprocal Rank Fusion (RRF) for result combination.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict
from src.search.vector_search import vector_search, SearchResult
from src.search.keyword_search import keyword_search
from config.settings import settings
from src.utils.logger import app_logger as logger


class HybridSearch:
    """Hybrid search engine combining vector and keyword search."""

    def __init__(
        self,
        vector_weight: float = None,
        keyword_weight: float = None,
        rrf_k: int = 60
    ):
        """
        Initialize hybrid search.

        Args:
            vector_weight: Weight for vector search scores (default: 0.7)
            keyword_weight: Weight for keyword search scores (default: 0.3)
            rrf_k: RRF constant (default: 60)
        """
        self.vector_search = vector_search
        self.keyword_search = keyword_search
        self.vector_weight = vector_weight or settings.hybrid_vector_weight
        self.keyword_weight = keyword_weight or settings.hybrid_keyword_weight
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        use_rrf: bool = True
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining vector and keyword search.

        Args:
            query: Search query
            top_k: Number of results to return
            filter: Metadata filter for vector search
            use_rrf: Use Reciprocal Rank Fusion (True) or weighted scores (False)

        Returns:
            List of search results
        """
        logger.info(f"Performing hybrid search: query='{query[:50]}...', top_k={top_k}, use_rrf={use_rrf}")

        try:
            # Perform vector search
            vector_results = self.vector_search.search(
                query=query,
                top_k=top_k * 2,  # Get more results for fusion
                filter=filter
            )

            # Perform keyword search
            keyword_results = self.keyword_search.search(
                query=query,
                top_k=top_k * 2
            )

            logger.info(f"Vector search: {len(vector_results)} results, Keyword search: {len(keyword_results)} results")

            # Combine results
            if use_rrf:
                combined_results = self._reciprocal_rank_fusion(
                    vector_results,
                    keyword_results,
                    top_k
                )
            else:
                combined_results = self._weighted_combination(
                    vector_results,
                    keyword_results,
                    top_k
                )

            logger.info(f"Hybrid search returned {len(combined_results)} results")
            return combined_results

        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            # Fallback to vector search only
            logger.warning("Falling back to vector search only")
            return self.vector_search.search(query=query, top_k=top_k, filter=filter)

    def _reciprocal_rank_fusion(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """
        Combine results using Reciprocal Rank Fusion (RRF).

        RRF formula: RRF(d) = sum(1 / (k + rank(d)))
        where k is a constant (typically 60) and rank starts from 1.

        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            top_k: Number of results to return

        Returns:
            Combined and ranked results
        """
        logger.debug("Applying Reciprocal Rank Fusion")

        # Calculate RRF scores
        rrf_scores = defaultdict(float)
        result_map = {}  # Map ID to SearchResult

        # Process vector results
        for rank, result in enumerate(vector_results, start=1):
            rrf_scores[result.id] += self.vector_weight / (self.rrf_k + rank)
            result_map[result.id] = result

        # Process keyword results
        for rank, result in enumerate(keyword_results, start=1):
            rrf_scores[result.id] += self.keyword_weight / (self.rrf_k + rank)
            if result.id not in result_map:
                result_map[result.id] = result

        # Sort by RRF score
        sorted_ids = sorted(
            rrf_scores.keys(),
            key=lambda x: rrf_scores[x],
            reverse=True
        )[:top_k]

        # Create final results with RRF scores
        final_results = []
        for result_id in sorted_ids:
            result = result_map[result_id]
            # Update score to RRF score
            result.score = rrf_scores[result_id]
            final_results.append(result)

        return final_results

    def _weighted_combination(
        self,
        vector_results: List[SearchResult],
        keyword_results: List[SearchResult],
        top_k: int
    ) -> List[SearchResult]:
        """
        Combine results using weighted score combination.

        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            top_k: Number of results to return

        Returns:
            Combined and ranked results
        """
        logger.debug("Applying weighted score combination")

        # Normalize scores
        vector_results = self._normalize_scores(vector_results)
        keyword_results = self._normalize_scores(keyword_results)

        # Calculate weighted scores
        combined_scores = defaultdict(float)
        result_map = {}

        # Process vector results
        for result in vector_results:
            combined_scores[result.id] += result.score * self.vector_weight
            result_map[result.id] = result

        # Process keyword results
        for result in keyword_results:
            combined_scores[result.id] += result.score * self.keyword_weight
            if result.id not in result_map:
                result_map[result.id] = result

        # Sort by combined score
        sorted_ids = sorted(
            combined_scores.keys(),
            key=lambda x: combined_scores[x],
            reverse=True
        )[:top_k]

        # Create final results
        final_results = []
        for result_id in sorted_ids:
            result = result_map[result_id]
            result.score = combined_scores[result_id]
            final_results.append(result)

        return final_results

    def _normalize_scores(
        self,
        results: List[SearchResult]
    ) -> List[SearchResult]:
        """
        Normalize scores to [0, 1] range using min-max normalization.

        Args:
            results: Search results to normalize

        Returns:
            Results with normalized scores
        """
        if not results:
            return results

        # Get min and max scores
        scores = [r.score for r in results]
        min_score = min(scores)
        max_score = max(scores)

        # Avoid division by zero
        if max_score == min_score:
            for result in results:
                result.score = 1.0
            return results

        # Normalize
        for result in results:
            result.score = (result.score - min_score) / (max_score - min_score)

        return results


# Global hybrid search instance
hybrid_search = HybridSearch()
