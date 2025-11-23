"""
Manual Entry & Evaluation API Routes
Handles manual book addition, batch imports, and book evaluation
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from app.services.manual_entry_service import get_manual_entry_service
from app.services.evaluation_service import get_evaluation_service

router = APIRouter(prefix="/api/manual", tags=["manual"])


# Request/Response Models
class BookData(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    genre: Optional[str] = "Unknown"
    page_count: Optional[int] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    publication_year: Optional[int] = None


class AddManualBookRequest(BaseModel):
    book_data: BookData
    source: str = Field(..., description="Source: friend, online, bookstore, other")
    recommender_name: Optional[str] = None
    why_read: Optional[str] = None
    auto_analyze: bool = True


class ExternalRecommendationRequest(BaseModel):
    book_id: int
    recommender_type: str = Field(..., description="Type: friend, family, online, critic, bookclub, other")
    recommender_name: str
    context: Optional[str] = None
    trust_score: float = Field(0.5, ge=0, le=1)


class FutureReadRequest(BaseModel):
    book_id: int
    user_notes: Optional[str] = None
    reminder_preference: str = Field("when_ready", description="when_ready, monthly, quarterly, never")


# MANUAL ENTRY ENDPOINTS

@router.post("/add-book")
async def add_manual_book(request: AddManualBookRequest):
    """
    Manually add a book to the library

    This endpoint allows users to add books that weren't discovered through
    the app's recommendation system. The book will be analyzed by AI if requested.
    """
    try:
        service = get_manual_entry_service()

        result = service.add_manual_book(
            book_data=request.book_data.dict(),
            source=request.source,
            recommender_name=request.recommender_name,
            why_read=request.why_read,
            auto_analyze=request.auto_analyze
        )

        return {
            "success": True,
            "book_id": result['book_id'],
            "manual_entry_id": result['manual_entry_id'],
            "analysis_completed": result['analysis_completed'],
            "message": "Book added successfully!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-import")
async def batch_import_goodreads(file: UploadFile = File(...)):
    """
    Batch import books from Goodreads CSV export

    Upload your Goodreads library export CSV to quickly add multiple books.
    Books will be analyzed automatically.
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        content = await file.read()
        csv_content = content.decode('utf-8')

        service = get_manual_entry_service()
        result = await service.batch_import_goodreads(csv_content)

        return {
            "success": True,
            "stats": result,
            "message": f"Imported {result['imported']} books successfully!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-book/{book_id}")
