@echo off
echo 🌐 Starting Cloudflare Tunnel
echo =============================

echo.
echo 📋 Make sure your API server is running on port 5000
echo 💡 If not, run: python app/api.py
echo.

REM Check if cloudflared exists
if not exist "cloudflared.exe" (
    echo ❌ Cloudflared not found. Installing...
    call .\install-cloudflared.bat
    if not exist "cloudflared.exe" (
        echo ❌ Failed to install cloudflared
        pause
        exit /b 1
    )
)

echo ✅ Cloudflared found
echo.

REM Start the tunnel
echo 🚀 Starting tunnel to http://127.0.0.1:5000
echo 📝 This will create a public URL for your local application
echo.
echo ⚠️  Keep this window open while using the tunnel
echo.

cloudflared tunnel --url http://127.0.0.1:5000

echo.
echo 🛑 Tunnel stopped
pause
