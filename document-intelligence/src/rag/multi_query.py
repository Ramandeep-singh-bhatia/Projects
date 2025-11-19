"""
Multi-query retrieval for RAG.
Generates multiple query variations to improve retrieval coverage.
"""

from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.search.hybrid_search import hybrid_search, SearchResult
from config.settings import settings
from src.utils.logger import app_logger as logger


class MultiQueryRetriever:
    """Multi-query retrieval strategy."""

    def __init__(self, num_queries: int = None):
        """
        Initialize multi-query retriever.

        Args:
            num_queries: Number of query variations to generate
        """
        self.num_queries = num_queries or settings.multi_query_num_queries
        self.llm = ChatOpenAI(
            model=settings.openai_cheap_model,  # Use cheaper model for query generation
            temperature=0.7,
            api_key=settings.openai_api_key
        )

    def generate_queries(self, original_query: str) -> List[str]:
        """
        Generate multiple query variations.

        Args:
            original_query: Original user query

        Returns:
            List of query variations (including original)
        """
        logger.info(f"Generating {self.num_queries} query variations for: '{original_query[:50]}...'")

        try:
            # Create prompt for query generation
            prompt = ChatPromptTemplate.from_template(
                """You are an AI assistant helping to improve search results.
Given an original query, generate {num_queries} different variations of the query that capture different aspects or perspectives of the question.

The variations should:
1. Use different wording while maintaining the core intent
2. Focus on different aspects of the question
3. Include related terms and synonyms
4. Be suitable for semantic search

Original query: {query}

Generate exactly {num_queries} query variations, one per line. Do not number them."""
            )

            # Generate variations
            response = self.llm.invoke(
                prompt.format_messages(
                    query=original_query,
                    num_queries=self.num_queries - 1  # Subtract 1 because we'll include original
                )
            )

            # Parse response
            variations = [line.strip() for line in response.content.strip().split('\n') if line.strip()]

            # Add original query
            queries = [original_query] + variations[:self.num_queries - 1]

            logger.info(f"Generated {len(queries)} query variations")
            return queries

        except Exception as e:
            logger.error(f"Failed to generate query variations: {str(e)}")
            # Return original query as fallback
            return [original_query]

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        deduplicate: bool = True
    ) -> List[SearchResult]:
        """
        Retrieve documents using multiple query variations.

        Args:
            query: Original query
            top_k: Number of results to return
            deduplicate: Remove duplicate results

        Returns:
            Combined search results
        """
        logger.info(f"Multi-query retrieval for: '{query[:50]}...'")

        try:
            # Generate query variations
            queries = self.generate_queries(query)

            # Retrieve results for each query
            all_results = []
            seen_ids = set()

            for q in queries:
                results = hybrid_search.search(query=q, top_k=top_k)

                for result in results:
                    if deduplicate:
                        if result.id not in seen_ids:
                            all_results.append(result)
                            seen_ids.add(result.id)
                    else:
                        all_results.append(result)

            # Sort by score and return top-k
            all_results.sort(key=lambda x: x.score, reverse=True)
            final_results = all_results[:top_k]

            logger.info(f"Multi-query retrieval returned {len(final_results)} results")
            return final_results

        except Exception as e:
            logger.error(f"Multi-query retrieval failed: {str(e)}")
            # Fallback to regular search
            return hybrid_search.search(query=query, top_k=top_k)


# Global multi-query retriever instance
multi_query_retriever = MultiQueryRetriever()
