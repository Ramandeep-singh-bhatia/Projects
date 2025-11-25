"""
JobFlow Backend - FastAPI Application
Main entry point for the job application automation system
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from .config import settings
from .database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOGS_DIR / 'jobflow.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    # Startup
    logger.info("Starting JobFlow Backend...")

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Start job scanner scheduler
    logger.info("Starting job scanner scheduler...")
    from .services.scheduler import start_scheduler
    start_scheduler()

    # TODO: Initialize Claude web client if configured

    logger.info("JobFlow Backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down JobFlow Backend...")

    # Stop scheduler
    logger.info("Stopping job scanner scheduler...")
    from .services.scheduler import stop_scheduler
    stop_scheduler()

    # TODO: Close Claude web client


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for JobFlow - Job Application Automation Tool",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import and include routers
from .api.routes import profile, questions, resumes, applications, jobs, analytics, scanner, review

app.include_router(profile.router)
app.include_router(questions.router)
app.include_router(resumes.router)
app.include_router(applications.router)
app.include_router(jobs.router)
app.include_router(analytics.router)
app.include_router(scanner.router)
app.include_router(review.router)
# TODO: Add claude router when implemented
# app.include_router(claude.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
