# VALORA API Optimization Guide

## 🔧 Immediate Fixes

### 1. Blockchain Configuration
```bash
# Option 1: Use proper smart contract
APP_ID=123456  # Replace with actual deployed contract ID

# Option 2: Accept simple payments (current setup is fine)
APP_ID=1  # Keep as is, but update code logic
```

### 2. CORS Security (Production)
```python
# In main.py, replace broad CORS with:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://api.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Correlation-ID"],
    expose_headers=["X-Correlation-ID", "X-Response-Time"]
)
```

### 3. Rate Limiting Enhancement
```python
# Switch to Redis-based rate limiting
RATE_LIMIT_CONFIG = {
    "storage": "redis://localhost:6379/1",
    "strategies": [
        {"window": "minute", "limit": 60},
        {"window": "hour", "limit": 1000},
        {"window": "day", "limit": 10000}
    ]
}
```

## 🚀 Performance Optimizations

### 1. Response Caching
```python
# Add response caching middleware
@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    if request.method == "GET":
        cache_key = f"cache:{request.url.path}:{hash(str(request.query_params))}"
        cached = await redis.get(cache_key)
        if cached:
            return Response(cached, media_type="application/json")
    
    response = await call_next(request)
    # Cache GET responses for 5 minutes
    if request.method == "GET" and response.status_code == 200:
        await redis.setex(cache_key, 300, response.body)
    return response
```

### 2. Database Connection Pooling
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 3. Async Database Operations
```python
# Use async SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

async_engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/valora"
)
```

## 🔒 Security Enhancements

### 1. Request Size Limiting
```python
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_size_bytes=1024 * 1024  # 1MB limit
)
```

### 2. IP-based Security
```python
# Block suspicious IPs
BLOCKED_IPS = set()
SUSPICIOUS_PATTERNS = [
    "sql injection patterns",
    "xss patterns"
]
```

### 3. JWT Enhancement
```python
# Stronger JWT configuration
JWT_CONFIG = {
    "algorithm": "RS256",  # Use RSA instead of HS256
    "expire_minutes": 30,   # Shorter expiry
    "refresh_enabled": True
}
```

## 📊 Monitoring & Observability

### 1. Health Check Enhancement
```python
@app.get("/api/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0",
        "services": {
            "database": await check_db_health(),
            "redis": await check_redis_health(),
            "blockchain": await check_blockchain_health()
        },
        "metrics": {
            "uptime_seconds": get_uptime(),
            "active_connections": get_connection_count()
        }
    }
```

### 2. Structured Logging
```python
# Enhanced logging with ELK stack compatibility
LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "correlation_id": "%(correlation_id)s", "message": "%(message)s", "service": "valora-backend"}'
        }
    }
}
```

### 3. Metrics Collection
```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🔄 Deployment Optimizations

### 1. Docker Configuration
```dockerfile
# Multi-stage build
FROM python:3.9-slim as builder
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

FROM python:3.9-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links /wheels -r requirements.txt
```

### 2. Uvicorn Production Settings
```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --loop uvloop
```

### 3. Environment-specific Configs
```python
# config/production.py
CORS_ORIGINS = ["https://yourdomain.com"]
RATE_LIMIT_PER_MINUTE = 100
LOG_LEVEL = "WARNING"
DEBUG = False

# config/development.py  
CORS_ORIGINS = ["*"]
RATE_LIMIT_PER_MINUTE = 1000
LOG_LEVEL = "DEBUG" 
DEBUG = True
```

## 📈 Current Performance Profile
- **Response Time**: 7.91ms (excellent)
- **Rate Limit**: 60/min (9 used in window)
- **CORS**: Properly configured for dev
- **Tracing**: Full correlation ID support
- **Blockchain**: Needs APP_ID fix

## Next Steps
1. Fix blockchain APP_ID configuration
2. Implement Redis rate limiting
3. Add response caching
4. Set up monitoring dashboard
5. Configure production CORS policies