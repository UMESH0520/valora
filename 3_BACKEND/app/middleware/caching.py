import redis
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
import gzip

logger = logging.getLogger('valora.cache')


class ResponseCachingMiddleware(BaseHTTPMiddleware):
    """
    Redis-based response caching middleware
    Caches GET requests with configurable TTL and cache keys
    """
    
    def __init__(
        self,
        app,
        redis_url: str = "redis://localhost:6379/0",
        default_ttl: int = 300,  # 5 minutes
        cache_prefix: str = "valora:cache",
        enable_compression: bool = True,
        max_response_size: int = 1024 * 1024,  # 1MB
        cacheable_status_codes: set = None
    ):
        super().__init__(app)
        self.default_ttl = default_ttl
        self.cache_prefix = cache_prefix
        self.enable_compression = enable_compression
        self.max_response_size = max_response_size
        self.cacheable_status_codes = cacheable_status_codes or {200, 201, 202}
        
        # Initialize Redis connection
        try:
            self.redis = redis.from_url(redis_url, decode_responses=False)  # Keep binary for compression
            self.redis.ping()
            logger.info(f"Response cache connected to Redis: {redis_url}")
        except Exception as e:
            logger.warning(f"Redis cache connection failed: {e}. Caching disabled.")
            self.redis = None
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate unique cache key for request"""
        # Include method, path, query params, and relevant headers
        key_data = {
            'method': request.method,
            'path': str(request.url.path),
            'query': str(request.query_params),
            'accept': request.headers.get('Accept', ''),
            'content_type': request.headers.get('Content-Type', '')
        }
        
        # Create hash of the key data
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]
        
        return f"{self.cache_prefix}:{key_hash}"
    
    def _is_cacheable_request(self, request: Request) -> bool:
        """Determine if request should be cached"""
        # Only cache GET requests
        if request.method != "GET":
            return False
        
        # Skip certain paths
        skip_paths = [
            "/api/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/products",   # dynamic price list – always fresh
            "/api/price"       # dynamic price endpoints – always fresh
        ]
        
        if any(request.url.path.startswith(path) for path in skip_paths):
            return False
        
        # Skip requests with certain headers
        if request.headers.get("Cache-Control") == "no-cache":
            return False
        
        if request.headers.get("Authorization"):
            return False  # Don't cache authenticated requests
        
        return True
    
    def _is_cacheable_response(self, response: Response) -> bool:
        """Determine if response should be cached"""
        if response.status_code not in self.cacheable_status_codes:
            return False
        
        # Check response size
        if hasattr(response, 'body'):
            body_size = len(response.body) if response.body else 0
            if body_size > self.max_response_size:
                return False
        
        # Check cache-control headers
        cache_control = response.headers.get("Cache-Control", "")
        if "no-cache" in cache_control or "no-store" in cache_control:
            return False
        
        return True
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data using gzip"""
        if not self.enable_compression:
            return data
        
        try:
            return gzip.compress(data)
        except Exception as e:
            logger.warning(f"Compression failed: {e}")
            return data
    
    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress gzipped data"""
        if not self.enable_compression:
            return data
        
        try:
            return gzip.decompress(data)
        except Exception:
            # Data might not be compressed
            return data
    
    async def _get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached response from Redis"""
        if not self.redis:
            return None
        
        try:
            cached_data = self.redis.get(cache_key)
            if cached_data:
                # Decompress and deserialize
                decompressed = self._decompress_data(cached_data)
                response_data = json.loads(decompressed.decode())
                
                logger.debug(f"Cache hit for key: {cache_key}")
                return response_data
        except Exception as e:
            logger.warning(f"Failed to retrieve from cache: {e}")
        
        return None
    
    async def _store_cached_response(
        self, 
        cache_key: str, 
        response_data: Dict, 
        ttl: int
    ):
        """Store response in Redis cache"""
        if not self.redis:
            return
        
        try:
            # Serialize and compress
            serialized = json.dumps(response_data).encode()
            compressed = self._compress_data(serialized)
            
            # Store with TTL
            self.redis.setex(cache_key, ttl, compressed)
            logger.debug(f"Cached response for key: {cache_key}, TTL: {ttl}s")
        except Exception as e:
            logger.warning(f"Failed to store in cache: {e}")
    
    def _get_ttl_for_path(self, path: str) -> int:
        """Get TTL based on path patterns"""
        # Configure different TTLs for different endpoints
        ttl_mapping = {
            "/api/products": 600,      # 10 minutes
            "/api/prices": 300,        # 5 minutes  
            "/api/search": 180,        # 3 minutes
            "/api/categories": 1800,   # 30 minutes
        }
        
        for path_pattern, ttl in ttl_mapping.items():
            if path.startswith(path_pattern):
                return ttl
        
        return self.default_ttl
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Check if request should be cached
        if not self._is_cacheable_request(request):
            return await call_next(request)
        
        cache_key = self._generate_cache_key(request)
        
        # Try to get cached response
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            # Return cached response
            response = StarletteResponse(
                content=cached_response['body'],
                status_code=cached_response['status_code'],
                headers=cached_response['headers'],
                media_type=cached_response.get('media_type')
            )
            # Add cache headers
            response.headers['X-Cache'] = 'HIT'
            response.headers['X-Cache-Key'] = cache_key[:12] + "..."
            return response
        
        # Process request
        response = await call_next(request)
        
        # Check if response should be cached
        if self._is_cacheable_response(response):
            # Safely extract body for caching; skip streaming responses
            body_bytes = None
            try:
                if hasattr(response, 'body'):
                    body_bytes = response.body or b''
            except Exception:
                body_bytes = None

            if body_bytes is None:
                # Cannot cache streaming response safely
                response.headers['X-Cache'] = 'SKIP'
                response.headers['X-Cache-Key'] = cache_key[:12] + "..."
                return response

            # Prepare response data for caching
            response_data = {
                'body': body_bytes.decode(),
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'media_type': response.media_type
            }
            
            # Get TTL for this path
            ttl = self._get_ttl_for_path(request.url.path)
            
            # Store in cache
            await self._store_cached_response(cache_key, response_data, ttl)
            
            # Add cache headers
            response.headers['X-Cache'] = 'MISS'
            response.headers['X-Cache-TTL'] = str(ttl)
        else:
            response.headers['X-Cache'] = 'SKIP'
        
        response.headers['X-Cache-Key'] = cache_key[:12] + "..."
        return response


