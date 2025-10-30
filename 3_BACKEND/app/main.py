from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.routes import health_route, price_routes, auth_routes
from app.routes import product_routes
from app.routes import blockchain_routes
from app.database import init_db
from app.config.logging_config import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware, PerformanceMonitoringMiddleware
from app.middleware.redis_rate_limit import RedisRateLimitMiddleware
from app.middleware.caching import ResponseCachingMiddleware
from app.middleware.security import (
    SecurityHeadersMiddleware, 
    RequestSizeLimitMiddleware, 
    IPSecurityMiddleware,
    CORSConfig,
    security_manager
)
from app.middleware.monitoring import MetricsMiddleware, health_checker, get_metrics_response
from app.middleware.exception_handler import (
    valora_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler
)
from app.exceptions import ValoraException
from app.utils.cache import init_cache
from app.seeds_frontend import seed_frontend_products

# Setup logging
setup_logging()
logger = logging.getLogger('valora.backend')

# Get environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Create FastAPI app
app = FastAPI(
    title='VALORA Backend - Enhanced',
    version='2.0',
    description='Price comparison and aggregation service with blockchain integration',
    docs_url='/docs' if ENVIRONMENT == 'development' else None,
    redoc_url='/redoc' if ENVIRONMENT == 'development' else None,
    openapi_url='/openapi.json' if ENVIRONMENT == 'development' else None
)

# Initialize database
@app.on_event('startup')
async def startup_event():
    """Initialize application on startup"""
    logger.info('Starting VALORA Backend...')
    
    # Initialize database
    try:
        init_db()
        logger.info('Database initialized successfully')
        # Seed products mirrored from frontend
        seed_frontend_products()
        logger.info('Frontend products seeded')
    except Exception as e:
        logger.error(f'Failed to initialize database: {e}')
    
    # Initialize cache
    redis_url = os.getenv('REDIS_URL')
    init_cache(redis_url=redis_url, default_ttl=300)
    logger.info('Cache initialized')

    # Start background price scheduler (auto-refresh DISPLAY price)
    try:
        from app.scheduler import scheduler
        scheduler.start()
        logger.info('Price scheduler started')
    except Exception as e:
        logger.error('Failed to start price scheduler: %s', e)

    # Log blockchain configuration status
    try:
        from app.contracts.submitter import ALGOD_ADDRESS, ORACLE_MNEMONIC, APP_ID
        bc_ok = bool(ALGOD_ADDRESS and ORACLE_MNEMONIC and APP_ID != 0)
        logger.info('Blockchain configured: %s (APP_ID=%s)', bc_ok, APP_ID)
    except Exception as e:
        logger.warning('Blockchain config check failed: %s', e)
    
    logger.info('VALORA Backend started successfully')

@app.on_event('shutdown')
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info('Shutting down VALORA Backend...')

# Add exception handlers
app.add_exception_handler(ValoraException, valora_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Add middleware (order matters - last added is executed first)
# Security headers (applied last, so they're added to all responses)
app.add_middleware(SecurityHeadersMiddleware, environment=ENVIRONMENT)

# CORS - environment-specific configuration
cors_config = CORSConfig.get_development_config() if ENVIRONMENT == 'development' else CORSConfig.get_production_config()
app.add_middleware(CORSMiddleware, **cors_config)

# Response caching (before rate limiting to cache efficiently)
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
app.add_middleware(
    ResponseCachingMiddleware,
    redis_url=redis_url,
    default_ttl=int(os.getenv('CACHE_DEFAULT_TTL', '300'))
)

# Rate limiting (Redis-based)
app.add_middleware(
    RedisRateLimitMiddleware,
    redis_url=os.getenv('REDIS_RATE_LIMIT_URL', 'redis://localhost:6379/1'),
    requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
    requests_per_hour=int(os.getenv('RATE_LIMIT_PER_HOUR', '1000')),
    requests_per_day=int(os.getenv('RATE_LIMIT_PER_DAY', '10000'))
)

# Request size limiting
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_size_bytes=int(os.getenv('MAX_REQUEST_SIZE', str(1024 * 1024)))  # 1MB default
)

# IP security (if enabled)
if os.getenv('ENABLE_IP_SECURITY', 'false').lower() == 'true':
    app.add_middleware(
        IPSecurityMiddleware,
        blocked_ips=security_manager.blocked_ips,
        allowed_ips=security_manager.allowed_ips
    )

# Metrics collection
app.add_middleware(MetricsMiddleware)

# Performance monitoring
app.add_middleware(PerformanceMonitoringMiddleware)

# Request/response logging (should be last, so it captures everything)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health_route.router)
app.include_router(auth_routes.router)
app.include_router(price_routes.router)
app.include_router(product_routes.router)
app.include_router(blockchain_routes.router)

@app.get('/', tags=["System"])
async def root():
    """Root endpoint"""
    return {
        'service': 'VALORA Backend',
        'version': '2.0',
        'status': 'running',
        'environment': ENVIRONMENT,
        'docs': '/docs' if ENVIRONMENT == 'development' else None
    }


@app.get('/api/health/detailed', tags=["System"])
async def detailed_health():
    """Detailed health check endpoint"""
    return await health_checker.get_comprehensive_health()


@app.get('/metrics', tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint"""
    return get_metrics_response()


@app.get('/api/admin/security/status', tags=["Admin","Security"])
async def security_status():
    """Get security configuration status"""
    return security_manager.get_security_status()


@app.post('/api/admin/security/block-ip', tags=["Admin","Security"])
async def block_ip(ip: str):
    """Block an IP address"""
    security_manager.add_blocked_ip(ip)
    return {'message': f'IP {ip} has been blocked'}


@app.post('/api/admin/security/unblock-ip', tags=["Admin","Security"])
async def unblock_ip(ip: str):
    """Unblock an IP address"""
    security_manager.remove_blocked_ip(ip)
    return {'message': f'IP {ip} has been unblocked'}


@app.get('/api/admin/cache/stats', tags=["Admin","Cache"])
async def cache_stats():
    """Get cache statistics"""
    from app.middleware.caching import CacheManager
    cache_manager = CacheManager()
    return cache_manager.get_cache_stats()


@app.post('/api/admin/cache/clear', tags=["Admin","Cache"])
async def clear_cache(pattern: str = "*"):
    """Clear cache entries matching pattern"""
    from app.middleware.caching import CacheManager
    cache_manager = CacheManager()
    cleared = cache_manager.clear_cache_pattern(pattern)
    return {'message': f'Cleared {cleared} cache entries matching pattern: {pattern}'}
