# VALORA Backend v2.0 - Enhanced Edition

## 🚀 Quick Start

```powershell
# 1. Setup virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
# Edit .env - IMPORTANT: Set JWT_SECRET_KEY!

# 4. Run server
python run.py
```

Server runs at: http://127.0.0.1:8000
API Docs: http://127.0.0.1:8000/docs

## ✨ What's New in v2.0

### 🔐 Authentication
- JWT-based user authentication
- Role-based access control (Admin/User/Viewer)
- Password hashing with bcrypt
- Token-based API access

### 🗄️ Database Layer
- SQLAlchemy ORM models
- Product catalog management
- Price history tracking
- User management
- Automatic migrations

### 🛒 More E-commerce Platforms
Now supporting **6 platforms**:
- Amazon
- Flipkart
- Myntra
- **Snapdeal** (NEW)
- **Ajio** (NEW)
- **Tata CLiQ** (NEW)

### 🧠 Smarter Price Aggregation
- Weighted averaging by confidence
- Time-decay for stale prices
- Advanced outlier detection
- Conservative pricing strategy

### ⛓️ Complete Blockchain Integration
- Full Algorand transaction support
- Automatic retry on failure
- Transaction confirmation tracking
- Graceful fallback when offline

### 📊 Monitoring & Observability
- Structured JSON logging
- Correlation IDs for request tracking
- Performance monitoring
- Slow request detection
- Rotating log files

### ⚡ Performance
- Redis caching (optional)
- In-memory fallback cache
- Connection pooling
- Async operation

### 🛡️ Security & Rate Limiting
- Rate limiting (60/min, 1000/hour)
- CORS configuration
- Input validation
- SQL injection protection
- Custom exception handling

## 📁 New Project Structure

```
3_BACKEND/
├── app/
│   ├── models/              # SQLAlchemy models (NEW)
│   │   ├── product.py
│   │   ├── price.py
│   │   └── user.py
│   ├── auth/                # Authentication (NEW)
│   │   ├── jwt_handler.py
│   │   ├── password.py
│   │   └── dependencies.py
│   ├── middleware/          # Middleware (NEW)
│   │   ├── logging_middleware.py
│   │   ├── rate_limit.py
│   │   └── exception_handler.py
│   ├── config/              # Configuration (NEW)
│   │   └── logging_config.py
│   ├── utils/               # Utilities (NEW)
│   │   └── cache.py
│   ├── adapters/            # Enhanced with 3 new adapters
│   │   ├── amazon.py
│   │   ├── flipkart.py
│   │   ├── myntra.py
│   │   ├── snapdeal.py     # NEW
│   │   ├── ajio.py         # NEW
│   │   └── tatacliq.py     # NEW
│   ├── ai/                  # Enhanced algorithms
│   │   ├── fetcher.py
│   │   ├── normalizer.py
│   │   └── aggregator.py   # Enhanced
│   ├── contracts/           # Complete blockchain
│   │   └── submitter.py    # Enhanced
│   ├── routes/              # API endpoints
│   │   ├── auth_routes.py  # NEW
│   │   ├── price_routes.py
│   │   └── health_route.py
│   ├── services/
│   │   └── price_service.py
│   ├── database.py          # NEW
│   ├── exceptions.py        # NEW
│   └── main.py              # Enhanced
├── logs/                    # NEW (auto-created)
├── requirements.txt         # Updated
├── .env.example             # Updated
├── ENHANCEMENTS.md          # NEW
└── README_V2.md             # This file
```

## 🔑 API Endpoints

### Authentication
```
POST   /api/auth/register    - Register new user
POST   /api/auth/login       - Login (get JWT token)
GET    /api/auth/me          - Get current user info
```

### Prices
```
POST   /api/price            - Get product price
GET    /api/health           - Health check
GET    /                     - API info
```

### Documentation
```
GET    /docs                 - Swagger UI
GET    /redoc                - ReDoc
```

## 🔧 Configuration

