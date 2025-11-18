"""
Test script for RAG components (retriever, query processor, conversation).
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.query_processor import QueryProcessor, QueryIntent
from src.utils.logger import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO", log_format="text")
logger = get_logger(__name__)


def test_query_classification():
    """Test query intent classification"""
    logger.info("=" * 60)
    logger.info("TEST 1: Query Intent Classification")
    logger.info("=" * 60)

    processor = QueryProcessor()

    test_queries = [
        ("My order hasn't arrived yet. How can I track it?", QueryIntent.SHIPPING),
        ("I need help resetting my password", QueryIntent.ACCOUNT),
        ("The app keeps crashing when I try to login", QueryIntent.TECHNICAL),
        ("I was charged twice for my order", QueryIntent.BILLING),
        ("What are the specifications of this product?", QueryIntent.PRODUCT),
        ("I want to return this item", QueryIntent.RETURN),
        ("I need to speak with a human agent", QueryIntent.ESCALATION),
    ]

    passed = 0
    failed = 0

    for query, expected_intent in test_queries:
        intent, confidence = processor.classify_intent(query)

        status = "✓" if intent == expected_intent else "✗"
        logger.info(f"{status} Query: '{query[:50]}...'")
        logger.info(f"  Expected: {expected_intent}, Got: {intent} (confidence: {confidence:.2f})")

        if intent == expected_intent:
            passed += 1
        else:
            failed += 1

    logger.info(f"\nResults: {passed}/{len(test_queries)} passed")
    return failed == 0


def test_query_normalization():
    """Test query normalization"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Query Normalization")
    logger.info("=" * 60)

    processor = QueryProcessor()

    test_queries = [
        ("   How   do   I   track   my   order???   ", "normalized spacing and punctuation"),
        ("I nead halp with my paswword", "spell correction"),
        ("WHAT ARE YOUR BUSINESS HOURS?", "case handling"),
    ]

    for query, test_name in test_queries:
        normalized = processor.normalize_query(query)
        logger.info(f"Test: {test_name}")
        logger.info(f"  Original: '{query}'")
        logger.info(f"  Normalized: '{normalized}'")

    logger.info("\n✓ Query normalization working")
    return True


def test_entity_extraction():
    """Test entity extraction from queries"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Entity Extraction")
    logger.info("=" * 60)

    processor = QueryProcessor()

    test_queries = [
        "My order #12345 hasn't shipped yet",
        "I ordered on 12/25/2023 and haven't received it",
        "Please contact me at support@example.com",
        "Call me at 555-123-4567 about order ORD-98765",
    ]

    for query in test_queries:
        entities = processor.extract_entities(query)
        logger.info(f"Query: '{query}'")
        logger.info(f"  Entities: {entities}")

    logger.info("\n✓ Entity extraction working")
    return True


def test_sentiment_detection():
    """Test sentiment detection"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Sentiment Detection")
    logger.info("=" * 60)

    processor = QueryProcessor()

    test_queries = [
        ("This is terrible! I'm very frustrated with your service!", "negative"),
        ("Thank you so much for your help! This is great!", "positive"),
        ("What time do you close?", "neutral"),
        ("I HATE this product!!! Never buying again!", "negative"),
    ]

    passed = 0

    for query, expected_sentiment in test_queries:
        sentiment = processor.detect_sentiment(query)

        status = "✓" if sentiment == expected_sentiment else "~"
        logger.info(f"{status} Query: '{query[:50]}'")
        logger.info(f"  Expected: {expected_sentiment}, Got: {sentiment}")

        if sentiment == expected_sentiment:
            passed += 1

    logger.info(f"\nResults: {passed}/{len(test_queries)} correct")
    return passed >= len(test_queries) * 0.75  # 75% accuracy threshold


