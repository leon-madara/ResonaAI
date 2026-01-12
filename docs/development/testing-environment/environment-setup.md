# Proper Testing Environment Setup

**Last Updated**: January 12, 2025  
**Purpose**: Guide for setting up a complete testing environment to avoid false test failures

---

## 🎯 Overview

This guide ensures AI models and developers can set up a proper testing environment that won't produce misleading test failures due to missing dependencies.

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.11+ (3.14 supported with version-specific dependencies)
- **Node.js**: 18+ (for frontend testing)
- **Docker**: Latest version (for containerized testing)
- **Git**: For repository access

### Platform Considerations
- **Windows**: Some audio libraries may need additional setup
- **Linux/Mac**: Generally better compatibility with audio processing
- **Docker**: Recommended for consistent environment across platforms

---

## 🐍 Python Environment Setup

### Option 1: Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip
```

### Option 2: Conda Environment
```bash
# Create conda environment
conda create -n resonaai python=3.11
conda activate resonaai
```

---

## 📦 Dependency Installation

### Core Dependencies (Required for All Tests)
```bash
# Web framework and API
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install httpx==0.25.2

# Data validation and settings
pip install pydantic==2.5.0  # or 2.12.5 for Python 3.13+
pip install pydantic-settings==2.1.0

# Database
pip install sqlalchemy==2.0.23
pip install psycopg2-binary==2.9.7

# Authentication
pip install python-jose[cryptography]==3.3.0
pip install bcrypt==4.1.2
pip install pyjwt==2.8.0

# Testing framework
pip install pytest==7.4.3
pip install pytest-asyncio==0.21.1
pip install pytest-mock==3.12.0
pip install pytest-cov==4.1.0

# Utilities
pip install python-dotenv==1.0.0
pip install redis==5.0.1
```

### Machine Learning Dependencies (For ML Services)
```bash
# PyTorch (choose based on your system)
# CPU only:
pip install torch==2.1.1 torchaudio==2.1.1 --index-url https://download.pytorch.org/whl/cpu

# GPU (CUDA 11.8):
pip install torch==2.1.1 torchaudio==2.1.1 --index-url https://download.pytorch.org/whl/cu118

# Transformers and NLP
pip install transformers==4.36.0
pip install sentence-transformers>=2.2.0

# Scientific computing
pip install numpy==1.24.4  # or 2.3.5 for Python 3.13+
pip install pandas==2.1.4   # or 2.3.3 for Python 3.13+
pip install scikit-learn==1.3.2  # or 1.8.0 for Python 3.13+
```

### Audio Processing Dependencies (For Audio Services)
```bash
# Audio processing
pip install librosa==0.10.1
pip install soundfile==0.12.1
pip install noisereduce==3.0.0

# Audio features
pip install python-speech-features==0.6
pip install pyAudioAnalysis==0.3.14

# System audio (optional, may need system libraries)
# Windows users may skip these if they cause issues
pip install pyaudio==0.2.11  # May need PortAudio
pip install webrtcvad==2.0.10  # May need compilation
```

### Using Requirements.txt (Easiest)
```bash
# Install all dependencies from requirements.txt
pip install -r requirements.txt

# If some packages fail, install core dependencies first
pip install fastapi uvicorn pydantic sqlalchemy pytest
pip install -r requirements.txt --no-deps  # Skip dependency resolution
```

---

## 🐳 Docker Environment Setup (Recommended)

### Why Docker?
- **Consistent environment** across all platforms
- **Pre-configured dependencies** 
- **Matches production environment**
- **Avoids local dependency conflicts**

### Docker Setup
```bash
# Build all services
docker-compose build

# Start services for testing
docker-compose up -d postgres redis

# Run tests in Docker environment
docker-compose run --rm dissonance-detector pytest
docker-compose run --rm emotion-analysis pytest
```

### Docker Test Commands
```bash
# Test specific service
docker-compose run --rm [service-name] pytest tests/

# Test with coverage
docker-compose run --rm [service-name] pytest --cov=. tests/

# Interactive testing
docker-compose run --rm [service-name] bash
# Then inside container:
pytest tests/services/[service-name]/ -v
```

---

## 🔧 Environment Variables

### Required Environment Variables
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/mental_health

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=test-secret-key-dev-only
JWT_ALGORITHM=HS256

# External APIs (for integration tests)
OPENAI_API_KEY=your_openai_key_here
AZURE_SPEECH_KEY=your_azure_key_here
AZURE_SPEECH_REGION=your_region

# Service URLs (for integration tests)
REACT_APP_API_URL=http://localhost:8000
```

### Environment File Setup
```bash
# Copy example environment file
cp config.env.example .env

# Edit with your values
# Windows:
notepad .env
# Linux/Mac:
nano .env
```

---

## 🧪 Testing Strategy

### 1. Verify Environment Setup
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(fastapi|pytest|transformers|torch)"

