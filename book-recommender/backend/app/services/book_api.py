"""
Book data API integration service.
Integrates with Open Library and Google Books APIs.
"""
import httpx
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime


class BookAPIService:
    """Service for fetching book data from external APIs."""

    OPEN_LIBRARY_BASE = "https://openlibrary.org"
    GOOGLE_BOOKS_BASE = "https://www.googleapis.com/books/v1"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def search_books(
        self,
        query: str,
        limit: int = 10,
        genre: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for books across multiple APIs.

        Args:
            query: Search query
            limit: Maximum number of results
            genre: Optional genre filter

        Returns:
            List of book dictionaries
        """
        # Try both APIs in parallel
        google_task = self._search_google_books(query, limit)
        openlibrary_task = self._search_open_library(query, limit)

        google_results, ol_results = await asyncio.gather(
            google_task,
            openlibrary_task,
            return_exceptions=True
        )

        # Combine and deduplicate results
        all_books = []

        if not isinstance(google_results, Exception):
            all_books.extend(google_results)

        if not isinstance(ol_results, Exception):
            all_books.extend(ol_results)

        # Deduplicate by ISBN or title+author
        seen = set()
        unique_books = []

        for book in all_books:
            key = book.get('isbn') or f"{book['title']}_{book['author']}"
            if key not in seen:
                seen.add(key)
                unique_books.append(book)

        return unique_books[:limit]

    async def _search_google_books(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search Google Books API.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of normalized book dictionaries
        """
        try:
            url = f"{self.GOOGLE_BOOKS_BASE}/volumes"
            params = {
                "q": query,
                "maxResults": min(limit, 40),
                "printType": "books"
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            books = []
            for item in data.get("items", []):
                volume_info = item.get("volumeInfo", {})

                # Extract ISBN
                isbn = None
                for identifier in volume_info.get("industryIdentifiers", []):
                    if identifier.get("type") in ["ISBN_13", "ISBN_10"]:
                        isbn = identifier.get("identifier")
                        break

                # Extract categories/genre
                categories = volume_info.get("categories", [])
                genre = categories[0] if categories else "General"

                # Extract cover image
                image_links = volume_info.get("imageLinks", {})
                cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

                # Extract authors
                authors = volume_info.get("authors", [])
                author = ", ".join(authors) if authors else "Unknown"

                book = {
                    "title": volume_info.get("title", "Unknown"),
                    "author": author,
                    "isbn": isbn,
                    "genre": genre,
                    "page_count": volume_info.get("pageCount"),
                    "cover_url": cover_url,
                    "description": volume_info.get("description"),
                    "publication_year": self._extract_year(volume_info.get("publishedDate")),
                    "source": "google_books"
                }

                books.append(book)

            return books

        except Exception as e:
            print(f"Error searching Google Books: {e}")
            return []

    async def _search_open_library(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search Open Library API.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of normalized book dictionaries
        """
        try:
            url = f"{self.OPEN_LIBRARY_BASE}/search.json"
            params = {
                "q": query,
                "limit": limit,
                "fields": "key,title,author_name,isbn,subject,number_of_pages,cover_i,first_publish_year"
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            books = []
            for doc in data.get("docs", []):
                # Extract ISBN
                isbns = doc.get("isbn", [])
                isbn = isbns[0] if isbns else None

                # Extract subject/genre
                subjects = doc.get("subject", [])
                genre = subjects[0] if subjects else "General"

                # Extract authors
                authors = doc.get("author_name", [])
                author = ", ".join(authors) if authors else "Unknown"

                # Cover URL
                cover_id = doc.get("cover_i")
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None

                book = {
                    "title": doc.get("title", "Unknown"),
                    "author": author,
                    "isbn": isbn,
                    "genre": genre,
                    "page_count": doc.get("number_of_pages"),
                    "cover_url": cover_url,
                    "description": None,  # Not available in search results
                    "publication_year": doc.get("first_publish_year"),
                    "source": "open_library"
                }

                books.append(book)

            return books

        except Exception as e:
            print(f"Error searching Open Library: {e}")
            return []

    async def get_book_details(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed book information by ISBN.

        Args:
            isbn: Book ISBN

        Returns:
            Book details dictionary or None
        """
        # Try Google Books first for better descriptions
        google_book = await self._get_google_book_by_isbn(isbn)
        if google_book:
            return google_book

        # Fallback to Open Library
        ol_book = await self._get_openlibrary_book_by_isbn(isbn)
        return ol_book

    async def _get_google_book_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """Get book details from Google Books by ISBN."""
        try:
            url = f"{self.GOOGLE_BOOKS_BASE}/volumes"
            params = {"q": f"isbn:{isbn}"}

            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get("items", [])
            if not items:
                return None

            volume_info = items[0].get("volumeInfo", {})

            # Extract all details
            categories = volume_info.get("categories", [])
            genre = categories[0] if categories else "General"

            image_links = volume_info.get("imageLinks", {})
            cover_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

            authors = volume_info.get("authors", [])
            author = ", ".join(authors) if authors else "Unknown"

            return {
                "title": volume_info.get("title", "Unknown"),
                "author": author,
                "isbn": isbn,
                "genre": genre,
                "page_count": volume_info.get("pageCount"),
                "cover_url": cover_url,
                "description": volume_info.get("description"),
                "publication_year": self._extract_year(volume_info.get("publishedDate")),
                "source": "google_books"
            }

        except Exception as e:
            print(f"Error fetching Google Books details: {e}")
            return None

    async def _get_openlibrary_book_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """Get book details from Open Library by ISBN."""
        try:
            url = f"{self.OPEN_LIBRARY_BASE}/isbn/{isbn}.json"

            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()

            # Get work details for more info
            work_key = None
            if "works" in data and data["works"]:
                work_key = data["works"][0]["key"]

            # Extract authors
            author_keys = data.get("authors", [])
            authors = []
            for author_ref in author_keys:
                author_key = author_ref.get("key")
                if author_key:
                    author_data = await self._get_openlibrary_author(author_key)
                    if author_data:
                        authors.append(author_data.get("name", "Unknown"))

            author = ", ".join(authors) if authors else "Unknown"

            # Extract cover
            cover_id = data.get("covers", [None])[0]
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else None

            return {
                "title": data.get("title", "Unknown"),
                "author": author,
                "isbn": isbn,
                "genre": "General",  # Would need to fetch work details
                "page_count": data.get("number_of_pages"),
                "cover_url": cover_url,
                "description": None,
                "publication_year": self._extract_year(data.get("publish_date")),
                "source": "open_library"
            }

        except Exception as e:
            print(f"Error fetching Open Library details: {e}")
            return None

    async def _get_openlibrary_author(self, author_key: str) -> Optional[Dict[str, Any]]:
        """Get author details from Open Library."""
        try:
            url = f"{self.OPEN_LIBRARY_BASE}{author_key}.json"
            response = await self.client.get(url)
            response.raise_for_status()
            return response.json()
        except:
            return None

    @staticmethod
    def _extract_year(date_string: Optional[str]) -> Optional[int]:
        """Extract year from various date formats."""
        if not date_string:
            return None

        try:
            # Try parsing as year only
            if len(date_string) == 4:
                return int(date_string)

            # Try parsing common date formats
            for fmt in ["%Y-%m-%d", "%Y-%m", "%Y", "%B %d, %Y", "%b %Y"]:
                try:
                    dt = datetime.strptime(date_string, fmt)
                    return dt.year
                except ValueError:
                    continue

            # Extract first 4 digits
            import re
            year_match = re.search(r'\d{4}', date_string)
            if year_match:
                return int(year_match.group())

        except:
            pass

        return None
