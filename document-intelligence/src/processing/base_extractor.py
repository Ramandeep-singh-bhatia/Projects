"""
Base extractor interface for document processing.
All document extractors should inherit from this class.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ExtractedDocument:
    """Container for extracted document content and metadata."""
    content: str
    metadata: Dict[str, Any]
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    language: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None


class BaseExtractor(ABC):
    """Abstract base class for document extractors."""

    @abstractmethod
    def extract(self, file_path: Path) -> ExtractedDocument:
        """
        Extract content and metadata from a document.

        Args:
            file_path: Path to the document file

        Returns:
            ExtractedDocument with content and metadata
        """
        pass

    @abstractmethod
    def can_handle(self, file_path: Path) -> bool:
        """
        Check if this extractor can handle the given file.

        Args:
            file_path: Path to the document file

        Returns:
            True if extractor can handle this file type
        """
        pass

    def _get_file_extension(self, file_path: Path) -> str:
        """Get file extension in lowercase."""
        return file_path.suffix.lower().lstrip('.')

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split())

    def _detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of text.
        Simple implementation - can be enhanced with langdetect library.
        """
        # Basic implementation - returns English as default
        # Can be enhanced with proper language detection
        return "en"
