"""
FastAPI routes for the book recommender API.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime

from ..models.book import (
    Book, BookCreate, ReadingLog, ReadingLogCreate,
    ReadingLogUpdate, ReadingStatus, BookWithReadingStatus,
    RecommendationWithBook
)
from ..models.stats import DashboardStats, ReadingGoal, ReadingGoalCreate
from ..services.book_service import BookService
from ..services.book_api import BookAPIService
from ..services.library_checker import LibraryChecker
from ..services.recommendation_engine import RecommendationEngine
from ..services.analytics_service import AnalyticsService

router = APIRouter()

# Initialize services
book_api_service = BookAPIService()
library_checker = LibraryChecker()
recommendation_engine = None  # Will be initialized with API key


# Book endpoints

@router.post("/books", response_model=dict)
async def create_book(book: BookCreate):
    """Create a new book entry."""
    try:
        # Check if book already exists by ISBN
        if book.isbn:
            existing = BookService.get_book_by_isbn(book.isbn)
            if existing:
                return {"id": existing['id'], "message": "Book already exists"}

        book_id = BookService.create_book(book)
        return {"id": book_id, "message": "Book created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books/{book_id}", response_model=dict)
async def get_book(book_id: int):
    """Get book by ID."""
    book = BookService.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/books", response_model=List[dict])
async def search_books(
    q: Optional[str] = None,
    genre: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Search books in the database."""
    if q:
        books = BookService.search_books(q, genre)
    else:
        books = BookService.get_all_books(limit, offset)
    return books


@router.get("/books/external/search", response_model=List[dict])
async def search_external_books(
    q: str = Query(..., description="Search query"),
    limit: int = 10,
    genre: Optional[str] = None
):
    """Search books from external APIs."""
    try:
        books = await book_api_service.search_books(q, limit, genre)
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/books/{book_id}/library-availability", response_model=dict)
async def check_library_availability(book_id: int):
    """Check if a book is available at Sno-Isle Libraries."""
    try:
        book = BookService.get_book_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        availability = await library_checker.check_availability(
            title=book['title'],
            author=book['author'],
            isbn=book.get('isbn')
        )

        # Update book with availability info
        if availability['available']:
            BookService.update_book(book_id, {
                'snoisle_available': True,
                'format_available': ', '.join(availability['formats'])
            })

        return availability
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Reading Log endpoints

@router.post("/reading-logs", response_model=dict)
async def create_reading_log(log: ReadingLogCreate):
    """Create a reading log entry."""
    try:
        log_id = BookService.create_reading_log(log)
        return {"id": log_id, "message": "Reading log created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading-logs", response_model=List[dict])
async def get_reading_logs(status: Optional[str] = None):
    """Get reading logs, optionally filtered by status."""
    try:
        if status:
            logs = BookService.get_reading_logs_by_status(ReadingStatus(status))
        else:
            logs = BookService.get_all_reading_logs()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/reading-logs/{log_id}", response_model=dict)
async def update_reading_log(log_id: int, update: ReadingLogUpdate):
    """Update a reading log entry."""
    try:
        success = BookService.update_reading_log(log_id, update)
        if not success:
            raise HTTPException(status_code=404, detail="Reading log not found")
        return {"message": "Reading log updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reading-logs/{log_id}/complete", response_model=dict)
async def mark_book_completed(
    log_id: int,
    rating: int = Query(..., ge=1, le=5),
    notes: Optional[str] = None,
    generate_summary: bool = True
):
    """Mark a book as completed and optionally generate AI summary."""
    try:
        # Mark as completed
        success = BookService.mark_book_completed(log_id, rating, notes)
        if not success:
            raise HTTPException(status_code=404, detail="Reading log not found")

        # Generate AI summary if requested
        if generate_summary and recommendation_engine:
            # Get book info
            log_query = "SELECT * FROM reading_log WHERE id = ?"
            from ..database.database import execute_query
            log = execute_query(log_query, (log_id,))[0]

            book = BookService.get_book_by_id(log['book_id'])

            summary = await recommendation_engine.generate_book_summary(
                book_title=book['title'],
                book_author=book['author'],
                user_notes=notes
            )

            # Update log with summary
            BookService.update_reading_log(
                log_id,
                ReadingLogUpdate(ai_summary=summary)
            )

            return {
                "message": "Book marked as completed",
                "summary": summary
            }

        return {"message": "Book marked as completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/books/{book_id}/start-reading", response_model=dict)
