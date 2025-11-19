"""
Text document extractor.
Handles plain text, markdown, HTML, and other text-based formats.
"""

from pathlib import Path
from typing import Dict, Any
import os
from datetime import datetime
from bs4 import BeautifulSoup
from src.processing.base_extractor import BaseExtractor, ExtractedDocument
from src.utils.logger import app_logger as logger


class TextExtractor(BaseExtractor):
    """Extractor for text-based documents."""

    SUPPORTED_EXTENSIONS = ['txt', 'md', 'markdown', 'html', 'htm', 'csv']

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a text-based format."""
        return self._get_file_extension(file_path) in self.SUPPORTED_EXTENSIONS

    def extract(self, file_path: Path) -> ExtractedDocument:
        """
        Extract content and metadata from text file.

        Args:
            file_path: Path to text file

        Returns:
            ExtractedDocument with content and metadata
        """
        logger.info(f"Extracting text file: {file_path}")

        try:
            # Detect encoding
            encoding = self._detect_encoding(file_path)

            # Read file
            with open(file_path, 'r', encoding=encoding) as f:
                raw_content = f.read()

            # Process based on file type
            ext = self._get_file_extension(file_path)
            if ext in ['html', 'htm']:
                content = self._extract_html(raw_content)
            else:
                content = raw_content

            # Extract metadata
            metadata = self._extract_metadata(file_path)

            word_count = self._count_words(content)
            language = self._detect_language(content)

            logger.info(f"Successfully extracted text file: {word_count} words")

            return ExtractedDocument(
                content=content,
                metadata=metadata,
                page_count=None,
                word_count=word_count,
                language=language,
                title=file_path.stem,
                author=None,
                created_date=metadata.get('created_date'),
                modified_date=metadata.get('modified_date')
            )

        except Exception as e:
            logger.error(f"Failed to extract text file {file_path}: {str(e)}")
            raise

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        # Try common encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    f.read()
                return encoding
            except UnicodeDecodeError:
                continue

        # Default to utf-8 with error handling
        return 'utf-8'

    def _extract_html(self, html_content: str) -> str:
        """Extract text from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract file metadata."""
        metadata = {}

        try:
            stat = os.stat(file_path)

            metadata['file_size'] = stat.st_size
            metadata['created_date'] = datetime.fromtimestamp(stat.st_ctime)
            metadata['modified_date'] = datetime.fromtimestamp(stat.st_mtime)

        except Exception as e:
            logger.warning(f"Failed to extract file metadata: {str(e)}")

        return metadata
