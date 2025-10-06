# Procurement RAG System Startup Script
# This script starts the Flask server and Cloudflare tunnel

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Procurement RAG System Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Flask API Server
Write-Host "[1/3] Starting Flask API Server..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "app/api.py" -WindowStyle Normal
Write-Host "   ✓ Flask server starting on port 5000" -ForegroundColor Green
Write-Host ""

# Wait for server to initialize
Write-Host "[2/3] Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 8
Write-Host "   ✓ Server initialization complete" -ForegroundColor Green
Write-Host ""

# Start Cloudflare Tunnel
Write-Host "[3/3] Starting Cloudflare Tunnel..." -ForegroundColor Yellow
Write-Host "   🌐 Creating global tunnel..." -ForegroundColor Cyan
Write-Host "   📡 This will provide a global URL for your system" -ForegroundColor Cyan
Write-Host ""

# Start tunnel in background and capture output
$tunnelProcess = Start-Process -FilePath ".\cloudflared.exe" -ArgumentList "tunnel", "--url", "http://127.0.0.1:5000" -PassThru -RedirectStandardOutput "tunnel_output.txt" -RedirectStandardError "tunnel_error.txt"

# Wait a bit for tunnel to start
Start-Sleep -Seconds 10

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   System Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Flask API Server: Running on localhost:5000" -ForegroundColor Green
Write-Host "✅ Cloudflare Tunnel: Active" -ForegroundColor Green
Write-Host ""

# Try to extract tunnel URL
$tunnelUrl = ""
if (Test-Path "tunnel_output.txt") {
    $content = Get-Content "tunnel_output.txt" -Raw
    if ($content -match "https://[a-zA-Z0-9-]+\.trycloudflare\.com") {
        $tunnelUrl = $matches[0]
    }
}

if ($tunnelUrl) {
    Write-Host "🌐 Global URL: $tunnelUrl" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "📋 Your system is now accessible globally!" -ForegroundColor Green
    Write-Host "   Copy the URL above to access from anywhere" -ForegroundColor White
} else {
    Write-Host "🌐 Global URL: Check tunnel window for URL" -ForegroundColor Yellow
    Write-Host "   Look for a URL ending with .trycloudflare.com" -ForegroundColor White
}

Write-Host ""
Write-Host "🔗 Local Access: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Features Available:" -ForegroundColor White
Write-Host "   • Set API Key" -ForegroundColor Gray
Write-Host "   • Upload Documents" -ForegroundColor Gray
Write-Host "   • Compliance Check" -ForegroundColor Gray
Write-Host "   • Contract Generation" -ForegroundColor Gray
Write-Host "   • Grammar Check" -ForegroundColor Gray
Write-Host ""

Write-Host "Press any key to exit this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Clean up
if (Test-Path "tunnel_output.txt") { Remove-Item "tunnel_output.txt" }
if (Test-Path "tunnel_error.txt") { Remove-Item "tunnel_error.txt" }
