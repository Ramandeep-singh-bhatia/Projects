"""
Main FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api.routes import router, init_recommendation_engine
from .api.enhanced_routes import router as enhanced_router, init_enhanced_services
from .database.database import init_database
from .services.book_api import BookAPIService
from .services.library_checker import LibraryChecker


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
    else:
        print("⚠ ANTHROPIC_API_KEY not set - AI features will be disabled")

    print("✓ Vocabulary Builder ready")
    print("✓ Series Tracker ready")

    yield

    # Shutdown
    print("Shutting down Enhanced Book Recommender API...")


# Create FastAPI app
app = FastAPI(
    title="Enhanced Book Recommender API",
    description="AI-powered personal book recommendation system with advanced features",
    version="2.0.0 (Tier 1 & 2)",
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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Book Recommender API",
        "version": "1.0.0",
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
