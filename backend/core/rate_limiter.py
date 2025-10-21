"""
Production-Grade Rate Limiting with Multi-Tier Support
Implements per-customer, per-agent, and per-endpoint rate limiting
Aligned with the 7-tier system: solo, basic, silver, standard, premium, elite, byok
"""

import time
import logging
from typing import Optional, Tuple, Dict, Any
from functools import wraps
from fastapi import HTTPException, Request
from redis import Redis
import asyncio

from core.model_tiers import ModelTier

logger = logging.getLogger(__name__)


class RateLimitConfig:
    """Rate limit configuration by customer tier - aligned with model tiers"""
    
    # Tier-based rate limits (requests per time window)
    TIER_LIMITS = {
        ModelTier.SOLO: {
            "requests_per_minute": 5,
            "requests_per_hour": 50,
            "requests_per_day": 500,
            "agent_executions_per_hour": 5,
            "agent_executions_per_day": 50,
            "concurrent_executions": 1,
            "max_tokens_per_day": 100_000,
            "description": "Entry-level limits for testing and learning"
        },
        ModelTier.BASIC: {
            "requests_per_minute": 20,
            "requests_per_hour": 500,
            "requests_per_day": 5_000,
            "agent_executions_per_hour": 50,
            "agent_executions_per_day": 500,
            "concurrent_executions": 2,
            "max_tokens_per_day": 1_000_000,
            "description": "Basic tier for small teams"
        },
        ModelTier.SILVER: {
            "requests_per_minute": 50,
            "requests_per_hour": 2_000,
            "requests_per_day": 20_000,
            "agent_executions_per_hour": 200,
            "agent_executions_per_day": 2_000,
            "concurrent_executions": 5,
            "max_tokens_per_day": 5_000_000,
            "description": "Silver tier for growing teams"
        },
        ModelTier.STANDARD: {
            "requests_per_minute": 100,
            "requests_per_hour": 5_000,
            "requests_per_day": 50_000,
            "agent_executions_per_hour": 500,
            "agent_executions_per_day": 5_000,
            "concurrent_executions": 10,
            "max_tokens_per_day": 10_000_000,
            "description": "Standard tier for regular enterprise use"
        },
        ModelTier.PREMIUM: {
            "requests_per_minute": 200,
            "requests_per_hour": 10_000,
            "requests_per_day": 100_000,
            "agent_executions_per_hour": 1_000,
            "agent_executions_per_day": 10_000,
            "concurrent_executions": 20,
            "max_tokens_per_day": 25_000_000,
            "description": "Premium tier for advanced agent usage"
        },
        ModelTier.ELITE: {
            "requests_per_minute": 500,
            "requests_per_hour": 25_000,
            "requests_per_day": 250_000,
            "agent_executions_per_hour": 2_500,
            "agent_executions_per_day": 25_000,
            "concurrent_executions": 50,
            "max_tokens_per_day": 100_000_000,
            "description": "Elite tier for mission-critical operations"
        },
        ModelTier.BYOK: {
            "requests_per_minute": 1_000,
            "requests_per_hour": 50_000,
            "requests_per_day": 500_000,
            "agent_executions_per_hour": 5_000,
            "agent_executions_per_day": 50_000,
            "concurrent_executions": 100,
            "max_tokens_per_day": None,  # Unlimited (user pays Anthropic directly)
            "description": "BYOK tier with generous limits (you pay Anthropic directly)"
        }
    }
    
    # Per-agent specific limits (resource-intensive agents have lower limits)
    AGENT_LIMITS = {
        "audit-agent": {
            "executions_per_hour": {"solo": 2, "basic": 10, "silver": 30, "standard": 50, "premium": 100, "elite": 200, "byok": 500},
            "description": "Compliance audits are resource-intensive"
        },
        "security-scanner": {
            "executions_per_hour": {"solo": 3, "basic": 15, "silver": 40, "standard": 75, "premium": 150, "elite": 300, "byok": 750},
            "description": "Security scans require significant processing"
        },
        "deployment-agent": {
            "executions_per_hour": {"solo": 2, "basic": 10, "silver": 25, "standard": 50, "premium": 100, "elite": 200, "byok": 500},
            "description": "Deployments are critical and rate-limited"
        },
        "report-generator": {
            "executions_per_hour": {"solo": 3, "basic": 20, "silver": 50, "standard": 100, "premium": 200, "elite": 400, "byok": 1000},
            "description": "Report generation uses significant resources"
        },
        "workflow-orchestrator": {
            "executions_per_hour": {"solo": 2, "basic": 10, "silver": 30, "standard": 60, "premium": 120, "elite": 250, "byok": 600},
            "description": "Complex workflows need rate limiting"
        }
    }


