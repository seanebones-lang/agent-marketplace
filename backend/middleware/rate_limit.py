"""
Rate Limiting Middleware

This module provides rate limiting middleware for FastAPI.
"""

from typing import Callable
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from core.security import rate_limiter
from core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.
    
    Rate limits are applied per API key or IP address.
    """
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        """
        Process request with rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware/route handler
            
        Returns:
            Response
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/api/v1/health", "/api/v1/health/ready", "/api/v1/health/live"]:
            return await call_next(request)
        
        # Get identifier (API key or IP)
        api_key = request.headers.get(settings.API_KEY_HEADER)
        identifier = api_key if api_key else request.client.host
        
        # Check rate limit
        if not rate_limiter.check_rate_limit(identifier, self.calls, self.period):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={
                    "Retry-After": str(self.period),
                    "X-RateLimit-Limit": str(self.calls),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self.period)
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        remaining = rate_limiter.get_remaining(identifier, self.calls, self.period)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(self.period)
        
        return response


def get_rate_limit_for_tier(tier: str) -> int:
    """
    Get rate limit based on customer tier.
    
    Args:
        tier: Customer tier (free, basic, pro, enterprise)
        
    Returns:
        Rate limit (requests per minute)
    """
    tier_limits = {
        "free": settings.RATE_LIMIT_FREE,
        "basic": settings.RATE_LIMIT_BASIC,
        "pro": settings.RATE_LIMIT_PRO,
        "enterprise": settings.RATE_LIMIT_ENTERPRISE
    }
    
    return tier_limits.get(tier, settings.RATE_LIMIT_FREE)

