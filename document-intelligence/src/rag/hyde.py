"""
HyDE (Hypothetical Document Embeddings) for RAG.
Generates a hypothetical answer and uses it for retrieval.
"""

from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.search.vector_search import vector_search, SearchResult
from src.core.embeddings import embedding_service
from config.settings import settings
from src.utils.logger import app_logger as logger


class HyDERetriever:
    """HyDE retrieval strategy."""

    def __init__(self):
        """Initialize HyDE retriever."""
        self.llm = ChatOpenAI(
            model=settings.openai_chat_model,
            temperature=0.7,
            api_key=settings.openai_api_key
        )
        self.embedding_service = embedding_service

    def generate_hypothetical_document(self, query: str) -> str:
        """
        Generate a hypothetical answer to the query.

        Args:
            query: User query

        Returns:
            Hypothetical document/answer
        """
        logger.info(f"Generating hypothetical document for: '{query[:50]}...'")

        try:
            # Create prompt for hypothetical document generation
            prompt = ChatPromptTemplate.from_template(
                """You are an AI assistant tasked with generating a hypothetical document that would answer the given question.

Write a detailed, informative passage that would likely answer this question. The passage should:
1. Be factual and comprehensive
2. Include relevant details and context
3. Use terminology and language that would appear in actual documents
4. Be 2-3 paragraphs long

Question: {query}

Write the hypothetical document:"""
            )

            # Generate hypothetical document
            response = self.llm.invoke(
                prompt.format_messages(query=query)
            )

            hypothetical_doc = response.content.strip()

            logger.info(f"Generated hypothetical document ({len(hypothetical_doc)} chars)")
            return hypothetical_doc

        except Exception as e:
            logger.error(f"Failed to generate hypothetical document: {str(e)}")
            # Fallback to original query
            return query

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        use_both: bool = True
    ) -> List[SearchResult]:
        """
        Retrieve documents using HyDE.

        Args:
            query: Original query
            top_k: Number of results to return
            use_both: Combine results from both query and hypothetical doc

        Returns:
            Search results
        """
        logger.info(f"HyDE retrieval for: '{query[:50]}...'")

        try:
            # Generate hypothetical document
            hypothetical_doc = self.generate_hypothetical_document(query)

            # Search using hypothetical document
            hyde_results = vector_search.search(
                query=hypothetical_doc,
                top_k=top_k * 2 if use_both else top_k
            )

            if use_both:
                # Also search with original query
                query_results = vector_search.search(
                    query=query,
                    top_k=top_k
                )

                # Combine and deduplicate
                all_results = []
                seen_ids = set()

                for result in hyde_results + query_results:
                    if result.id not in seen_ids:
                        all_results.append(result)
                        seen_ids.add(result.id)

                # Sort by score and return top-k
                all_results.sort(key=lambda x: x.score, reverse=True)
                final_results = all_results[:top_k]

                logger.info(f"HyDE retrieval (combined) returned {len(final_results)} results")
                return final_results

            else:
                logger.info(f"HyDE retrieval returned {len(hyde_results[:top_k])} results")
                return hyde_results[:top_k]

        except Exception as e:
            logger.error(f"HyDE retrieval failed: {str(e)}")
            # Fallback to regular vector search
            return vector_search.search(query=query, top_k=top_k)


# Global HyDE retriever instance
hyde_retriever = HyDERetriever()
