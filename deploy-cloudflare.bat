@echo off
echo 🚀 Deploying to Cloudflare Workers...
echo.
echo 📋 This will deploy the Cloudflare-compatible version
echo 🌐 Your local development system will remain unchanged
echo.

REM Check if wrangler is installed
wrangler --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Wrangler not found. Please install it first:
    echo    npm install -g wrangler
    pause
    exit /b 1
)

REM Check if user is logged in
wrangler whoami >nul 2>&1
if %errorlevel% neq 0 (
    echo 🔐 Please log in to Cloudflare first:
    echo    wrangler login
    pause
    exit /b 1
)

echo ✅ Wrangler is ready
echo.

REM Deploy to Cloudflare
echo 🚀 Deploying to Cloudflare Workers...
wrangler deploy

if %errorlevel% equ 0 (
    echo.
    echo ✅ Successfully deployed to Cloudflare Workers!
    echo 🌐 Your system is now available globally
    echo 📝 Note: This is a simplified version optimized for Cloudflare
    echo.
) else (
    echo.
    echo ❌ Deployment failed
    echo 📝 Check the error messages above
    echo.
)

pause