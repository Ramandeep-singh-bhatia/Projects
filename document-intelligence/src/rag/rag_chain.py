"""
RAG chain orchestration.
Combines retrieval and generation for question answering.
"""

from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from src.search.hybrid_search import hybrid_search, SearchResult
from src.rag.multi_query import multi_query_retriever
from src.rag.hyde import hyde_retriever
from config.settings import settings
from src.utils.logger import app_logger as logger
import time


class RAGChain:
    """RAG chain for question answering."""

    def __init__(self):
        """Initialize RAG chain."""
        self.llm = ChatOpenAI(
            model=settings.openai_chat_model,
            temperature=0.7,
            api_key=settings.openai_api_key
        )

    def query(
        self,
        question: str,
        retrieval_strategy: str = "hybrid",
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Answer a question using RAG.

        Args:
            question: User question
            retrieval_strategy: Strategy to use (hybrid, multi_query, hyde, vector)
            top_k: Number of documents to retrieve
            filter: Metadata filter

        Returns:
            Dict with answer, sources, and metadata
        """
        start_time = time.time()
        logger.info(f"RAG query: '{question[:50]}...', strategy={retrieval_strategy}")

        try:
            # Retrieve relevant documents
            if retrieval_strategy == "multi_query":
                results = multi_query_retriever.retrieve(question, top_k=top_k)
            elif retrieval_strategy == "hyde":
                results = hyde_retriever.retrieve(question, top_k=top_k)
            elif retrieval_strategy == "vector":
                from src.search.vector_search import vector_search
                results = vector_search.search(question, top_k=top_k, filter=filter)
            else:  # hybrid (default)
                results = hybrid_search.search(question, top_k=top_k, filter=filter)

            if not results:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0,
                    "retrieval_strategy": retrieval_strategy,
                    "num_sources": 0,
                    "execution_time": time.time() - start_time
                }

            # Generate answer
            answer = self._generate_answer(question, results)

            # Prepare sources
            sources = self._format_sources(results)

            execution_time = time.time() - start_time

            logger.info(f"RAG query completed in {execution_time:.2f}s")

            return {
                "answer": answer,
                "sources": sources,
                "confidence": self._calculate_confidence(results),
                "retrieval_strategy": retrieval_strategy,
                "num_sources": len(sources),
                "execution_time": execution_time
            }

        except Exception as e:
            logger.error(f"RAG query failed: {str(e)}")
            raise

    def _generate_answer(
        self,
        question: str,
        results: List[SearchResult]
    ) -> str:
        """
        Generate an answer using retrieved context.

        Args:
            question: User question
            results: Retrieved search results

        Returns:
            Generated answer
        """
        # Prepare context from results
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Source {i}]\n{result.content}\n"
            )

        context = "\n".join(context_parts)

        # Truncate context if too long
        max_context_length = settings.max_context_length
        if len(context) > max_context_length:
            context = context[:max_context_length] + "\n...[truncated]"

        # Create prompt
        prompt = ChatPromptTemplate.from_template(
            """You are a helpful AI assistant answering questions based on the provided context.

Context:
{context}

Question: {question}

Instructions:
1. Answer the question based on the information in the context
2. Be specific and cite relevant details from the sources
3. If the context doesn't contain enough information, acknowledge this
4. Use a clear, professional tone
5. Organize your answer with bullet points or paragraphs as appropriate

Answer:"""
        )

        # Generate answer
        response = self.llm.invoke(
            prompt.format_messages(
                context=context,
                question=question
            )
        )

        return response.content.strip()

    def _format_sources(
        self,
        results: List[SearchResult]
    ) -> List[Dict[str, Any]]:
        """Format search results as sources."""
        sources = []

        for i, result in enumerate(results, 1):
            source = {
                "number": i,
                "content": result.content[:500] + "..." if len(result.content) > 500 else result.content,
                "score": result.score,
                "document_id": result.document_id,
                "metadata": result.metadata
            }
            sources.append(source)

        return sources

    def _calculate_confidence(
        self,
        results: List[SearchResult]
    ) -> float:
        """
        Calculate confidence score based on retrieval results.

        Args:
            results: Search results

        Returns:
            Confidence score (0-1)
        """
        if not results:
            return 0.0

        # Use average of top 3 scores
        top_scores = [r.score for r in results[:3]]
        avg_score = sum(top_scores) / len(top_scores)

        # Normalize to 0-1 range
        confidence = min(avg_score, 1.0)

        return confidence

    def multi_hop_query(
        self,
        question: str,
        max_hops: int = 3
    ) -> Dict[str, Any]:
        """
        Answer complex questions using multi-hop reasoning.

        Args:
            question: Complex question
            max_hops: Maximum number of reasoning hops

        Returns:
            Dict with answer and reasoning chain
        """
        logger.info(f"Multi-hop query: '{question[:50]}...', max_hops={max_hops}")

        try:
            # Decompose question into sub-questions
            sub_questions = self._decompose_question(question)

            # Answer each sub-question
            intermediate_answers = []
            for sub_q in sub_questions[:max_hops]:
                result = self.query(sub_q, top_k=3)
                intermediate_answers.append({
                    "question": sub_q,
                    "answer": result["answer"]
                })

            # Generate final answer using all intermediate results
            final_answer = self._synthesize_multi_hop_answer(
                question,
                intermediate_answers
            )

            return {
                "answer": final_answer,
                "reasoning_chain": intermediate_answers,
                "num_hops": len(intermediate_answers)
            }

        except Exception as e:
            logger.error(f"Multi-hop query failed: {str(e)}")
            # Fallback to single-hop
            return self.query(question)

    def _decompose_question(self, question: str) -> List[str]:
        """Decompose complex question into sub-questions."""
        prompt = ChatPromptTemplate.from_template(
            """Break down this complex question into 2-3 simpler sub-questions that need to be answered to fully address the main question.

Main question: {question}

Provide the sub-questions, one per line:"""
        )

        response = self.llm.invoke(
            prompt.format_messages(question=question)
        )

        sub_questions = [
            line.strip()
            for line in response.content.strip().split('\n')
            if line.strip()
        ]

        return sub_questions

    def _synthesize_multi_hop_answer(
        self,
        question: str,
        intermediate_answers: List[Dict[str, str]]
    ) -> str:
        """Synthesize final answer from intermediate results."""
        # Prepare intermediate context
        context = "\n\n".join([
            f"Q: {item['question']}\nA: {item['answer']}"
            for item in intermediate_answers
        ])

        prompt = ChatPromptTemplate.from_template(
            """Based on the following intermediate answers, provide a comprehensive answer to the main question.

Intermediate Q&A:
{context}

Main question: {question}

Provide a synthesized answer:"""
        )

        response = self.llm.invoke(
            prompt.format_messages(
                context=context,
                question=question
            )
        )

        return response.content.strip()


# Global RAG chain instance
rag_chain = RAGChain()
