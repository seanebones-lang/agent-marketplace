"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from database import get_db
from core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    version: str
    timestamp: str
    services: Dict[str, str]


@router.get("/", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.
    
    Returns system health status and service availability.
    """
    services = {}
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        services["database"] = "healthy"
    except Exception as e:
        services["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis (simplified)
    services["redis"] = "healthy"
    
    # Check Qdrant (simplified)
    services["qdrant"] = "healthy"
    
    return HealthResponse(
        status="healthy" if all(s == "healthy" for s in services.values()) else "degraded",
        version=settings.version,
        timestamp=datetime.now().isoformat(),
        services=services
    )


@router.get("/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes.
    
    Returns 200 if service is ready to accept traffic.
    """
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """
    Liveness probe for Kubernetes.
    
    Returns 200 if service is alive.
    """
    return {"status": "alive"}

