"""
Response generation and conversation management for RAG system.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import time
import uuid

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from tenacity import retry, stop_after_attempt, wait_exponential

from .retriever import HybridRetriever, RetrievedDocument
from ..database import crud
from ..database.db import MessageRole
from ..utils.config import get_settings, calculate_cost
from ..utils.logger import get_logger, PerformanceLogger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


class ResponseGenerator:
    """Generator for AI responses using Claude/GPT"""

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize response generator.

        Args:
            anthropic_api_key: Anthropic API key
            openai_api_key: OpenAI API key
        """
        self.settings = get_settings()
        self.logger = logger
        self.perf_logger = PerformanceLogger(logger)

        # Initialize LLMs
        api_key_anthropic = anthropic_api_key or self.settings.anthropic_api_key
        api_key_openai = openai_api_key or self.settings.openai_api_key

        try:
            self.primary_llm = ChatAnthropic(
                model=self.settings.llm_model,
                anthropic_api_key=api_key_anthropic,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )
            self.logger.info(f"Initialized primary LLM: {self.settings.llm_model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic LLM: {e}")
            self.primary_llm = None

        try:
            self.fallback_llm = ChatOpenAI(
                model=self.settings.fallback_llm_model,
                openai_api_key=api_key_openai,
                temperature=self.settings.llm_temperature,
                max_tokens=self.settings.llm_max_tokens,
            )
            self.logger.info(f"Initialized fallback LLM: {self.settings.fallback_llm_model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI LLM: {e}")
            self.fallback_llm = None

    def build_prompt(
        self,
        query: str,
        context: List[RetrievedDocument],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        intent: Optional[str] = None
    ) -> List[Any]:
        """
        Build prompt messages for LLM.

        Args:
            query: User query
            context: Retrieved context documents
            conversation_history: Previous conversation messages
            intent: Detected intent

        Returns:
            List of message objects
        """
        # System prompt
        system_prompt = """You are an expert customer support AI assistant. Your role is to help customers by answering their questions accurately based on the provided context from our knowledge base.

Guidelines:
1. ONLY use information from the provided context to answer questions
2. If the context doesn't contain enough information, say "I don't have enough information to answer that accurately. Let me connect you with a human agent."
3. Always cite your sources by mentioning which document the information came from
4. Be concise but thorough
5. Use a friendly, professional tone
6. If you detect frustration or complex issues, offer to escalate to a human agent
7. Never make up information or hallucinate facts
8. If you're uncertain about any part of your answer, acknowledge it

When citing sources, use this format: [Source: document_name]"""

        messages = [SystemMessage(content=system_prompt)]

        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-self.settings.max_conversation_history:]:
                if msg['role'] == 'user':
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == 'assistant':
                    messages.append(AIMessage(content=msg['content']))

        # Build context string
        if context:
            context_text = "Context from Knowledge Base:\n\n"
            for idx, doc in enumerate(context, 1):
                source_name = doc.metadata.get('filename', 'Unknown')
                doc_id = doc.metadata.get('document_id', 'N/A')
                context_text += f"[Document {idx} - {source_name}]:\n{doc.content}\n\n"

            context_text += f"\nCustomer Question: {query}\n\n"
            context_text += "Provide a helpful, accurate response with source citations."
        else:
            context_text = f"Customer Question: {query}\n\n"
            context_text += "No relevant context was found in the knowledge base. "
            context_text += "Politely inform the customer and offer to escalate to a human agent."

        # Add current query with context
        messages.append(HumanMessage(content=context_text))

        return messages

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _generate_with_retry(self, messages: List[Any], use_fallback: bool = False) -> Tuple[str, int, int]:
        """
        Generate response with retry logic.

        Args:
            messages: List of message objects
            use_fallback: Whether to use fallback LLM

        Returns:
            Tuple of (response_text, input_tokens, output_tokens)
        """
        llm = self.fallback_llm if use_fallback else self.primary_llm

        if llm is None:
            raise ValueError("No LLM available")

        response = llm.invoke(messages)

        # Extract token usage if available
        input_tokens = getattr(response, 'usage_metadata', {}).get('input_tokens', 0) if hasattr(response, 'usage_metadata') else 0
        output_tokens = getattr(response, 'usage_metadata', {}).get('output_tokens', 0) if hasattr(response, 'usage_metadata') else 0

        # Estimate if not available
        if input_tokens == 0:
            input_tokens = sum(len(msg.content.split()) for msg in messages) * 1.3
        if output_tokens == 0:
            output_tokens = len(response.content.split()) * 1.3

        return response.content, int(input_tokens), int(output_tokens)

    def generate_response(
        self,
        query: str,
        context: List[RetrievedDocument],
        conversation_history: Optional[List[Dict[str, str]]] = None,
        intent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response for query.

        Args:
            query: User query
            context: Retrieved context documents
            conversation_history: Previous messages
            intent: Detected intent

        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()

        try:
            # Build prompt
            messages = self.build_prompt(query, context, conversation_history, intent)

            # Try primary LLM first
            try:
                response_text, input_tokens, output_tokens = self._generate_with_retry(messages, use_fallback=False)
                model_used = self.settings.llm_model
            except Exception as e:
                self.logger.warning(f"Primary LLM failed, using fallback: {e}")
                if self.fallback_llm:
                    response_text, input_tokens, output_tokens = self._generate_with_retry(messages, use_fallback=True)
                    model_used = self.settings.fallback_llm_model
                else:
                    raise

            # Calculate confidence
            confidence_score = self.calculate_confidence(response_text, context, query)

            # Format response with sources
            formatted_response = self.format_response(response_text, context)

            # Calculate cost
            cost = calculate_cost(model_used, input_tokens, output_tokens)

            # Determine if escalation is needed
            should_escalate = self.should_escalate(query, response_text, confidence_score)

            # Generate suggested questions
            suggested_questions = self.generate_suggested_questions(query, context)

            duration_ms = (time.time() - start_time) * 1000

            # Log performance
            self.perf_logger.log_token_usage(
                operation="generate_response",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                model=model_used,
                duration_ms=duration_ms
            )

            result = {
                'response': formatted_response,
                'confidence_score': confidence_score,
                'should_escalate': should_escalate,
                'suggested_questions': suggested_questions,
                'sources': [doc.to_dict() for doc in context],
                'model_used': model_used,
                'tokens_used': input_tokens + output_tokens,
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'cost': cost,
                'processing_time_ms': duration_ms,
            }

            self.logger.info(
                "Response generated successfully",
                confidence=confidence_score,
                should_escalate=should_escalate,
                model=model_used,
                tokens=input_tokens + output_tokens
            )

            return result

        except Exception as e:
            self.logger.error(f"Response generation failed: {e}", exc_info=True)

            # Return fallback response
            return {
                'response': "I apologize, but I'm having trouble processing your request right now. Please let me connect you with a human agent who can help you.",
                'confidence_score': 0.0,
                'should_escalate': True,
                'suggested_questions': [],
                'sources': [],
                'model_used': 'none',
                'tokens_used': 0,
                'input_tokens': 0,
                'output_tokens': 0,
                'cost': 0.0,
                'processing_time_ms': (time.time() - start_time) * 1000,
                'error': str(e)
            }

    def calculate_confidence(
        self,
        response: str,
        retrieved_docs: List[RetrievedDocument],
        query: str
    ) -> float:
        """
        Calculate confidence score for response.

        Args:
            response: Generated response
            retrieved_docs: Retrieved documents used
            query: Original query

        Returns:
            Confidence score (0-1)
        """
        score = 0.0

        try:
            # Factor 1: Semantic similarity of top retrieved doc (0-0.4)
            if retrieved_docs:
                top_similarity = retrieved_docs[0].score
                score += min(top_similarity * 0.4, 0.4)

            # Factor 2: Number of relevant docs (0-0.3)
            relevant_docs = [d for d in retrieved_docs if d.score > 0.75]
            score += min(len(relevant_docs) * 0.1, 0.3)

            # Factor 3: Response length appropriateness (0-0.2)
            response_length = len(response)
            if 50 < response_length < 500:
                score += 0.2
            elif 500 <= response_length < 1000:
                score += 0.15
            else:
                score += 0.05

            # Factor 4: Citation presence (0-0.1)
            if "source:" in response.lower() or "[source" in response.lower():
                score += 0.1

            # Normalize to 0-1
            score = min(max(score, 0.0), 1.0)

            return round(score, 3)

        except Exception as e:
            self.logger.error(f"Confidence calculation failed: {e}")
            return 0.5

    def format_response(
        self,
        response: str,
        sources: List[RetrievedDocument]
    ) -> str:
        """
        Format response with source citations.

        Args:
            response: Generated response
            sources: Source documents

        Returns:
            Formatted response
        """
        # Response is already formatted by the LLM with citations
        # We could add additional formatting here if needed
        return response

    def should_escalate(
        self,
        query: str,
        response: str,
        confidence: float
    ) -> bool:
        """
        Determine if query should be escalated to human agent.

        Args:
            query: User query
            response: Generated response
            confidence: Confidence score

        Returns:
            True if escalation recommended
        """
        # Check confidence threshold
        if confidence < self.settings.escalation_confidence_threshold:
            return True

        # Check for explicit escalation language in response
        escalation_phrases = [
            "connect you with a human",
            "transfer to an agent",
            "speak with a representative",
            "don't have enough information"
        ]

        response_lower = response.lower()
        if any(phrase in response_lower for phrase in escalation_phrases):
            return True

        return False

    def generate_suggested_questions(
        self,
        query: str,
        context: List[RetrievedDocument]
    ) -> List[str]:
        """
        Generate suggested follow-up questions.

        Args:
            query: Current query
            context: Retrieved context

        Returns:
            List of suggested questions
        """
        # Simple rule-based suggestions
        suggestions = []

        query_lower = query.lower()

        # Topic-based suggestions
        if 'shipping' in query_lower or 'delivery' in query_lower:
            suggestions.extend([
                "How can I track my order?",
                "What are your shipping rates?",
                "Do you offer expedited shipping?"
            ])
        elif 'return' in query_lower or 'refund' in query_lower:
            suggestions.extend([
                "What is your return policy?",
                "How do I initiate a return?",
                "How long does a refund take?"
            ])
        elif 'product' in query_lower or 'item' in query_lower:
            suggestions.extend([
                "What are the product specifications?",
                "Is this item in stock?",
                "Do you have similar products?"
            ])
        else:
            suggestions.extend([
                "How can I contact customer support?",
                "What are your business hours?",
                "Do you have a warranty policy?"
            ])

        return suggestions[:3]  # Return top 3


class ConversationManager:
    """Manager for conversation state and history"""

    def __init__(
        self,
        db: Session,
        retriever: Optional[HybridRetriever] = None,
        response_generator: Optional[ResponseGenerator] = None
    ):
        """
        Initialize conversation manager.

        Args:
            db: Database session
            retriever: HybridRetriever instance
            response_generator: ResponseGenerator instance
        """
        self.settings = get_settings()
        self.logger = logger
        self.db = db

        self.retriever = retriever or HybridRetriever()
        self.response_generator = response_generator or ResponseGenerator()

    def create_session(self, user_id: Optional[str] = None) -> str:
        """
        Create a new conversation session.

        Args:
            user_id: Optional user ID

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        try:
            # Create conversation in database
            crud.create_conversation(
                self.db,
                session_id=session_id,
                user_id=user_id
            )

            self.logger.info(f"Created new conversation session: {session_id}")

            return session_id

        except Exception as e:
            self.logger.error(f"Failed to create session: {e}", exc_info=True)
            raise

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        confidence_score: Optional[float] = None,
        sources_used: Optional[List[Dict[str, Any]]] = None
    ) -> int:
        """
        Add message to conversation.

        Args:
            session_id: Session ID
            role: Message role (user/assistant)
            content: Message content
            confidence_score: Confidence score for assistant messages
            sources_used: Sources used for assistant messages

        Returns:
            Message ID
        """
        try:
            # Get or create conversation
            conversation = crud.get_or_create_conversation(self.db, session_id)

            # Add message
            message = crud.create_message(
                self.db,
                conversation_id=conversation.id,
                role=MessageRole(role),
                content=content,
                confidence_score=confidence_score,
                sources_used=sources_used or []
            )

            return message.id

        except Exception as e:
            self.logger.error(f"Failed to add message: {e}", exc_info=True)
            raise

    def get_history(
        self,
        session_id: str,
        last_n: int = 5
    ) -> List[Dict[str, str]]:
        """
        Get conversation history.

        Args:
            session_id: Session ID
            last_n: Number of recent messages to retrieve

        Returns:
            List of messages
        """
        try:
            conversation = crud.get_conversation_by_session_id(self.db, session_id)

            if not conversation:
                return []

            messages = crud.get_recent_messages(self.db, conversation.id, last_n)

            history = []
            for msg in messages:
                history.append({
                    'role': msg.role.value,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                })

            return history

        except Exception as e:
            self.logger.error(f"Failed to get history: {e}", exc_info=True)
            return []

    def detect_handoff_intent(self, query: str) -> bool:
        """
        Detect if user wants to speak with human agent.

        Args:
            query: User query

        Returns:
            True if handoff requested
        """
        handoff_keywords = [
            'speak to human', 'talk to person', 'human agent',
            'real person', 'customer service', 'representative',
            'agent', 'operator', 'manager', 'supervisor'
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in handoff_keywords)

    def process_message(
        self,
        session_id: str,
        query: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response.

        Args:
            session_id: Session ID
            query: User query
            user_id: Optional user ID

        Returns:
            Dictionary with response and metadata
        """
        start_time = time.time()

        try:
            # Get conversation history
            history = self.get_history(session_id, last_n=self.settings.max_conversation_history)

            # Add user message
            self.add_message(session_id, 'user', query)

            # Check for handoff intent
            if self.detect_handoff_intent(query):
                response_text = "I'd be happy to connect you with one of our customer service representatives. Please hold while I transfer you."
                result = {
                    'response': response_text,
                    'confidence_score': 1.0,
                    'should_escalate': True,
                    'suggested_questions': [],
                    'sources': [],
                    'processing_time_ms': (time.time() - start_time) * 1000
                }

                # Add assistant message
                self.add_message(session_id, 'assistant', response_text, confidence_score=1.0)

                return result

            # Retrieve relevant context
            retrieved_docs = self.retriever.retrieve(query, k=self.settings.top_k_retrieval)

            # Generate response
            response_data = self.response_generator.generate_response(
                query=query,
                context=retrieved_docs,
                conversation_history=history
            )

            # Add assistant message
            self.add_message(
                session_id,
                'assistant',
                response_data['response'],
                confidence_score=response_data['confidence_score'],
                sources_used=response_data.get('sources', [])
            )

            # Track analytics if enabled
            if self.settings.enable_analytics:
                crud.create_analytics_record(
                    self.db,
                    session_id=session_id,
                    query=query,
                    response=response_data['response'],
                    confidence_score=response_data['confidence_score'],
                    resolution_time=response_data['processing_time_ms'] / 1000,
                    sources_used=response_data.get('sources', []),
                    was_escalated=response_data['should_escalate'],
                    tokens_used=response_data.get('tokens_used', 0),
                    cost=response_data.get('cost', 0.0)
                )

            return response_data

        except Exception as e:
            self.logger.error(f"Message processing failed: {e}", exc_info=True)

            error_response = {
                'response': "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team directly.",
                'confidence_score': 0.0,
                'should_escalate': True,
                'suggested_questions': [],
                'sources': [],
                'processing_time_ms': (time.time() - start_time) * 1000,
                'error': str(e)
            }

            return error_response
