@echo off
echo 🚀 Simple Cloudflare Deployment
echo ==============================

echo.
echo 📋 Manual Deployment Steps:
echo.
echo 1. Go to https://dash.cloudflare.com/
echo 2. Create a new Worker
echo 3. Copy the code from app/worker.py
echo 4. Set environment variables:
echo    - ANTHROPIC_API_KEY: Your API key
echo    - ENVIRONMENT: production
echo.
echo 🌐 Alternative: Use Cloudflare Pages
echo 1. Go to https://dash.cloudflare.com/pages
echo 2. Connect your GitHub repository
echo 3. Set build command: pip install -r requirements-cloudflare.txt
echo 4. Set output directory: app
echo.
echo 📁 Files ready for deployment:
echo - app/worker.py (main application)
echo - requirements-cloudflare.txt (dependencies)
echo - wrangler.toml (configuration)
echo.
pause