class AdvancedRateLimiter:
    """
    Production-grade rate limiter with sliding window algorithm
    Supports multiple time windows, hierarchical limits, and token tracking
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
        Check if request is within rate limit using sliding window algorithm
        
        Args:
            identifier: Customer ID or IP address
            tier: Customer tier (solo, basic, silver, standard, premium, elite, byok)
            window: Time window (minute, hour, day)
            scope: Scope of limit (global, agent, endpoint)
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        try:
            # Convert string tier to ModelTier enum
            tier_enum = ModelTier(tier.lower())
        except ValueError:
            logger.warning(f"Invalid tier '{tier}', defaulting to SOLO")
            tier_enum = ModelTier.SOLO
        
        tier_config = self.config.TIER_LIMITS.get(tier_enum)
        if not tier_config:
            logger.error(f"No config found for tier {tier_enum}, using SOLO")
            tier_config = self.config.TIER_LIMITS[ModelTier.SOLO]
        
        limit_key = f"requests_per_{window}"
        max_requests = tier_config.get(limit_key, 10)
        
        # Use sliding window algorithm with sorted sets
        key = self._get_key(identifier, window, scope)
        current_time = time.time()
        window_seconds = self._get_window_seconds(window)
        window_start = current_time - window_seconds
        
        try:
            # Remove old entries outside the window
            self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count current requests in window
            current_count = self.redis.zcard(key)
            
            # Check if limit exceeded
            if current_count >= max_requests:
                # Get reset time (when oldest entry expires)
                oldest_entry = self.redis.zrange(key, 0, 0, withscores=True)
                reset_time = oldest_entry[0][1] + window_seconds if oldest_entry else current_time + window_seconds
                
                metadata = {
                    "limit": max_requests,
                    "remaining": 0,
                    "reset": int(reset_time),
                    "retry_after": int(reset_time - current_time),
                    "tier": tier,
                    "window": window,
                    "scope": scope
                }
                
                logger.warning(
                    f"Rate limit exceeded for {identifier} (tier: {tier}, scope: {scope}, window: {window})",
                    extra={"metadata": metadata}
                )
                
                return False, metadata
            
            # Add current request to sorted set
            self.redis.zadd(key, {str(current_time): current_time})
            self.redis.expire(key, window_seconds * 2)  # Keep data for 2x window for safety
            
            metadata = {
                "limit": max_requests,
                "remaining": max_requests - current_count - 1,
                "reset": int(current_time + window_seconds),
                "tier": tier,
                "window": window
            }
            
            return True, metadata
            
        except Exception as e:
            logger.error(f"Redis error in rate limiter: {e}")
            # Fail open - allow request if Redis is down
            return True, {"limit": max_requests, "remaining": max_requests, "reset": int(current_time + window_seconds)}
    
    async def check_agent_limit(
        self,
        customer_id: str,
        agent_id: str,
        tier: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check agent-specific rate limit with tier-based restrictions
        
        Args:
            customer_id: Customer identifier
            agent_id: Agent package ID
            tier: Customer tier
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        try:
            tier_enum = ModelTier(tier.lower())
        except ValueError:
            tier_enum = ModelTier.SOLO
        
        # Check global agent execution limit for tier
        tier_config = self.config.TIER_LIMITS.get(tier_enum, self.config.TIER_LIMITS[ModelTier.SOLO])
        global_limit = tier_config["agent_executions_per_hour"]
        
        allowed, metadata = await self.check_limit(
            identifier=customer_id,
            tier=tier,
            window="hour",
            scope="agent_execution"
        )
        
        if not allowed:
            metadata["reason"] = "Global agent execution limit exceeded"
            return False, metadata
        
        # Check agent-specific limit if configured
        agent_config = self.config.AGENT_LIMITS.get(agent_id)
        if agent_config:
            tier_limits = agent_config["executions_per_hour"]
            agent_limit = tier_limits.get(tier.lower(), tier_limits.get("solo", 5))
            
            key = self._get_key(f"{customer_id}:{agent_id}", "hour", "agent_specific")
            
            current_time = time.time()
            window_start = current_time - 3600  # 1 hour
            
            try:
                self.redis.zremrangebyscore(key, 0, window_start)
                current_count = self.redis.zcard(key)
                
                if current_count >= agent_limit:
                    metadata = {
                        "limit": agent_limit,
                        "remaining": 0,
                        "reset": int(current_time + 3600),
                        "agent_id": agent_id,
                        "tier": tier,
                        "reason": f"Agent-specific limit exceeded for {agent_id}"
                    }
                    logger.warning(f"Agent limit exceeded: {customer_id} - {agent_id} ({current_count}/{agent_limit})")
                    return False, metadata
                
                self.redis.zadd(key, {str(current_time): current_time})
                self.redis.expire(key, 7200)  # 2 hours
                
                metadata["agent_limit"] = agent_limit
                metadata["agent_remaining"] = agent_limit - current_count - 1
                
            except Exception as e:
                logger.error(f"Redis error checking agent limit: {e}")
                # Fail open
                pass
        
        return True, metadata
    
    async def check_concurrent_limit(
        self,
        customer_id: str,
        tier: str
    ) -> Tuple[bool, int]:
        """
        Check concurrent execution limit for customer tier
        
        Args:
            customer_id: Customer identifier
            tier: Customer tier
        
        Returns:
            Tuple of (allowed: bool, current_count: int)
        """
        try:
            tier_enum = ModelTier(tier.lower())
        except ValueError:
            tier_enum = ModelTier.SOLO
        
        tier_config = self.config.TIER_LIMITS.get(tier_enum, self.config.TIER_LIMITS[ModelTier.SOLO])
        max_concurrent = tier_config["concurrent_executions"]
        
        key = f"concurrent:{customer_id}"
        
        try:
            current_count = int(self.redis.get(key) or 0)
            
            if current_count >= max_concurrent:
                logger.warning(
                    f"Concurrent limit exceeded for {customer_id} (tier: {tier})",
                    extra={"current": current_count, "max": max_concurrent}
                )
                return False, current_count
            
            return True, current_count
            
        except Exception as e:
            logger.error(f"Redis error checking concurrent limit: {e}")
            return True, 0  # Fail open
    
    async def check_token_limit(
        self,
        customer_id: str,
        tier: str,
        tokens_to_use: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if customer is within daily token limit
        
        Args:
            customer_id: Customer identifier
            tier: Customer tier
            tokens_to_use: Number of tokens for this request
        
        Returns:
            Tuple of (allowed: bool, metadata: dict)
        """
        try:
            tier_enum = ModelTier(tier.lower())
        except ValueError:
            tier_enum = ModelTier.SOLO
        
        tier_config = self.config.TIER_LIMITS.get(tier_enum, self.config.TIER_LIMITS[ModelTier.SOLO])
        max_tokens = tier_config.get("max_tokens_per_day")
        
        # BYOK tier has unlimited tokens
        if max_tokens is None:
            return True, {"limit": None, "used": 0, "remaining": None}
        
        key = f"tokens:{customer_id}:day"
        
        try:
            current_tokens = int(self.redis.get(key) or 0)
            
            if current_tokens + tokens_to_use > max_tokens:
                metadata = {
                    "limit": max_tokens,
                    "used": current_tokens,
                    "remaining": max(0, max_tokens - current_tokens),
                    "requested": tokens_to_use,
                    "tier": tier
                }
                logger.warning(f"Token limit exceeded for {customer_id}: {current_tokens}/{max_tokens}")
                return False, metadata
            
            metadata = {
                "limit": max_tokens,
                "used": current_tokens,
                "remaining": max_tokens - current_tokens - tokens_to_use,
                "tier": tier
            }
            
            return True, metadata
            
        except Exception as e:
            logger.error(f"Redis error checking token limit: {e}")
            return True, {"limit": max_tokens, "used": 0, "remaining": max_tokens}
    
    async def record_token_usage(
        self,
        customer_id: str,
        tokens_used: int
    ) -> int:
        """
        Record token usage for daily tracking
        
        Args:
            customer_id: Customer identifier
            tokens_used: Number of tokens used
        
        Returns:
            Total tokens used today
        """
        key = f"tokens:{customer_id}:day"
        
        try:
            # Increment token counter
            total = self.redis.incrby(key, tokens_used)
            
            # Set expiry to end of day (86400 seconds = 24 hours)
            ttl = self.redis.ttl(key)
            if ttl == -1:  # No expiry set
                self.redis.expire(key, 86400)
            
            return total
            
        except Exception as e:
            logger.error(f"Redis error recording token usage: {e}")
            return tokens_used
    
    async def increment_concurrent(self, customer_id: str) -> int:
        """Increment concurrent execution counter"""
        key = f"concurrent:{customer_id}"
        
        try:
            count = self.redis.incr(key)
            self.redis.expire(key, 3600)  # Auto-expire after 1 hour as safety
            return count
        except Exception as e:
            logger.error(f"Redis error incrementing concurrent: {e}")
            return 1
    
    async def decrement_concurrent(self, customer_id: str) -> int:
        """Decrement concurrent execution counter"""
        key = f"concurrent:{customer_id}"
        
        try:
            count = self.redis.decr(key)
            if count <= 0:
                self.redis.delete(key)
            return max(0, count)
        except Exception as e:
            logger.error(f"Redis error decrementing concurrent: {e}")
            return 0
    
    def _get_window_seconds(self, window: str) -> int:
        """Convert window name to seconds"""
        windows = {
            "minute": 60,
            "hour": 3600,
            "day": 86400
        }
        return windows.get(window, 60)
    
    async def get_usage_stats(self, customer_id: str, tier: str) -> Dict[str, Any]:
        """
        Get current usage statistics for a customer
        
        Args:
            customer_id: Customer identifier
            tier: Customer tier
        
        Returns:
            Dictionary with usage statistics
        """
        try:
            tier_enum = ModelTier(tier.lower())
        except ValueError:
            tier_enum = ModelTier.SOLO
        
        tier_config = self.config.TIER_LIMITS.get(tier_enum, self.config.TIER_LIMITS[ModelTier.SOLO])
        
        stats = {
            "tier": tier,
            "limits": tier_config,
            "current_usage": {}
        }
        
        try:
            # Get request counts for each window
            for window in ["minute", "hour", "day"]:
                key = self._get_key(customer_id, window, "global")
                count = self.redis.zcard(key)
                limit_key = f"requests_per_{window}"
                stats["current_usage"][f"requests_{window}"] = {
                    "used": count,
                    "limit": tier_config.get(limit_key, 0),
                    "remaining": max(0, tier_config.get(limit_key, 0) - count)
                }
            
            # Get concurrent executions
            concurrent_key = f"concurrent:{customer_id}"
            concurrent_count = int(self.redis.get(concurrent_key) or 0)
            stats["current_usage"]["concurrent_executions"] = {
                "used": concurrent_count,
                "limit": tier_config["concurrent_executions"],
                "remaining": max(0, tier_config["concurrent_executions"] - concurrent_count)
            }
            
            # Get token usage
            token_key = f"tokens:{customer_id}:day"
            tokens_used = int(self.redis.get(token_key) or 0)
            max_tokens = tier_config.get("max_tokens_per_day")
            stats["current_usage"]["tokens_today"] = {
                "used": tokens_used,
                "limit": max_tokens,
                "remaining": None if max_tokens is None else max(0, max_tokens - tokens_used)
            }
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
        
        return stats
    
    async def reset_limits(self, customer_id: str):
        """Reset all rate limits for a customer (admin function)"""
        try:
            pattern = f"ratelimit:*:{customer_id}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            
            # Reset concurrent counter
            self.redis.delete(f"concurrent:{customer_id}")
            
            # Reset token counter
            self.redis.delete(f"tokens:{customer_id}:day")
            
            logger.info(f"Reset all rate limits for customer {customer_id}")
        except Exception as e:
            logger.error(f"Error resetting limits: {e}")


