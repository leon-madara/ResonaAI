# Quick Backend Restart Script
# Stops any running backend and starts it fresh

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Restarting Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing Python processes running the gateway
Write-Host "[1/3] Stopping existing backend..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*ResonaAI*" -or 
    $_.CommandLine -like "*gateway*main.py*"
} | Stop-Process -Force -ErrorAction SilentlyContinue

Start-Sleep -Seconds 2

# Set environment variables
Write-Host "[2/3] Setting environment..." -ForegroundColor Yellow
$env:DATABASE_URL = "postgresql://postgres:9009@localhost:5432/mental_health"
$env:JWT_SECRET_KEY = "test-secret-key-dev-only"

# Start backend
Write-Host "[3/3] Starting backend server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend will start on: http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location "c:\Users\Dev Projects\ResonaAI\ResonaAI\apps\backend\gateway"
python main.py
