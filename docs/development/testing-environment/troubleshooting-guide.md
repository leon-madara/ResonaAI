# Testing Environment Troubleshooting Guide

**Last Updated**: January 12, 2025  
**Purpose**: Solutions for common testing environment issues that cause misleading test failures

---

## 🎯 Quick Diagnosis

### Is this an Environment Issue or Implementation Issue?

**Environment Issue Signs**:
- ✅ Service directory exists with complete files
- ✅ Python cache files (`.pyc`) present
- ✅ Docker configuration exists
- ✅ Error is `ModuleNotFoundError` on well-known libraries
- ✅ Error occurs during import, not business logic

**Implementation Issue Signs**:
- ❌ Service directory missing or empty
- ❌ Files contain TODO comments or NotImplementedError
- ❌ Error is AttributeError on business logic
- ❌ Logic errors in test assertions

---

## 🔧 Common Environment Issues & Solutions

### 1. Missing Python Dependencies

#### Problem: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'transformers'
ModuleNotFoundError: No module named 'torch'
ModuleNotFoundError: No module named 'fastapi'
```

#### Quick Fix
```bash
# Install missing package
pip install transformers torch fastapi

# Or install all requirements
pip install -r requirements.txt
```

#### Advanced Fix
```bash
# Check what's installed
pip list | grep -E "(transformers|torch|fastapi)"

# Install with specific versions
pip install transformers==4.36.0
pip install torch==2.1.1 --index-url https://download.pytorch.org/whl/cpu

# Use Docker if local issues persist
docker-compose run --rm [service-name] pytest
```

### 2. Python Version Compatibility

#### Problem: Version-specific dependency conflicts
```
ERROR: No matching distribution found for torch==2.1.1
pydantic version incompatibility
```

#### Solution: Check Python version and use correct dependencies
```bash
# Check Python version
python --version

# For Python 3.13+, use newer versions
pip install torch==2.9.1 pydantic==2.12.5

# For Python < 3.13, use older versions  
pip install torch==2.1.1 pydantic==2.5.0

# Or let requirements.txt handle it
pip install -r requirements.txt
```

### 3. Pydantic Settings Import Issues

#### Problem: Pydantic settings not found
```
ModuleNotFoundError: No module named 'pydantic_settings'
ImportError: cannot import name 'BaseSettings'
```

#### Solution: Install pydantic-settings
```bash
# Install pydantic-settings
pip install pydantic-settings==2.1.0

# Verify installation
python -c "from pydantic_settings import BaseSettings; print('Success')"
```

### 4. Database Connection Issues

#### Problem: Database connection failures
```
sqlalchemy.exc.OperationalError: connection refused
psycopg2.OperationalError: could not connect to server
```

#### Solution: Start database services
```bash
# Start PostgreSQL with Docker
docker-compose up -d postgres

# Or use SQLite for testing
export DATABASE_URL=sqlite:///test.db

# Verify connection
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:password@localhost:5432/mental_health'); print('Connected')"
```

### 5. PyTorch Installation Issues

#### Problem: PyTorch installation fails
```
ERROR: Could not find a version that satisfies the requirement torch
RuntimeError: Couldn't load custom C++ ops
```

#### Solution: Install with correct index URL
```bash
# CPU-only version (recommended for testing)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# GPU version (if you have CUDA)
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify installation
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
```

### 6. Audio Processing Library Issues

#### Problem: Audio libraries fail to install
```
error: Microsoft Visual C++ 14.0 is required
Failed building wheel for pyaudio
```

#### Solution: Use pre-compiled wheels or skip audio tests
```bash
# Install pre-compiled wheels only
pip install --only-binary=all librosa soundfile

# Skip problematic audio libraries for testing
pip install librosa soundfile noisereduce
# Skip: pyaudio webrtcvad (optional for testing)

# Or use conda for better audio library support
conda install -c conda-forge librosa soundfile pyaudio
```

### 7. Import Path Issues

#### Problem: Module import path errors
```
ImportError: attempted relative import with no known parent package
ModuleNotFoundError: No module named 'services.sentiment_analyzer'
```

#### Solution: Fix Python path and working directory
```bash
# Run tests from project root
cd /path/to/ResonaAI
python -m pytest tests/services/dissonance-detector/ -v

# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/ResonaAI"

# Or use Docker for consistent paths
docker-compose run --rm dissonance-detector pytest
```

### 8. JWT/Authentication Library Issues

#### Problem: JWT library not found
```
ModuleNotFoundError: No module named 'jwt'
ImportError: No module named 'jose'
```

#### Solution: Install authentication libraries
```bash
# Install PyJWT
pip install pyjwt==2.8.0

# Install python-jose for more features
pip install python-jose[cryptography]==3.3.0

# Verify installation
python -c "import jwt; print('JWT library installed')"
```

---

## 🐳 Docker-Based Solutions

### When Local Environment is Too Complex

#### Use Docker for Consistent Testing
```bash
# Build service images
docker-compose build

# Run tests in Docker environment
docker-compose run --rm dissonance-detector pytest tests/ -v
docker-compose run --rm emotion-analysis pytest tests/ -v

# Interactive debugging in Docker
docker-compose run --rm dissonance-detector bash
# Inside container:
pytest tests/services/dissonance-detector/ -v --pdb
```

#### Docker Troubleshooting
```bash
# Check if services are built
docker-compose images

