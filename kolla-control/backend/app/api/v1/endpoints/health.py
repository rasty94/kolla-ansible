"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import HealthCheck, Message

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    
    Returns basic health status of the API
    """
    from app.core.config import settings
    
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
    )


@router.get("/health/db", response_model=Message)
async def database_health_check(db: AsyncSession = Depends(get_db)):
    """
    Database health check
    
    Verifies database connectivity
    """
    try:
        # Execute a simple query
        await db.execute("SELECT 1")
        return Message(message="Database connection successful")
    except Exception as e:
        return Message(message=f"Database connection failed: {str(e)}")
