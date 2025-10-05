@echo off
echo 🚀 Deploying Procurement RAG System to Cloudflare
echo ================================================

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if wrangler is installed
wrangler --version >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Wrangler CLI...
    npm install -g wrangler
)

REM Login to Cloudflare
echo 🔐 Logging into Cloudflare...
wrangler login

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements-cloudflare.txt

REM Deploy to Cloudflare Workers
echo 🌐 Deploying to Cloudflare Workers...
wrangler deploy

echo ✅ Deployment complete!
echo 🌍 Your application is now live on Cloudflare!
echo 📋 Check your Cloudflare dashboard for the URL
pause
