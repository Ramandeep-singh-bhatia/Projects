"""
Main FastAPI application entry point.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .api.routes import router, init_recommendation_engine
from .database.database import init_database
from .services.book_api import BookAPIService
from .services.library_checker import LibraryChecker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Initializing Book Recommender API...")

    # Initialize database
    init_database()
    print("✓ Database initialized")

    # Initialize recommendation engine
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        init_recommendation_engine(api_key)
        print("✓ AI Recommendation Engine initialized")
    else:
        print("⚠ ANTHROPIC_API_KEY not set - AI features will be disabled")

    yield

    # Shutdown
    print("Shutting down Book Recommender API...")


# Create FastAPI app
app = FastAPI(
    title="Book Recommender API",
    description="AI-powered personal book recommendation system",
    version="1.0.0",
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
