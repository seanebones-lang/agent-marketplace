"""
Monitoring and Health Check API Endpoints
Provides visibility into system health, circuit breakers, and error metrics
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from api.deps import get_current_customer
from models.customer import Customer
from core.circuit_breaker import circuit_breaker_registry
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


class CircuitBreakerStatus(BaseModel):
    """Circuit breaker status response"""
    name: str
    state: str
    metrics: Dict[str, Any]


class SystemHealthResponse(BaseModel):
    """System health response"""
    status: str
    circuit_breakers: Dict[str, Any]
    services: Dict[str, str]


@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health():
    """
    Get overall system health status.
    
    Returns:
        System health including circuit breaker status
    """
    try:
        # Get circuit breaker health
        cb_health = circuit_breaker_registry.get_health_status()
        
        # Determine overall status
        if cb_health["open"] > 0:
            overall_status = "degraded"
        elif cb_health["half_open"] > 0:
            overall_status = "recovering"
        else:
            overall_status = "healthy"
        
        return SystemHealthResponse(
            status=overall_status,
            circuit_breakers=cb_health,
            services={
                "database": "healthy",  # TODO: Add actual health checks
                "redis": "healthy",
                "llm_providers": "healthy"
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system health"
        )


@router.get("/circuit-breakers", response_model=Dict[str, Dict[str, Any]])
async def get_circuit_breakers():
    """
    Get status of all circuit breakers.
    
    Returns:
        Dictionary of circuit breaker metrics
    """
    try:
        metrics = circuit_breaker_registry.get_all_metrics()
        return metrics
    
    except Exception as e:
        logger.error(f"Failed to get circuit breaker metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve circuit breaker metrics"
        )


@router.get("/circuit-breakers/{name}", response_model=CircuitBreakerStatus)
async def get_circuit_breaker(name: str):
    """
    Get status of a specific circuit breaker.
    
    Args:
        name: Circuit breaker name
    
    Returns:
        Circuit breaker status and metrics
    """
    try:
        breaker = circuit_breaker_registry.get(name)
        
        if not breaker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Circuit breaker not found: {name}"
            )
        
        metrics = breaker.get_metrics()
        
        return CircuitBreakerStatus(
            name=name,
            state=breaker.state.value,
            metrics=metrics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get circuit breaker {name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve circuit breaker: {name}"
        )


@router.post("/circuit-breakers/{name}/reset")
async def reset_circuit_breaker(name: str):
    """
    Reset a specific circuit breaker (admin only).
    
    Args:
        name: Circuit breaker name
    
    Returns:
        Success message
    """
    # TODO: Add admin authentication
    
    try:
        breaker = circuit_breaker_registry.get(name)
        
        if not breaker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Circuit breaker not found: {name}"
            )
        
        await breaker.reset()
        
        logger.info(f"Circuit breaker reset: {name}")
        
        return {
            "message": f"Circuit breaker {name} has been reset",
            "name": name,
            "state": breaker.state.value
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset circuit breaker {name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset circuit breaker: {name}"
        )


@router.post("/circuit-breakers/reset-all")
async def reset_all_circuit_breakers():
    """
    Reset all circuit breakers (admin only).
    
    Returns:
        Success message
    """
    # TODO: Add admin authentication
    
    try:
        await circuit_breaker_registry.reset_all()
        
        logger.info("All circuit breakers reset")
        
        return {
            "message": "All circuit breakers have been reset",
            "count": len(circuit_breaker_registry._breakers)
        }
    
    except Exception as e:
        logger.error(f"Failed to reset all circuit breakers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset circuit breakers"
        )