class CacheManager:
    """Utility class for cache management operations"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", cache_prefix: str = "valora:cache"):
        self.cache_prefix = cache_prefix
        try:
            self.redis = redis.from_url(redis_url, decode_responses=False)
            self.redis.ping()
        except Exception as e:
            logger.error(f"Cache manager Redis connection failed: {e}")
            self.redis = None
    
    def clear_cache_pattern(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern"""
        if not self.redis:
            return 0
        
        try:
            full_pattern = f"{self.cache_prefix}:*{pattern}*"
            keys = self.redis.keys(full_pattern)
            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries matching pattern: {pattern}")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Failed to clear cache pattern {pattern}: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis:
            return {'error': 'Redis not available'}
        
        try:
            info = self.redis.info('memory')
            keyspace = self.redis.info('keyspace')
            
            # Count cache keys
            cache_keys = self.redis.keys(f"{self.cache_prefix}:*")
            
            return {
                'total_cache_keys': len(cache_keys),
                'memory_used_bytes': info.get('used_memory', 0),
                'memory_used_human': info.get('used_memory_human', '0B'),
                'keyspace_hits': keyspace.get('keyspace_hits', 0),
                'keyspace_misses': keyspace.get('keyspace_misses', 0),
                'cache_hit_rate': self._calculate_hit_rate(
                    keyspace.get('keyspace_hits', 0),
                    keyspace.get('keyspace_misses', 0)
                )
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)