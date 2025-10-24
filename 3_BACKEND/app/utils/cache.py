import json
import logging
from typing import Optional, Any
from functools import wraps
import hashlib

logger = logging.getLogger('valora.cache')

# In-memory cache as fallback
_memory_cache = {}

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed, using in-memory cache")


class CacheManager:
    """Unified cache manager supporting Redis and in-memory fallback"""
    
    def __init__(self, redis_url: Optional[str] = None, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self.redis_client = None
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                self.redis_client.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}, using in-memory cache")
                self.redis_client = None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = f"{prefix}:{str(args)}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # In-memory fallback
                if key in _memory_cache:
                    return _memory_cache[key]['value']
        except Exception as e:
            logger.error(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        ttl = ttl or self.default_ttl
        try:
            serialized = json.dumps(value)
            
            if self.redis_client:
                self.redis_client.setex(key, ttl, serialized)
            else:
                # In-memory fallback (simplified, no actual expiration)
                _memory_cache[key] = {'value': value, 'ttl': ttl}
            
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            else:
                _memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern (Redis only)"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return 0


# Global cache instance
cache_manager: Optional[CacheManager] = None


def init_cache(redis_url: Optional[str] = None, default_ttl: int = 300):
    """Initialize global cache manager"""
    global cache_manager
    cache_manager = CacheManager(redis_url, default_ttl)
    return cache_manager


def cached(ttl: int = 300, key_prefix: str = "valora"):
    """Decorator for caching function results"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not cache_manager:
                return await func(*args, **kwargs)
            
            # Generate cache key
            cache_key = cache_manager._generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Execute function and cache result
            logger.debug(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not cache_manager:
                return func(*args, **kwargs)
            
            cache_key = cache_manager._generate_key(
                f"{key_prefix}:{func.__name__}",
                *args,
                **kwargs
            )
            
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
