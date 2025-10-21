"""
Advanced Rate Limiting with Multi-Tier Support
Implements per-customer, per-agent, and per-endpoint rate limiting
"""

import time
import logging
from typing import Optional, Tuple, Dict, Any
from functools import wraps
from fastapi import HTTPException, Request
from redis import Redis
import asyncio

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration by customer tier"""
    
    TIER_LIMITS = {
        "free": {
            "requests_per_minute": 10,
            "requests_per_hour": 100,
            "requests_per_day": 1000,
            "agent_executions_per_hour": 10,
            "concurrent_executions": 1
        },
        "basic": {
            "requests_per_minute": 100,
            "requests_per_hour": 5000,
            "requests_per_day": 50000,
            "agent_executions_per_hour": 100,
            "concurrent_executions": 3
        },
        "pro": {
            "requests_per_minute": 1000,
            "requests_per_hour": 50000,
            "requests_per_day": 500000,
            "agent_executions_per_hour": 1000,
            "concurrent_executions": 10
        },
        "enterprise": {
            "requests_per_minute": 10000,
            "requests_per_hour": 500000,
            "requests_per_day": 5000000,
            "agent_executions_per_hour": 10000,
            "concurrent_executions": 50
        }
    }
    
    # Per-agent specific limits (more expensive agents have lower limits)
    AGENT_LIMITS = {
        "audit-agent": {"executions_per_hour": 20},
        "security-scanner": {"executions_per_hour": 30},
        "report-generator": {"executions_per_hour": 50},
        "data-processor": {"executions_per_hour": 100},
    }


class AdvancedRateLimiter:
    """
    Advanced rate limiter with sliding window algorithm
    Supports multiple time windows and hierarchical limits
    """
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.config = RateLimitConfig()
    
    def _get_key(self, identifier: str, window: str, scope: str = "global") -> str:
        """Generate Redis key for rate limit tracking"""
        return f"ratelimit:{scope}:{identifier}:{window}"
    
    async def check_limit(
        self,
        identifier: str,
        tier: str,
        window: str = "minute",
        scope: str = "global"
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: Customer ID or IP address
            tier: Customer tier (free, basic, pro, enterprise)
            window: Time window (minute, hour, day)
            scope: Scope of limit (global, agent, endpoint)
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        tier_config = self.config.TIER_LIMITS.get(tier.lower(), self.config.TIER_LIMITS["free"])
        limit_key = f"requests_per_{window}"
        max_requests = tier_config.get(limit_key, 100)
        
        # Use sliding window algorithm
        key = self._get_key(identifier, window, scope)
        current_time = time.time()
        window_seconds = self._get_window_seconds(window)
        window_start = current_time - window_seconds
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = self.redis.zcard(key)
        
        # Check if limit exceeded
        if current_count >= max_requests:
            # Get reset time
            oldest_entry = self.redis.zrange(key, 0, 0, withscores=True)
            reset_time = oldest_entry[0][1] + window_seconds if oldest_entry else current_time + window_seconds
            
            metadata = {
                "limit": max_requests,
                "remaining": 0,
                "reset": int(reset_time),
                "retry_after": int(reset_time - current_time)
            }
            
            logger.warning(
                f"Rate limit exceeded for {identifier} (tier: {tier}, scope: {scope})",
                extra={"metadata": metadata}
            )
            
            return False, metadata
        
        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window_seconds)
        
        metadata = {
            "limit": max_requests,
            "remaining": max_requests - current_count - 1,
            "reset": int(current_time + window_seconds)
        }
        
        return True, metadata
    
    async def check_agent_limit(
        self,
        customer_id: str,
        agent_id: str,
        tier: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check agent-specific rate limit
        
        Args:
            customer_id: Customer identifier
            agent_id: Agent package ID
            tier: Customer tier
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        # Check global agent execution limit
        tier_config = self.config.TIER_LIMITS.get(tier.lower(), self.config.TIER_LIMITS["free"])
        global_limit = tier_config["agent_executions_per_hour"]
        
        allowed, metadata = await self.check_limit(
            identifier=customer_id,
            tier=tier,
            window="hour",
            scope="agent_execution"
        )
        
        if not allowed:
            return False, metadata
        
        # Check agent-specific limit if configured
        agent_config = self.config.AGENT_LIMITS.get(agent_id)
        if agent_config:
            agent_limit = agent_config["executions_per_hour"]
            key = self._get_key(f"{customer_id}:{agent_id}", "hour", "agent_specific")
            
            current_time = time.time()
            window_start = current_time - 3600  # 1 hour
            
            self.redis.zremrangebyscore(key, 0, window_start)
            current_count = self.redis.zcard(key)
            
            if current_count >= agent_limit:
                metadata = {
                    "limit": agent_limit,
                    "remaining": 0,
                    "reset": int(current_time + 3600),
                    "agent_id": agent_id
                }
                return False, metadata
            
            self.redis.zadd(key, {str(current_time): current_time})
            self.redis.expire(key, 3600)
        
        return True, metadata
    
    async def check_concurrent_limit(
        self,
        customer_id: str,
        tier: str
    ) -> Tuple[bool, int]:
        """
        Check concurrent execution limit
        
        Args:
            customer_id: Customer identifier
            tier: Customer tier
        
        Returns:
            Tuple of (allowed: bool, current_count: int)
        """
        tier_config = self.config.TIER_LIMITS.get(tier.lower(), self.config.TIER_LIMITS["free"])
        max_concurrent = tier_config["concurrent_executions"]
        
        key = f"concurrent:{customer_id}"
        current_count = int(self.redis.get(key) or 0)
        
        if current_count >= max_concurrent:
            logger.warning(
                f"Concurrent limit exceeded for {customer_id} (tier: {tier})",
                extra={"current": current_count, "max": max_concurrent}
            )
            return False, current_count
        
        return True, current_count
    
    async def increment_concurrent(self, customer_id: str) -> int:
        """Increment concurrent execution counter"""
        key = f"concurrent:{customer_id}"
        count = self.redis.incr(key)
        self.redis.expire(key, 3600)  # Auto-expire after 1 hour as safety
        return count
    
    async def decrement_concurrent(self, customer_id: str) -> int:
        """Decrement concurrent execution counter"""
        key = f"concurrent:{customer_id}"
        count = self.redis.decr(key)
        if count <= 0:
            self.redis.delete(key)
        return max(0, count)
    
    def _get_window_seconds(self, window: str) -> int:
        """Convert window name to seconds"""
        windows = {
            "minute": 60,
            "hour": 3600,
            "day": 86400
        }
        return windows.get(window, 60)
    
    async def get_usage_stats(self, customer_id: str) -> Dict[str, Any]:
        """Get current usage statistics for a customer"""
        stats = {}
        
        for window in ["minute", "hour", "day"]:
            key = self._get_key(customer_id, window, "global")
            count = self.redis.zcard(key)
            stats[f"requests_{window}"] = count
        
        concurrent_key = f"concurrent:{customer_id}"
        stats["concurrent_executions"] = int(self.redis.get(concurrent_key) or 0)
        
        return stats


def rate_limit(
    window: str = "minute",
    scope: str = "global"
):
    """
    Decorator for rate limiting endpoints
    
    Usage:
        @rate_limit(window="minute", scope="api")
        async def my_endpoint(request: Request):
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and customer info from args/kwargs
            request = None
            customer_id = None
            tier = "free"
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get("request")
            
            if request:
                # Get customer info from request state (set by auth middleware)
                customer_id = getattr(request.state, "customer_id", None)
                tier = getattr(request.state, "tier", "free")
            
            if not customer_id:
                customer_id = request.client.host if request else "unknown"
            
            # Get rate limiter from app state
            limiter = getattr(request.app.state, "rate_limiter", None)
            
            if limiter:
                allowed, metadata = await limiter.check_limit(
                    identifier=customer_id,
                    tier=tier,
                    window=window,
                    scope=scope
                )
                
                if not allowed:
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded",
                        headers={
                            "X-RateLimit-Limit": str(metadata["limit"]),
                            "X-RateLimit-Remaining": str(metadata["remaining"]),
                            "X-RateLimit-Reset": str(metadata["reset"]),
                            "Retry-After": str(metadata.get("retry_after", 60))
                        }
                    )
                
                # Add rate limit headers to response
                if request:
                    request.state.rate_limit_metadata = metadata
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    import redis
    
    # Initialize rate limiter
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    limiter = AdvancedRateLimiter(redis_client)
    
    # Check rate limit
    async def test():
        allowed, metadata = await limiter.check_limit(
            identifier="customer_123",
            tier="pro",
            window="minute"
        )
        print(f"Allowed: {allowed}, Metadata: {metadata}")
        
        # Check agent-specific limit
        allowed, metadata = await limiter.check_agent_limit(
            customer_id="customer_123",
            agent_id="audit-agent",
            tier="pro"
        )
        print(f"Agent allowed: {allowed}, Metadata: {metadata}")
    
    asyncio.run(test())

