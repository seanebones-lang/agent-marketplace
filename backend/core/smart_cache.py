"""
Advanced Caching Strategy with Smart Cache Decorator
Provides intelligent caching with TTL, invalidation, and tenant isolation
"""

import json
import hashlib
import logging
from typing import Any, Callable, Optional, Union, List
from functools import wraps
import asyncio
from datetime import datetime, timedelta
import aioredis
from redis import Redis

from backend.core.tenant_context import get_tenant_context

logger = logging.getLogger(__name__)


class CacheConfig:
    """Cache configuration"""
    DEFAULT_TTL = 300  # 5 minutes
    SHORT_TTL = 60  # 1 minute
    MEDIUM_TTL = 600  # 10 minutes
    LONG_TTL = 3600  # 1 hour
    VERY_LONG_TTL = 86400  # 24 hours


class SmartCache:
    """
    Advanced caching with tenant isolation and intelligent invalidation
    """
    
    def __init__(self, redis_client: Union[Redis, aioredis.Redis]):
        self.redis = redis_client
        self.config = CacheConfig()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _get_tenant_prefix(self) -> str:
        """Get tenant-specific cache prefix"""
        tenant_context = get_tenant_context()
        tenant_id = tenant_context.get_tenant()
        return f"cache:tenant:{tenant_id}" if tenant_id else "cache:global"
    
    def _generate_cache_key(
        self,
        namespace: str,
        key: str,
        args: tuple = (),
        kwargs: dict = None
    ) -> str:
        """
        Generate cache key with tenant isolation
        
        Args:
            namespace: Cache namespace (e.g., "agent_execution")
            key: Base key
            args: Function arguments
            kwargs: Function keyword arguments
        
        Returns:
            Tenant-prefixed cache key
        """
        tenant_prefix = self._get_tenant_prefix()
        
        # Create deterministic hash from args and kwargs
        if args or kwargs:
            arg_str = json.dumps({
                "args": args,
                "kwargs": kwargs or {}
            }, sort_keys=True, default=str)
            arg_hash = hashlib.sha256(arg_str.encode()).hexdigest()[:16]
            cache_key = f"{tenant_prefix}:{namespace}:{key}:{arg_hash}"
        else:
            cache_key = f"{tenant_prefix}:{namespace}:{key}"
        
        return cache_key
    
    async def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            namespace: Cache namespace
            key: Cache key
        
        Returns:
            Cached value or None
        """
        cache_key = self._generate_cache_key(namespace, key)
        
        try:
            if isinstance(self.redis, aioredis.Redis):
                cached_data = await self.redis.get(cache_key)
            else:
                cached_data = self.redis.get(cache_key)
            
            if cached_data:
                self._stats["hits"] += 1
                logger.debug(f"Cache hit: {cache_key}")
                return json.loads(cached_data)
            else:
                self._stats["misses"] += 1
                logger.debug(f"Cache miss: {cache_key}")
                return None
        
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        ttl: int = None
    ) -> bool:
        """
        Set value in cache
        
        Args:
            namespace: Cache namespace
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        
        Returns:
            True if successful
        """
        cache_key = self._generate_cache_key(namespace, key)
        ttl = ttl or self.config.DEFAULT_TTL
        
        try:
            serialized_value = json.dumps(value, default=str)
            
            if isinstance(self.redis, aioredis.Redis):
                await self.redis.setex(cache_key, ttl, serialized_value)
            else:
                self.redis.setex(cache_key, ttl, serialized_value)
            
            self._stats["sets"] += 1
            logger.debug(f"Cache set: {cache_key} (TTL: {ttl}s)")
            return True
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, namespace: str, key: str) -> bool:
        """Delete value from cache"""
        cache_key = self._generate_cache_key(namespace, key)
        
        try:
            if isinstance(self.redis, aioredis.Redis):
                await self.redis.delete(cache_key)
            else:
                self.redis.delete(cache_key)
            
            self._stats["deletes"] += 1
            logger.debug(f"Cache delete: {cache_key}")
            return True
        
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, namespace: str, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            namespace: Cache namespace
            pattern: Key pattern (e.g., "user:*")
        
        Returns:
            Number of keys deleted
        """
        tenant_prefix = self._get_tenant_prefix()
        full_pattern = f"{tenant_prefix}:{namespace}:{pattern}"
        
        try:
            if isinstance(self.redis, aioredis.Redis):
                keys = await self.redis.keys(full_pattern)
                if keys:
                    deleted = await self.redis.delete(*keys)
                else:
                    deleted = 0
            else:
                keys = self.redis.keys(full_pattern)
                if keys:
                    deleted = self.redis.delete(*keys)
                else:
                    deleted = 0
            
            logger.info(f"Cache pattern delete: {full_pattern} ({deleted} keys)")
            return deleted
        
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")
            return 0
    
    async def clear_namespace(self, namespace: str) -> int:
        """Clear all keys in namespace"""
        return await self.delete_pattern(namespace, "*")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = (self._stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self._stats,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2)
        }
    
    def cached(
        self,
        namespace: str,
        ttl: int = None,
        key_func: Optional[Callable] = None
    ):
        """
        Decorator for caching function results
        
        Args:
            namespace: Cache namespace
            ttl: Time to live in seconds
            key_func: Optional function to generate custom cache key
        
        Usage:
            @cache.cached(namespace="user_data", ttl=300)
            async def get_user_data(user_id: str):
                return fetch_from_db(user_id)
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = func.__name__
                
                # Try to get from cache
                cached_value = await self.get(namespace, cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.set(namespace, cache_key, result, ttl)
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = func.__name__
                
                # Try to get from cache (sync)
                cache_key_full = self._generate_cache_key(namespace, cache_key, args, kwargs)
                cached_data = self.redis.get(cache_key_full)
                
                if cached_data:
                    self._stats["hits"] += 1
                    return json.loads(cached_data)
                
                self._stats["misses"] += 1
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result (sync)
                ttl_value = ttl or self.config.DEFAULT_TTL
                serialized = json.dumps(result, default=str)
                self.redis.setex(cache_key_full, ttl_value, serialized)
                self._stats["sets"] += 1
                
                return result
            
            # Return appropriate wrapper
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator
    
    def invalidate_on_change(self, namespace: str, key_pattern: str):
        """
        Decorator to invalidate cache when function is called
        
        Usage:
            @cache.invalidate_on_change(namespace="user_data", key_pattern="user:*")
            async def update_user(user_id: str, data: dict):
                # Update logic
                pass
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                result = await func(*args, **kwargs)
                await self.delete_pattern(namespace, key_pattern)
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                result = func(*args, **kwargs)
                # Sync invalidation
                tenant_prefix = self._get_tenant_prefix()
                full_pattern = f"{tenant_prefix}:{namespace}:{key_pattern}"
                keys = self.redis.keys(full_pattern)
                if keys:
                    self.redis.delete(*keys)
                return result
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        
        return decorator


# Global cache instance
_cache_instance: Optional[SmartCache] = None


def get_cache() -> Optional[SmartCache]:
    """Get global cache instance"""
    return _cache_instance


def initialize_cache(redis_client: Union[Redis, aioredis.Redis]) -> SmartCache:
    """Initialize global cache instance"""
    global _cache_instance
    _cache_instance = SmartCache(redis_client)
    return _cache_instance


# Example usage
if __name__ == "__main__":
    import redis
    
    # Initialize cache
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    cache = initialize_cache(redis_client)
    
    # Use cache decorator
    @cache.cached(namespace="user_data", ttl=300)
    def get_user(user_id: str):
        print(f"Fetching user {user_id} from database...")
        return {"id": user_id, "name": "John Doe"}
    
    # First call - cache miss
    user1 = get_user("123")
    print(user1)
    
    # Second call - cache hit
    user2 = get_user("123")
    print(user2)
    
    # Get stats
    print(cache.get_stats())