### Required Environment Variables
```bash
# Minimal setup
JWT_SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./valora.db
```

### Optional Environment Variables
```bash
# Blockchain
ALGOD_ADDRESS=https://testnet-api.algonode.cloud
ALGOD_API_TOKEN=
ORACLE_MNEMONIC=your-mnemonic-here
APP_ID=12345

# Caching
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# CORS
FRONTEND_URL=http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

## 📖 Usage Examples

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john",
    "password": "securepass123"
  }'
```

### 3. Get Price (with auth)
```bash
curl -X POST http://localhost:8000/api/price \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "product_id": "VAL-PRD-001",
    "margin_percent": 3.0
  }'
```

### 4. Get Price (without auth - public)
```bash
curl -X POST http://localhost:8000/api/price \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "VAL-PRD-001",
    "margin_percent": 3.0
  }'
```

## 📈 Response Headers

All responses include:
- `X-Correlation-ID` - Unique request ID for tracking
- `X-Response-Time` - Request duration in milliseconds
- `X-RateLimit-Limit` - Rate limit threshold
- `X-RateLimit-Remaining` - Remaining requests

## 🧪 Testing

```powershell
# Run all tests
pytest 4_TESTS -v

# Run with coverage
pytest 4_TESTS --cov=app --cov-report=html

# View coverage report
start htmlcov/index.html
```

## 📊 Monitoring

### Logs
- **Console**: Standard format for development
- **File**: JSON format at `logs/valora.log`
- **Errors**: Separate file at `logs/valora_errors.log`

### Metrics (via logs)
- Request/response times
- Error rates by type
- Cache hit/miss rates
- Rate limit violations
- Slow requests (>5 seconds)

## 🔒 Security Features

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based access control
3. **Password Security**: Bcrypt hashing (cost 12)
4. **Rate Limiting**: Prevents abuse
5. **Input Validation**: Pydantic models
6. **SQL Injection**: Protected by ORM
7. **CORS**: Configurable origins
8. **Error Handling**: No sensitive data leaks

## 🚦 Rate Limits

Default limits (configurable):
- **60 requests per minute** per IP
- **1000 requests per hour** per IP
- Health endpoint is exempt

Headers in response:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
Retry-After: 30  (if exceeded)
```

## 💾 Database

### SQLite (Default)
No setup required. Database file created automatically at `valora.db`.

### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/valora
```

### Tables
- `users` - User accounts
- `products` - Product catalog
- `prices` - Current prices
- `price_history` - Historical price data

## 🎯 Performance Tips

1. **Enable Redis caching**: Reduces scraping load by ~80%
2. **Configure rate limits**: Prevent abuse
3. **Monitor logs**: Check for slow requests
4. **Use PostgreSQL**: Better performance at scale
5. **Enable gzip**: Compress responses

## 🐛 Troubleshooting

### Import Errors
```powershell
pip install -r requirements.txt --upgrade
```

### Database Errors
```powershell
# Delete old database
del valora.db
# Restart server (auto-creates tables)
python run.py
```

### Redis Connection Failed
Redis is optional. The system will fall back to in-memory caching.

### Blockchain Errors
Blockchain integration is optional. Set environment variables only if you want blockchain features.

## 📚 Additional Documentation

- `ENHANCEMENTS.md` - Detailed changelog and migration guide
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Development

### Adding a New Adapter
1. Create `app/adapters/yoursite.py`
2. Implement `async def fetch(session, product)` function
3. Add to `ADAPTER_LIST` in `app/adapters/__init__.py`
4. Test and submit PR

### Code Style
- Follow existing patterns
- Add type hints
- Include docstrings
- Handle errors gracefully
- Log important events

## 📄 License

Same as parent project.

## 🆘 Support

For issues or questions:
1. Check `ENHANCEMENTS.md` for detailed docs
2. Review API docs at `/docs`
3. Check logs in `logs/` directory
4. Review error messages (include correlation ID)

---

**VALORA Backend v2.0** - Production-ready price aggregation with enterprise features
