"""
Core RAG functionality including document processing, retrieval, and conversation management.
"""

from .document_processor import DocumentIngestionPipeline, ChunkingStrategy
from .embeddings import EmbeddingsManager

__all__ = [
    "DocumentIngestionPipeline",
    "ChunkingStrategy",
    "EmbeddingsManager",
]
