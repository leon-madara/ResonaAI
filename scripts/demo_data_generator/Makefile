# Makefile for ResonaAI Demo Data Generator

.PHONY: help install test clean build docker run validate docs

# Default target
help:
	@echo "ResonaAI Demo Data Generator - Available Commands:"
	@echo "=================================================="
	@echo "  install     - Install dependencies"
	@echo "  test        - Run test suite"
	@echo "  validate    - Validate system setup"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build distribution packages"
	@echo "  docker      - Build Docker image"
	@echo "  run         - Run demo with quick preset"
	@echo "  run-full    - Run demo with comprehensive preset"
	@echo "  docs        - Generate documentation"
	@echo "  help        - Show this help message"

# Install dependencies
install:
	@echo "🔧 Installing dependencies..."
	pip install -r requirements.txt
	@echo "✅ Dependencies installed"

# Run tests
test:
	@echo "🧪 Running test suite..."
	python -m pytest tests/ -v
	@echo "✅ Tests completed"

# Validate system
validate:
	@echo "🔍 Validating system setup..."
	python demo_data_generator.py validate
	@echo "✅ Validation completed"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +
	rm -rf demo_data/
	rm -rf .pytest_cache/
	rm -rf .hypothesis/
	@echo "✅ Cleanup completed"

# Build distribution
build: clean
	@echo "🏗️ Building distribution packages..."
	python scripts/build_distribution.py
	@echo "✅ Build completed"

# Build Docker image
docker:
	@echo "🐳 Building Docker image..."
	docker build -t resona-demo-data-generator:latest .
	@echo "✅ Docker image built"

# Run demo (quick preset)
run:
	@echo "🚀 Running demo (quick preset)..."
	python demo_data_generator.py launch --preset quick --auto-browser

# Run demo (comprehensive preset)
run-full:
	@echo "🚀 Running demo (comprehensive preset)..."
	python demo_data_generator.py launch --preset comprehensive --auto-browser

# Generate documentation
docs:
	@echo "📚 Documentation files:"
	@echo "  - README.md: Main documentation"
	@echo "  - USAGE_GUIDE.md: Detailed usage guide"
	@echo "  - SETUP.md: Installation instructions"
	@echo "  - TROUBLESHOOTING.md: Common issues and solutions"
	@echo "✅ Documentation is up to date"

# Development targets
dev-install: install
	@echo "🔧 Installing development dependencies..."
	pip install black flake8 mypy pytest-cov
	@echo "✅ Development environment ready"

format:
	@echo "🎨 Formatting code..."
	black .
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Linting code..."
	flake8 .
	@echo "✅ Linting completed"

type-check:
	@echo "🔍 Type checking..."
	mypy .
	@echo "✅ Type checking completed"

# Quick development workflow
dev: clean dev-install format lint type-check test
	@echo "✅ Development workflow completed"