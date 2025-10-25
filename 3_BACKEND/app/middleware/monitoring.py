import time
import logging
import psutil
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
import redis
import sqlite3
from contextlib import asynccontextmanager

logger = logging.getLogger('valora.monitoring')


# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'client_type']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'status_code'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections_total',
    'Number of active connections'
)

CACHE_OPERATIONS = Counter(
    'cache_operations_total',
    'Cache operations',
    ['operation', 'result']  # operation: get/set, result: hit/miss/error
)

DATABASE_OPERATIONS = Counter(
    'database_operations_total',
    'Database operations',
    ['operation', 'table', 'result']
)

BLOCKCHAIN_OPERATIONS = Counter(
    'blockchain_operations_total',
    'Blockchain operations',
    ['operation', 'result']
)

SYSTEM_INFO = Info(
    'valora_system_info',
    'System information'
)

MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    ['type']  # total, available, used, percentage
)

CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

UPTIME_SECONDS = Gauge(
    'valora_uptime_seconds',
    'Application uptime in seconds'
)

ERROR_RATE = Gauge(
    'error_rate_per_minute',
    'Error rate per minute'
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all requests
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.start_time = time.time()
        self.error_timestamps: List[float] = []
    
    def _get_endpoint_name(self, request: Request) -> str:
        """Extract endpoint name for metrics"""
        path = request.url.path
        
        # Normalize paths with IDs
        if '/api/products/' in path and path.count('/') > 3:
            return '/api/products/{id}'
        if '/api/prices/' in path and path.count('/') > 3:
            return '/api/prices/{id}'
        if '/api/users/' in path and path.count('/') > 3:
            return '/api/users/{id}'
        
        return path
    
    def _get_client_type(self, request: Request) -> str:
        """Determine client type from User-Agent"""
        user_agent = request.headers.get('User-Agent', '').lower()
        
        if 'bot' in user_agent or 'crawler' in user_agent:
            return 'bot'
        elif 'mobile' in user_agent:
            return 'mobile'
        elif 'postman' in user_agent:
            return 'postman'
        elif 'curl' in user_agent:
            return 'curl'
        elif any(browser in user_agent for browser in ['chrome', 'firefox', 'safari', 'edge']):
            return 'browser'
        else:
            return 'unknown'
    
    def _update_error_rate(self):
        """Update error rate metric"""
        current_time = time.time()
        # Keep errors from last minute
        self.error_timestamps = [
            timestamp for timestamp in self.error_timestamps
            if current_time - timestamp < 60
        ]
        ERROR_RATE.set(len(self.error_timestamps))
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Update active connections
        ACTIVE_CONNECTIONS.inc()
        
        start_time = time.time()
        endpoint = self._get_endpoint_name(request)
        client_type = self._get_client_type(request)
        
        try:
            response = await call_next(request)
            status_code = str(response.status_code)
            
            # Track errors
            if response.status_code >= 400:
                self.error_timestamps.append(time.time())
                self._update_error_rate()
            
        except Exception as e:
            # Handle middleware exceptions
            logger.error(f"Request failed with exception: {e}")
            status_code = "500"
            self.error_timestamps.append(time.time())
            self._update_error_rate()
            raise
        finally:
            # Update metrics
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=status_code,
                client_type=client_type
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint,
                status_code=status_code
            ).observe(duration)
            
            ACTIVE_CONNECTIONS.dec()
            
            # Update uptime
            UPTIME_SECONDS.set(time.time() - self.start_time)
        
        return response


