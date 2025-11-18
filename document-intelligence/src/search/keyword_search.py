"""
Keyword search implementation using BM25.
Provides exact keyword matching and ranking.
"""

from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
import re
from src.search.vector_search import SearchResult
from src.utils.logger import app_logger as logger
from config.settings import settings


class KeywordSearch:
    """Keyword search engine using BM25."""

    def __init__(self):
        """Initialize keyword search."""
        self.bm25 = None
        self.documents: List[Dict[str, Any]] = []
        self.tokenized_corpus = []

    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Build BM25 index from documents.

        Args:
            documents: List of documents with 'id', 'content', and 'metadata'
        """
        logger.info(f"Indexing {len(documents)} documents for keyword search")

        self.documents = documents

        # Tokenize all documents
        self.tokenized_corpus = [
            self._tokenize(doc['content'])
            for doc in documents
        ]

        # Build BM25 index
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            logger.info("BM25 index built successfully")
        else:
            logger.warning("No documents to index")

    def search(
        self,
        query: str,
        top_k: int = None,
        min_score: float = 0.0
    ) -> List[SearchResult]:
        """
        Perform keyword search using BM25.

        Args:
            query: Search query
            top_k: Number of results to return
            min_score: Minimum BM25 score threshold

        Returns:
            List of search results
        """
        if not self.bm25:
            logger.warning("BM25 index not initialized")
            return []

        top_k = top_k or settings.keyword_search_top_k

        logger.info(f"Performing keyword search: query='{query[:50]}...', top_k={top_k}")

        try:
            # Tokenize query
            tokenized_query = self._tokenize(query)

            # Get BM25 scores for all documents
            scores = self.bm25.get_scores(tokenized_query)

            # Get top-k document indices
            top_indices = sorted(
                range(len(scores)),
                key=lambda i: scores[i],
                reverse=True
            )[:top_k]

            # Convert to SearchResult objects
            search_results = []

            for idx in top_indices:
                score = scores[idx]

                # Apply score threshold
                if score < min_score:
                    continue

                doc = self.documents[idx]

                result = SearchResult(
                    id=doc['id'],
                    score=score,
                    content=doc['content'],
                    metadata=doc.get('metadata', {}),
                    document_id=doc.get('document_id'),
                    chunk_index=doc.get('chunk_index')
                )

                search_results.append(result)

            logger.info(f"Keyword search returned {len(search_results)} results")
            return search_results

        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            raise

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25.

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters except spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)

        # Split into tokens
        tokens = text.split()

        # Remove stopwords (optional - keeping it simple for now)
        # Can be enhanced with NLTK stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
            'to', 'for', 'of', 'as', 'by', 'with', 'from', 'is', 'was',
            'are', 'were', 'be', 'been', 'being'
        }

        tokens = [token for token in tokens if token not in stopwords]

        return tokens

    def add_document(self, document: Dict[str, Any]):
        """
        Add a single document to the index.

        Args:
            document: Document dict with 'id', 'content', 'metadata'
        """
        self.documents.append(document)
        tokenized = self._tokenize(document['content'])
        self.tokenized_corpus.append(tokenized)

        # Rebuild BM25 index
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

    def remove_document(self, document_id: str):
        """
        Remove a document from the index.

        Args:
            document_id: ID of document to remove
        """
        # Find document index
        for i, doc in enumerate(self.documents):
            if doc['id'] == document_id:
                # Remove from documents and tokenized corpus
                self.documents.pop(i)
                self.tokenized_corpus.pop(i)

                # Rebuild BM25 index
                if self.tokenized_corpus:
                    self.bm25 = BM25Okapi(self.tokenized_corpus)
                else:
                    self.bm25 = None

                logger.info(f"Removed document {document_id} from index")
                return

        logger.warning(f"Document {document_id} not found in index")

    def get_index_size(self) -> int:
        """Get number of documents in index."""
        return len(self.documents)


# Global keyword search instance
keyword_search = KeywordSearch()
