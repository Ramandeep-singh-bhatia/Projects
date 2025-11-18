"""
Query processing for intent classification, normalization, and expansion.
"""
from typing import List, Dict, Any, Optional, Tuple
import re
from langdetect import detect, LangDetectException
from spellchecker import SpellChecker

from ..utils.logger import get_logger

logger = get_logger(__name__)


class QueryIntent:
    """Query intent classifications"""
    TECHNICAL = "technical"
    BILLING = "billing"
    PRODUCT = "product"
    SHIPPING = "shipping"
    RETURN = "return"
    ACCOUNT = "account"
    GENERAL = "general"
    ESCALATION = "escalation"


class QueryProcessor:
    """Processor for query analysis and preprocessing"""

    def __init__(self):
        """Initialize query processor"""
        self.logger = logger
        self.spell_checker = SpellChecker()

        # Intent keywords mapping
        self.intent_keywords = {
            QueryIntent.TECHNICAL: [
                'error', 'bug', 'not working', 'broken', 'issue', 'problem',
                'crash', 'freeze', 'slow', 'performance', 'install', 'update',
                'configure', 'setup', 'technical', 'troubleshoot'
            ],
            QueryIntent.BILLING: [
                'payment', 'charge', 'bill', 'invoice', 'refund', 'credit',
                'card', 'subscription', 'cancel', 'price', 'cost', 'fee',
                'transaction', 'receipt', 'billing', 'paid'
            ],
            QueryIntent.PRODUCT: [
                'product', 'feature', 'specification', 'specs', 'detail',
                'information', 'availability', 'stock', 'compare', 'difference',
                'recommend', 'suggestion', 'compatible', 'works with'
            ],
            QueryIntent.SHIPPING: [
                'ship', 'shipping', 'delivery', 'tracking', 'track', 'arrived',
                'arrive', 'when', 'where', 'status', 'transit', 'carrier',
                'package', 'order status', 'estimated delivery'
            ],
            QueryIntent.RETURN: [
                'return', 'exchange', 'warranty', 'defective', 'damaged',
                'wrong item', 'send back', 'replacement', 'rma', 'policy'
            ],
            QueryIntent.ACCOUNT: [
                'account', 'login', 'password', 'reset', 'email', 'profile',
                'settings', 'update', 'change', 'delete', 'register', 'signup',
                'username', 'authentication', 'verify'
            ],
            QueryIntent.ESCALATION: [
                'speak', 'talk', 'human', 'agent', 'representative', 'person',
                'manager', 'supervisor', 'call', 'phone', 'urgent', 'help',
                'frustrated', 'angry', 'complaint'
            ]
        }

        # Escalation trigger phrases
        self.escalation_triggers = [
            'speak to a human',
            'talk to a person',
            'need help',
            'this is not working',
            'i want to speak',
            'transfer me',
            'real person',
            'live agent',
            'customer service',
        ]

    def classify_intent(self, query: str) -> Tuple[str, float]:
        """
        Classify the intent of a query.

        Args:
            query: User query

        Returns:
            Tuple of (intent, confidence)
        """
        try:
            query_lower = query.lower()

            # Check for escalation triggers first
            for trigger in self.escalation_triggers:
                if trigger in query_lower:
                    return QueryIntent.ESCALATION, 0.95

            # Count keyword matches for each intent
            intent_scores = {}

            for intent, keywords in self.intent_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in query_lower:
                        # Exact match
                        score += 1.0
                    elif any(word in keyword for word in query_lower.split()):
                        # Partial match
                        score += 0.5

                if score > 0:
                    intent_scores[intent] = score

            # Find intent with highest score
            if intent_scores:
                best_intent = max(intent_scores.items(), key=lambda x: x[1])
                intent = best_intent[0]

                # Calculate confidence (normalize by total possible matches)
                max_possible = len(self.intent_keywords[intent])
                confidence = min(best_intent[1] / max_possible, 1.0)

                # Boost confidence if score is high
                if best_intent[1] >= 2:
                    confidence = min(confidence * 1.5, 0.95)

                self.logger.debug(
                    f"Classified intent: {intent}",
                    intent=intent,
                    confidence=confidence,
                    score=best_intent[1]
                )

                return intent, confidence
            else:
                # No clear intent
                return QueryIntent.GENERAL, 0.5

        except Exception as e:
            self.logger.error(f"Intent classification failed: {e}", exc_info=True)
            return QueryIntent.GENERAL, 0.3

    def expand_query(self, query: str, intent: Optional[str] = None) -> List[str]:
        """
        Expand query with synonyms and related terms.

        Args:
            query: Original query
            intent: Query intent (optional)

        Returns:
            List of expanded query variations
        """
        expanded_queries = [query]

        try:
            query_lower = query.lower()

            # Common synonyms for customer support queries
            synonyms = {
                'order': ['purchase', 'item', 'product'],
                'return': ['send back', 'refund', 'exchange'],
                'track': ['tracking', 'status', 'where is'],
                'cancel': ['stop', 'discontinue', 'end'],
                'change': ['update', 'modify', 'edit'],
                'help': ['assist', 'support', 'guide'],
                'problem': ['issue', 'trouble', 'error'],
                'buy': ['purchase', 'order', 'get'],
            }

            # Add synonym variations
            for word, synonym_list in synonyms.items():
                if word in query_lower:
                    for synonym in synonym_list:
                        expanded_query = query_lower.replace(word, synonym)
                        if expanded_query not in expanded_queries:
                            expanded_queries.append(expanded_query)

            # Limit to top 3 variations
            expanded_queries = expanded_queries[:3]

            if len(expanded_queries) > 1:
                self.logger.debug(
                    f"Expanded query to {len(expanded_queries)} variations",
                    original=query,
                    variations=len(expanded_queries)
                )

            return expanded_queries

        except Exception as e:
            self.logger.error(f"Query expansion failed: {e}", exc_info=True)
            return [query]

    def normalize_query(self, query: str) -> str:
        """
        Normalize query text.

        Args:
            query: Original query

        Returns:
            Normalized query
        """
        try:
            # Remove extra whitespace
            normalized = ' '.join(query.split())

            # Remove special characters (keep basic punctuation)
            normalized = re.sub(r'[^\w\s.,!?\'-]', '', normalized)

            # Fix common misspellings (simple implementation)
            words = normalized.split()
            corrected_words = []

            for word in words:
                # Skip short words and capitalized words (might be proper nouns)
                if len(word) > 3 and word.islower():
                    # Check if word is misspelled
                    if word not in self.spell_checker:
                        # Get correction
                        correction = self.spell_checker.correction(word)
                        if correction and correction != word:
                            self.logger.debug(
                                f"Corrected spelling: {word} -> {correction}"
                            )
                            corrected_words.append(correction)
                        else:
                            corrected_words.append(word)
                    else:
                        corrected_words.append(word)
                else:
                    corrected_words.append(word)

            normalized = ' '.join(corrected_words)

            # Trim to reasonable length
            if len(normalized) > 500:
                normalized = normalized[:500]

            return normalized

        except Exception as e:
            self.logger.error(f"Query normalization failed: {e}", exc_info=True)
            return query

    def detect_language(self, query: str) -> Tuple[str, float]:
        """
        Detect the language of the query.

        Args:
            query: Query text

        Returns:
            Tuple of (language_code, confidence)
        """
        try:
            # Detect language
            lang = detect(query)
            confidence = 0.9  # langdetect doesn't provide confidence directly

            self.logger.debug(
                f"Detected language: {lang}",
                language=lang
            )

            return lang, confidence

        except LangDetectException as e:
            self.logger.warning(f"Language detection failed: {e}")
            return 'en', 0.5  # Default to English
        except Exception as e:
            self.logger.error(f"Language detection error: {e}", exc_info=True)
            return 'en', 0.5

    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """
        Extract entities from query (simplified implementation).

        Args:
            query: Query text

        Returns:
            Dictionary of entity types and values
        """
        entities = {
            'order_number': [],
            'product_name': [],
            'email': [],
            'phone': [],
            'date': [],
        }

        try:
            # Extract order numbers (e.g., ORD-12345, #12345)
            order_pattern = r'(?:order|#|ord[-_]?)\s*(\d{4,})'
            order_matches = re.finditer(order_pattern, query, re.IGNORECASE)
            entities['order_number'] = [match.group(1) for match in order_matches]

            # Extract emails
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_matches = re.finditer(email_pattern, query)
            entities['email'] = [match.group(0) for match in email_matches]

            # Extract phone numbers (simplified)
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phone_matches = re.finditer(phone_pattern, query)
            entities['phone'] = [match.group(0) for match in phone_matches]

            # Extract dates (simplified)
            date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'
            date_matches = re.finditer(date_pattern, query)
            entities['date'] = [match.group(0) for match in date_matches]

            # Remove empty lists
            entities = {k: v for k, v in entities.items() if v}

            if entities:
                self.logger.debug(f"Extracted entities: {entities}")

            return entities

        except Exception as e:
            self.logger.error(f"Entity extraction failed: {e}", exc_info=True)
            return {}

    def detect_sentiment(self, query: str) -> str:
        """
        Detect sentiment of query (simplified rule-based).

        Args:
            query: Query text

        Returns:
            Sentiment (positive, negative, neutral)
        """
        try:
            query_lower = query.lower()

            # Negative sentiment indicators
            negative_words = [
                'angry', 'frustrated', 'terrible', 'awful', 'horrible',
                'worst', 'hate', 'disgusted', 'disappointed', 'useless',
                'broken', 'failed', 'never', 'always', 'unacceptable'
            ]

            # Positive sentiment indicators
            positive_words = [
                'thank', 'thanks', 'great', 'excellent', 'love', 'perfect',
                'amazing', 'wonderful', 'helpful', 'appreciate', 'awesome'
            ]

            # Count indicators
            negative_count = sum(1 for word in negative_words if word in query_lower)
            positive_count = sum(1 for word in positive_words if word in query_lower)

            # Check for exclamation marks (can indicate strong emotion)
            exclamation_count = query.count('!')

            if negative_count > positive_count or exclamation_count > 2:
                sentiment = 'negative'
            elif positive_count > negative_count:
                sentiment = 'positive'
            else:
                sentiment = 'neutral'

            self.logger.debug(
                f"Detected sentiment: {sentiment}",
                sentiment=sentiment,
                negative_count=negative_count,
                positive_count=positive_count
            )

            return sentiment

        except Exception as e:
            self.logger.error(f"Sentiment detection failed: {e}", exc_info=True)
            return 'neutral'

    def process_query(
        self,
        query: str,
        normalize: bool = True,
        expand: bool = False,
        detect_lang: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrate full query processing pipeline.

        Args:
            query: User query
            normalize: Whether to normalize the query
            expand: Whether to expand the query
            detect_lang: Whether to detect language

        Returns:
            Dictionary with processed query and metadata
        """
        try:
            # Normalize query
            if normalize:
                normalized_query = self.normalize_query(query)
            else:
                normalized_query = query

            # Classify intent
            intent, intent_confidence = self.classify_intent(normalized_query)

            # Expand query
            if expand:
                query_variations = self.expand_query(normalized_query, intent)
            else:
                query_variations = [normalized_query]

            # Detect language
            if detect_lang:
                language, lang_confidence = self.detect_language(normalized_query)
            else:
                language, lang_confidence = 'en', 1.0

            # Extract entities
            entities = self.extract_entities(normalized_query)

            # Detect sentiment
            sentiment = self.detect_sentiment(normalized_query)

            # Determine if escalation is needed
            should_escalate = intent == QueryIntent.ESCALATION or sentiment == 'negative'

            result = {
                'original_query': query,
                'normalized_query': normalized_query,
                'query_variations': query_variations,
                'intent': intent,
                'intent_confidence': intent_confidence,
                'language': language,
                'language_confidence': lang_confidence,
                'entities': entities,
                'sentiment': sentiment,
                'should_escalate': should_escalate,
            }

            self.logger.info(
                "Query processed",
                intent=intent,
                sentiment=sentiment,
                language=language,
                num_entities=len(entities)
            )

            return result

        except Exception as e:
            self.logger.error(f"Query processing failed: {e}", exc_info=True)
            return {
                'original_query': query,
                'normalized_query': query,
                'query_variations': [query],
                'intent': QueryIntent.GENERAL,
                'intent_confidence': 0.3,
                'language': 'en',
                'language_confidence': 0.5,
                'entities': {},
                'sentiment': 'neutral',
                'should_escalate': False,
            }

    def is_question(self, query: str) -> bool:
        """
        Check if query is a question.

        Args:
            query: Query text

        Returns:
            True if query is a question
        """
        query_lower = query.lower().strip()

        # Check for question mark
        if query.endswith('?'):
            return True

        # Check for question words at start
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'can', 'could',
                          'would', 'should', 'is', 'are', 'do', 'does', 'will']

        first_word = query_lower.split()[0] if query_lower.split() else ''

        return first_word in question_words
