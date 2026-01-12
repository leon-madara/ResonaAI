# Test Failure Patterns: Environment vs Implementation Issues

**Last Updated**: January 12, 2025  
**Purpose**: Help AI models distinguish between real implementation problems and environment setup issues

---

## 🔍 Pattern Recognition Guide

This document provides patterns to help identify whether test failures indicate:
- **Environment Issue**: Missing dependencies, configuration problems
- **Implementation Issue**: Actual missing or broken code

---

## 🚨 Environment Issue Patterns

### Pattern 1: ModuleNotFoundError on Import
```python
ModuleNotFoundError: No module named 'transformers'
ModuleNotFoundError: No module named 'torch'
ModuleNotFoundError: No module named 'fastapi'
```

**Indicators**:
- Error occurs during import phase
- Module name is a well-known library
- Error happens before any business logic runs

**Verification**:
- Check if service files exist and contain imports
- Look for requirements.txt with the missing module
- Verify Docker configuration includes the dependency

**Conclusion**: **Environment Issue** - Service is implemented, just missing runtime dependency

### Pattern 2: Pydantic/Settings Import Errors
```python
ModuleNotFoundError: No module named 'pydantic_settings'
ImportError: cannot import name 'BaseSettings'
```

**Indicators**:
- Configuration-related imports failing
- Service has config.py with settings classes
- Error in configuration loading, not business logic

**Verification**:
- Check if config.py exists with proper settings classes
- Verify requirements.txt includes pydantic-settings
- Look for environment variable usage

**Conclusion**: **Environment Issue** - Configuration is implemented, missing settings library

### Pattern 3: Test Setup Failures
```python
ERROR at setup of TestServiceName.test_method_name
ImportError while loading conftest
```

**Indicators**:
- Failure during test setup, not test execution
- Error in test infrastructure, not service code
- Multiple tests failing with same import error

**Verification**:
- Check if service implementation files exist
- Verify test files are properly written
- Look for missing test dependencies

**Conclusion**: **Environment Issue** - Tests are written, missing test environment setup

### Pattern 4: Docker/Path Related Errors
```python
FileNotFoundError: [Errno 2] No such file or directory: 'service_dir'
ImportError: attempted relative import with no known parent package
```

**Indicators**:
- Path or directory resolution issues
- Import path problems
- Working directory context issues

**Verification**:
- Check if service directory structure exists
- Verify Docker configuration
- Look for proper Python path setup

**Conclusion**: **Environment Issue** - Code exists, path/context problem

---

## ❌ Implementation Issue Patterns

### Pattern 1: AttributeError on Business Logic
```python
AttributeError: 'ServiceClass' object has no attribute 'method_name'
AttributeError: module 'service' has no attribute 'function_name'
```

**Indicators**:
- Error occurs in business logic execution
- Missing methods or attributes in service classes
- Code successfully imports but fails on execution

**Verification**:
- Check if service class exists but missing methods
- Look for incomplete implementation stubs
- Verify API endpoints are actually implemented

**Conclusion**: **Implementation Issue** - Service partially implemented, missing functionality

### Pattern 2: NotImplementedError or TODO Comments
```python
NotImplementedError: Service method not yet implemented
# TODO: Implement this functionality
raise NotImplementedError("Coming soon")
```

**Indicators**:
- Explicit not-implemented errors
- TODO comments in critical paths
- Placeholder implementations

**Verification**:
- Check service files for TODO comments
- Look for NotImplementedError raises
- Verify if methods return placeholder values

**Conclusion**: **Implementation Issue** - Service structure exists but functionality not implemented

### Pattern 3: Missing Service Directory
```python
ModuleNotFoundError: No module named 'services.service_name'
ImportError: No module named 'service_name.main'
```

**Indicators**:
- Service directory doesn't exist
- No service files found
- Import fails because code doesn't exist

**Verification**:
- Check if `apps/backend/services/service-name/` exists
- Look for main.py, config.py files
- Verify Docker compose configuration

**Conclusion**: **Implementation Issue** - Service not implemented at all

### Pattern 4: Logic Errors in Tests
```python
AssertionError: Expected 'high' but got 'low'
ValueError: Invalid input format
TypeError: unsupported operand type(s)
```

**Indicators**:
- Tests run but fail on assertions
- Business logic produces wrong results
- Type errors in actual computation

