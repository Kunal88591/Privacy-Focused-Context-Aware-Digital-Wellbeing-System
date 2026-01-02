"""
Caching Configuration and Utilities
Redis-based caching for improved API performance
"""

import json
import logging
from typing import Optional, Any
from functools import wraps
import hashlib

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching operations with Redis"""
    
    def __init__(self, redis_client=None):
        """Initialize cache manager with optional Redis client"""
        self.redis_client = redis_client
        self.enabled = redis_client is not None
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        # Create string representation of arguments
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        # Hash for consistent key length
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                self.hits += 1
                return json.loads(value)
            self.misses += 1
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (default 5 minutes)"""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear(self, pattern: str = "*"):
        """Clear cache keys matching pattern"""
        if not self.enabled:
            return False
        
        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis_client.scan(cursor, match=pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                if cursor == 0:
                    break
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_stats(self):
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "enabled": self.enabled,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2)
        }


def cached(ttl: int = 300, key_prefix: str = "cache"):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get cache manager from app state
            # In actual implementation, this would be injected
            cache = getattr(func, '_cache_manager', None)
            
            if cache and cache.enabled:
                # Generate cache key
                cache_key = cache._generate_key(key_prefix, *args, **kwargs)
                
                # Try to get from cache
                cached_result = await cache.get(cache_key)
                if cached_result is not None:
                    logger.debug(f"Cache HIT for {func.__name__}")
                    return cached_result
                
                logger.debug(f"Cache MISS for {func.__name__}")
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            if cache and cache.enabled:
                await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Global cache manager instance
cache_manager = CacheManager()
