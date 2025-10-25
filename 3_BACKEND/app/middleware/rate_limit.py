from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Callable, Dict
import time
import logging

from app.exceptions import RateLimitException

logger = logging.getLogger('valora.rate_limit')


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    For production, use Redis-based rate limiting
    """
    
    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory storage: {ip: {'minute': [(timestamp, count)], 'hour': [(timestamp, count)]}}
        self.rate_limit_data: Dict[str, Dict] = {}
    
    def _clean_old_requests(self, client_ip: str):
        """Remove old request records"""
        current_time = time.time()
        
        if client_ip not in self.rate_limit_data:
            self.rate_limit_data[client_ip] = {'minute': [], 'hour': []}
            return
        
        # Clean minute data (older than 60 seconds)
        self.rate_limit_data[client_ip]['minute'] = [
            (ts, count) for ts, count in self.rate_limit_data[client_ip]['minute']
            if current_time - ts < 60
        ]
        
        # Clean hour data (older than 3600 seconds)
        self.rate_limit_data[client_ip]['hour'] = [
            (ts, count) for ts, count in self.rate_limit_data[client_ip]['hour']
            if current_time - ts < 3600
        ]
    
    def _check_rate_limit(self, client_ip: str) -> tuple[bool, str, int]:
        """
        Check if client has exceeded rate limit
        Returns: (is_allowed, limit_type, retry_after_seconds)
        """
        self._clean_old_requests(client_ip)
        
        data = self.rate_limit_data[client_ip]
        current_time = time.time()
        
        # Count requests in last minute
        minute_requests = sum(count for ts, count in data['minute'])
        if minute_requests >= self.requests_per_minute:
            oldest_minute = min(ts for ts, _ in data['minute']) if data['minute'] else current_time
            retry_after = int(60 - (current_time - oldest_minute))
            return False, 'minute', retry_after
        
        # Count requests in last hour
        hour_requests = sum(count for ts, count in data['hour'])
        if hour_requests >= self.requests_per_hour:
            oldest_hour = min(ts for ts, _ in data['hour']) if data['hour'] else current_time
            retry_after = int(3600 - (current_time - oldest_hour))
            return False, 'hour', retry_after
        
        return True, '', 0
    
    def _record_request(self, client_ip: str):
        """Record a new request"""
        current_time = time.time()
        data = self.rate_limit_data[client_ip]
        
        # Add to minute tracking
        data['minute'].append((current_time, 1))
        
        # Add to hour tracking
        data['hour'].append((current_time, 1))
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Check rate limit
        is_allowed, limit_type, retry_after = self._check_rate_limit(client_ip)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for {client_ip}",
                extra={
                    'client_ip': client_ip,
                    'limit_type': limit_type,
                    'retry_after': retry_after,
                    'path': request.url.path
                }
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    'error': 'RateLimitExceeded',
                    'message': f'Too many requests. Retry after {retry_after} seconds.',
                    'retry_after': retry_after,
                    'limit_type': limit_type
                },
                headers={
                    'Retry-After': str(retry_after),
                    'X-RateLimit-Limit': str(self.requests_per_minute if limit_type == 'minute' else self.requests_per_hour),
                    'X-RateLimit-Remaining': '0'
                }
            )
        
        # Record request
        self._record_request(client_ip)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        minute_requests = sum(count for ts, count in self.rate_limit_data[client_ip]['minute'])
        response.headers['X-RateLimit-Limit'] = str(self.requests_per_minute)
        response.headers['X-RateLimit-Remaining'] = str(max(0, self.requests_per_minute - minute_requests))
        
        return response
