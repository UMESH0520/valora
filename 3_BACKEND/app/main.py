from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

from app.routes import health_route, price_routes, auth_routes
from app.routes import product_routes
from app.routes import blockchain_routes
from app.database import init_db
from app.config.logging_config import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware, PerformanceMonitoringMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
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

# Create FastAPI app
app = FastAPI(
    title='VALORA Backend - Enhanced',
    version='2.0',
    description='Price comparison and aggregation service with blockchain integration',
    docs_url='/docs',
    redoc_url='/redoc'
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        os.getenv('FRONTEND_URL', '')
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', '60')),
    requests_per_hour=int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))
)

# Performance monitoring
app.add_middleware(PerformanceMonitoringMiddleware)

# Request/response logging
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health_route.router)
app.include_router(auth_routes.router)
app.include_router(price_routes.router)
app.include_router(product_routes.router)
app.include_router(blockchain_routes.router)

@app.get('/')
async def root():
    """Root endpoint"""
    return {
        'service': 'VALORA Backend',
        'version': '2.0',
        'status': 'running',
        'docs': '/docs'
    }
