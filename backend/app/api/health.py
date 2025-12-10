"""Health check API endpoints"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app.cache import cache
from app.schemas.api_schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    """
    # Check database
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass
    
    # Check Redis
    redis_ok = cache.is_connected()
    
    # Determine overall status
    if db_ok and redis_ok:
        status = "healthy"
    elif db_ok or redis_ok:
        status = "degraded"
    else:
        status = "unhealthy"
    
    return HealthResponse(
        status=status,
        timestamp=datetime.utcnow(),
        database=db_ok,
        redis=redis_ok
    )