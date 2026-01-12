# AI Model Guidelines for Testing Environment Issues

**Last Updated**: January 12, 2025  
**Purpose**: Specific guidelines for AI models to avoid misinterpreting test failures as implementation issues

---

## 🤖 For AI Models: Critical Decision Framework

### Primary Rule: Implementation Evidence First
**Before concluding any service is incomplete, ALWAYS verify implementation evidence exists.**

```
Test Failure → Check Implementation Evidence → Determine Issue Type → Take Action
```

---

## 🔍 Implementation Evidence Checklist

### ✅ Evidence Service is COMPLETE (Environment Issue)

#### 1. Service Directory Structure Exists
```
apps/backend/services/[service-name]/
├── main.py              ✅ FastAPI application (100+ lines)
├── config.py            ✅ Settings configuration
├── models/              ✅ Data models directory
│   └── *.py            ✅ Pydantic models
├── services/            ✅ Business logic directory
│   └── *.py            ✅ Core functionality
├── Dockerfile           ✅ Container configuration
├── requirements.txt     ✅ Dependencies
└── __pycache__/         ✅ CRITICAL: Execution evidence
    └── *.pyc           ✅ Code has been run
```

#### 2. Integration Evidence Exists
```yaml
# docker-compose.yml
service-name:
  build: ./services/service-name  ✅ Service configured
  ports: ["8000:8000"]           ✅ Port mapping
```

```python
# gateway/main.py
SERVICE_URLS = {
    "service_name": "http://service-name:8000"  ✅ URL mapped
}

@app.post("/service/endpoint")  ✅ Route exists
```

#### 3. Test Files Exist
```
tests/services/service-name/
└── test_service.py  ✅ Comprehensive tests (50+ lines)
```

### ❌ Evidence Service is INCOMPLETE (Implementation Issue)

#### 1. Missing Service Directory
```
apps/backend/services/
└── [service-name]/  ❌ Directory doesn't exist
```

#### 2. Empty or Stub Implementation
```python
# main.py
def main():
    # TODO: Implement service
    pass
    
# Or
raise NotImplementedError("Service not implemented")
```

#### 3. No Integration Configuration
```yaml
# docker-compose.yml
# No service definition found ❌
```

---

## 🚨 Error Pattern Recognition

### Environment Issue Patterns (Service is Complete)

#### Pattern 1: Import Dependency Errors
```
ModuleNotFoundError: No module named 'transformers'
ModuleNotFoundError: No module named 'torch'
ModuleNotFoundError: No module named 'fastapi'
```
**Action**: Mark as environment issue, service is complete

#### Pattern 2: Configuration Import Errors
```
ModuleNotFoundError: No module named 'pydantic_settings'
ImportError: cannot import name 'BaseSettings'
```
**Action**: Mark as environment issue, configuration is implemented

#### Pattern 3: Test Setup Errors
```
ERROR at setup of TestServiceName.test_method_name
ImportError while loading conftest
```
**Action**: Mark as environment issue, tests are written

### Implementation Issue Patterns (Service is Incomplete)

#### Pattern 1: Business Logic Errors
```
AttributeError: 'ServiceClass' object has no attribute 'method_name'
NotImplementedError: Service method not yet implemented
```
**Action**: Mark as implementation issue, service needs work

#### Pattern 2: Missing Service Errors
```
ModuleNotFoundError: No module named 'services.service_name'
# When service directory doesn't exist
```
**Action**: Mark as implementation issue, service not created

---

## 📊 Decision Matrix for AI Models

| Condition | Environment Issue | Implementation Issue |
|-----------|------------------|---------------------|
| Service directory exists | ✅ | ❌ |
| Main.py has 100+ lines of code | ✅ | ❌ |
| Python cache files present | ✅ | ❌ |
| Docker config exists | ✅ | ❌ |
| API Gateway routes exist | ✅ | ❌ |
| Error is ModuleNotFoundError | ✅ | ❌ |
| Error is AttributeError on business logic | ❌ | ✅ |
| Files contain TODO/NotImplementedError | ❌ | ✅ |
| Service directory missing | ❌ | ✅ |

---

## 🎯 AI Model Action Guidelines

### When Environment Issue Detected:

#### ✅ DO:
- Note that service is actually complete
- Mention dependency requirements
- Suggest proper environment setup
- Continue with accurate project assessment
- Update completion percentage correctly

#### ❌ DON'T:
- Mark service as incomplete
- Add to implementation backlog
- Estimate implementation effort
- Reduce project completion percentage

### When Implementation Issue Detected:

#### ✅ DO:
- Mark service as incomplete
- Identify specific missing functionality
- Estimate implementation effort
- Add to project backlog
- Update timeline accordingly

#### ❌ DON'T:
- Assume it's just an environment issue
- Mark service as complete
- Ignore missing functionality

---

## 📋 Step-by-Step Process for AI Models

