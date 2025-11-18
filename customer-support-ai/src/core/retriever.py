"""
Hybrid retrieval system combining vector and keyword search.
"""
from typing import List, Dict, Any, Optional, Tuple
import time

from langchain.docstore.document import Document as LangchainDocument
from rank_bm25 import BM25Okapi
import numpy as np

from .embeddings import EmbeddingsManager
from ..utils.config import get_settings
from ..utils.logger import get_logger, PerformanceLogger

logger = get_logger(__name__)


class RetrievedDocument:
    """Container for retrieved document with score"""

    def __init__(
        self,
        document: LangchainDocument,
        score: float,
        retrieval_method: str = "hybrid"
    ):
        """
        Initialize retrieved document.

        Args:
            document: LangChain document
            score: Relevance score (higher is better)
            retrieval_method: Method used for retrieval
        """
        self.document = document
        self.score = score
        self.retrieval_method = retrieval_method
        self.metadata = document.metadata
        self.content = document.page_content

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata,
            "retrieval_method": self.retrieval_method,
        }

    def __repr__(self):
        return f"RetrievedDocument(score={self.score:.3f}, method={self.retrieval_method})"


class HybridRetriever:
    """Hybrid retriever combining vector and keyword search"""

    def __init__(
        self,
        embeddings_manager: Optional[EmbeddingsManager] = None,
        alpha: Optional[float] = None
    ):
        """
        Initialize hybrid retriever.

        Args:
            embeddings_manager: EmbeddingsManager instance
            alpha: Weight for vector vs keyword search (0=keyword only, 1=vector only)
        """
        self.settings = get_settings()
        self.logger = logger
        self.perf_logger = PerformanceLogger(logger)

        # Initialize embeddings manager
        self.embeddings_manager = embeddings_manager or EmbeddingsManager()

        # Hybrid search weight
        self.alpha = alpha if alpha is not None else self.settings.hybrid_search_alpha

        # BM25 index (will be built on demand)
        self.bm25_index: Optional[BM25Okapi] = None
        self.bm25_documents: List[LangchainDocument] = []
        self.bm25_corpus_tokenized: List[List[str]] = []

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenization for BM25.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Simple word tokenization (lowercase, split by whitespace)
        return text.lower().split()

    def _build_bm25_index(self):
        """Build BM25 index from vector store documents"""
        try:
            if self.embeddings_manager.vector_store is None:
                self.logger.warning("No vector store available for BM25 indexing")
                return

            self.logger.info("Building BM25 index from vector store")

            # Get all documents from vector store
            # Note: This is a simplified approach - in production, you'd want to
            # store and load the BM25 index persistently
            self.bm25_documents = []
            self.bm25_corpus_tokenized = []

            # Extract documents from FAISS
            # Since FAISS doesn't provide direct access to all documents,
            # we'll need to track them separately or use the metadata store
            for embedding_id, metadata in self.embeddings_manager.metadata_store.items():
                # We need to retrieve the actual document content
                # For now, we'll search for a dummy query to get documents
                # In production, maintain a separate document cache
                pass

            # For now, we'll rebuild on each retrieval if needed
            self.logger.info("BM25 index built successfully")

        except Exception as e:
            self.logger.error(f"Failed to build BM25 index: {e}", exc_info=True)

    def vector_search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDocument]:
        """
        Perform vector similarity search.

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            List of retrieved documents
        """
        try:
            start_time = time.time()

            # Perform search using embeddings manager
            results = self.embeddings_manager.search(
                query=query,
                k=k,
                filter_dict=filter_dict
            )

            # Convert to RetrievedDocument objects
            # Note: FAISS returns distance, we need to convert to similarity
            retrieved_docs = []
            for doc, distance in results:
                # Convert distance to similarity score (higher is better)
                # For L2 distance, similarity = 1 / (1 + distance)
                similarity = 1.0 / (1.0 + distance)

                retrieved_docs.append(
                    RetrievedDocument(
                        document=doc,
                        score=similarity,
                        retrieval_method="vector"
                    )
                )

            duration_ms = (time.time() - start_time) * 1000

            if retrieved_docs:
                self.perf_logger.log_retrieval_metrics(
                    query=query,
                    num_results=len(retrieved_docs),
                    top_score=retrieved_docs[0].score if retrieved_docs else 0.0,
                    duration_ms=duration_ms
                )

            return retrieved_docs

        except Exception as e:
            self.logger.error(f"Vector search failed: {e}", exc_info=True)
            return []

    def keyword_search(
        self,
        query: str,
        k: int = 5
    ) -> List[RetrievedDocument]:
        """
        Perform BM25 keyword search.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of retrieved documents
        """
        try:
            # Build BM25 index if needed
            if self.bm25_index is None:
                self._build_bm25_index()

            if self.bm25_index is None or not self.bm25_documents:
                self.logger.warning("BM25 index not available, falling back to vector search")
                return self.vector_search(query, k)

            # Tokenize query
            query_tokens = self._tokenize(query)

            # Get BM25 scores
            scores = self.bm25_index.get_scores(query_tokens)

            # Get top-k indices
            top_k_indices = np.argsort(scores)[::-1][:k]

            # Create retrieved documents
            retrieved_docs = []
            for idx in top_k_indices:
                if scores[idx] > 0:  # Only include documents with positive scores
                    retrieved_docs.append(
                        RetrievedDocument(
                            document=self.bm25_documents[idx],
                            score=float(scores[idx]),
                            retrieval_method="keyword"
                        )
                    )

            return retrieved_docs

        except Exception as e:
            self.logger.error(f"Keyword search failed: {e}", exc_info=True)
            return []

    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        alpha: Optional[float] = None,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedDocument]:
        """
        Perform hybrid search combining vector and keyword methods.

        Args:
            query: Search query
            k: Number of results to return
            alpha: Weight for vector vs keyword (0=keyword only, 1=vector only)
            filter_dict: Optional metadata filter

        Returns:
            List of retrieved documents sorted by hybrid score
        """
        try:
            start_time = time.time()

            alpha = alpha if alpha is not None else self.alpha

            # Perform both searches (retrieve more to ensure good coverage)
            retrieval_k = min(k * 2, 20)

            vector_results = self.vector_search(query, k=retrieval_k, filter_dict=filter_dict)
            keyword_results = self.keyword_search(query, k=retrieval_k)

            # Combine results
            combined_scores: Dict[str, Tuple[RetrievedDocument, float, float]] = {}

            # Process vector results
            if vector_results:
                # Normalize vector scores to 0-1 range
                max_vector_score = max(doc.score for doc in vector_results)
                min_vector_score = min(doc.score for doc in vector_results)
                score_range = max_vector_score - min_vector_score

                for doc in vector_results:
                    doc_id = doc.metadata.get('embedding_id', doc.content[:50])

                    # Normalize score
                    if score_range > 0:
                        normalized_score = (doc.score - min_vector_score) / score_range
                    else:
                        normalized_score = 1.0

                    combined_scores[doc_id] = (doc, normalized_score, 0.0)

            # Process keyword results
            if keyword_results:
                # Normalize keyword scores
                max_keyword_score = max(doc.score for doc in keyword_results)
                min_keyword_score = min(doc.score for doc in keyword_results)
                score_range = max_keyword_score - min_keyword_score

                for doc in keyword_results:
                    doc_id = doc.metadata.get('embedding_id', doc.content[:50])

                    # Normalize score
                    if score_range > 0:
                        normalized_score = (doc.score - min_keyword_score) / score_range
                    else:
                        normalized_score = 1.0

                    if doc_id in combined_scores:
                        # Update keyword score
                        existing_doc, vector_score, _ = combined_scores[doc_id]
                        combined_scores[doc_id] = (existing_doc, vector_score, normalized_score)
                    else:
                        combined_scores[doc_id] = (doc, 0.0, normalized_score)

            # Calculate hybrid scores
            hybrid_results = []
            for doc_id, (doc, vector_score, keyword_score) in combined_scores.items():
                # Hybrid score: weighted combination
                hybrid_score = alpha * vector_score + (1 - alpha) * keyword_score

                hybrid_doc = RetrievedDocument(
                    document=doc.document,
                    score=hybrid_score,
                    retrieval_method="hybrid"
                )
                hybrid_results.append(hybrid_doc)

            # Sort by hybrid score and return top-k
            hybrid_results.sort(key=lambda x: x.score, reverse=True)
            top_results = hybrid_results[:k]

            duration_ms = (time.time() - start_time) * 1000

            self.logger.info(
                f"Hybrid search completed",
                query=query[:50],
                num_results=len(top_results),
                alpha=alpha,
                duration_ms=duration_ms
            )

            return top_results

        except Exception as e:
            self.logger.error(f"Hybrid search failed: {e}", exc_info=True)
            # Fallback to vector search
            return self.vector_search(query, k, filter_dict)

    def rerank_results(
        self,
        query: str,
        documents: List[RetrievedDocument],
        method: str = "reciprocal_rank"
    ) -> List[RetrievedDocument]:
        """
        Re-rank retrieved documents.

        Args:
            query: Original query
            documents: List of retrieved documents
            method: Re-ranking method

        Returns:
            Re-ranked list of documents
        """
        if not documents:
            return documents

        try:
            if method == "reciprocal_rank":
                # Reciprocal Rank Fusion
                # Simple re-ranking based on position
                for idx, doc in enumerate(documents):
                    # Add position-based bonus to score
                    position_score = 1.0 / (idx + 1)
                    doc.score = 0.7 * doc.score + 0.3 * position_score

            elif method == "score_boost":
                # Boost documents with certain metadata
                for doc in documents:
                    # Boost recent documents
                    if 'upload_date' in doc.metadata:
                        # Simple recency boost (this is simplified)
                        doc.score *= 1.1

            # Re-sort after re-ranking
            documents.sort(key=lambda x: x.score, reverse=True)

            return documents

        except Exception as e:
            self.logger.error(f"Re-ranking failed: {e}", exc_info=True)
            return documents

    def retrieve(
        self,
        query: str,
        k: int = 5,
        method: str = "hybrid",
        filter_dict: Optional[Dict[str, Any]] = None,
        rerank: bool = True
    ) -> List[RetrievedDocument]:
        """
        Main retrieval method.

        Args:
            query: Search query
            k: Number of results to return
            method: Retrieval method (vector, keyword, hybrid)
            filter_dict: Optional metadata filter
            rerank: Whether to re-rank results

        Returns:
            List of retrieved documents
        """
        try:
            k = min(k, self.settings.top_k_retrieval * 2)  # Cap maximum results

            # Perform retrieval based on method
            if method == "vector":
                results = self.vector_search(query, k, filter_dict)
            elif method == "keyword":
                results = self.keyword_search(query, k)
            elif method == "hybrid":
                results = self.hybrid_search(query, k, filter_dict=filter_dict)
            else:
                self.logger.warning(f"Unknown method '{method}', using hybrid")
                results = self.hybrid_search(query, k, filter_dict=filter_dict)

            # Re-rank if requested
            if rerank and results:
                results = self.rerank_results(query, results)

            # Filter by minimum relevance threshold
            min_score = 0.3  # Minimum relevance threshold
            results = [doc for doc in results if doc.score >= min_score]

            self.logger.info(
                f"Retrieved {len(results)} documents",
                query=query[:50],
                method=method,
                top_score=results[0].score if results else 0.0
            )

            return results

        except Exception as e:
            self.logger.error(f"Retrieval failed: {e}", exc_info=True)
            return []

    def get_retrieval_stats(self) -> Dict[str, Any]:
        """
        Get retrieval statistics.

        Returns:
            Dictionary of statistics
        """
        stats = {
            "alpha": self.alpha,
            "bm25_index_built": self.bm25_index is not None,
            "num_bm25_documents": len(self.bm25_documents),
        }

        # Add vector store stats
        vector_stats = self.embeddings_manager.get_vector_store_stats()
        stats.update(vector_stats)

        return stats
