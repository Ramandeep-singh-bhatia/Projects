"""
Document processor factory.
Orchestrates document extraction using appropriate extractors.
"""

from pathlib import Path
from typing import Optional, List
from src.processing.base_extractor import BaseExtractor, ExtractedDocument
from src.processing.pdf_extractor import PDFExtractor
from src.processing.docx_extractor import DOCXExtractor
from src.processing.xlsx_extractor import XLSXExtractor
from src.processing.pptx_extractor import PPTXExtractor
from src.processing.text_extractor import TextExtractor
from src.utils.logger import app_logger as logger


class DocumentProcessor:
    """
    Factory class for processing documents.
    Automatically selects the appropriate extractor based on file type.
    """

    def __init__(self):
        """Initialize document processor with all extractors."""
        self.extractors: List[BaseExtractor] = [
            PDFExtractor(),
            DOCXExtractor(),
            XLSXExtractor(),
            PPTXExtractor(),
            TextExtractor(),
        ]

    def process_document(self, file_path: Path) -> ExtractedDocument:
        """
        Process a document using the appropriate extractor.

        Args:
            file_path: Path to the document file

        Returns:
            ExtractedDocument with content and metadata

        Raises:
            ValueError: If no suitable extractor is found
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Find suitable extractor
        extractor = self._get_extractor(file_path)

        if not extractor:
            raise ValueError(
                f"No suitable extractor found for file type: {file_path.suffix}"
            )

        logger.info(f"Processing {file_path} with {extractor.__class__.__name__}")

        # Extract content
        return extractor.extract(file_path)

    def _get_extractor(self, file_path: Path) -> Optional[BaseExtractor]:
        """
        Find the appropriate extractor for the file.

        Args:
            file_path: Path to the document file

        Returns:
            Suitable extractor or None
        """
        for extractor in self.extractors:
            if extractor.can_handle(file_path):
                return extractor

        return None

    def can_process(self, file_path: Path) -> bool:
        """
        Check if this document can be processed.

        Args:
            file_path: Path to the document file

        Returns:
            True if a suitable extractor exists
        """
        return self._get_extractor(file_path) is not None

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of all supported file extensions.

        Returns:
            List of supported extensions
        """
        extensions = set()

        # Collect extensions from all extractors
        for extractor in self.extractors:
            if hasattr(extractor, 'SUPPORTED_EXTENSIONS'):
                extensions.update(extractor.SUPPORTED_EXTENSIONS)
            else:
                # Try common extensions for each extractor type
                ext_map = {
                    'PDFExtractor': ['pdf'],
                    'DOCXExtractor': ['docx'],
                    'XLSXExtractor': ['xlsx', 'xls'],
                    'PPTXExtractor': ['pptx'],
                }
                ext_name = extractor.__class__.__name__
                if ext_name in ext_map:
                    extensions.update(ext_map[ext_name])

        return sorted(list(extensions))


# Global document processor instance
document_processor = DocumentProcessor()
