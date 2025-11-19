"""
Enhanced API routes for Tier 1 & 2 features.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import date

from ..services.reading_coach import ReadingCoachService
from ..services.enhanced_recommendations import EnhancedRecommendationEngine
from ..services.vocabulary_service import VocabularyService
from ..services.series_tracker import SeriesTrackerService
from ..services.reading_journal import ReadingJournalService
from ..services.annual_reports import AnnualReportsService

router = APIRouter()

# Initialize services
reading_coach = None
enhanced_recommender = None
vocabulary_service = VocabularyService()
series_tracker = SeriesTrackerService()
reading_journal = None
annual_reports = None


# TIER 1: AI Reading Coach

@router.post("/reading-coach/create-plan")
async def create_reading_plan(
    goal: str,
    duration_days: int,
    difficulty: str = "gradual"
):
    """Generate a personalized reading plan."""
    if not reading_coach:
        raise HTTPException(status_code=503, detail="Reading coach not initialized")

    try:
        from ..services.book_service import BookService
        reading_history = BookService.get_all_reading_logs()

        plan = await reading_coach.generate_reading_plan(
            goal=goal,
            duration_days=duration_days,
            difficulty=difficulty,
            reading_history=reading_history
        )

        return plan

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading-coach/pace-analysis/{book_id}")
async def analyze_reading_pace(
    book_id: int,
    target_date: Optional[str] = None
):
    """Analyze reading pace for a book."""
    if not reading_coach:
        raise HTTPException(status_code=503, detail="Reading coach not initialized")

    try:
        target = date.fromisoformat(target_date) if target_date else None
        analysis = await reading_coach.analyze_reading_pace(book_id, target)

        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reading-coach/slump-check")
async def check_reading_slump():
    """Check if user is in a reading slump."""
    if not reading_coach:
        raise HTTPException(status_code=503, detail="Reading coach not initialized")

    try:
        slump_data = reading_coach.detect_reading_slump()

        if slump_data:
            from ..services.book_service import BookService
            reading_history = BookService.get_all_reading_logs()

            recovery = await reading_coach.suggest_slump_recovery(slump_data, reading_history)

            return {
                "in_slump": True,
                "slump_data": slump_data,
                "recovery_suggestions": recovery
            }
        else:
            return {"in_slump": False, "message": "You're doing great!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TIER 1: Enhanced Recommendations

@router.post("/recommendations/mood-based")
async def get_mood_recommendations(
    mood_selections: Dict[str, Any],
    count: int = 3
):
    """Get mood-based book recommendations."""
    if not enhanced_recommender:
        raise HTTPException(status_code=503, detail="Enhanced recommender not initialized")

    try:
        from ..services.book_service import BookService
        reading_history = BookService.get_all_reading_logs()

        recommendations = await enhanced_recommender.recommend_by_mood(
            mood_selections=mood_selections,
            reading_history=reading_history,
            count=count
        )

        return recommendations

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/reading-dna")
async def get_reading_dna():
    """Generate Reading DNA profile."""
    if not enhanced_recommender:
        raise HTTPException(status_code=503, detail="Enhanced recommender not initialized")

    try:
        from ..services.book_service import BookService
        reading_history = BookService.get_all_reading_logs()

        dna_profile = await enhanced_recommender.generate_reading_dna(reading_history)

        return dna_profile

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/predict-completion/{book_id}")
async def predict_book_completion(book_id: int):
    """Predict likelihood of completing a book."""
    if not enhanced_recommender:
        raise HTTPException(status_code=503, detail="Enhanced recommender not initialized")

    try:
        from ..services.book_service import BookService
        from ..services.analytics_service import AnalyticsService

        book = BookService.get_book_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        # Get user patterns
        reading_history = BookService.get_all_reading_logs()
        genre_stats = AnalyticsService.get_genre_stats()

        # Build user patterns
        user_patterns = {
            "genre_completion_rate": 75,  # Would calculate from history
            "avg_completed_length": 350,
            "avg_complexity": 6,
            "top_genres": [s['genre'] for s in genre_stats[:3]],
            "dnf_patterns": "None identified"
        }

        prediction = await enhanced_recommender.predict_completion_probability(book, user_patterns)

        return prediction

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations/book-pairing/{book_id}")
async def suggest_book_pairing(book_id: int):
    """Suggest a complementary book pairing."""
    if not enhanced_recommender:
        raise HTTPException(status_code=503, detail="Enhanced recommender not initialized")

    try:
        from ..services.book_service import BookService

        book = BookService.get_book_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        pairing = await enhanced_recommender.suggest_book_pairing(book)

        return pairing

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TIER 2: Vocabulary Builder

@router.post("/vocabulary/add")
async def add_vocabulary_word(
    word: str,
    context_sentence: str,
    book_id: int,
    page_number: Optional[int] = None
):
    """Add a new vocabulary word."""
    try:
        result = await vocabulary_service.add_word(
            word=word,
            context_sentence=context_sentence,
            book_id=book_id,
            page_number=page_number
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vocabulary/review")
async def get_words_for_review(limit: int = 10):
    """Get words due for review."""
    try:
        words = vocabulary_service.get_words_for_review(limit)
        return words

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vocabulary/review/{word_id}")
async def review_vocabulary_word(
    word_id: int,
    knew_it: bool
):
    """Record a vocabulary review."""
    try:
        result = vocabulary_service.review_word(word_id, knew_it)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vocabulary/stats")
async def get_vocabulary_stats():
    """Get vocabulary learning statistics."""
    try:
        stats = vocabulary_service.get_vocabulary_stats()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vocabulary/search")
async def search_vocabulary(q: str, limit: int = 50):
    """Search vocabulary."""
    try:
        results = vocabulary_service.search_vocabulary(q, limit)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TIER 2: Series Tracker

@router.get("/series")
async def get_all_series():
    """Get all book series."""
    try:
        series = series_tracker.get_all_series()
        return series

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series/{series_id}")
async def get_series_details(series_id: int):
    """Get detailed series information."""
    try:
        details = series_tracker.get_series_details(series_id)

        if not details:
            raise HTTPException(status_code=404, detail="Series not found")

        return details

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/series")
async def create_new_series(
    series_name: str,
    primary_author: str,
    genre: str,
    total_books: Optional[int] = None,
    description: Optional[str] = None
):
    """Create a new book series."""
    try:
        series_id = series_tracker.create_series(
            series_name=series_name,
            primary_author=primary_author,
            genre=genre,
            total_books=total_books,
            description=description
        )

        return {"series_id": series_id, "message": "Series created"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/series/{series_id}/add-book")
async def add_book_to_series(
    series_id: int,
    book_id: int,
    book_number: int,
    reading_order: Optional[int] = None
):
    """Add a book to a series."""
    try:
        entry_id = series_tracker.add_book_to_series(
            series_id=series_id,
            book_id=book_id,
            book_number=book_number,
            reading_order=reading_order
        )

        return {"entry_id": entry_id, "message": "Book added to series"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series/in-progress")
async def get_in_progress_series():
    """Get series currently being read."""
    try:
        series = series_tracker.get_in_progress_series()
        return series

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series/{series_id}/next-book")
async def get_next_book(series_id: int):
    """Get next unread book in series."""
    try:
        next_book = series_tracker.get_next_book_in_series(series_id)

        if not next_book:
            return {"message": "No more books in series or all completed"}

        return next_book

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series/stats")
async def get_series_stats():
    """Get series reading statistics."""
    try:
        stats = series_tracker.get_series_statistics()
        return stats

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TIER 2: Reading Journal

@router.post("/journal/notes")
async def add_reading_note(
    book_id: int,
    content: str,
    note_type: str = "thought",
    page_number: Optional[int] = None,
    chapter: Optional[str] = None,
    tags: Optional[List[str]] = None
):
    """Add a reading note."""
    if not reading_journal:
        raise HTTPException(status_code=503, detail="Reading journal not initialized")

    try:
        note_id = reading_journal.add_note(
            book_id=book_id,
            content=content,
            note_type=note_type,
            page_number=page_number,
            chapter=chapter,
            tags=tags
        )

        return {"note_id": note_id, "message": "Note added"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal/notes/{book_id}")
async def get_book_notes(
    book_id: int,
    note_type: Optional[str] = None
):
    """Get all notes for a book."""
    if not reading_journal:
        raise HTTPException(status_code=503, detail="Reading journal not initialized")

    try:
        notes = reading_journal.get_notes_for_book(book_id, note_type)
        return notes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal/analyze/{book_id}")
async def analyze_book_notes(book_id: int):
    """Get AI analysis of all notes for a book."""
    if not reading_journal:
        raise HTTPException(status_code=503, detail="Reading journal not initialized")

    try:
        analysis = await reading_journal.analyze_notes(book_id)
        return analysis

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal/favorites")
async def get_favorite_notes(limit: int = 50):
    """Get favorite notes across all books."""
    if not reading_journal:
        raise HTTPException(status_code=503, detail="Reading journal not initialized")

    try:
        notes = reading_journal.get_favorite_notes(limit)
        return notes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/journal/search")
async def search_notes(
    q: str,
    note_type: Optional[str] = None,
    tag: Optional[str] = None
):
    """Search reading notes."""
    if not reading_journal:
        raise HTTPException(status_code=503, detail="Reading journal not initialized")

    try:
        notes = reading_journal.search_notes(q, note_type, tag)
        return notes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TIER 2: Annual Reports

@router.get("/reports/annual/{year}")
async def get_annual_report(year: int):
    """Generate or retrieve annual reading report."""
    if not annual_reports:
        raise HTTPException(status_code=503, detail="Annual reports service not initialized")

    try:
        # Check if report already exists
        saved_report = annual_reports.get_saved_report(year)

        if saved_report:
            return saved_report

        # Generate new report
        report = await annual_reports.generate_annual_report(year)

        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/annual/{year}/regenerate")
async def regenerate_annual_report(year: int):
    """Force regeneration of annual report."""
    if not annual_reports:
        raise HTTPException(status_code=503, detail="Annual reports service not initialized")

    try:
        report = await annual_reports.generate_annual_report(year)
        return report

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Initialization function
def init_enhanced_services(api_key: str):
    """Initialize all enhanced services."""
    global reading_coach, enhanced_recommender, reading_journal, annual_reports

    try:
        reading_coach = ReadingCoachService(api_key)
        enhanced_recommender = EnhancedRecommendationEngine(api_key)
        reading_journal = ReadingJournalService(api_key)
        annual_reports = AnnualReportsService(api_key)

        print("✓ Enhanced services initialized")

    except Exception as e:
        print(f"Failed to initialize enhanced services: {e}")
