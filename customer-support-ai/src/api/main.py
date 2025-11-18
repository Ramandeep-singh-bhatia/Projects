"""
FastAPI application for AI Customer Support System.
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time
import uuid

from ..database import init_database
from ..utils.config import get_settings
from ..utils.logger import setup_logging, get_logger, set_request_id, clear_request_id
from ..models.schemas import ErrorResponse
from .routes import router

# Initialize settings and logging
settings = get_settings()
setup_logging(log_level=settings.log_level, log_format=settings.log_format)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting AI Customer Support API")
    logger.info(f"Environment: {'production' if settings.is_production else 'development'}")

    try:
        # Initialize database
        init_database(settings.get_database_url())
        logger.info("Database initialized successfully")

        # Ensure data directories exist
        settings.create_directories()
        logger.info("Data directories verified")

    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Customer Support API")


# Create FastAPI application
app = FastAPI(
    title="AI Customer Support System",
    description="RAG-based intelligent customer support chatbot with 70% autonomous resolution rate",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# ==================== Middleware ====================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Import rate limiting middleware
from .middleware import rate_limit_middleware


@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Apply rate limiting"""
    return await rate_limit_middleware(request, call_next)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """
    Add request ID to each request for tracking.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response with request ID header
    """
    # Generate or extract request ID
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    # Set request ID in context
    set_request_id(request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        clear_request_id()


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """
    Log all requests with timing information.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response
    """
    start_time = time.time()

    # Log request
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log response
    logger.info(
        f"Request completed: {request.method} {request.url.path}",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2)
    )

    # Add timing header
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

    return response


# ==================== Exception Handlers ====================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSON error response
    """
    errors = exc.errors()

    logger.warning(
        f"Validation error on {request.url.path}",
        errors=errors
    )

    error_response = ErrorResponse(
        error="Validation Error",
        detail=str(errors),
        request_id=request.headers.get("X-Request-ID")
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError exceptions.

    Args:
        request: FastAPI request
        exc: ValueError exception

    Returns:
        JSON error response
    """
    logger.error(f"ValueError on {request.url.path}: {str(exc)}")

    error_response = ErrorResponse(
        error="Invalid Value",
        detail=str(exc),
        request_id=request.headers.get("X-Request-ID")
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all other exceptions.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON error response
    """
    logger.error(
        f"Unhandled exception on {request.url.path}: {str(exc)}",
        exc_info=True
    )

    error_response = ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred. Please try again later.",
        request_id=request.headers.get("X-Request-ID")
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


# ==================== Root Endpoints ====================

@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        API information
    """
    return {
        "name": "AI Customer Support System",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=dict)
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    from datetime import datetime
    from ..database import db_manager
    from ..core.embeddings import EmbeddingsManager

    # Check database
    db_status = "healthy"
    try:
        if db_manager:
            db_session = db_manager.get_session()
            db_session.execute("SELECT 1")
            db_session.close()
        else:
            db_status = "not initialized"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {e}")

    # Check vector store
    vector_store_status = "healthy"
    num_documents = 0
    try:
        embeddings_manager = EmbeddingsManager()
        stats = embeddings_manager.get_vector_store_stats()
        num_documents = stats.get("num_documents", 0)
        if not stats.get("exists"):
            vector_store_status = "not initialized"
    except Exception as e:
        vector_store_status = f"unhealthy: {str(e)}"
        logger.error(f"Vector store health check failed: {e}")

    return {
        "status": "healthy" if db_status == "healthy" and vector_store_status in ["healthy", "not initialized"] else "unhealthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0",
        "database": db_status,
        "vector_store": vector_store_status,
        "num_documents": num_documents
    }


# ==================== Include Routers ====================

app.include_router(router, prefix="/api")


# ==================== Development Mode ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )
