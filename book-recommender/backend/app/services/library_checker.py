"""
Sno-Isle Libraries availability checker.
"""
import httpx
import asyncio
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup
import re


class LibraryChecker:
    """Check book availability at Sno-Isle Libraries."""

    SNOISLE_SEARCH_URL = "https://sno-isle.bibliocommons.com/v2/search"
    SNOISLE_CATALOG_URL = "https://sno-isle.bibliocommons.com"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def check_availability(
        self,
        title: str,
        author: Optional[str] = None,
        isbn: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if a book is available at Sno-Isle Libraries.

        Args:
            title: Book title
            author: Optional author name
            isbn: Optional ISBN

        Returns:
            Dictionary with availability information
        """
        try:
            # Build search query
            if isbn:
                query = f"isbn:{isbn}"
            else:
                query = f'title:"{title}"'
                if author:
                    query += f' author:"{author}"'

            # Search the catalog
            search_url = f"{self.SNOISLE_SEARCH_URL}?query={query}&searchType=smart"

            response = await self.client.get(
                search_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                },
                follow_redirects=True
            )

            if response.status_code != 200:
                return self._unavailable_result()

            # Parse the response
            html = response.text
            availability = self._parse_availability(html)

            return availability

        except Exception as e:
            print(f"Error checking Sno-Isle availability: {e}")
            return self._unavailable_result()

    def _parse_availability(self, html: str) -> Dict[str, Any]:
        """
        Parse availability from catalog HTML.

        Args:
            html: HTML response from catalog

        Returns:
            Availability information
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Look for search results
            results = soup.find_all('div', class_=re.compile(r'cp-bib-list-item|result'))

            if not results:
                return self._unavailable_result()

            # Get the first result (most relevant)
            first_result = results[0]

            # Check for format availability
            formats_available = []

            # Look for format badges/indicators
            format_elements = first_result.find_all(['span', 'div'], class_=re.compile(r'format|badge'))

            for elem in format_elements:
                text = elem.get_text(strip=True).lower()

                if 'ebook' in text or 'pdf' in text or 'epub' in text:
                    formats_available.append('Digital/PDF')
                elif 'book' in text or 'print' in text or 'hardcover' in text or 'paperback' in text:
                    formats_available.append('Physical')
                elif 'audiobook' in text or 'audio' in text:
                    formats_available.append('Audiobook')

            # Check availability status
            status_elem = first_result.find(['span', 'div'], class_=re.compile(r'availability|status'))
            is_available = False

            if status_elem:
                status_text = status_elem.get_text(strip=True).lower()
                is_available = 'available' in status_text or 'on shelf' in status_text

            # Get link to the item
            link_elem = first_result.find('a', href=re.compile(r'/item/'))
            item_url = None

            if link_elem:
                item_url = self.SNOISLE_CATALOG_URL + link_elem.get('href')

            # Deduplicate formats
            formats_available = list(set(formats_available))

            if not formats_available:
                # Default assumption if we found a result but no specific formats
                formats_available = ['Physical']

            return {
                "available": True,
                "is_available_now": is_available,
                "formats": formats_available,
                "catalog_url": item_url,
                "library_system": "Sno-Isle Libraries"
            }

        except Exception as e:
            print(f"Error parsing availability HTML: {e}")
            return self._unavailable_result()

    def _unavailable_result(self) -> Dict[str, Any]:
        """Return structure for unavailable book."""
        return {
            "available": False,
            "is_available_now": False,
            "formats": [],
            "catalog_url": None,
            "library_system": "Sno-Isle Libraries"
        }

    async def get_catalog_link(
        self,
        title: str,
        author: Optional[str] = None
    ) -> Optional[str]:
        """
        Get direct catalog link for a book.

        Args:
            title: Book title
            author: Optional author name

        Returns:
            Catalog URL or None
        """
        availability = await self.check_availability(title, author)
        return availability.get("catalog_url")

    @staticmethod
    def get_search_url(title: str, author: Optional[str] = None) -> str:
        """
        Generate a search URL for Sno-Isle catalog.

        Args:
            title: Book title
            author: Optional author name

        Returns:
            Search URL
        """
        query = f'title:"{title}"'
        if author:
            query += f' author:"{author}"'

        return f"https://sno-isle.bibliocommons.com/v2/search?query={query}&searchType=smart"
