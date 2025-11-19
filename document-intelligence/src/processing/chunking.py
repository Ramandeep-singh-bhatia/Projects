"""
Smart chunking strategies for document processing.
Implements semantic chunking, recursive splitting, and parent-child relationships.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter
)
from config.settings import settings
from src.utils.logger import app_logger as logger


@dataclass
class Chunk:
    """Container for a text chunk."""
    content: str
    index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]
    parent_chunk_id: Optional[int] = None


class ChunkingStrategy:
    """Smart chunking strategies for document processing."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        min_chunk_size: int = None
    ):
        """
        Initialize chunking strategy.

        Args:
            chunk_size: Target size for chunks
            chunk_overlap: Overlap between chunks
            min_chunk_size: Minimum chunk size
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.min_chunk_size = min_chunk_size or settings.min_chunk_size

    def chunk_recursive(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Recursive character text splitting with structure awareness.

        Args:
            text: Text to chunk
            metadata: Optional metadata for chunks

        Returns:
            List of chunks
        """
        logger.info(f"Chunking text with recursive strategy (size={self.chunk_size}, overlap={self.chunk_overlap})")

        # Create splitter with structure-aware separators
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n\n",  # Major sections
                "\n\n",    # Paragraphs
                "\n",      # Lines
                ". ",      # Sentences
                ", ",      # Clauses
                " ",       # Words
                ""         # Characters
            ]
        )

        # Split text
        text_chunks = splitter.split_text(text)

        # Create Chunk objects
        chunks = []
        current_pos = 0

        for i, chunk_text in enumerate(text_chunks):
            # Find chunk position in original text
            start_pos = text.find(chunk_text, current_pos)
            if start_pos == -1:
                start_pos = current_pos

            end_pos = start_pos + len(chunk_text)

            # Create chunk
            chunk = Chunk(
                content=chunk_text,
                index=i,
                start_char=start_pos,
                end_char=end_pos,
                metadata=metadata or {}
            )

            chunks.append(chunk)
            current_pos = end_pos

        logger.info(f"Created {len(chunks)} chunks")
        return chunks

    def chunk_with_parent_child(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_chunk_size: int = None,
        child_chunk_size: int = None
    ) -> tuple[List[Chunk], List[Chunk]]:
        """
        Create parent and child chunks for hierarchical retrieval.

        Parent chunks provide context, child chunks provide precision.

        Args:
            text: Text to chunk
            metadata: Optional metadata
            parent_chunk_size: Size for parent chunks (default: 3x chunk_size)
            child_chunk_size: Size for child chunks (default: chunk_size)

        Returns:
            Tuple of (parent_chunks, child_chunks)
        """
        parent_size = parent_chunk_size or (self.chunk_size * 3)
        child_size = child_chunk_size or self.chunk_size

        logger.info(f"Creating parent-child chunks (parent={parent_size}, child={child_size})")

        # Create parent chunks (larger)
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_size,
            chunk_overlap=self.chunk_overlap * 2,
            length_function=len,
        )

        parent_texts = parent_splitter.split_text(text)
        parent_chunks = []

        for i, parent_text in enumerate(parent_texts):
            parent_chunk = Chunk(
                content=parent_text,
                index=i,
                start_char=text.find(parent_text),
                end_char=text.find(parent_text) + len(parent_text),
                metadata={
                    **(metadata or {}),
                    "chunk_type": "parent",
                }
            )
            parent_chunks.append(parent_chunk)

        # Create child chunks (smaller) for each parent
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

        all_child_chunks = []
        child_index = 0

        for parent_idx, parent_chunk in enumerate(parent_chunks):
            child_texts = child_splitter.split_text(parent_chunk.content)

            for child_text in child_texts:
                child_chunk = Chunk(
                    content=child_text,
                    index=child_index,
                    start_char=text.find(child_text, parent_chunk.start_char),
                    end_char=text.find(child_text, parent_chunk.start_char) + len(child_text),
                    metadata={
                        **(metadata or {}),
                        "chunk_type": "child",
                        "parent_index": parent_idx,
                    },
                    parent_chunk_id=parent_idx
                )
                all_child_chunks.append(child_chunk)
                child_index += 1

        logger.info(f"Created {len(parent_chunks)} parent chunks and {len(all_child_chunks)} child chunks")
        return parent_chunks, all_child_chunks

    def chunk_by_tokens(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        tokens_per_chunk: int = 256
    ) -> List[Chunk]:
        """
        Chunk text by token count (useful for LLM context windows).

        Args:
            text: Text to chunk
            metadata: Optional metadata
            tokens_per_chunk: Target tokens per chunk

        Returns:
            List of chunks
        """
        logger.info(f"Chunking text by tokens (tokens_per_chunk={tokens_per_chunk})")

        splitter = TokenTextSplitter(
            chunk_size=tokens_per_chunk,
            chunk_overlap=50
        )

        text_chunks = splitter.split_text(text)

        chunks = []
        current_pos = 0

        for i, chunk_text in enumerate(text_chunks):
            start_pos = text.find(chunk_text, current_pos)
            if start_pos == -1:
                start_pos = current_pos

            end_pos = start_pos + len(chunk_text)

            chunk = Chunk(
                content=chunk_text,
                index=i,
                start_char=start_pos,
                end_char=end_pos,
                metadata={
                    **(metadata or {}),
                    "chunking_method": "token"
                }
            )

            chunks.append(chunk)
            current_pos = end_pos

        logger.info(f"Created {len(chunks)} token-based chunks")
        return chunks

    def chunk_by_section(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Chunk]:
        """
        Chunk text by sections (preserves document structure).

        Looks for section markers like headings, page breaks, etc.

        Args:
            text: Text to chunk
            metadata: Optional metadata

        Returns:
            List of chunks
        """
        logger.info("Chunking text by sections")

        # Split by common section markers
        sections = []
        current_section = []
        current_pos = 0

        for line in text.split('\n'):
            # Check if line is a section marker
            if self._is_section_marker(line):
                # Save previous section
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []

            current_section.append(line)

        # Add final section
        if current_section:
            sections.append('\n'.join(current_section))

        # Create chunks from sections
        chunks = []
        current_pos = 0

        for i, section_text in enumerate(sections):
            # If section is too large, split it further
            if len(section_text) > self.chunk_size * 2:
                section_chunks = self.chunk_recursive(section_text, metadata)
                chunks.extend(section_chunks)
            else:
                start_pos = text.find(section_text, current_pos)
                if start_pos == -1:
                    start_pos = current_pos

                end_pos = start_pos + len(section_text)

                chunk = Chunk(
                    content=section_text,
                    index=i,
                    start_char=start_pos,
                    end_char=end_pos,
                    metadata={
                        **(metadata or {}),
                        "chunking_method": "section"
                    }
                )

                chunks.append(chunk)
                current_pos = end_pos

        logger.info(f"Created {len(chunks)} section-based chunks")
        return chunks

    def _is_section_marker(self, line: str) -> bool:
        """Check if line is a section marker (heading, page break, etc.)."""
        line = line.strip()

        # Check for various section markers
        markers = [
            line.startswith('==='),  # Page separator
            line.startswith('# '),   # Markdown heading
            line.startswith('## '),
            line.startswith('### '),
            line.isupper() and len(line) < 100,  # All caps heading
            line.endswith(':') and len(line) < 100,  # Heading with colon
        ]

        return any(markers)


# Global chunking strategy instance
chunking_strategy = ChunkingStrategy()
