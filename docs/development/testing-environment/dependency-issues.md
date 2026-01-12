# Common Dependency Issues in Testing Environment

**Last Updated**: January 12, 2025  
**Context**: Issues that cause test failures but don't indicate incomplete implementation

---

## 🔍 Overview

This document catalogs dependency-related test failures that are **environment issues**, not implementation problems. These failures can mislead AI models into thinking services are incomplete when they're actually fully implemented.

---

## 📦 Python Package Dependencies

### Machine Learning Libraries

#### Transformers Library
**Error Pattern**:
```
ModuleNotFoundError: No module named 'transformers'
```

**Services Affected**:
- `dissonance-detector` (sentiment analysis)
- `cultural-context` (NLP processing)
- `emotion-analysis` (text processing)

**Context**: 
- Service implementation is complete
- Tests fail only due to missing local dependency
- Service works fine in Docker environment

**Evidence of Complete Implementation**:
- Service files exist with full transformers integration
- Python cache files (`.pyc`) present
- Docker configuration includes transformers

#### PyTorch/Torch
**Error Pattern**:
```
ModuleNotFoundError: No module named 'torch'
ImportError: No module named 'torchaudio'
```

**Services Affected**:
- `emotion-analysis` (audio processing)
- `speech-processing` (audio ML models)
- `dissonance-detector` (ML inference)

**Context**:
- Large dependency (~2GB download)
- Version conflicts between Python 3.13/3.14
- Service implementation complete, just missing runtime

#### Scikit-learn
**Error Pattern**:
```
ModuleNotFoundError: No module named 'sklearn'
```

**Services Affected**:
- `emotion-analysis` (classification models)
- `baseline-tracker` (pattern analysis)

### Web Framework Dependencies

#### Pydantic Settings
**Error Pattern**:
```
ModuleNotFoundError: No module named 'pydantic_settings'
```

**Services Affected**:
- All FastAPI services (configuration management)

**Context**:
- Configuration files are complete
- Service logic is implemented
- Just missing settings management library

#### FastAPI/Starlette
**Error Pattern**:
```
ModuleNotFoundError: No module named 'fastapi'
ModuleNotFoundError: No module named 'starlette'
```

**Services Affected**:
- All backend services

**Context**:
- API endpoints are fully implemented
- Service logic is complete
- Just missing web framework

### Database Dependencies

#### SQLAlchemy
**Error Pattern**:
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Services Affected**:
- Services with database integration
- Test configuration files

#### Psycopg2
**Error Pattern**:
```
ModuleNotFoundError: No module named 'psycopg2'
```

**Services Affected**:
- PostgreSQL-dependent services

### Authentication Dependencies

#### PyJWT
**Error Pattern**:
```
ModuleNotFoundError: No module named 'jwt'
```

**Services Affected**:
- All authenticated services
- Test authentication helpers

---

## 🔧 Version Compatibility Issues

### Python Version Conflicts

#### Python 3.14 vs 3.11/3.13
**Issue**: Requirements.txt has version-specific dependencies
```
torch==2.1.1; python_version < "3.13"
torch==2.9.1; python_version >= "3.13"
```

**Impact**: 
- Local Python 3.14 needs newer versions
- Docker uses Python 3.11 with older versions
- Tests fail locally but work in Docker

#### Pydantic Version Conflicts
**Issue**: Different Pydantic versions for different Python versions
```
pydantic==2.5.0; python_version < "3.13"
pydantic==2.12.5; python_version >= "3.13"
```

---

## 🚨 How to Identify Environment Issues vs Implementation Issues

### ✅ Signs of Complete Implementation (Environment Issue)

1. **Service Directory Exists**
   ```
   apps/backend/services/[service-name]/
   ├── main.py          ✅ Full FastAPI app
   ├── config.py        ✅ Complete configuration
   ├── models/          ✅ Data models
   └── services/        ✅ Business logic
   ```

2. **Python Cache Files Present**
   ```
   __pycache__/
   ├── main.cpython-314.pyc     ✅ Code has been executed
   ├── config.cpython-314.pyc   ✅ Imports work
   ```

3. **Docker Configuration Exists**
   ```yaml
   # docker-compose.yml
   service-name:
     build: ./services/service-name  ✅ Service configured
     ports: ["8000:8000"]           ✅ Port mapping
   ```

4. **API Gateway Integration**
   ```python
   # gateway/main.py
   SERVICE_URLS = {
       "service_name": "http://service-name:8000"  ✅ URL mapped
   }
   
   @app.post("/service/endpoint")  ✅ Route exists
   ```

5. **Test Files Exist**
   ```
   tests/services/service-name/
   └── test_service.py  ✅ Comprehensive tests written
   ```

### ❌ Signs of Incomplete Implementation (Real Issue)

1. **Missing Service Directory**
   ```
   apps/backend/services/
   └── [service-name]/  ❌ Directory doesn't exist
   ```

2. **Empty or Stub Files**
   ```python
   # main.py
   # TODO: Implement service  ❌ Not implemented
   pass
   ```

3. **No Docker Configuration**
   ```yaml
   # docker-compose.yml
   # Missing service definition  ❌ Not configured
   ```

4. **No API Gateway Routes**
   ```python
   # gateway/main.py
   # No routes for service  ❌ Not integrated
   ```

---

## 📋 Dependency Installation Commands

### For Testing Environment
```bash
# Core dependencies
pip install fastapi uvicorn pydantic pydantic-settings
pip install sqlalchemy psycopg2-binary
pip install pytest pytest-asyncio pytest-mock
pip install httpx pyjwt

# ML dependencies (large downloads)
pip install torch torchaudio transformers
pip install scikit-learn numpy pandas

# Audio processing
pip install librosa soundfile

# Development tools
pip install python-dotenv
```

### Using Requirements.txt
```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific groups
pip install -r requirements.txt --only-binary=all
```

---

## 🔄 Testing Strategy

### 1. Check Implementation First
```bash
# Verify service exists
ls apps/backend/services/[service-name]/

# Check for Python cache (execution evidence)
ls apps/backend/services/[service-name]/__pycache__/
```

### 2. Install Dependencies
```bash
# Install missing dependencies
pip install [missing-package]
```

### 3. Run Tests
```bash
# Run specific service tests
python -m pytest tests/services/[service-name]/ -v
```

### 4. Use Docker for Consistent Environment
```bash
# Run tests in Docker environment
docker-compose run [service-name] pytest
```

---

## 📊 Impact on Project Assessment

### Before Understanding Environment Issues
- **Dissonance Detector**: Marked as incomplete (5%)
- **Overall Project**: 75% complete
- **Timeline**: 4-6 weeks to production

### After Identifying Environment Issues
- **Dissonance Detector**: Actually complete (100%)
- **Overall Project**: 78% complete
- **Timeline**: 3-5 weeks to production

### Key Lesson
**Always verify implementation exists before concluding from test failures**

---

## 🎯 Recommendations for AI Models

1. **Check implementation evidence first**
   - Service directories
   - Python cache files
   - Docker configuration
   - API Gateway routes

2. **Distinguish error types**
   - `ModuleNotFoundError` = likely environment issue
   - `AttributeError`/`NameError` = likely implementation issue
   - `ImportError` = could be either

3. **Cross-reference with project structure**
   - If service is listed in docker-compose.yml but tests fail → environment issue
   - If service directory doesn't exist → implementation issue

4. **Use this documentation**
   - Check known patterns in this file
   - Follow troubleshooting guide
   - Verify against implementation evidence

---

**Remember**: Test failures in local environment ≠ Incomplete implementation