# Rebuild if needed
docker-compose build --no-cache [service-name]

# Check service logs
docker-compose logs [service-name]

# Clean up and restart
docker-compose down
docker-compose up -d
```

---

## 🔍 Diagnostic Commands

### Environment Verification
```bash
# Check Python and pip
python --version
pip --version

# Check virtual environment
which python
echo $VIRTUAL_ENV

# Check installed packages
pip list | grep -E "(fastapi|pytest|torch|transformers)"

# Test critical imports
python -c "
import fastapi
import pytest  
import torch
import transformers
import sqlalchemy
import pydantic
print('All critical imports successful')
"
```

### Service Implementation Verification
```bash
# Check service exists
ls -la apps/backend/services/dissonance-detector/

# Check main files
ls -la apps/backend/services/dissonance-detector/main.py
ls -la apps/backend/services/dissonance-detector/config.py

# Check for execution evidence (Python cache)
ls -la apps/backend/services/dissonance-detector/__pycache__/

# Check Docker configuration
grep -n "dissonance-detector" infra/docker/docker-compose.yml

# Check API Gateway integration
grep -n "dissonance" apps/backend/gateway/main.py
```

### Test Environment Verification
```bash
# Check test files exist
ls -la tests/services/dissonance-detector/

# Check test content
wc -l tests/services/dissonance-detector/test_*.py

# Run simple test
python -m pytest tests/services/dissonance-detector/test_dissonance_detector.py::TestDissonanceDetector::test_health_check -v
```

---

## 📊 Step-by-Step Troubleshooting Process

### Step 1: Identify Error Type
```bash
# Run failing test and capture full error
python -m pytest tests/services/[service-name]/ -v --tb=long > test_output.txt 2>&1

# Analyze error pattern
grep -E "(ModuleNotFoundError|ImportError|AttributeError)" test_output.txt
```

### Step 2: Check Implementation Evidence
```bash
# Service directory exists?
test -d apps/backend/services/[service-name] && echo "Service exists" || echo "Service missing"

# Main files exist?
test -f apps/backend/services/[service-name]/main.py && echo "Main file exists" || echo "Main file missing"

# Python cache exists (execution evidence)?
test -d apps/backend/services/[service-name]/__pycache__ && echo "Code executed" || echo "Code not executed"
```

### Step 3: Determine Issue Type
```bash
# If service exists but tests fail with ModuleNotFoundError:
echo "Environment Issue - Install missing dependencies"

# If service doesn't exist:
echo "Implementation Issue - Service not implemented"

# If service exists but tests fail with AttributeError:
echo "Implementation Issue - Service incomplete"
```

### Step 4: Apply Appropriate Solution

#### For Environment Issues:
```bash
# Install dependencies
pip install -r requirements.txt

# Or use Docker
docker-compose run --rm [service-name] pytest
```

#### For Implementation Issues:
```bash
# Check what's missing
cat apps/backend/services/[service-name]/main.py | grep -E "(TODO|NotImplementedError|pass)"

# Add to backlog for implementation
echo "Service [service-name] needs implementation" >> project/backlog/issues.md
```

---

## 🚨 Emergency Quick Fixes

### When Tests Must Run Immediately

#### Option 1: Skip Problematic Dependencies
```bash
# Install core dependencies only
pip install fastapi uvicorn pydantic sqlalchemy pytest httpx

# Run tests with mocked dependencies
python -m pytest tests/ -v --mock-external-deps
```

#### Option 2: Use Docker (Fastest)
```bash
# Use pre-built Docker environment
docker-compose run --rm [service-name] pytest tests/ -v
```

#### Option 3: Use Minimal Test Set
```bash
# Run only unit tests (no external dependencies)
python -m pytest tests/services/ -v -k "not integration"

# Run only health check tests
python -m pytest tests/ -v -k "health_check"
```

---

## 📈 Prevention Strategies

### For AI Models
1. **Always check implementation evidence first**
2. **Use Docker when local environment is complex**
3. **Distinguish between import errors and logic errors**
4. **Cross-reference with project structure documentation**

### For Developers
1. **Use virtual environments**
2. **Keep requirements.txt updated**
3. **Document environment-specific issues**
4. **Use Docker for consistent testing**

### For Project Setup
1. **Provide setup scripts**
2. **Document known issues**
3. **Use Docker Compose for services**
4. **Include environment validation scripts**

---

## 📋 Troubleshooting Checklist

### Before Concluding Service is Incomplete:
- [ ] Service directory exists
- [ ] Main implementation files exist
- [ ] Python cache files present (execution evidence)
- [ ] Docker configuration exists
- [ ] API Gateway routes exist
- [ ] Error is environment-related (ModuleNotFoundError, etc.)

### Before Installing Dependencies:
- [ ] Check Python version compatibility
- [ ] Verify virtual environment is activated
- [ ] Check available disk space (ML libraries are large)
- [ ] Consider using Docker instead

### Before Reporting Implementation Issues:
- [ ] Verify error is not environment-related
- [ ] Check for actual missing functionality
- [ ] Look for TODO comments or NotImplementedError
- [ ] Confirm business logic is incomplete

---

**Remember**: Most test failures in this project are environment issues, not implementation issues. Always verify implementation exists before concluding services are incomplete.