class HealthChecker:
    """
    Comprehensive health checking system
    """
    
    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            # For SQLite
            start_time = time.time()
            conn = sqlite3.connect('valora.db', timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time * 1000, 2),
                'type': 'sqlite'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'type': 'sqlite'
            }
    
    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and performance"""
        try:
            redis_url = "redis://localhost:6379/0"
            redis_client = redis.from_url(redis_url, socket_timeout=5)
            
            start_time = time.time()
            redis_client.ping()
            response_time = time.time() - start_time
            
            # Get Redis info
            info = redis_client.info()
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time * 1000, 2),
                'memory_usage_mb': round(info.get('used_memory', 0) / 1024 / 1024, 2),
                'connected_clients': info.get('connected_clients', 0),
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    async def check_blockchain_health(self) -> Dict[str, Any]:
        """Check blockchain connectivity"""
        try:
            from app.contracts.submitter import get_blockchain_status
            status = get_blockchain_status()
            
            if status['configured']:
                return {
                    'status': 'healthy',
                    'app_id': status['app_id'],
                    'method': status['method'],
                    'algod_address': status['algod_address'],
                    'algod_status': status.get('algod_status', 'unknown')
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': status['message']
                }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system resource metrics"""
        try:
            # Memory info
            memory = psutil.virtual_memory()
            MEMORY_USAGE.labels(type='total').set(memory.total)
            MEMORY_USAGE.labels(type='available').set(memory.available)
            MEMORY_USAGE.labels(type='used').set(memory.used)
            MEMORY_USAGE.labels(type='percentage').set(memory.percent)
            
            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            return {
                'memory': {
                    'total_gb': round(memory.total / 1024 / 1024 / 1024, 2),
                    'available_gb': round(memory.available / 1024 / 1024 / 1024, 2),
                    'used_gb': round(memory.used / 1024 / 1024 / 1024, 2),
                    'percentage': memory.percent
                },
                'cpu': {
                    'usage_percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'count_logical': psutil.cpu_count(logical=True)
                },
                'disk': {
                    'usage_percent': psutil.disk_usage('/').percent,
                    'free_gb': round(psutil.disk_usage('/').free / 1024 / 1024 / 1024, 2)
                }
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {'error': str(e)}
    
    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        uptime = datetime.now(timezone.utc) - self.start_time
        
        # Check all services
        database_health = await self.check_database_health()
        redis_health = await self.check_redis_health()
        blockchain_health = await self.check_blockchain_health()
        system_metrics = self.get_system_metrics()
        
        # Determine overall status
        all_healthy = all([
            database_health['status'] == 'healthy',
            redis_health['status'] == 'healthy',
            blockchain_health['status'] == 'healthy'
        ])
        
        return {
            'status': 'healthy' if all_healthy else 'degraded',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'uptime': {
                'seconds': int(uptime.total_seconds()),
                'human': str(uptime).split('.')[0]
            },
            'version': '2.0',
            'services': {
                'database': database_health,
                'redis': redis_health,
                'blockchain': blockchain_health
            },
            'system': system_metrics,
            'metrics_summary': {
                'total_requests': REQUEST_COUNT._value.sum(),
                'active_connections': ACTIVE_CONNECTIONS._value._value,
                'error_rate_per_minute': ERROR_RATE._value._value
            }
        }


# Initialize system info metric
SYSTEM_INFO.info({
    'version': '2.0',
    'python_version': f"{psutil.Process().memory_info()}",
    'startup_time': datetime.now(timezone.utc).isoformat()
})


class MetricsCollector:
    """
    Utility class for collecting custom metrics
    """
    
    @staticmethod
    def record_cache_operation(operation: str, result: str):
        """Record cache operation metric"""
        CACHE_OPERATIONS.labels(operation=operation, result=result).inc()
    
    @staticmethod
    def record_database_operation(operation: str, table: str, result: str):
        """Record database operation metric"""
        DATABASE_OPERATIONS.labels(operation=operation, table=table, result=result).inc()
    
    @staticmethod
    def record_blockchain_operation(operation: str, result: str):
        """Record blockchain operation metric"""
        BLOCKCHAIN_OPERATIONS.labels(operation=operation, result=result).inc()


# Global health checker instance
health_checker = HealthChecker()
metrics_collector = MetricsCollector()


def get_metrics_response() -> Response:
    """Generate Prometheus metrics response"""
    try:
        metrics_data = generate_latest()
        return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Failed to generate metrics: {e}")
        return Response(
            content=f"# Error generating metrics: {e}\n",
            media_type="text/plain",
            status_code=500
        )