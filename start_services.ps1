# VALORA Services Startup Script
# This script starts both the backend and frontend services simultaneously

Write-Host "🚀 Starting VALORA Services..." -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Function to start a service in a new window
function Start-ServiceInNewWindow {
    param(
        [string]$Title,
        [string]$Path,
        [string]$Command,
        [string]$Color = "Blue"
    )
    
    Write-Host "Starting $Title..." -ForegroundColor $Color
    
    # Start the service in a new PowerShell window
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "Set-Location '$Path'; Write-Host '$Title Starting...' -ForegroundColor $Color; $Command"
    ) -WindowStyle Normal
}

# Start Backend Service
Write-Host ""
Write-Host "🔧 Backend Service (Port 8001)" -ForegroundColor Cyan
Start-ServiceInNewWindow -Title "VALORA Backend" -Path "C:\Users\shrav\Downloads\valora\3_BACKEND" -Command "python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload" -Color "Cyan"

# Wait a moment for backend to start
Write-Host "⏳ Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend Service
Write-Host ""
Write-Host "🎨 Frontend Service (Port 5173)" -ForegroundColor Magenta
Start-ServiceInNewWindow -Title "VALORA Frontend" -Path "C:\Users\shrav\Downloads\valora\2_FRONTEND" -Command "npm run dev" -Color "Magenta"

# Display service information
Write-Host ""
Write-Host "✅ Services Starting..." -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service URLs:" -ForegroundColor White
Write-Host "   🔧 Backend API:     http://127.0.0.1:8001" -ForegroundColor Cyan
Write-Host "   📚 API Docs:        http://127.0.0.1:8001/docs" -ForegroundColor Cyan
Write-Host "   🎨 Frontend App:    http://127.0.0.1:5173" -ForegroundColor Magenta
Write-Host "   🌐 Frontend (Vite): http://localhost:5173" -ForegroundColor Magenta
Write-Host ""

Write-Host "🔗 Blockchain Integration:" -ForegroundColor Green
Write-Host "   ✅ Algorand Testnet configured" -ForegroundColor Green
Write-Host "   💰 Wallet balance: 20 ALGO" -ForegroundColor Green
Write-Host "   🏷️  APP_ID: 1 (Simple transactions)" -ForegroundColor Green
Write-Host ""

Write-Host "📝 Features Available:" -ForegroundColor Yellow
Write-Host "   • Real-time price updates via WebSocket" -ForegroundColor Yellow
Write-Host "   • Blockchain price verification" -ForegroundColor Yellow
Write-Host "   • Manual price refresh buttons" -ForegroundColor Yellow
Write-Host "   • Confidence indicators" -ForegroundColor Yellow
Write-Host "   • Verification badges" -ForegroundColor Yellow
Write-Host ""

Write-Host "🛠️  Development Notes:" -ForegroundColor DarkGray
Write-Host "   • Backend runs with auto-reload" -ForegroundColor DarkGray
Write-Host "   • Frontend runs with hot-reload" -ForegroundColor DarkGray
Write-Host "   • Redis is disabled (using in-memory caching)" -ForegroundColor DarkGray
Write-Host ""

Write-Host "🎉 Both services are starting in separate windows!" -ForegroundColor Green
Write-Host "Close this window or press Ctrl+C to stop monitoring." -ForegroundColor White

# Keep this window open to show status
Write-Host ""
Write-Host "Press any key to exit this status window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")