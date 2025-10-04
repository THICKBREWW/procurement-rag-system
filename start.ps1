Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PROCUREMENT RAG SYSTEM" -ForegroundColor Yellow
Write-Host "  AI-Powered Contract Compliance" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Flask API server..." -ForegroundColor Green
Write-Host ""
Write-Host "Once started, open your browser to:" -ForegroundColor White
Write-Host "http://localhost:5000" -ForegroundColor Blue
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

try {
    python app/api.py
} catch {
    Write-Host "Error starting server. Make sure Python is installed." -ForegroundColor Red
}

Read-Host "Press Enter to exit"
