# ResonaAI Makefile
# Common commands for development, testing, and deployment

.PHONY: help install dev test lint build deploy clean

# Default target
help:
	@echo "ResonaAI Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install all dependencies"
	@echo "  make install-backend  - Install Python dependencies"
	@echo "  make install-frontend - Install Node dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev           - Start development servers"
	@echo "  make dev-backend   - Start backend services"
	@echo "  make dev-frontend  - Start frontend dev server"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all tests"
	@echo "  make test-backend  - Run backend tests"
	@echo "  make test-frontend - Run frontend tests"
	@echo "  make coverage      - Run tests with coverage"
	@echo ""
	@echo "Quality:"
	@echo "  make lint          - Run all linters"
	@echo "  make lint-backend  - Lint Python code"
	@echo "  make lint-frontend - Lint TypeScript code"
	@echo "  make format        - Format all code"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  make build         - Build all applications"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers"
	@echo "  make docker-down   - Stop Docker containers"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove build artifacts"

# ============================================================
# Setup
# ============================================================

install: install-backend install-frontend
	@echo "All dependencies installed"

install-backend:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

install-frontend:
	@echo "Installing Node dependencies..."
	cd web-app && npm install

# ============================================================
# Development
# ============================================================

dev:
	@echo "Starting development servers..."
	@make -j2 dev-backend dev-frontend

dev-backend:
	@echo "Starting backend services..."
	python main.py

dev-frontend:
	@echo "Starting frontend dev server..."
	cd web-app && npm start

# ============================================================
# Testing
# ============================================================

test: test-backend test-frontend
	@echo "All tests complete"

test-backend:
	@echo "Running backend tests..."
	pytest tests/ -v

test-frontend:
	@echo "Running frontend tests..."
	cd web-app && npm test -- --watchAll=false

coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov=services --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

# ============================================================
# Code Quality
# ============================================================

lint: lint-backend lint-frontend
	@echo "Linting complete"

lint-backend:
	@echo "Linting Python code..."
	flake8 src/ services/ tests/
	mypy src/ services/

lint-frontend:
	@echo "Linting TypeScript code..."
	cd web-app && npm run lint

format:
	@echo "Formatting code..."
	black src/ services/ tests/
	cd web-app && npm run format

# ============================================================
# Build & Deploy
# ============================================================

build: build-backend build-frontend
	@echo "Build complete"

build-backend:
	@echo "Building backend..."
	# Add backend build steps

build-frontend:
	@echo "Building frontend..."
	cd web-app && npm run build

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs:
	docker-compose logs -f

# ============================================================
# Database
# ============================================================

db-migrate:
	@echo "Running database migrations..."
	# Add migration command

db-seed:
	@echo "Seeding database..."
	# Add seed command

# ============================================================
# Cleanup
# ============================================================

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf web-app/build 2>/dev/null || true
	@echo "Cleanup complete"

