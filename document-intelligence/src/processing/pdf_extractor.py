"""
PDF document extractor.
Handles both native and scanned PDFs using PyPDF2 and pdfplumber.
"""

from pathlib import Path
from typing import Dict, Any
import PyPDF2
import pdfplumber
from datetime import datetime
from src.processing.base_extractor import BaseExtractor, ExtractedDocument
from src.utils.logger import app_logger as logger


class PDFExtractor(BaseExtractor):
    """Extractor for PDF documents."""

    def can_handle(self, file_path: Path) -> bool:
        """Check if file is a PDF."""
        return self._get_file_extension(file_path) == 'pdf'

    def extract(self, file_path: Path) -> ExtractedDocument:
        """
        Extract content and metadata from PDF.

        Args:
            file_path: Path to PDF file

        Returns:
            ExtractedDocument with content and metadata
        """
        logger.info(f"Extracting PDF: {file_path}")

        try:
            # Try pdfplumber first (better for complex layouts)
            content = self._extract_with_pdfplumber(file_path)

            # If pdfplumber fails or returns empty, try PyPDF2
            if not content or len(content.strip()) < 100:
                logger.info("Pdfplumber extraction insufficient, trying PyPDF2")
                content = self._extract_with_pypdf2(file_path)

            # Extract metadata
            metadata = self._extract_metadata(file_path)

            # Count pages and words
            page_count = metadata.get('page_count')
            word_count = self._count_words(content)
            language = self._detect_language(content)

            logger.info(f"Successfully extracted PDF: {page_count} pages, {word_count} words")

            return ExtractedDocument(
                content=content,
                metadata=metadata,
                page_count=page_count,
                word_count=word_count,
                language=language,
                title=metadata.get('title'),
                author=metadata.get('author'),
                created_date=metadata.get('created_date'),
                modified_date=metadata.get('modified_date')
            )

        except Exception as e:
            logger.error(f"Failed to extract PDF {file_path}: {str(e)}")
            raise

    def _extract_with_pdfplumber(self, file_path: Path) -> str:
        """Extract text using pdfplumber (better for tables and layout)."""
        content = []

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        content.append(f"=== Page {page_num} ===\n{page_text}")

                    # Extract tables if present
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            table_text = self._format_table(table)
                            content.append(f"\n[Table]\n{table_text}\n")

            return "\n\n".join(content)

        except Exception as e:
            logger.warning(f"Pdfplumber extraction failed: {str(e)}")
            return ""

    def _extract_with_pypdf2(self, file_path: Path) -> str:
        """Extract text using PyPDF2 (fallback method)."""
        content = []

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        content.append(f"=== Page {page_num} ===\n{page_text}")

            return "\n\n".join(content)

        except Exception as e:
            logger.error(f"PyPDF2 extraction failed: {str(e)}")
            raise

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract PDF metadata."""
        metadata = {}

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Page count
                metadata['page_count'] = len(pdf_reader.pages)

                # Document info
                if pdf_reader.metadata:
                    metadata['title'] = pdf_reader.metadata.get('/Title', '')
                    metadata['author'] = pdf_reader.metadata.get('/Author', '')
                    metadata['subject'] = pdf_reader.metadata.get('/Subject', '')
                    metadata['creator'] = pdf_reader.metadata.get('/Creator', '')
                    metadata['producer'] = pdf_reader.metadata.get('/Producer', '')

                    # Parse dates
                    created = pdf_reader.metadata.get('/CreationDate')
                    if created:
                        metadata['created_date'] = self._parse_pdf_date(created)

                    modified = pdf_reader.metadata.get('/ModDate')
                    if modified:
                        metadata['modified_date'] = self._parse_pdf_date(modified)

        except Exception as e:
            logger.warning(f"Failed to extract PDF metadata: {str(e)}")

        return metadata

    def _parse_pdf_date(self, date_str: str) -> datetime:
        """Parse PDF date format (D:YYYYMMDDHHmmSS)."""
        try:
            # Remove 'D:' prefix and timezone info
            date_str = date_str.replace('D:', '').split('+')[0].split('-')[0]
            # Parse the date
            return datetime.strptime(date_str[:14], '%Y%m%d%H%M%S')
        except Exception:
            return None

    def _format_table(self, table: list) -> str:
        """Format extracted table as text."""
        if not table:
            return ""

        # Simple tab-separated format
        formatted_rows = []
        for row in table:
            formatted_row = "\t".join(str(cell or '') for cell in row)
            formatted_rows.append(formatted_row)

        return "\n".join(formatted_rows)