async def analyze_book(book_id: int):
    """
    Trigger AI analysis for a specific book

    Analyzes complexity, themes, moods, and other characteristics.
    """
    try:
        service = get_manual_entry_service()
        analysis = await service.analyze_book(book_id)

        return {
            "success": True,
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile-impact/{book_id}")
async def calculate_profile_impact(book_id: int):
    """
    Calculate how this book affects your reading profile

    Shows if the book is in/out of your comfort zone and its impact
    on your reading diversity.
    """
    try:
        service = get_manual_entry_service()
        impact = await service.calculate_profile_impact(book_id)

        return {
            "success": True,
            "impact": impact
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entries")
async def get_manual_entries(limit: int = 50):
    """
    Get all manually added books

    Returns books added outside the app's recommendation system.
    """
    try:
        service = get_manual_entry_service()
        entries = service.get_manual_entries(limit)

        return {
            "success": True,
            "count": len(entries),
            "entries": entries
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/external-recommendation")
async def add_external_recommendation(request: ExternalRecommendationRequest):
    """
    Track a recommendation from a friend, critic, or other external source

    Helps the system learn which external sources give you good recommendations.
    """
    try:
        service = get_manual_entry_service()

        rec_id = service.add_external_recommendation(
            book_id=request.book_id,
            recommender_type=request.recommender_type,
            recommender_name=request.recommender_name,
            context=request.context,
            trust_score=request.trust_score
        )

        return {
            "success": True,
            "recommendation_id": rec_id,
            "message": "External recommendation tracked!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# BOOK EVALUATION ENDPOINTS

@router.post("/evaluate/{book_id}")
async def evaluate_book_readiness(book_id: int):
    """
    "Should I Read This?" - Evaluate if you're ready for this book

    Provides a comprehensive readiness assessment with:
    - Readiness score (0-100)
    - Recommendation type (read_now, maybe_later, not_yet, different_direction)
    - Detailed reasoning and factors
    - Preparation suggestions if needed
    """
    try:
        service = get_evaluation_service()
        evaluation = await service.evaluate_readiness(book_id)

        return {
            "success": True,
            "evaluation": evaluation
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/future-reads/add")
async def add_to_future_reads(request: FutureReadRequest, evaluation_data: Optional[Dict[str, Any]] = None):
    """
    Add a book to your Future Reads list

    Books you want to read eventually but aren't quite ready for yet.
    The system will monitor your reading and notify you when you're ready.
    """
    try:
        # If no evaluation provided, evaluate first
        if not evaluation_data:
            eval_service = get_evaluation_service()
            evaluation_data = await eval_service.evaluate_readiness(request.book_id)

        eval_service = get_evaluation_service()
        future_read_id = await eval_service.add_to_future_reads(
            book_id=request.book_id,
            evaluation=evaluation_data,
            user_notes=request.user_notes,
            reminder_preference=request.reminder_preference
        )

        return {
            "success": True,
            "future_read_id": future_read_id,
            "message": "Added to Future Reads!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/future-reads")
async def get_future_reads(
    status: Optional[str] = None,
    min_readiness: Optional[int] = None
):
    """
    Get your Future Reads list

    Optional filters:
    - status: waiting, preparing, ready, moved_to_reading, abandoned
    - min_readiness: Minimum readiness score (0-100)
    """
    try:
        service = get_evaluation_service()
        books = service.get_future_reads(status, min_readiness)

        return {
            "success": True,
            "count": len(books),
            "books": books
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preparation-plan/{book_id}")
async def generate_preparation_plan(book_id: int, evaluation_data: Optional[Dict[str, Any]] = None):
    """
    Generate a reading plan to prepare you for a challenging book

    Creates a 3-4 book roadmap that bridges gaps and builds up to the target book.
    """
    try:
        service = get_evaluation_service()

        # If no evaluation provided, evaluate first
        if not evaluation_data:
            evaluation_data = await service.evaluate_readiness(book_id)

        plan = await service.generate_preparation_plan(book_id, evaluation_data)

        return {
            "success": True,
            "plan": plan
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/readiness-check/run")
async def run_readiness_check():
    """
    Check all Future Reads for readiness updates

    Re-evaluates books in your Future Reads list to see if you're now ready
    for any of them. Run this weekly or after completing books.
    """
    try:
        service = get_evaluation_service()
        updates = await service.check_readiness_updates()

        return {
            "success": True,
            "updates_found": len(updates),
            "updates": updates
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/readiness-check/notifications")
async def get_readiness_notifications():
    """
    Get books that are now ready to read

    Returns Future Reads that have reached readiness score >= 75.
    """
    try:
        service = get_evaluation_service()
        ready_books = service.get_future_reads(status='ready', min_readiness=75)

        return {
            "success": True,
            "count": len(ready_books),
            "ready_books": ready_books,
            "message": f"You have {len(ready_books)} books ready to read!"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# QUICK ADD SHORTCUTS

@router.post("/quick-add/isbn/{isbn}")
async def quick_add_by_isbn(
    isbn: str,
    source: str = "manual",
    recommender_name: Optional[str] = None,
    why_read: Optional[str] = None
):
    """
    Quick add a book by ISBN

    Fetches book metadata from external APIs and adds it to your library.
    """
    try:
        # Import book API service
        from app.services.book_api import get_book_api_service

        book_api = get_book_api_service()

        # Search for book by ISBN
        results = await book_api.search_books(isbn, limit=1)

        if not results:
            raise HTTPException(status_code=404, detail="Book not found by ISBN")

        book_data = results[0]

        # Add the book
        service = get_manual_entry_service()
        result = service.add_manual_book(
            book_data=book_data,
            source=source,
            recommender_name=recommender_name,
            why_read=why_read,
            auto_analyze=True
        )

        return {
            "success": True,
            "book_id": result['book_id'],
            "book_data": book_data,
            "message": "Book added successfully by ISBN!"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick-add/search")
async def quick_add_by_search(
    query: str,
    source: str = "manual",
    recommender_name: Optional[str] = None,
    why_read: Optional[str] = None
):
    """
    Quick add a book by searching title/author

    Searches external APIs and adds the first match.
    """
    try:
        from app.services.book_api import get_book_api_service

        book_api = get_book_api_service()
        results = await book_api.search_books(query, limit=1)

        if not results:
            raise HTTPException(status_code=404, detail="No books found")

        book_data = results[0]

        service = get_manual_entry_service()
        result = service.add_manual_book(
            book_data=book_data,
            source=source,
            recommender_name=recommender_name,
            why_read=why_read,
            auto_analyze=True
        )

        return {
            "success": True,
            "book_id": result['book_id'],
            "book_data": book_data,
            "message": "Book added successfully!"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
