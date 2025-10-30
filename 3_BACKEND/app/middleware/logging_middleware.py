from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid
from typing import Callable

logger = logging.getLogger('valora.requests')


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses with correlation IDs"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID
        correlation_id = str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request started",
            extra={
                'correlation_id': correlation_id,
                'method': request.method,
                'path': request.url.path,
                'query_params': dict(request.query_params),
                'client_host': request.client.host if request.client else None,
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Request completed",
                extra={
                    'correlation_id': correlation_id,
                    'method': request.method,
                    'path': request.url.path,
                    'status_code': response.status_code,
                    'duration_ms': round(duration * 1000, 2),
                }
            )
            
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = correlation_id
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed",
                extra={
                    'correlation_id': correlation_id,
                    'method': request.method,
                    'path': request.url.path,
                    'duration_ms': round(duration * 1000, 2),
                    'error': str(e),
                },
                exc_info=True
            )
            raise


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring slow requests"""
    
    SLOW_REQUEST_THRESHOLD = 5.0  # seconds
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Log slow requests
        if duration > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"Slow request detected",
                extra={
                    'method': request.method,
                    'path': request.url.path,
                    'duration_ms': round(duration * 1000, 2),
                    'threshold_ms': self.SLOW_REQUEST_THRESHOLD * 1000,
                }
            )
        
        # Add performance header
        response.headers['X-Response-Time'] = f"{round(duration * 1000, 2)}ms"
        
        return response