async def start_reading(book_id: int, format_used: str = "Physical"):
    """Start reading a book."""
    try:
        log_id = BookService.start_reading_book(book_id, format_used)
        return {"id": log_id, "message": "Started reading"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Recommendations endpoints

@router.get("/recommendations/{genre}", response_model=List[dict])
async def get_recommendations(
    genre: str,
    count: int = 3,
    refresh: bool = False
):
    """Get AI-powered book recommendations for a genre."""
    try:
        if not recommendation_engine:
            raise HTTPException(
                status_code=503,
                detail="Recommendation engine not initialized. Please set ANTHROPIC_API_KEY."
            )

        # Build user profile
        reading_history = BookService.get_all_reading_logs()

        total_books = len([log for log in reading_history if log['status'] == 'completed'])

        user_profile = {
            "reading_level": "naive" if total_books < 20 else "experienced",
            "total_books_read": total_books
        }

        # Get recommendations
        recommendations = await recommendation_engine.generate_recommendations(
            genre=genre,
            user_profile=user_profile,
            reading_history=reading_history,
            count=count
        )

        # For each recommendation, try to find/create the book and check library
        enriched_recommendations = []

        for rec in recommendations:
            # Search for book in external APIs
            books = await book_api_service.search_books(
                f"{rec['title']} {rec['author']}",
                limit=1
            )

            if books:
                book_data = books[0]

                # Create or get book
                existing = None
                if book_data.get('isbn'):
                    existing = BookService.get_book_by_isbn(book_data['isbn'])

                if not existing:
                    book_create = BookCreate(**book_data)
                    book_id = BookService.create_book(book_create)
                else:
                    book_id = existing['id']

                # Check library availability
                availability = await library_checker.check_availability(
                    title=rec['title'],
                    author=rec['author'],
                    isbn=rec.get('isbn')
                )

                enriched_recommendations.append({
                    **rec,
                    "book_id": book_id,
                    "library_availability": availability,
                    "cover_url": book_data.get('cover_url'),
                    "description": book_data.get('description')
                })
            else:
                enriched_recommendations.append(rec)

        return enriched_recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints

@router.get("/analytics/dashboard", response_model=dict)
async def get_dashboard_stats(year: Optional[int] = None):
    """Get comprehensive dashboard statistics."""
    try:
        stats = AnalyticsService.get_dashboard_stats(year)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/genre-stats", response_model=List[dict])
async def get_genre_stats():
    """Get statistics per genre."""
    try:
        stats = AnalyticsService.get_genre_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/reading-patterns", response_model=dict)
async def get_reading_patterns():
    """Get reading pattern analysis."""
    try:
        patterns = AnalyticsService.get_reading_patterns()
        return patterns
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/ai-insights", response_model=dict)
async def get_ai_insights():
    """Get AI-powered insights about reading patterns."""
    try:
        if not recommendation_engine:
            raise HTTPException(
                status_code=503,
                detail="Recommendation engine not initialized."
            )

        reading_history = BookService.get_all_reading_logs()

        insights = await recommendation_engine.analyze_reading_patterns(reading_history)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Initialize recommendation engine
def init_recommendation_engine(api_key: str):
    """Initialize the recommendation engine with API key."""
    global recommendation_engine
    try:
        recommendation_engine = RecommendationEngine(api_key)
    except Exception as e:
        print(f"Failed to initialize recommendation engine: {e}")
