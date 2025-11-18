"""
Embeddings generation and vector store management.
"""
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pickle
import time

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document as LangchainDocument
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import numpy as np

from ..utils.config import get_settings
from ..utils.logger import get_logger, PerformanceLogger

logger = get_logger(__name__)


class EmbeddingsManager:
    """Manager for generating embeddings and maintaining vector store"""

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize embeddings manager.

        Args:
            openai_api_key: OpenAI API key (uses config if not provided)
        """
        self.settings = get_settings()
        self.logger = logger
        self.perf_logger = PerformanceLogger(logger)

        # Initialize OpenAI embeddings
        api_key = openai_api_key or self.settings.openai_api_key
        self.embeddings = OpenAIEmbeddings(
            model=self.settings.embedding_model,
            openai_api_key=api_key
        )

        # Vector store
        self.vector_store: Optional[FAISS] = None
        self.vector_store_path = self.settings.get_vector_store_path()
        self.index_path = self.settings.get_faiss_index_path()

        # Metadata storage (maps embedding IDs to chunk metadata)
        self.metadata_store: Dict[str, Dict[str, Any]] = {}

        # Load existing vector store if available
        self._load_vector_store()

    def _load_vector_store(self):
        """Load existing FAISS vector store from disk"""
        try:
            if self.index_path.exists():
                self.logger.info(f"Loading existing vector store from {self.index_path}")

                self.vector_store = FAISS.load_local(
                    str(self.vector_store_path),
                    self.embeddings,
                    self.settings.faiss_index_name,
                    allow_dangerous_deserialization=True
                )

                # Load metadata
                metadata_path = self.vector_store_path / f"{self.settings.faiss_index_name}_metadata.pkl"
                if metadata_path.exists():
                    with open(metadata_path, 'rb') as f:
                        self.metadata_store = pickle.load(f)

                self.logger.info(
                    "Vector store loaded successfully",
                    num_vectors=self.vector_store.index.ntotal if self.vector_store else 0
                )
            else:
                self.logger.info("No existing vector store found, will create new one")

        except Exception as e:
            self.logger.warning(
                f"Failed to load vector store: {e}",
                exc_info=True
            )
            self.vector_store = None

    def _save_vector_store(self):
        """Save FAISS vector store to disk"""
        try:
            if self.vector_store is None:
                self.logger.warning("No vector store to save")
                return

            self.logger.info(f"Saving vector store to {self.vector_store_path}")

            # Ensure directory exists
            self.vector_store_path.mkdir(parents=True, exist_ok=True)

            # Save FAISS index
            self.vector_store.save_local(
                str(self.vector_store_path),
                self.settings.faiss_index_name
            )

            # Save metadata
            metadata_path = self.vector_store_path / f"{self.settings.faiss_index_name}_metadata.pkl"
            with open(metadata_path, 'wb') as f:
                pickle.dump(self.metadata_store, f)

            self.logger.info("Vector store saved successfully")

        except Exception as e:
            self.logger.error(
                f"Failed to save vector store: {e}",
                exc_info=True
            )
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for texts with retry logic.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts to embed per batch

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        start_time = time.time()

        try:
            all_embeddings = []

            # Process in batches
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                self.logger.debug(
                    f"Generating embeddings for batch {i // batch_size + 1}",
                    batch_size=len(batch)
                )

                # Generate embeddings
                batch_embeddings = self.embeddings.embed_documents(batch)
                all_embeddings.extend(batch_embeddings)

                # Small delay to avoid rate limits
                if i + batch_size < len(texts):
                    time.sleep(0.1)

            duration_ms = (time.time() - start_time) * 1000

            # Log performance
            self.perf_logger.log_token_usage(
                operation="generate_embeddings",
                input_tokens=sum(len(text.split()) for text in texts),  # Approximation
                output_tokens=0,
                cost=0.0001 * (sum(len(text.split()) for text in texts) / 1000),  # Approximate cost
                model=self.settings.embedding_model,
                num_embeddings=len(all_embeddings),
                duration_ms=duration_ms
            )

            return all_embeddings

        except Exception as e:
            self.logger.error(
                f"Failed to generate embeddings: {e}",
                num_texts=len(texts),
                exc_info=True
            )
            raise

    def store_embeddings(
        self,
        chunks: List[Dict[str, Any]],
        document_id: int,
        embeddings: Optional[List[List[float]]] = None
    ) -> List[str]:
        """
        Store embeddings in vector store.

        Args:
            chunks: List of chunk dictionaries
            document_id: ID of the document
            embeddings: Pre-generated embeddings (optional, will generate if not provided)

        Returns:
            List of embedding IDs
        """
        if not chunks:
            self.logger.warning("No chunks to store")
            return []

        try:
            start_time = time.time()

            # Extract texts
            texts = [chunk['chunk_text'] for chunk in chunks]

            # Generate embeddings if not provided
            if embeddings is None:
                self.logger.info(f"Generating embeddings for {len(texts)} chunks")
                embeddings = self.generate_embeddings(texts)

            # Create LangChain documents
            documents = []
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                # Create unique embedding ID
                embedding_id = f"doc_{document_id}_chunk_{chunk['chunk_index']}"

                # Create document with metadata
                metadata = {
                    **chunk.get('metadata', {}),
                    'embedding_id': embedding_id,
                    'document_id': document_id,
                    'chunk_index': chunk['chunk_index'],
                }

                doc = LangchainDocument(
                    page_content=chunk['chunk_text'],
                    metadata=metadata
                )
                documents.append(doc)

                # Store metadata
                self.metadata_store[embedding_id] = metadata

            # Add to vector store
            if self.vector_store is None:
                # Create new vector store
                self.logger.info("Creating new FAISS vector store")
                self.vector_store = FAISS.from_documents(
                    documents,
                    self.embeddings
                )
            else:
                # Add to existing vector store
                self.logger.info(f"Adding {len(documents)} documents to existing vector store")
                self.vector_store.add_documents(documents)

            # Save vector store
            self._save_vector_store()

            duration_ms = (time.time() - start_time) * 1000

            self.logger.info(
                f"Stored {len(documents)} embeddings successfully",
                document_id=document_id,
                num_chunks=len(chunks),
                duration_ms=duration_ms
            )

            # Return embedding IDs
            return [f"doc_{document_id}_chunk_{chunk['chunk_index']}" for chunk in chunks]

        except Exception as e:
            self.logger.error(
                f"Failed to store embeddings: {e}",
                document_id=document_id,
                exc_info=True
            )
            raise

    def update_vector_store(self, rebuild: bool = False):
        """
        Update or rebuild the vector store.

        Args:
            rebuild: If True, rebuild from scratch
        """
        try:
            if rebuild:
                self.logger.info("Rebuilding vector store from scratch")
                self.vector_store = None
                self.metadata_store = {}

                # Clear existing files
                if self.index_path.exists():
                    import shutil
                    shutil.rmtree(self.vector_store_path)
                    self.vector_store_path.mkdir(parents=True, exist_ok=True)

            self._save_vector_store()

            self.logger.info("Vector store updated successfully")

        except Exception as e:
            self.logger.error(
                f"Failed to update vector store: {e}",
                exc_info=True
            )
            raise

    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[LangchainDocument, float]]:
        """
        Search for similar documents.

        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            List of (document, score) tuples
        """
        if self.vector_store is None:
            self.logger.warning("No vector store available for search")
            return []

        try:
            start_time = time.time()

            # Perform similarity search with scores
            results = self.vector_store.similarity_search_with_score(
                query,
                k=k,
                filter=filter_dict
            )

            duration_ms = (time.time() - start_time) * 1000

            # Log retrieval metrics
            if results:
                top_score = results[0][1] if results else 0.0
                self.perf_logger.log_retrieval_metrics(
                    query=query,
                    num_results=len(results),
                    top_score=top_score,
                    duration_ms=duration_ms
                )

            return results

        except Exception as e:
            self.logger.error(
                f"Search failed: {e}",
                query=query,
                exc_info=True
            )
            return []

    def delete_document_embeddings(self, document_id: int) -> bool:
        """
        Delete all embeddings for a document.

        Args:
            document_id: ID of the document

        Returns:
            True if successful
        """
        try:
            if self.vector_store is None:
                self.logger.warning("No vector store available")
                return False

            # Find all embedding IDs for this document
            embedding_ids_to_delete = [
                eid for eid, meta in self.metadata_store.items()
                if meta.get('document_id') == document_id
            ]

            if not embedding_ids_to_delete:
                self.logger.info(f"No embeddings found for document {document_id}")
                return True

            # FAISS doesn't support direct deletion, so we need to rebuild
            # For now, we'll mark them in metadata and rebuild on next update
            for eid in embedding_ids_to_delete:
                if eid in self.metadata_store:
                    del self.metadata_store[eid]

            self.logger.info(
                f"Marked {len(embedding_ids_to_delete)} embeddings for deletion",
                document_id=document_id
            )

            # Note: Full rebuild would be needed for actual deletion from FAISS
            # This is a simplified implementation

            return True

        except Exception as e:
            self.logger.error(
                f"Failed to delete embeddings: {e}",
                document_id=document_id,
                exc_info=True
            )
            return False

    def get_vector_store_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary of statistics
        """
        stats = {
            "exists": self.vector_store is not None,
            "num_vectors": 0,
            "num_documents": 0,
            "embedding_dimension": 0,
            "index_path": str(self.index_path),
        }

        if self.vector_store:
            try:
                stats["num_vectors"] = self.vector_store.index.ntotal
                stats["embedding_dimension"] = self.vector_store.index.d

                # Count unique documents
                unique_docs = set(
                    meta.get('document_id')
                    for meta in self.metadata_store.values()
                    if 'document_id' in meta
                )
                stats["num_documents"] = len(unique_docs)

            except Exception as e:
                self.logger.warning(f"Failed to get vector store stats: {e}")

        return stats

    def validate_embeddings(self, embeddings: List[List[float]]) -> bool:
        """
        Validate embedding vectors.

        Args:
            embeddings: List of embedding vectors

        Returns:
            True if valid
        """
        if not embeddings:
            return False

        try:
            # Check all embeddings have same dimension
            dimensions = [len(emb) for emb in embeddings]
            if len(set(dimensions)) > 1:
                self.logger.error("Embeddings have inconsistent dimensions")
                return False

            # Check for NaN or Inf values
            for emb in embeddings:
                if np.isnan(emb).any() or np.isinf(emb).any():
                    self.logger.error("Embeddings contain NaN or Inf values")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Embedding validation failed: {e}")
            return False
