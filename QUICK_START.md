# VALORA - Quick Start Guide

## 🚀 Run Everything (Easiest Method)

### Option 1: Automated Startup Script
```powershell
# From the VALORA root directory
.\start-all.ps1
```

This will:
- ✅ Start the backend on http://127.0.0.1:8000
- ✅ Start the frontend on http://localhost:5173
- ✅ Open two PowerShell windows (one for each service)

### Option 2: Manual Startup

#### Terminal 1 - Backend
```powershell
cd 3_BACKEND
.\venv\Scripts\Activate.ps1
python run.py
```

#### Terminal 2 - Frontend  
```powershell
cd 2_FRONTEND
npm run dev
```

---

## 📡 Access Points

Once both services are running:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Main web application |
| **Backend API** | http://127.0.0.1:8000 | REST API endpoints |
| **API Docs** | http://127.0.0.1:8000/docs | Interactive Swagger UI |
| **ReDoc** | http://127.0.0.1:8000/redoc | Alternative API docs |

---

## 🔧 Initial Setup (First Time Only)

### Backend Setup
```powershell
cd 3_BACKEND

# 1. Create virtual environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements_simple.txt

# 4. Setup environment
copy .env.example .env
# Edit .env if needed (optional)
```

### Frontend Setup
```powershell
cd 2_FRONTEND

# Install dependencies
npm install
```

---

## ✨ What's Running?

### Backend Features
- ✅ **6 E-commerce Adapters** - Amazon, Flipkart, Myntra, Snapdeal, Ajio, Tata CLiQ
- ✅ **JWT Authentication** - Secure user auth
- ✅ **Price Aggregation** - Smart price comparison
- ✅ **Algorand Blockchain** - Price verification
- ✅ **Rate Limiting** - DDoS protection
- ✅ **Caching** - Fast responses
- ✅ **Structured Logging** - Production-ready monitoring

### Frontend Features
- ✅ **React + Vite** - Fast development
- ✅ **shadcn/ui** - Beautiful components
- ✅ **Tailwind CSS** - Modern styling
- ✅ **React Router** - Client-side routing
- ✅ **TanStack Query** - Data fetching
- ✅ **Razorpay** - Payment integration

---

## 🧪 Testing the Integration

### 1. Test Backend Health
```powershell
# In browser or curl
curl http://127.0.0.1:8000/api/health
```

Expected response:
```json
{
  "status": "ok"
}
```

### 2. Test Frontend
Open http://localhost:5173 in your browser. You should see the VALORA homepage.

### 3. Test Backend API (Get Price)
```powershell
# Using PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/price" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"product_id":"VAL-PRD-001","margin_percent":3.0}'
```

---

## 🛑 Stopping Services

### If using start-all.ps1:
- Press `Ctrl+C` in each PowerShell window

### Manual:
- Press `Ctrl+C` in each terminal running the services

---

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Reinstall dependencies
cd 3_BACKEND
.\venv\Scripts\Activate.ps1
pip install -r requirements_simple.txt --upgrade
```

### Frontend won't start
```powershell
# Reinstall dependencies
cd 2_FRONTEND
npm install --force
```

### Port already in use
```powershell
# Backend (port 8000)
netstat -ano | findstr :8000
# Kill process using PID from above
taskkill /PID <PID> /F

# Frontend (port 5173)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Can't connect to backend from frontend
- Make sure both services are running
- Check that backend is on http://127.0.0.1:8000
- Check CORS settings in `3_BACKEND/app/main.py`

---

## 📚 Next Steps

### For Users:
1. Open http://localhost:5173
2. Browse products
3. Compare prices
4. Make purchases

### For Developers:
1. Read `3_BACKEND/README_V2.md` for backend docs
2. Read `3_BACKEND/ENHANCEMENTS.md` for features
3. Check API docs at http://127.0.0.1:8000/docs
4. Explore code in `3_BACKEND/app/` and `2_FRONTEND/src/`

---

## 🔐 Authentication (Optional)

To use authenticated endpoints:

1. Register a user:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/register" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"test","email":"test@example.com","password":"password123"}'
```

2. Login and get token:
```powershell
$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"username":"test","password":"password123"}'

$token = $response.access_token
```

3. Use token in requests:
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/auth/me" `
  -Method GET `
  -Headers @{"Authorization"="Bearer $token"}
```

---

## 💡 Tips

- Keep both terminal windows open to see logs
- Use Swagger UI (http://127.0.0.1:8000/docs) to test APIs
- Frontend automatically reloads on code changes
- Backend reloads on code changes (via uvicorn --reload)
- Check `logs/` directory for detailed backend logs

---

## 🎉 You're All Set!

**Frontend**: http://localhost:5173  
**Backend**: http://127.0.0.1:8000  
**API Docs**: http://127.0.0.1:8000/docs

Happy coding! 🚀