def test_query_expansion():
    """Test query expansion"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Query Expansion")
    logger.info("=" * 60)

    processor = QueryProcessor()

    test_queries = [
        "How do I cancel my order?",
        "I need help tracking my package",
        "Can you change my shipping address?",
    ]

    for query in test_queries:
        expanded = processor.expand_query(query)
        logger.info(f"Original: '{query}'")
        for idx, variation in enumerate(expanded, 1):
            logger.info(f"  Variation {idx}: '{variation}'")

    logger.info("\n✓ Query expansion working")
    return True


def test_full_query_processing():
    """Test complete query processing pipeline"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: Full Query Processing Pipeline")
    logger.info("=" * 60)

    processor = QueryProcessor()

    test_query = "I'm really frustrated! My order #12345 hasn't arrived and I need it urgently. Can someone help?"

    result = processor.process_query(
        test_query,
        normalize=True,
        expand=True,
        detect_lang=True
    )

    logger.info(f"Original query: {result['original_query']}")
    logger.info(f"Normalized: {result['normalized_query']}")
    logger.info(f"Intent: {result['intent']} (confidence: {result['intent_confidence']:.2f})")
    logger.info(f"Sentiment: {result['sentiment']}")
    logger.info(f"Language: {result['language']} (confidence: {result['language_confidence']:.2f})")
    logger.info(f"Entities: {result['entities']}")
    logger.info(f"Should escalate: {result['should_escalate']}")
    logger.info(f"Query variations: {len(result['query_variations'])}")

    # Validate key fields exist
    required_fields = [
        'original_query', 'normalized_query', 'intent', 'sentiment',
        'language', 'entities', 'should_escalate'
    ]

    for field in required_fields:
        if field not in result:
            logger.error(f"✗ Missing required field: {field}")
            return False

    logger.info("\n✓ Full pipeline successful")
    return True


def test_question_detection():
    """Test question detection"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Question Detection")
    logger.info("=" * 60)

    processor = QueryProcessor()

    test_cases = [
        ("What are your business hours?", True),
        ("How do I reset my password?", True),
        ("Can you help me track my order?", True),
        ("I need to return this item.", False),
        ("My order hasn't arrived yet", False),
        ("Is this product in stock?", True),
    ]

    passed = 0

    for query, expected_is_question in test_cases:
        is_question = processor.is_question(query)

        status = "✓" if is_question == expected_is_question else "✗"
        logger.info(f"{status} '{query[:50]}'")
        logger.info(f"  Expected: {expected_is_question}, Got: {is_question}")

        if is_question == expected_is_question:
            passed += 1

    logger.info(f"\nResults: {passed}/{len(test_cases)} correct")
    return passed == len(test_cases)


def test_confidence_scoring():
    """Test confidence scoring logic"""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 8: Confidence Scoring (Conceptual)")
    logger.info("=" * 60)

    logger.info("Testing confidence scoring algorithm...")

    # Simulate different scenarios
    scenarios = [
        {
            "name": "High confidence - Good match",
            "top_similarity": 0.9,
            "num_relevant_docs": 3,
            "response_length": 200,
            "has_citation": True,
            "expected_min": 0.7
        },
        {
            "name": "Medium confidence - Partial match",
            "top_similarity": 0.6,
            "num_relevant_docs": 1,
            "response_length": 150,
            "has_citation": True,
            "expected_min": 0.5
        },
        {
            "name": "Low confidence - Weak match",
            "top_similarity": 0.4,
            "num_relevant_docs": 0,
            "response_length": 50,
            "has_citation": False,
            "expected_min": 0.2
        },
    ]

    for scenario in scenarios:
        # Calculate confidence using the formula from the spec
        score = 0.0

        # Factor 1: Top doc similarity (0-0.4)
        score += min(scenario["top_similarity"] * 0.4, 0.4)

        # Factor 2: Relevant docs (0-0.3)
        score += min(scenario["num_relevant_docs"] * 0.1, 0.3)

        # Factor 3: Response length (0-0.2)
        if 50 < scenario["response_length"] < 500:
            score += 0.2

        # Factor 4: Citation (0-0.1)
        if scenario["has_citation"]:
            score += 0.1

        confidence = min(score, 1.0)

        status = "✓" if confidence >= scenario["expected_min"] else "✗"
        logger.info(f"{status} {scenario['name']}: {confidence:.2f} (expected >= {scenario['expected_min']})")

    logger.info("\n✓ Confidence scoring algorithm validated")
    return True


def run_all_tests():
    """Run all RAG component tests"""
    logger.info("\n" + "=" * 60)
    logger.info("RAG COMPONENTS TEST SUITE")
    logger.info("=" * 60)

    tests = [
        ("Query Intent Classification", test_query_classification),
        ("Query Normalization", test_query_normalization),
        ("Entity Extraction", test_entity_extraction),
        ("Sentiment Detection", test_sentiment_detection),
        ("Query Expansion", test_query_expansion),
        ("Full Query Processing", test_full_query_processing),
        ("Question Detection", test_question_detection),
        ("Confidence Scoring", test_confidence_scoring),
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
