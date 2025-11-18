"""
Document processing pipeline for ingesting and chunking documents.
"""
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import hashlib
import re

from langchain.docstore.document import Document as LangchainDocument
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
    UnstructuredHTMLLoader,
)
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
)
import tiktoken

from ..utils.config import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChunkingStrategy:
    """Enumeration of chunking strategies"""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    STRUCTURE_AWARE = "structure_aware"


class DocumentIngestionPipeline:
    """Pipeline for ingesting and processing documents"""

    def __init__(self):
        """Initialize the document ingestion pipeline"""
        self.settings = get_settings()
        self.logger = logger

        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            self.logger.warning(f"Failed to initialize tiktoken, using approximation: {e}")
            self.tokenizer = None

        # Supported file types
        self.supported_extensions = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
            '.csv': CSVLoader,
            '.html': UnstructuredHTMLLoader,
            '.htm': UnstructuredHTMLLoader,
        }

    def load_document(self, file_path: str) -> List[LangchainDocument]:
        """
        Load a document from file path.

        Args:
            file_path: Path to the document file

        Returns:
            List of LangChain Document objects

        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = path.suffix.lower()

        if file_extension not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {list(self.supported_extensions.keys())}"
            )

        loader_class = self.supported_extensions[file_extension]

        try:
            self.logger.info(f"Loading document: {file_path}", file_type=file_extension)

            # Special handling for different loaders
            if file_extension == '.txt':
                loader = loader_class(file_path, encoding='utf-8')
            else:
                loader = loader_class(file_path)

            documents = loader.load()

            self.logger.info(
                f"Document loaded successfully",
                file_path=file_path,
                num_pages=len(documents)
            )

            return documents

        except Exception as e:
            self.logger.error(
                f"Failed to load document: {file_path}",
                error=str(e),
                exc_info=True
            )
            raise

    def extract_metadata(
        self,
        document: LangchainDocument,
        file_path: str,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract metadata from document.

        Args:
            document: LangChain Document object
            file_path: Path to the document file
            additional_metadata: Additional metadata to include

        Returns:
            Dictionary of metadata
        """
        path = Path(file_path)

        metadata = {
            "source": str(path),
            "filename": path.name,
            "file_type": path.suffix.lower().replace('.', ''),
            "file_size": path.stat().st_size if path.exists() else 0,
            "upload_date": datetime.utcnow().isoformat(),
        }

        # Extract metadata from the document itself
        if hasattr(document, 'metadata') and document.metadata:
            # Add page number if available
            if 'page' in document.metadata:
                metadata['page'] = document.metadata['page']

            # Add source metadata
            if 'source' in document.metadata:
                metadata['original_source'] = document.metadata['source']

        # Add any additional metadata
        if additional_metadata:
            metadata.update(additional_metadata)

        # Try to detect author, date, etc. from content (simplified)
        content = document.page_content[:500]  # First 500 chars

        # Simple date detection (YYYY-MM-DD format)
        date_pattern = r'\b(\d{4}[-/]\d{2}[-/]\d{2})\b'
        dates = re.findall(date_pattern, content)
        if dates:
            metadata['detected_date'] = dates[0]

        return metadata

    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Number of tokens
        """
        if self.tokenizer:
            try:
                return len(self.tokenizer.encode(text))
            except Exception:
                pass

        # Fallback: approximate 1 token ≈ 4 characters
        return len(text) // 4

    def chunk_document(
        self,
        document: LangchainDocument,
        strategy: str = ChunkingStrategy.FIXED_SIZE,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document using specified strategy.

        Args:
            document: LangChain Document object
            strategy: Chunking strategy to use
            chunk_size: Size of chunks (overrides config)
            chunk_overlap: Overlap between chunks (overrides config)

        Returns:
            List of chunks with metadata
        """
        chunk_size = chunk_size or self.settings.chunk_size
        chunk_overlap = chunk_overlap or self.settings.chunk_overlap

        self.logger.debug(
            f"Chunking document with strategy: {strategy}",
            strategy=strategy,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        if strategy == ChunkingStrategy.FIXED_SIZE:
            chunks = self._chunk_fixed_size(
                document,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif strategy == ChunkingStrategy.SEMANTIC:
            chunks = self._chunk_semantic(
                document,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif strategy == ChunkingStrategy.STRUCTURE_AWARE:
            chunks = self._chunk_structure_aware(
                document,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        else:
            raise ValueError(f"Unknown chunking strategy: {strategy}")

        self.logger.info(
            f"Document chunked successfully",
            strategy=strategy,
            num_chunks=len(chunks)
        )

        return chunks

    def _chunk_fixed_size(
        self,
        document: LangchainDocument,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk document with fixed size and overlap.

        Args:
            document: LangChain Document object
            chunk_size: Size of chunks in tokens
            chunk_overlap: Overlap between chunks in tokens

        Returns:
            List of chunks with metadata
        """
        # Use RecursiveCharacterTextSplitter for better splitting
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self._count_tokens,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        split_docs = text_splitter.split_documents([document])

        chunks = []
        for idx, chunk_doc in enumerate(split_docs):
            chunk_data = {
                "chunk_text": chunk_doc.page_content,
                "chunk_index": idx,
                "metadata": {
                    **document.metadata,
                    "chunk_strategy": "fixed_size",
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "token_count": self._count_tokens(chunk_doc.page_content),
                }
            }
            chunks.append(chunk_data)

        return chunks

    def _chunk_semantic(
        self,
        document: LangchainDocument,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk document with semantic/sentence awareness.

        Args:
            document: LangChain Document object
            chunk_size: Target size of chunks in tokens
            chunk_overlap: Overlap between chunks in tokens

        Returns:
            List of chunks with metadata
        """
        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', document.page_content)

        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_idx = 0

        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)

            # If adding this sentence exceeds chunk_size, save current chunk
            if current_tokens + sentence_tokens > chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "chunk_text": chunk_text,
                    "chunk_index": chunk_idx,
                    "metadata": {
                        **document.metadata,
                        "chunk_strategy": "semantic",
                        "token_count": current_tokens,
                    }
                })
                chunk_idx += 1

                # Keep last sentence for overlap (simplified)
                if chunk_overlap > 0 and current_chunk:
                    overlap_text = current_chunk[-1]
                    overlap_tokens = self._count_tokens(overlap_text)
                    current_chunk = [overlap_text] if overlap_tokens < chunk_overlap else []
                    current_tokens = overlap_tokens if overlap_tokens < chunk_overlap else 0
                else:
                    current_chunk = []
                    current_tokens = 0

            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Add remaining chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "chunk_text": chunk_text,
                "chunk_index": chunk_idx,
                "metadata": {
                    **document.metadata,
                    "chunk_strategy": "semantic",
                    "token_count": current_tokens,
                }
            })

        return chunks

    def _chunk_structure_aware(
        self,
        document: LangchainDocument,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[Dict[str, Any]]:
        """
        Chunk document while preserving structure (headers, sections).

        Args:
            document: LangChain Document object
            chunk_size: Target size of chunks in tokens
            chunk_overlap: Overlap between chunks in tokens

        Returns:
            List of chunks with metadata
        """
        content = document.page_content

        # Detect markdown-style headers
        header_pattern = r'^#{1,6}\s+.+$'
        lines = content.split('\n')

        sections = []
        current_section = []
        current_header = None

        for line in lines:
            if re.match(header_pattern, line):
                # Save previous section
                if current_section:
                    sections.append({
                        'header': current_header,
                        'content': '\n'.join(current_section)
                    })
                current_header = line
                current_section = [line]
            else:
                current_section.append(line)

        # Add last section
        if current_section:
            sections.append({
                'header': current_header,
                'content': '\n'.join(current_section)
            })

        # Now chunk each section
        chunks = []
        chunk_idx = 0

        for section in sections:
            section_content = section['content']
            section_tokens = self._count_tokens(section_content)

            if section_tokens <= chunk_size:
                # Section fits in one chunk
                chunks.append({
                    "chunk_text": section_content,
                    "chunk_index": chunk_idx,
                    "metadata": {
                        **document.metadata,
                        "chunk_strategy": "structure_aware",
                        "section_header": section['header'],
                        "token_count": section_tokens,
                    }
                })
                chunk_idx += 1
            else:
                # Section too large, use recursive splitting
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    length_function=self._count_tokens
                )

                section_doc = LangchainDocument(
                    page_content=section_content,
                    metadata=document.metadata
                )
                split_docs = text_splitter.split_documents([section_doc])

                for sub_chunk in split_docs:
                    chunks.append({
                        "chunk_text": sub_chunk.page_content,
                        "chunk_index": chunk_idx,
                        "metadata": {
                            **document.metadata,
                            "chunk_strategy": "structure_aware",
                            "section_header": section['header'],
                            "token_count": self._count_tokens(sub_chunk.page_content),
                        }
                    })
                    chunk_idx += 1

        return chunks

    def detect_duplicates(
        self,
        chunks: List[Dict[str, Any]],
        threshold: float = 0.95
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Detect and remove duplicate chunks.

        Args:
            chunks: List of chunks to check
            threshold: Similarity threshold for duplicates (0-1)

        Returns:
            Tuple of (unique chunks, duplicate hashes)
        """
        seen_hashes = set()
        unique_chunks = []
        duplicates = []

        for chunk in chunks:
            # Create hash of chunk text
            chunk_hash = hashlib.md5(
                chunk['chunk_text'].encode('utf-8')
            ).hexdigest()

            if chunk_hash not in seen_hashes:
                seen_hashes.add(chunk_hash)
                unique_chunks.append(chunk)
            else:
                duplicates.append(chunk_hash)

        if duplicates:
            self.logger.info(
                f"Detected {len(duplicates)} duplicate chunks",
                num_duplicates=len(duplicates),
                num_unique=len(unique_chunks)
            )

        return unique_chunks, duplicates

    def process_document(
        self,
        file_path: str,
        chunking_strategy: str = ChunkingStrategy.FIXED_SIZE,
        additional_metadata: Optional[Dict[str, Any]] = None,
        remove_duplicates: bool = True
    ) -> Dict[str, Any]:
        """
        Orchestrate the full document processing pipeline.

        Args:
            file_path: Path to the document file
            chunking_strategy: Strategy for chunking
            additional_metadata: Additional metadata to include
            remove_duplicates: Whether to remove duplicate chunks

        Returns:
            Dictionary with processed document data
        """
        try:
            start_time = datetime.utcnow()

            # Step 1: Load document
            documents = self.load_document(file_path)

            all_chunks = []
            all_metadata = []

            # Step 2: Process each page/section
            for doc in documents:
                # Extract metadata
                metadata = self.extract_metadata(
                    doc,
                    file_path,
                    additional_metadata
                )
                all_metadata.append(metadata)

                # Chunk document
                chunks = self.chunk_document(
                    doc,
                    strategy=chunking_strategy
                )
                all_chunks.extend(chunks)

            # Step 3: Detect duplicates
            if remove_duplicates:
                all_chunks, duplicates = self.detect_duplicates(all_chunks)
            else:
                duplicates = []

            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()

            result = {
                "success": True,
                "file_path": file_path,
                "num_pages": len(documents),
                "num_chunks": len(all_chunks),
                "num_duplicates": len(duplicates),
                "chunks": all_chunks,
                "metadata": all_metadata[0] if all_metadata else {},
                "processing_time": processing_time,
                "chunking_strategy": chunking_strategy,
            }

            self.logger.info(
                f"Document processing completed",
                file_path=file_path,
                num_chunks=len(all_chunks),
                processing_time=processing_time
            )

            return result

        except Exception as e:
            self.logger.error(
                f"Document processing failed: {file_path}",
                error=str(e),
                exc_info=True
            )
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }

    def validate_document(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a document can be processed.

        Args:
            file_path: Path to the document file

        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return False, f"File not found: {file_path}"

        # Check file extension
        if path.suffix.lower() not in self.supported_extensions:
            return False, f"Unsupported file type: {path.suffix}"

        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if path.stat().st_size > max_size:
            return False, f"File too large (max 50MB): {path.stat().st_size / 1024 / 1024:.2f}MB"

        # Check if file is readable
        try:
            with open(file_path, 'rb') as f:
                f.read(1)
        except Exception as e:
            return False, f"File not readable: {str(e)}"

        return True, None