**Verification**:
- Check if service logic is implemented
- Verify algorithm correctness
- Look for proper input/output handling

**Conclusion**: **Implementation Issue** - Service implemented but has bugs

---

## 🔍 Diagnostic Checklist

### Step 1: Check Implementation Evidence
```bash
# Service directory exists?
ls apps/backend/services/[service-name]/

# Main files exist?
ls apps/backend/services/[service-name]/main.py
ls apps/backend/services/[service-name]/config.py

# Python cache files (execution evidence)?
ls apps/backend/services/[service-name]/__pycache__/
```

### Step 2: Check Integration Evidence
```bash
# Docker configuration?
grep -n "service-name" infra/docker/docker-compose.yml

# API Gateway routes?
grep -n "service-name" apps/backend/gateway/main.py

# Service URL mapping?
grep -n "service-name" apps/backend/gateway/main.py
```

### Step 3: Check Test Evidence
```bash
# Test files exist?
ls tests/services/[service-name]/

# Test content is comprehensive?
wc -l tests/services/[service-name]/test_*.py
```

### Step 4: Analyze Error Pattern
- **Import errors** → Likely environment issue
- **Logic errors** → Likely implementation issue
- **Setup errors** → Likely environment issue
- **Business logic errors** → Likely implementation issue

---

## 📊 Real Example: Dissonance Detector Analysis

### Test Failure Output
```
ERROR tests/services/dissonance-detector/test_dissonance_detector.py::TestDissonanceDetector::test_health_check
ModuleNotFoundError: No module named 'transformers'
```

### Diagnostic Process

#### ✅ Implementation Evidence Found
```bash
# Service directory exists
apps/backend/services/dissonance-detector/
├── main.py                    ✅ 200+ lines of FastAPI code
├── config.py                  ✅ Complete configuration
├── models/dissonance_models.py ✅ Pydantic models
├── services/
│   ├── sentiment_analyzer.py  ✅ Full transformers integration
│   └── dissonance_calculator.py ✅ Complete business logic
└── __pycache__/               ✅ Python cache files present
```

#### ✅ Integration Evidence Found
```yaml
# docker-compose.yml
dissonance-detector:
  build: ../../apps/backend/services/dissonance-detector  ✅
  ports: ["8008:8000"]                                   ✅
```

```python
# gateway/main.py
SERVICE_URLS = {
    "dissonance_detector": "http://dissonance-detector:8000"  ✅
}

@app.post("/dissonance/analyze")  ✅
```

#### ✅ Test Evidence Found
```python
# tests/services/dissonance-detector/test_dissonance_detector.py
# 7 comprehensive test cases, 200+ lines  ✅
```

#### 🔍 Error Pattern Analysis
- **Error Type**: `ModuleNotFoundError` on import
- **Missing Module**: `transformers` (well-known ML library)
- **Error Location**: Import phase, not business logic
- **Pattern Match**: Environment Issue Pattern #1

### Conclusion
**Environment Issue** - Service is 100% complete, just missing `transformers` library in local test environment.

---

## 🎯 Decision Matrix

| Evidence | Environment Issue | Implementation Issue |
|----------|------------------|---------------------|
| Service directory exists | ✅ | ❌ |
| Main files have content | ✅ | ❌ |
| Python cache files present | ✅ | ❌ |
| Docker configuration exists | ✅ | ❌ |
| API Gateway routes exist | ✅ | ❌ |
| Test files are comprehensive | ✅ | ❌ |
| Error is ModuleNotFoundError | ✅ | ❌ |
| Error is AttributeError | ❌ | ✅ |
| Error is NotImplementedError | ❌ | ✅ |
| Error in business logic | ❌ | ✅ |

---

## 🚀 Action Guidelines for AI Models

### If Environment Issue Detected:
1. **Don't mark service as incomplete**
2. **Note dependency requirements**
3. **Suggest proper environment setup**
4. **Continue with implementation assessment**
5. **Update project completion percentage accurately**

### If Implementation Issue Detected:
1. **Mark service as incomplete**
2. **Identify specific missing functionality**
3. **Estimate implementation effort**
4. **Add to project backlog**
5. **Update timeline accordingly**

### If Uncertain:
1. **Gather more evidence**
2. **Check multiple indicators**
3. **Cross-reference with project documentation**
4. **Default to checking implementation evidence first**

---

**Key Principle**: Always verify implementation exists before concluding from test failures.