"""
Caching Module

This module provides caching utilities for agent execution results.
"""

import json
import hashlib
from typing import Any, Optional
from datetime import timedelta
import redis
from core.config import settings
from core.logging import get_logger


logger = get_logger(__name__)


class CacheManager:
    """
    Manages caching of agent execution results.
    """
    
    def __init__(self):
        """Initialize cache manager with Redis connection."""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Redis cache connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def _generate_cache_key(self, package_id: str, task_input: dict) -> str:
        """
        Generate a cache key from package ID and task input.
        
        Args:
            package_id: Agent package identifier
            task_input: Task input data
            
        Returns:
            Cache key string
        """
        # Create a deterministic hash of the input
        input_str = json.dumps(task_input, sort_keys=True)
        input_hash = hashlib.sha256(input_str.encode()).hexdigest()
        return f"agent:{package_id}:{input_hash}"
    
    def get(self, package_id: str, task_input: dict) -> Optional[dict]:
        """
        Get cached result for agent execution.
        
        Args:
            package_id: Agent package identifier
            task_input: Task input data
            
        Returns:
            Cached result or None if not found
        """
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(package_id, task_input)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"Cache hit for {package_id}")
                return json.loads(cached_data)
            
            logger.debug(f"Cache miss for {package_id}")
            return None
        
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(
        self,
        package_id: str,
        task_input: dict,
        result: dict,
        ttl: int = 3600
    ) -> bool:
        """
        Cache agent execution result.
        
        Args:
            package_id: Agent package identifier
            task_input: Task input data
            result: Execution result to cache
            ttl: Time to live in seconds (default 1 hour)
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(package_id, task_input)
            result_json = json.dumps(result)
            
            self.redis_client.setex(
                cache_key,
                ttl,
                result_json
            )
            
            logger.info(f"Cached result for {package_id} (TTL: {ttl}s)")
            return True
        
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, package_id: str, task_input: dict) -> bool:
        """
        Delete cached result.
        
        Args:
            package_id: Agent package identifier
            task_input: Task input data
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(package_id, task_input)
            self.redis_client.delete(cache_key)
            logger.info(f"Deleted cache for {package_id}")
            return True
        
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_package_cache(self, package_id: str) -> int:
        """
        Clear all cached results for a package.
        
        Args:
            package_id: Agent package identifier
            
        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            return 0
        
        try:
            pattern = f"agent:{package_id}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries for {package_id}")
                return deleted
            
            return 0
        
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Cache statistics
        """
        if not self.redis_client:
            return {"status": "disconnected"}
        
        try:
            info = self.redis_client.info("stats")
            
            return {
                "status": "connected",
                "total_keys": self.redis_client.dbsize(),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"status": "error", "error": str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100


# Global cache manager instance
cache_manager = CacheManager()