def rate_limit(
    window: str = "minute",
    scope: str = "global"
):
    """
    Decorator for rate limiting endpoints
    
    Usage:
        @rate_limit(window="minute", scope="api")
        async def my_endpoint(request: Request, customer: Customer):
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and customer info from args/kwargs
            request = None
            customer = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                request = kwargs.get("request")
            
            # Try to get customer from kwargs
            customer = kwargs.get("customer")
            
            if not customer and request:
                # Get customer info from request state (set by auth middleware)
                customer = getattr(request.state, "customer", None)
            
            # Determine identifier and tier
            if customer:
                customer_id = str(customer.id)
                tier = customer.tier if hasattr(customer, 'tier') else "solo"
            elif request:
                customer_id = request.client.host
                tier = "solo"
            else:
                customer_id = "unknown"
                tier = "solo"
            
            # Get rate limiter from app state
            if request:
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
                            detail={
                                "error": "Rate limit exceeded",
                                "message": f"You have exceeded the rate limit for your {tier} tier",
                                "metadata": metadata
                            },
                            headers={
                                "X-RateLimit-Limit": str(metadata["limit"]),
                                "X-RateLimit-Remaining": str(metadata["remaining"]),
                                "X-RateLimit-Reset": str(metadata["reset"]),
                                "Retry-After": str(metadata.get("retry_after", 60))
                            }
                        )
                    
                    # Add rate limit headers to response metadata
                    if request:
                        request.state.rate_limit_metadata = metadata
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Singleton instance
_rate_limiter_instance: Optional[AdvancedRateLimiter] = None


def get_rate_limiter(redis_client: Redis) -> AdvancedRateLimiter:
    """Get or create rate limiter singleton"""
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        _rate_limiter_instance = AdvancedRateLimiter(redis_client)
    return _rate_limiter_instance
