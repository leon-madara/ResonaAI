#!/bin/bash

# Setup and Run Script for ResonaAI Platform
# Sets up the environment and runs both backend and frontend servers

set -e

echo "============================================================"
echo "ResonaAI Platform - Setup and Run"
echo "============================================================"

# Colors for output
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd apps/frontend
npm install
cd ../..

# Check if PostgreSQL is running
print_status "Checking database connection..."
if command -v psql &> /dev/null; then
    print_status "PostgreSQL is available"
else
    print_warning "PostgreSQL client not found. Make sure database is running."
fi

# Create .env file if it doesn't exist
if [ ! -f "config.env" ]; then
    print_status "Creating config.env from example..."
    cp config.env.example config.env
    print_warning "Please update config.env with your actual configuration"
fi

echo ""
echo "============================================================"
echo "Starting Servers"
echo "============================================================"

# Start backend server in background
print_status "Starting backend server on http://localhost:8000..."
cd apps/backend/gateway
python main.py &
BACKEND_PID=$!
cd ../../..

# Wait a moment for backend to start
sleep 3

# Start frontend server
print_status "Starting frontend server on http://localhost:3000..."
cd apps/frontend
npm start &
FRONTEND_PID=$!
cd ../..

echo ""
print_status "Servers started successfully!"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
