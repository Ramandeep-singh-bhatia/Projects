"""
Web search tools for research agents.
Supports multiple search providers: Serper, Tavily, and Brave Search.
"""

import os
import json
from typing import List, Dict, Any, Optional
import aiohttp
from loguru import logger

from backend.config import settings


class WebSearchTool:
    """Web search tool using multiple providers."""

    def __init__(self, provider: str = "serper"):
        """
        Initialize web search tool.

        Args:
            provider: Search provider ('serper', 'tavily', or 'brave')
        """
        self.provider = provider
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> str:
        """Get API key for the selected provider."""
        if self.provider == "serper":
            return settings.serper_api_key or ""
        elif self.provider == "tavily":
            return settings.tavily_api_key or ""
        elif self.provider == "brave":
            return settings.brave_search_api_key or ""
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    async def search(
        self,
        query: str,
        num_results: int = 10,
        search_type: str = "web",
    ) -> List[Dict[str, Any]]:
        """
        Perform web search.

        Args:
            query: Search query
            num_results: Number of results to return
            search_type: Type of search ('web', 'news', 'images')

        Returns:
            List of search results
        """
        if self.provider == "serper":
            return await self._search_serper(query, num_results, search_type)
        elif self.provider == "tavily":
            return await self._search_tavily(query, num_results)
        elif self.provider == "brave":
            return await self._search_brave(query, num_results)
        else:
            logger.error(f"Unknown provider: {self.provider}")
            return []

    async def _search_serper(
        self,
        query: str,
        num_results: int,
        search_type: str,
    ) -> List[Dict[str, Any]]:
        """Search using Serper API."""
        if not self.api_key:
            logger.warning("Serper API key not configured")
            return []

        url = "https://google.serper.dev/search"

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "q": query,
            "num": num_results,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_serper_results(data)
                    else:
                        logger.error(
                            f"Serper API error: {response.status}"
                        )
                        return []
        except Exception as e:
            logger.error(f"Error in Serper search: {e}")
            return []

    def _parse_serper_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Serper API results."""
        results = []

        # Parse organic results
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "date": item.get("date", ""),
            })

        return results

    async def _search_tavily(
        self,
        query: str,
        num_results: int,
    ) -> List[Dict[str, Any]]:
        """Search using Tavily AI API."""
        if not self.api_key:
            logger.warning("Tavily API key not configured")
            return []

        url = "https://api.tavily.com/search"

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": num_results,
            "search_depth": "advanced",
            "include_answer": True,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_tavily_results(data)
                    else:
                        logger.error(f"Tavily API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error in Tavily search: {e}")
            return []

    def _parse_tavily_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Tavily API results."""
        results = []

        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("url", ""),
                "snippet": item.get("content", ""),
                "score": item.get("score", 0),
            })

        return results

    async def _search_brave(
        self,
        query: str,
        num_results: int,
    ) -> List[Dict[str, Any]]:
        """Search using Brave Search API."""
        if not self.api_key:
            logger.warning("Brave API key not configured")
            return []

        url = "https://api.search.brave.com/res/v1/web/search"

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key,
        }

        params = {
            "q": query,
            "count": num_results,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_brave_results(data)
                    else:
                        logger.error(f"Brave API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error in Brave search: {e}")
            return []

    def _parse_brave_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Brave Search API results."""
        results = []

        for item in data.get("web", {}).get("results", []):
            results.append({
                "title": item.get("title", ""),
                "link": item.get("url", ""),
                "snippet": item.get("description", ""),
            })

        return results


# Convenience function for LangChain tool integration
async def web_search(query: str, num_results: int = 10) -> str:
    """
    Search the web for information.

    Args:
        query: Search query
        num_results: Number of results to return

    Returns:
        JSON string of search results
    """
    tool = WebSearchTool(provider="serper")
    results = await tool.search(query, num_results)
    return json.dumps(results, indent=2)
