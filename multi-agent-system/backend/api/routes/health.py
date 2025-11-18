"""Health check endpoints."""

from fastapi import APIRouter
from datetime import datetime

from backend.config import settings
from backend.memory import redis_manager, postgres_manager

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns the health status of the system and all dependencies.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "environment": settings.app_env,
        "services": {},
    }

    # Check Redis
    try:
        if redis_manager.redis_client:
            await redis_manager.redis_client.ping()
            health_status["services"]["redis"] = "healthy"
        else:
            health_status["services"]["redis"] = "not_connected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check PostgreSQL
    try:
        if postgres_manager.engine:
            with postgres_manager.engine.connect() as conn:
                conn.execute("SELECT 1")
            health_status["services"]["postgres"] = "healthy"
        else:
            health_status["services"]["postgres"] = "not_connected"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["postgres"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@router.get("/metrics")
async def metrics():
    """
    Prometheus-compatible metrics endpoint.
    """
    # In production, integrate with prometheus_client
    return {
        "total_workflows_executed": 0,
        "total_agents_deployed": 7,
        "total_tasks_completed": 0,
    }
