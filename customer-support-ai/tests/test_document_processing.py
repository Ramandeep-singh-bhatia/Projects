"""
Test script for document processing pipeline.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.document_processor import DocumentIngestionPipeline, ChunkingStrategy
from src.utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO", log_format="text")
logger = get_logger(__name__)


def test_document_loading():
    """Test document loading functionality"""
    logger.info("=" * 60)
    logger.info("TEST 1: Document Loading")
    logger.info("=" * 60)

    pipeline = DocumentIngestionPipeline()

    # Test with sample document
    sample_doc_path = "data/documents/sample_support_doc.txt"

    try:
        # Validate document
        is_valid, error = pipeline.validate_document(sample_doc_path)
        logger.info(f"Document validation: {'PASS' if is_valid else 'FAIL'}")
        if error:
            logger.error(f"Validation error: {error}")
            return False

        # Load document
        documents = pipeline.load_document(sample_doc_path)
        logger.info(f"✓ Loaded {len(documents)} document(s)")

        # Display first 200 chars
        if documents:
            preview = documents[0].page_content[:200]
            logger.info(f"Preview: {preview}...")

        return True

    except Exception as e:
        logger.error(f"✗ Document loading failed: {e}", exc_info=True)
        return False


def test_metadata_extraction():
    """Test metadata extraction"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Metadata Extraction")
    logger.info("=" * 60)

    pipeline = DocumentIngestionPipeline()
    sample_doc_path = "data/documents/sample_support_doc.txt"

    try:
        documents = pipeline.load_document(sample_doc_path)
        metadata = pipeline.extract_metadata(
            documents[0],
            sample_doc_path,
            additional_metadata={"category": "support", "language": "en"}
        )

        logger.info("Extracted metadata:")
        for key, value in metadata.items():
            logger.info(f"  {key}: {value}")

        # Validate required fields
        required_fields = ["source", "filename", "file_type", "upload_date"]
        for field in required_fields:
            if field not in metadata:
                logger.error(f"✗ Missing required field: {field}")
                return False

        logger.info("✓ Metadata extraction successful")
        return True

    except Exception as e:
        logger.error(f"✗ Metadata extraction failed: {e}", exc_info=True)
        return False


def test_chunking_strategies():
    """Test different chunking strategies"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Chunking Strategies")
    logger.info("=" * 60)

    pipeline = DocumentIngestionPipeline()
    sample_doc_path = "data/documents/sample_support_doc.txt"

    try:
        documents = pipeline.load_document(sample_doc_path)
        doc = documents[0]

        strategies = [
            ChunkingStrategy.FIXED_SIZE,
            ChunkingStrategy.SEMANTIC,
            ChunkingStrategy.STRUCTURE_AWARE
        ]

        results = {}

        for strategy in strategies:
            logger.info(f"\nTesting {strategy} strategy:")
            chunks = pipeline.chunk_document(doc, strategy=strategy)

            results[strategy] = {
                "num_chunks": len(chunks),
                "chunks": chunks
            }

            logger.info(f"  ✓ Created {len(chunks)} chunks")

            # Show first chunk preview
            if chunks:
                first_chunk = chunks[0]
                preview = first_chunk['chunk_text'][:150]
                logger.info(f"  Preview: {preview}...")
                logger.info(f"  Metadata: {first_chunk['metadata']}")

        # Validate results
        for strategy, result in results.items():
            if result['num_chunks'] == 0:
                logger.error(f"✗ {strategy} produced no chunks")
                return False

        logger.info("\n✓ All chunking strategies successful")
        return True

    except Exception as e:
        logger.error(f"✗ Chunking failed: {e}", exc_info=True)
        return False


def test_duplicate_detection():
    """Test duplicate chunk detection"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Duplicate Detection")
    logger.info("=" * 60)

    pipeline = DocumentIngestionPipeline()

    # Create sample chunks with duplicates
    chunks = [
        {"chunk_text": "This is chunk 1", "chunk_index": 0, "metadata": {}},
        {"chunk_text": "This is chunk 2", "chunk_index": 1, "metadata": {}},
        {"chunk_text": "This is chunk 1", "chunk_index": 2, "metadata": {}},  # Duplicate
        {"chunk_text": "This is chunk 3", "chunk_index": 3, "metadata": {}},
    ]

    try:
        unique_chunks, duplicates = pipeline.detect_duplicates(chunks)

        logger.info(f"Original chunks: {len(chunks)}")
        logger.info(f"Unique chunks: {len(unique_chunks)}")
        logger.info(f"Duplicates found: {len(duplicates)}")

        if len(duplicates) != 1:
            logger.error(f"✗ Expected 1 duplicate, found {len(duplicates)}")
            return False

        if len(unique_chunks) != 3:
            logger.error(f"✗ Expected 3 unique chunks, found {len(unique_chunks)}")
            return False

        logger.info("✓ Duplicate detection successful")
        return True

    except Exception as e:
        logger.error(f"✗ Duplicate detection failed: {e}", exc_info=True)
        return False


def test_full_pipeline():
    """Test the complete document processing pipeline"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Full Pipeline")
    logger.info("=" * 60)

    pipeline = DocumentIngestionPipeline()
    sample_doc_path = "data/documents/sample_support_doc.txt"

    try:
        result = pipeline.process_document(
            file_path=sample_doc_path,
            chunking_strategy=ChunkingStrategy.FIXED_SIZE,
            additional_metadata={"category": "support", "version": "1.0"},
            remove_duplicates=True
        )

        if not result.get("success"):
            logger.error(f"✗ Pipeline failed: {result.get('error')}")
            return False

        logger.info("Pipeline results:")
        logger.info(f"  File: {result['file_path']}")
        logger.info(f"  Pages: {result['num_pages']}")
        logger.info(f"  Chunks: {result['num_chunks']}")
        logger.info(f"  Duplicates: {result['num_duplicates']}")
        logger.info(f"  Processing time: {result['processing_time']:.3f}s")
        logger.info(f"  Strategy: {result['chunking_strategy']}")

        # Validate results
        if result['num_chunks'] == 0:
            logger.error("✗ No chunks created")
            return False

        logger.info("✓ Full pipeline successful")
        return True

    except Exception as e:
        logger.error(f"✗ Full pipeline failed: {e}", exc_info=True)
        return False


def run_all_tests():
    """Run all tests"""
    logger.info("\n" + "=" * 60)
    logger.info("DOCUMENT PROCESSING PIPELINE TESTS")
    logger.info("=" * 60)

    tests = [
        ("Document Loading", test_document_loading),
        ("Metadata Extraction", test_metadata_extraction),
        ("Chunking Strategies", test_chunking_strategies),
        ("Duplicate Detection", test_duplicate_detection),
        ("Full Pipeline", test_full_pipeline),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}", exc_info=True)
            results[test_name] = False

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info("-" * 60)
    logger.info(f"Results: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
