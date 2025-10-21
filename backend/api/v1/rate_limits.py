"""
Rate Limit Status API Endpoints
Provides customers with visibility into their rate limit usage
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from api.deps import get_current_customer
from models.customer import Customer
from core.rate_limiter import get_rate_limiter, RateLimitConfig
from core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/rate-limits", tags=["Rate Limits"])


class RateLimitStatusResponse(BaseModel):
    """Response model for rate limit status"""
    tier: str
    limits: Dict[str, Any]
    current_usage: Dict[str, Any]
    
    class Config:
        from_attributes = True


class TierLimitsResponse(BaseModel):
    """Response model for tier limits comparison"""
    tiers: Dict[str, Dict[str, Any]]


@router.get("/status", response_model=RateLimitStatusResponse)
async def get_rate_limit_status(
    request: Request,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Get current rate limit status for the authenticated customer.
    
    Returns:
        Current usage and limits for the customer's tier
    """
    customer_tier = getattr(customer, 'tier', 'solo')
    customer_id = str(customer.id)
    
    # Get rate limiter from app state
    rate_limiter = getattr(request.app.state, "rate_limiter", None)
    
    if not rate_limiter:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiter not available"
        )
    
    try:
        # Get usage statistics
        stats = await rate_limiter.get_usage_stats(customer_id, customer_tier)
        
        return RateLimitStatusResponse(
            tier=customer_tier,
            limits=stats["limits"],
            current_usage=stats["current_usage"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get rate limit status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rate limit status: {str(e)}"
        )


@router.get("/tiers", response_model=TierLimitsResponse)
async def get_tier_limits():
    """
    Get rate limits for all available tiers.
    Useful for displaying upgrade options to customers.
    
    Returns:
        Rate limits for all tiers
    """
    config = RateLimitConfig()
    
    tiers_data = {}
    for tier, limits in config.TIER_LIMITS.items():
        tiers_data[tier.value] = {
            "requests_per_minute": limits["requests_per_minute"],
            "requests_per_hour": limits["requests_per_hour"],
            "requests_per_day": limits["requests_per_day"],
            "agent_executions_per_hour": limits["agent_executions_per_hour"],
            "agent_executions_per_day": limits["agent_executions_per_day"],
            "concurrent_executions": limits["concurrent_executions"],
            "max_tokens_per_day": limits["max_tokens_per_day"],
            "description": limits["description"]
        }
    
    return TierLimitsResponse(tiers=tiers_data)


@router.post("/reset")
async def reset_rate_limits(
    request: Request,
    customer: Customer = Depends(get_current_customer),
    db: Session = Depends(get_db)
):
    """
    Reset rate limits for the authenticated customer.
    Admin-only endpoint (should be protected by additional auth).
    
    Returns:
        Success message
    """
    # TODO: Add admin-only check
    # For now, customers can reset their own limits (useful for testing)
    
    customer_id = str(customer.id)
    
    # Get rate limiter from app state
    rate_limiter = getattr(request.app.state, "rate_limiter", None)
    
    if not rate_limiter:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiter not available"
        )
    
    try:
        await rate_limiter.reset_limits(customer_id)
        
        logger.info(f"Rate limits reset for customer {customer_id}")
        
        return {
            "message": "Rate limits reset successfully",
            "customer_id": customer_id
        }
        
    except Exception as e:
        logger.error(f"Failed to reset rate limits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset rate limits: {str(e)}"
        )


@router.get("/agent-limits")
async def get_agent_limits():
    """
    Get agent-specific rate limits.
    Shows which agents have special rate limiting rules.
    
    Returns:
        Agent-specific rate limits
    """
    config = RateLimitConfig()
    
    agent_limits = {}
    for agent_id, limits in config.AGENT_LIMITS.items():
        agent_limits[agent_id] = {
            "executions_per_hour_by_tier": limits["executions_per_hour"],
            "description": limits["description"]
        }
    
    return {
        "agent_limits": agent_limits,
        "note": "Agents not listed here use the default tier limits"
    }

