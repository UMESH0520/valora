import redis
import time
import json
import logging
from typing import Dict, Optional, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger('valora.rate_limit')


class RedisRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-based distributed rate limiting middleware
    Supports multiple time windows and better scalability
    """
    
    def __init__(
        self, 
        app, 
        redis_url: str = "redis://localhost:6379/1",
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
        key_prefix: str = "valora:ratelimit"
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.key_prefix = key_prefix
        
        # Initialize Redis connection
        try:
            self.redis = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis.ping()
            logger.info(f"Redis rate limiter connected to {redis_url}")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to in-memory rate limiting")
            self.redis = None
            self._fallback_storage: Dict[str, Dict] = {}
    
    def _get_client_key(self, request: Request) -> str:
        """Generate unique key for client identification"""
        # Use X-Forwarded-For if behind proxy, otherwise client IP
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        # Include user agent for better identification
        user_agent = request.headers.get("User-Agent", "")[:50]  # Truncate UA
        user_agent_hash = str(hash(user_agent))[:8]
        
        return f"{self.key_prefix}:{client_ip}:{user_agent_hash}"
    
    def _check_rate_limit_redis(self, client_key: str) -> Tuple[bool, str, int, Dict]:
        """Check rate limits using Redis with sliding window"""
        current_time = int(time.time())
        
        # Define time windows
        windows = [
            ("minute", 60, self.requests_per_minute),
            ("hour", 3600, self.requests_per_hour),
            ("day", 86400, self.requests_per_day)
        ]
        
        pipe = self.redis.pipeline()
        
        # Check all windows
        for window_name, window_seconds, limit in windows:
            key = f"{client_key}:{window_name}"
            window_start = current_time - window_seconds
            
            # Remove old entries and count current requests
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.expire(key, window_seconds)
        
        try:
            results = pipe.execute()
            
            # Process results (every 3rd item is the count)
            counts = [results[i] for i in range(1, len(results), 3)]
            
            # Check if any limit is exceeded
            for i, (window_name, window_seconds, limit) in enumerate(windows):
                current_count = counts[i]
                if current_count >= limit:
                    retry_after = window_seconds
                    return False, window_name, retry_after, {
                        'minute': counts[0] if len(counts) > 0 else 0,
                        'hour': counts[1] if len(counts) > 1 else 0,
                        'day': counts[2] if len(counts) > 2 else 0
                    }
            
            return True, "", 0, {
                'minute': counts[0] if len(counts) > 0 else 0,
                'hour': counts[1] if len(counts) > 1 else 0,
                'day': counts[2] if len(counts) > 2 else 0
            }
            
        except Exception as e:
            logger.error(f"Redis rate limit check failed: {e}")
            return True, "", 0, {}  # Allow request on Redis failure
    
    def _record_request_redis(self, client_key: str):
        """Record request in Redis"""
        current_time = time.time()
        
        # Record in all time windows
        windows = ["minute", "hour", "day"]
        pipe = self.redis.pipeline()
        
        for window in windows:
            key = f"{client_key}:{window}"
            pipe.zadd(key, {str(current_time): current_time})
        
        try:
            pipe.execute()
        except Exception as e:
            logger.error(f"Failed to record request in Redis: {e}")
    
    def _check_rate_limit_fallback(self, client_key: str) -> Tuple[bool, str, int, Dict]:
        """Fallback to in-memory rate limiting when Redis is unavailable"""
        current_time = time.time()
        
        if client_key not in self._fallback_storage:
            self._fallback_storage[client_key] = {'minute': [], 'hour': [], 'day': []}
        
        data = self._fallback_storage[client_key]
        
        # Clean old requests
        data['minute'] = [t for t in data['minute'] if current_time - t < 60]
        data['hour'] = [t for t in data['hour'] if current_time - t < 3600]
        data['day'] = [t for t in data['day'] if current_time - t < 86400]
        
        # Check limits
        counts = {
            'minute': len(data['minute']),
            'hour': len(data['hour']),
            'day': len(data['day'])
        }
        
        if counts['minute'] >= self.requests_per_minute:
            return False, 'minute', 60, counts
        if counts['hour'] >= self.requests_per_hour:
            return False, 'hour', 3600, counts
        if counts['day'] >= self.requests_per_day:
            return False, 'day', 86400, counts
        
        return True, '', 0, counts
    
    def _record_request_fallback(self, client_key: str):
        """Record request in fallback storage"""
        current_time = time.time()
        
        if client_key not in self._fallback_storage:
            self._fallback_storage[client_key] = {'minute': [], 'hour': [], 'day': []}
        
        data = self._fallback_storage[client_key]
        data['minute'].append(current_time)
        data['hour'].append(current_time)
        data['day'].append(current_time)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks and metrics
        if request.url.path in ["/api/health", "/metrics", "/docs", "/redoc"]:
            return await call_next(request)
        
        client_key = self._get_client_key(request)
        
        # Check rate limits
        if self.redis:
            is_allowed, limit_type, retry_after, counts = self._check_rate_limit_redis(client_key)
        else:
            is_allowed, limit_type, retry_after, counts = self._check_rate_limit_fallback(client_key)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded",
                extra={
                    'client_key': client_key,
                    'limit_type': limit_type,
                    'retry_after': retry_after,
                    'path': request.url.path,
                    'counts': counts
                }
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'RateLimitExceeded',
                    'message': f'Too many requests. Retry after {retry_after} seconds.',
                    'retry_after': retry_after,
                    'limit_type': limit_type,
                    'current_usage': counts
                },
                headers={
                    'Retry-After': str(retry_after),
                    'X-RateLimit-Limit-Minute': str(self.requests_per_minute),
                    'X-RateLimit-Limit-Hour': str(self.requests_per_hour),
                    'X-RateLimit-Limit-Day': str(self.requests_per_day),
                    'X-RateLimit-Remaining-Minute': str(max(0, self.requests_per_minute - counts.get('minute', 0))),
                    'X-RateLimit-Remaining-Hour': str(max(0, self.requests_per_hour - counts.get('hour', 0))),
                    'X-RateLimit-Remaining-Day': str(max(0, self.requests_per_day - counts.get('day', 0)))
                }
            )
        
        # Record request
        if self.redis:
            self._record_request_redis(client_key)
        else:
            self._record_request_fallback(client_key)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers.update({
            'X-RateLimit-Limit-Minute': str(self.requests_per_minute),
            'X-RateLimit-Limit-Hour': str(self.requests_per_hour),
            'X-RateLimit-Limit-Day': str(self.requests_per_day),
            'X-RateLimit-Remaining-Minute': str(max(0, self.requests_per_minute - counts.get('minute', 0))),
            'X-RateLimit-Remaining-Hour': str(max(0, self.requests_per_hour - counts.get('hour', 0))),
            'X-RateLimit-Remaining-Day': str(max(0, self.requests_per_day - counts.get('day', 0)))
        })
        
        return response


class RateLimitConfig:
    """Configuration for rate limiting"""
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/1",
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
        enable_redis: bool = True
    ):
        self.redis_url = redis_url
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.enable_redis = enable_redis