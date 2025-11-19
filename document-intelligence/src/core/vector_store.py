"""
Pinecone vector store management.
Handles initialization, upserting, and querying of vector embeddings.
"""

from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
from config.settings import settings
from src.utils.logger import app_logger as logger


class VectorStore:
    """Pinecone vector store manager."""

    def __init__(self):
        """Initialize Pinecone client."""
        self.pc = None
        self.index = None
        self._initialize()

    def _initialize(self):
        """Initialize Pinecone connection and index."""
        try:
            logger.info("Initializing Pinecone client...")
            self.pc = Pinecone(api_key=settings.pinecone_api_key)

            # Check if index exists, create if not
            if settings.pinecone_index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {settings.pinecone_index_name}")
                self.pc.create_index(
                    name=settings.pinecone_index_name,
                    dimension=settings.pinecone_dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.pinecone_environment
                    )
                )
                logger.info(f"Index {settings.pinecone_index_name} created successfully")
            else:
                logger.info(f"Index {settings.pinecone_index_name} already exists")

            # Connect to index
            self.index = self.pc.Index(settings.pinecone_index_name)
            logger.info("Pinecone initialization completed")

        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}")
            raise

    def upsert_vectors(
        self,
        vectors: List[tuple],
        namespace: str = ""
    ) -> Dict[str, Any]:
        """
        Upsert vectors to Pinecone.

        Args:
            vectors: List of tuples (id, embedding, metadata)
            namespace: Optional namespace for multi-tenancy

        Returns:
            Upsert response
        """
        try:
            logger.info(f"Upserting {len(vectors)} vectors to namespace: {namespace or 'default'}")
            response = self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info(f"Successfully upserted {response.upserted_count} vectors")
            return response
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {str(e)}")
            raise

    def query(
        self,
        vector: List[float],
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        namespace: str = "",
        include_metadata: bool = True,
        include_values: bool = False
    ) -> Dict[str, Any]:
        """
        Query vectors from Pinecone.

        Args:
            vector: Query embedding
            top_k: Number of results to return
            filter: Metadata filter
            namespace: Optional namespace
            include_metadata: Include metadata in results
            include_values: Include vector values in results

        Returns:
            Query results
        """
        try:
            logger.debug(f"Querying Pinecone with top_k={top_k}, namespace={namespace or 'default'}")
            results = self.index.query(
                vector=vector,
                top_k=top_k,
                filter=filter,
                namespace=namespace,
                include_metadata=include_metadata,
                include_values=include_values
            )
            logger.debug(f"Query returned {len(results.matches)} matches")
            return results
        except Exception as e:
            logger.error(f"Failed to query vectors: {str(e)}")
            raise

    def delete_by_ids(
        self,
        ids: List[str],
        namespace: str = ""
    ) -> None:
        """
        Delete vectors by IDs.

        Args:
            ids: List of vector IDs to delete
            namespace: Optional namespace
        """
        try:
            logger.info(f"Deleting {len(ids)} vectors from namespace: {namespace or 'default'}")
            self.index.delete(ids=ids, namespace=namespace)
            logger.info("Vectors deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete vectors: {str(e)}")
            raise

    def delete_by_filter(
        self,
        filter: Dict[str, Any],
        namespace: str = ""
    ) -> None:
        """
        Delete vectors by metadata filter.

        Args:
            filter: Metadata filter
            namespace: Optional namespace
        """
        try:
            logger.info(f"Deleting vectors by filter from namespace: {namespace or 'default'}")
            self.index.delete(filter=filter, namespace=namespace)
            logger.info("Vectors deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete vectors by filter: {str(e)}")
            raise

    def delete_namespace(self, namespace: str) -> None:
        """
        Delete all vectors in a namespace.

        Args:
            namespace: Namespace to delete
        """
        try:
            logger.info(f"Deleting namespace: {namespace}")
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Namespace {namespace} deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete namespace: {str(e)}")
            raise

    def get_index_stats(self, namespace: str = "") -> Dict[str, Any]:
        """
        Get index statistics.

        Args:
            namespace: Optional namespace

        Returns:
            Index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            logger.debug(f"Index stats: {stats}")
            return stats
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            raise


# Global vector store instance
vector_store = VectorStore()
