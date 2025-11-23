"""
Main FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api.routes import router, init_recommendation_engine
from .api.enhanced_routes import router as enhanced_router, init_enhanced_services
from .api.manual_routes import router as manual_router
from .database.database import init_database
from .services.book_api import BookAPIService
from .services.library_checker import LibraryChecker
from .services.manual_entry_service import init_manual_entry_service
from .services.evaluation_service import init_evaluation_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Initializing Enhanced Book Recommender API...")

    # Initialize database
    init_database()
    print("✓ Database initialized (with Tier 1 & 2 enhancements)")

    # Initialize AI services
    api_key = os.getenv("ANTHROPIC_API_KEY")
    db_path = os.getenv("DATABASE_PATH", "./data/books.db")

    if api_key:
        # Initialize base recommendation engine
        init_recommendation_engine(api_key)
        print("✓ AI Recommendation Engine initialized")

        # Initialize enhanced services (Tier 1 & 2)
        init_enhanced_services(api_key)
        print("✓ Enhanced Services initialized:")
        print("  - AI Reading Coach")
        print("  - Reading DNA Profiler")
        print("  - Mood-Based Recommendations")
        print("  - Completion Predictor")
        print("  - Reading Journal with AI Insights")
        print("  - Annual Reports Generator")

        # Initialize manual entry & evaluation services
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        init_manual_entry_service(db_path, client)
        init_evaluation_service(db_path, client)
        print("✓ Manual Entry & Evaluation Services initialized:")
        print("  - Manual Book Addition with AI Analysis")
        print("  - 'Should I Read This?' Evaluation System")
        print("  - Future Reads Management")
        print("  - Readiness Monitoring")
        print("  - Preparation Plan Generator")
    else:
        print("⚠ ANTHROPIC_API_KEY not set - AI features will be disabled")
        # Initialize without AI
        init_manual_entry_service(db_path, None)
        init_evaluation_service(db_path, None)
        print("⚠ Manual entry services initialized without AI")

    print("✓ Vocabulary Builder ready")
    print("✓ Series Tracker ready")

    yield

    # Shutdown
    print("Shutting down Enhanced Book Recommender API...")


# Create FastAPI app
app = FastAPI(
    title="Enhanced Book Recommender API",
    description="AI-powered personal book recommendation system with advanced features",
    version="3.0.0 (Full Feature Set: Manual Entry & Evaluation)",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api")
app.include_router(enhanced_router, prefix="/api/enhanced", tags=["Tier 1 & 2 Features"])
app.include_router(manual_router, tags=["Manual Entry & Evaluation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Book Recommender API",
        "version": "3.0.0",
        "features": [
            "AI-Powered Recommendations",
            "Reading DNA Profile",
            "Manual Book Entry & Analysis",
            "Should I Read This? Evaluation",
            "Future Reads Management",
            "Reading Coach & Plans",
            "Vocabulary Builder",
            "Series Tracker",
            "Annual Reading Reports"
        ],
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
