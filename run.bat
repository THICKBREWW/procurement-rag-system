@echo off
title Procurement RAG System

echo.
echo ========================================
echo   Procurement RAG System
echo ========================================
echo.
echo Starting system...
echo.

REM Start Flask server
start "Flask Server" cmd /k "python app/api.py"

REM Wait for server to start
timeout /t 5 /nobreak > nul

REM Start Cloudflare tunnel
start "Cloudflare Tunnel" cmd /k ".\cloudflared tunnel --url http://127.0.0.1:5000"

echo.
echo ========================================
echo   System Started Successfully!
echo ========================================
echo.
echo ✅ Flask Server: Running on localhost:5000
echo ✅ Cloudflare Tunnel: Starting...
echo.
echo 📋 Next Steps:
echo    1. Wait for the tunnel window to show a URL
echo    2. Copy the tunnel URL (ends with .trycloudflare.com)
echo    3. Use that URL to access your system globally
echo.
echo 🔗 Local Access: http://localhost:5000
echo 🌐 Global Access: Check the tunnel window
echo.
echo Press any key to close this window...
pause > nul
