@echo off
echo 🚀 Installing Cloudflared for Tunnel Setup
echo ========================================

echo.
echo 📥 Downloading Cloudflared...
echo.

REM Download cloudflared for Windows
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"

echo ✅ Cloudflared downloaded successfully!
echo.
echo 🔐 Next steps:
echo 1. Run: cloudflared tunnel login
echo 2. Run: cloudflared tunnel --url http://127.0.0.1:5000
echo.
echo 📋 Or use the quick tunnel script: .\start-tunnel.bat
echo.
pause