# Test imports
python -c "import fastapi, pytest, transformers, torch; print('All imports successful')"
```

### 2. Run Tests by Category

#### Unit Tests (Fast, No External Dependencies)
```bash
# Test individual services
python -m pytest tests/services/dissonance-detector/ -v
python -m pytest tests/services/emotion-analysis/ -v

# Test specific functionality
python -m pytest tests/services/ -k "test_health_check" -v
```

#### Integration Tests (Require Services Running)
```bash
# Start required services
docker-compose up -d postgres redis

# Run integration tests
python -m pytest tests/integration/ -v
```

#### End-to-End Tests (Full System)
```bash
# Start all services
docker-compose up -d

# Run E2E tests
python -m pytest tests/e2e/ -v
```

### 3. Handle Test Failures

#### If Tests Fail with Import Errors:
1. **Check dependency installation**:
   ```bash
   pip list | grep [missing-package]
   ```

2. **Install missing dependencies**:
   ```bash
   pip install [missing-package]
   ```

3. **Use Docker if local issues persist**:
   ```bash
   docker-compose run --rm [service] pytest
   ```

#### If Tests Fail with Logic Errors:
1. **Check service implementation**
2. **Verify business logic**
3. **Check for actual bugs**

---

## 🔍 Troubleshooting Common Issues

### Issue 1: Transformers Model Download Fails
```bash
# Error: Connection timeout downloading models
# Solution: Set cache directory and retry
export TRANSFORMERS_CACHE=/path/to/cache
pip install transformers --upgrade
```

### Issue 2: PyTorch Installation Issues
```bash
# Error: No matching distribution found for torch
# Solution: Use specific index URL
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Issue 3: Audio Library Compilation Errors
```bash
# Error: Microsoft Visual C++ 14.0 is required
# Solution: Install pre-compiled wheels or skip audio tests
pip install --only-binary=all librosa soundfile
```

### Issue 4: Database Connection Errors
```bash
# Error: Connection refused to PostgreSQL
# Solution: Start database service
docker-compose up -d postgres
# Or use SQLite for testing
export DATABASE_URL=sqlite:///test.db
```

### Issue 5: Permission Errors on Windows
```bash
# Error: Permission denied
# Solution: Run as administrator or use virtual environment
python -m venv venv
venv\Scripts\activate
```

---

## 📊 Environment Validation Checklist

### ✅ Basic Environment
- [ ] Python 3.11+ installed
- [ ] Virtual environment activated
- [ ] pip upgraded to latest version
- [ ] Core dependencies installed (fastapi, pytest, etc.)

### ✅ ML Environment
- [ ] PyTorch installed and working
- [ ] Transformers library installed
- [ ] Can import torch and transformers without errors
- [ ] GPU support working (if applicable)

### ✅ Database Environment
- [ ] PostgreSQL accessible (Docker or local)
- [ ] SQLAlchemy can connect to database
- [ ] Redis accessible for caching
- [ ] Environment variables set correctly

### ✅ Testing Environment
- [ ] Pytest installed and working
- [ ] Can run basic tests without import errors
- [ ] Test database accessible
- [ ] Mock dependencies available

### ✅ Service Environment
- [ ] All service directories exist
- [ ] Can import service modules
- [ ] Docker Compose configuration valid
- [ ] API Gateway routes accessible

---

## 🚀 Quick Setup Script

### Automated Setup (Linux/Mac)
```bash
#!/bin/bash
# setup-test-env.sh

echo "Setting up ResonaAI testing environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install fastapi uvicorn pydantic sqlalchemy pytest httpx

# Install ML dependencies (CPU only for testing)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers scikit-learn numpy pandas

# Install testing dependencies
pip install pytest-asyncio pytest-mock pytest-cov

# Install remaining dependencies
pip install -r requirements.txt --no-deps

echo "Environment setup complete!"
echo "Activate with: source venv/bin/activate"
```

### Automated Setup (Windows)
```powershell
# setup-test-env.ps1

Write-Host "Setting up ResonaAI testing environment..."

# Create virtual environment
python -m venv venv
venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install core dependencies
pip install fastapi uvicorn pydantic sqlalchemy pytest httpx

# Install ML dependencies (CPU only for testing)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install transformers scikit-learn numpy pandas

# Install testing dependencies
pip install pytest-asyncio pytest-mock pytest-cov

Write-Host "Environment setup complete!"
Write-Host "Activate with: venv\Scripts\Activate.ps1"
```

---

## 📈 Performance Considerations

### Dependency Size Management
- **Full ML stack**: ~5GB download
- **Core testing only**: ~500MB download
- **Docker images**: Pre-built, faster setup

### Test Execution Speed
- **Unit tests**: < 30 seconds
- **Integration tests**: 1-2 minutes
- **Full test suite**: 5-10 minutes

### Resource Requirements
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 10GB free space for dependencies
- **CPU**: Multi-core recommended for parallel testing

---

**Remember**: A properly configured environment prevents false test failures and ensures accurate project assessment.