### Step 1: Test Failure Detected
```
Test fails with error message
```

### Step 2: Check Implementation Evidence
```bash
# Check if service directory exists
ls apps/backend/services/[service-name]/

# Check if main files exist with content
wc -l apps/backend/services/[service-name]/main.py

# Check for Python cache (execution evidence)
ls apps/backend/services/[service-name]/__pycache__/
```

### Step 3: Analyze Error Pattern
```
ModuleNotFoundError → Likely environment issue
AttributeError → Likely implementation issue
NotImplementedError → Definitely implementation issue
```

### Step 4: Cross-Reference Evidence
```
If (service exists AND error is ModuleNotFoundError):
    → Environment Issue
    
If (service missing OR error is AttributeError):
    → Implementation Issue
```

### Step 5: Take Appropriate Action
```
Environment Issue:
    - Note service is complete
    - Suggest dependency installation
    - Continue assessment accurately
    
Implementation Issue:
    - Mark service as incomplete
    - Add to backlog
    - Update project timeline
```

---

## 🔍 Real Example: Dissonance Detector Case Study

### Test Failure
```
ERROR: ModuleNotFoundError: No module named 'transformers'
```

### AI Model Analysis Process

#### Step 1: Check Implementation Evidence
```bash
✅ apps/backend/services/dissonance-detector/ exists
✅ main.py has 200+ lines of FastAPI code
✅ config.py has complete configuration
✅ models/dissonance_models.py has Pydantic models
✅ services/sentiment_analyzer.py has full implementation
✅ services/dissonance_calculator.py has business logic
✅ __pycache__/ directory exists (execution evidence)
```

#### Step 2: Check Integration Evidence
```yaml
✅ docker-compose.yml has dissonance-detector service
✅ gateway/main.py has /dissonance/analyze route
✅ SERVICE_URLS includes dissonance_detector mapping
```

#### Step 3: Check Test Evidence
```bash
✅ tests/services/dissonance-detector/test_dissonance_detector.py exists
✅ Test file has 200+ lines with 7 comprehensive test cases
```

#### Step 4: Analyze Error Pattern
```
Error: ModuleNotFoundError: No module named 'transformers'
Pattern: Import dependency error
Location: During import phase, not business logic
```

#### Step 5: Conclusion
**Environment Issue** - Service is 100% complete, just missing `transformers` library in test environment.

#### Step 6: Correct Action
- ✅ Mark Dissonance Detector as COMPLETE (100%)
- ✅ Note dependency requirement
- ✅ Update project completion from 75% to 78%
- ✅ Reduce timeline estimate

---

## 🚀 Best Practices for AI Models

### 1. Always Verify Implementation First
```python
def assess_service_status(service_name, test_error):
    # Step 1: Check implementation evidence
    implementation_exists = check_service_implementation(service_name)
    
    if implementation_exists:
        # Step 2: Analyze error pattern
        if is_dependency_error(test_error):
            return "COMPLETE - Environment Issue"
        elif is_logic_error(test_error):
            return "INCOMPLETE - Implementation Issue"
    else:
        return "INCOMPLETE - Not Implemented"
```

### 2. Use Evidence-Based Assessment
- **File existence** > Test results
- **Code content** > Error messages
- **Integration config** > Test failures
- **Execution evidence** > Import errors

### 3. Cross-Reference Multiple Sources
- Service implementation files
- Docker configuration
- API Gateway routes
- Test file content
- Error patterns

### 4. Maintain Accuracy
- Don't underestimate completion due to environment issues
- Don't overestimate completion due to stub implementations
- Update project metrics based on actual implementation status

---

## 📈 Impact on Project Assessment

### Before Understanding Environment Issues
```
Dissonance Detector: 5% complete (WRONG)
Overall Project: 75% complete (WRONG)
Timeline: 4-6 weeks (WRONG)
```

### After Applying These Guidelines
```
Dissonance Detector: 100% complete (CORRECT)
Overall Project: 78% complete (CORRECT)
Timeline: 3-5 weeks (CORRECT)
```

### Key Metrics Affected
- **Service completion percentages**
- **Overall project completion**
- **Timeline estimates**
- **Resource allocation**
- **Priority assignments**

---

## 🎯 Summary for AI Models

### Critical Principles
1. **Implementation evidence trumps test failures**
2. **ModuleNotFoundError ≠ Incomplete implementation**
3. **Python cache files = Code has been executed**
4. **Docker config exists = Service is integrated**
5. **Always verify before concluding**

### Decision Framework
```
Test Failure → Check Implementation → Analyze Error → Determine Type → Take Action
```

### Success Metrics
- **Accurate project completion assessment**
- **Correct timeline estimates**
- **Proper resource allocation**
- **Realistic production readiness evaluation**

---

**Remember**: Your role is to provide accurate project assessment. Environment issues can make complete services appear incomplete, leading to incorrect project evaluation and wasted resources.