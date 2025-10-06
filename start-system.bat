@echo off
echo ========================================
echo   Procurement RAG System Startup
echo ========================================
echo.

echo [1/3] Starting Flask API Server...
start "Flask API Server" cmd /k "python app/api.py"
echo    ✓ Flask server starting on port 5000
echo.

echo [2/3] Waiting for server to initialize...
timeout /t 5 /nobreak > nul
echo    ✓ Server initialization complete
echo.

echo [3/3] Starting Cloudflare Tunnel...
echo    🌐 Creating global tunnel...
echo    📡 This will provide a global URL for your system
echo.

start "Cloudflare Tunnel" cmd /k ".\cloudflared tunnel --url http://127.0.0.1:5000"
echo.

echo ========================================
echo   System Status
echo ========================================
echo.
echo ✅ Flask API Server: Running on localhost:5000
echo ✅ Cloudflare Tunnel: Starting...
echo.
echo 📋 Next Steps:
echo    1. Wait for the tunnel to generate a URL
echo    2. Copy the tunnel URL from the tunnel window
echo    3. Access your system globally via that URL
echo.
echo 🔗 Local Access: http://localhost:5000
echo 🌐 Global Access: Check the tunnel window for URL
echo.
echo Press any key to exit this window...
pause > nul
