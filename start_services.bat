@echo off
echo ========================================
echo 🚀 Starting VALORA Services
echo ========================================
echo.

echo 🔧 Starting Backend Service...
echo Opening new window for Backend API (Port 8001)
start "VALORA Backend" cmd /k "cd /d C:\Users\shrav\Downloads\valora\3_BACKEND && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"

echo.
echo ⏳ Waiting 5 seconds for backend to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 🎨 Starting Frontend Service...
echo Opening new window for Frontend App (Port 5173)
start "VALORA Frontend" cmd /k "cd /d C:\Users\shrav\Downloads\valora\2_FRONTEND && npm run dev"

echo.
echo ✅ Both services are starting!
echo.
echo 📊 Service URLs:
echo    🔧 Backend API:     http://127.0.0.1:8001
echo    📚 API Docs:        http://127.0.0.1:8001/docs  
echo    🎨 Frontend App:    http://127.0.0.1:5173
echo.
echo 🔗 Blockchain Features:
echo    • Algorand Testnet integration
echo    • Real-time price updates
echo    • Blockchain verification badges
echo    • Manual price refresh buttons
echo.
echo 🎉 Services launched in separate windows!
echo Close this window or press any key to exit...
pause