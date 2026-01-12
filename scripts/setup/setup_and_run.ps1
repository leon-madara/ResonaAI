# Setup and Run Script for ResonaAI Platform (PowerShell)
# Sets up the environment and runs both backend and frontend servers

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ResonaAI Platform - Setup and Run" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

function Print-Status {
    param($Message)
    Write-Host "[✓] $Message" -ForegroundColor Green
}

function Print-Warning {
    param($Message)
    Write-Host "[!] $Message" -ForegroundColor Yellow
}

function Print-Error {
    param($Message)
    Write-Host "[✗] $Message" -ForegroundColor Red
}

# Check Python version
Print-Status "Checking Python version..."
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion"

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Print-Status "Creating virtual environment..."
    python -m venv venv
}

# Activate virtual environment
Print-Status "Activating virtual environment..."
.\venv\Scripts\Activate.ps1

# Install Python dependencies
Print-Status "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Print-Status "Node.js version: $nodeVersion"
    $npmVersion = npm --version
    Print-Status "npm version: $npmVersion"
} catch {
    Print-Error "Node.js is not installed. Please install Node.js first."
    exit 1
}

# Install frontend dependencies
Print-Status "Installing frontend dependencies..."
Set-Location apps\frontend
npm install
Set-Location ..\..

# Check database connection
Print-Status "Database setup..."
Print-Warning "Make sure PostgreSQL is running on localhost:5432"
Print-Warning "Database: mental_health, User: postgres, Password: 9009"

# Create config.env if it doesn't exist
if (-not (Test-Path "config.env")) {
    Print-Status "Creating config.env from example..."
    Copy-Item config.env.example config.env
    Print-Warning "Please update config.env with your actual configuration"
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Starting Servers" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Start backend server
Print-Status "Starting backend server on http://localhost:8000..."
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    .\venv\Scripts\Activate.ps1
    Set-Location apps\backend\gateway
    python main.py
}

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend server
Print-Status "Starting frontend server on http://localhost:3000..."
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    Set-Location apps\frontend
    $env:BROWSER = "none"
    npm start
}

Write-Host ""
Print-Status "Servers started successfully!"
Write-Host ""
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Show job status
Write-Host "Jobs running:" -ForegroundColor Cyan
Get-Job

# Wait for user to press Ctrl+C
try {
    # Keep showing output from both jobs
    while ($true) {
        Receive-Job -Job $backendJob -ErrorAction SilentlyContinue
        Receive-Job -Job $frontendJob -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob, $frontendJob
    Remove-Job -Job $backendJob, $frontendJob
    Print-Status "Servers stopped"
}
