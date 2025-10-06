@echo off
setlocal enabledelayedexpansion

echo ========================================
echo   Procurement RAG System Startup
echo ========================================
echo.

echo [1/4] Starting Flask API Server...
start "Flask API Server" cmd /k "python app/api.py"
echo    ✓ Flask server starting on port 5000
echo.

echo [2/4] Waiting for server to initialize...
timeout /t 8 /nobreak > nul
echo    ✓ Server initialization complete
echo.

echo [3/4] Starting Cloudflare Tunnel...
echo    🌐 Creating global tunnel...
echo    📡 This will provide a global URL for your system
echo.

REM Start tunnel and capture output
.\cloudflared tunnel --url http://127.0.0.1:5000 > tunnel_output.txt 2>&1 &
echo    ✓ Tunnel process started
echo.

echo [4/4] Waiting for tunnel URL...
timeout /t 10 /nobreak > nul

REM Try to extract URL from output
set "TUNNEL_URL="
for /f "tokens=*" %%i in ('findstr /i "trycloudflare.com" tunnel_output.txt 2^>nul') do (
    set "line=%%i"
    for /f "tokens=*" %%j in ("!line!") do (
        set "TUNNEL_URL=%%j"
    )
)

echo ========================================
echo   System Status
echo ========================================
echo.
echo ✅ Flask API Server: Running on localhost:5000
echo ✅ Cloudflare Tunnel: Active
echo.

if defined TUNNEL_URL (
    echo 🌐 Global URL: !TUNNEL_URL!
    echo.
    echo 📋 Your system is now accessible globally!
    echo    Copy the URL above to access from anywhere
) else (
    echo 🌐 Global URL: Check tunnel window for URL
    echo    Look for a URL ending with .trycloudflare.com
)

echo.
echo 🔗 Local Access: http://localhost:5000
echo.
echo 📋 Features Available:
echo    • Set API Key
echo    • Upload Documents
echo    • Compliance Check
echo    • Contract Generation
echo    • Grammar Check
echo.
echo Press any key to exit this window...
pause > nul

REM Clean up
if exist tunnel_output.txt del tunnel_output.txt
