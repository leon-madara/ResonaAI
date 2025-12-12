# Tests Documentation Index

**Last Updated**: December 12, 2025

## Quick Navigation

This directory contains comprehensive testing documentation for the ResonaAI platform. Use this index to quickly find what you need.

## Documentation Files

### 📋 [README.md](README.md)
**Purpose**: Main testing documentation and overview  
**Contents**:
- Test status summary
- Test structure overview
- Quick start guide
- Test coverage details
- Known issues and limitations
- Next steps

**When to Use**: Start here for a comprehensive overview of testing in ResonaAI.

---

### 🚀 [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md)
**Purpose**: Detailed guide on how to run tests  
**Contents**:
- Prerequisites and setup
- Multiple test execution methods
- Common test execution scenarios
- Troubleshooting guide
- Best practices
- CI/CD integration examples

**When to Use**: When you need to run tests or troubleshoot test execution issues.

---

### 📊 [TEST_STATUS_REPORT.md](TEST_STATUS_REPORT.md)
**Purpose**: Detailed test status and metrics  
**Contents**:
- Executive summary
- Test statistics
- Detailed status by service
- Test coverage analysis
- Known issues
- Recommendations

**When to Use**: When you need detailed test metrics and status information.

---

### 🏗️ [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
**Purpose**: Complete project overview and architecture  
**Contents**:
- Project description
- System architecture
- Microservices overview
- Technology stack
- Security and privacy
- Compliance and legal
- Deployment information

**When to Use**: When you need to understand the overall project structure and architecture.

---

## Test Files Structure

```
tests/
├── README.md                    # Main testing documentation
├── TEST_EXECUTION_GUIDE.md      # How to run tests
├── TEST_STATUS_REPORT.md        # Detailed test status
├── PROJECT_OVERVIEW.md          # Project overview
├── INDEX.md                     # This file
│
├── services/                    # Service-specific tests
│   ├── encryption-service/
│   │   └── test_encryption_service.py  # 13/15 passing
│   ├── dissonance-detector/
│   │   └── test_dissonance_detector.py  # 7/7 passing
│   ├── baseline-tracker/
│   │   └── test_baseline_tracker.py    # 9/9 passing
│   ├── conversation-engine/
│   │   └── test_conversation_engine.py  # 9/9 passing
│   ├── crisis-detection/
│   │   └── test_crisis_detection.py     # 10/10 passing
│   ├── consent-management/
│   │   └── test_consent_management.py   # 13/13 passing
│   └── api-gateway/
│       ├── test_auth.py                  # Auth tests
│       └── test_routing.py               # Routing tests
│
├── integration/                 # Integration tests
│   ├── test_auth_flow.py
│   ├── test_crisis_detection.py
│   └── test_speech_processing.py
│
└── test_*.py                    # Core component tests
```

## Quick Reference

### Test Status Summary

| Service | Tests | Status |
|---------|-------|--------|
| Encryption Service | 13/15 | ✅ Passing (2 skipped) |
| Dissonance Detector | 7/7 | ✅ Complete |
| Baseline Tracker | 9/9 | ✅ Complete |
| Conversation Engine | 9/9 | ✅ Complete |
| Crisis Detection | 10/10 | ✅ Complete |
| Consent Management | 13/13 | ✅ Complete |

**Total**: 63+ test cases across 17+ test files

### Quick Commands

```bash
# Run encryption service tests (most complete)
pytest tests/services/encryption-service/ -v

# Run all service tests individually
for service in encryption-service dissonance-detector baseline-tracker conversation-engine crisis-detection consent-management; do
    pytest tests/services/$service/ -v
done

# Run with coverage
pytest tests/services/encryption-service/ --cov=services/encryption-service --cov-report=html
```

## Common Tasks

### I want to...

- **Understand the testing setup**: Read [README.md](README.md)
- **Run tests**: Read [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md)
- **Check test status**: Read [TEST_STATUS_REPORT.md](TEST_STATUS_REPORT.md)
- **Understand the project**: Read [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **Find a specific test**: Check the test files structure above
- **Troubleshoot issues**: Read [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md) troubleshooting section

## Related Documentation

### External Documentation

- **[System Design](../../architecture/system-design.md)** - System architecture documentation
- **[API Documentation](../../docs/API.md)** - Complete API reference
- **[Architecture Documentation](../../docs/ARCHITECTURE.md)** - System architecture details
- **[Testing Completion Status](../../Completed/06-Testing.md)** - Testing completion status

### Internal Documentation

- **[Test Execution Guide](TEST_EXECUTION_GUIDE.md)** - How to run tests
- **[Test Status Report](TEST_STATUS_REPORT.md)** - Detailed test status
- **[Project Overview](PROJECT_OVERVIEW.md)** - Project architecture

## Key Information

### Test Execution
- ✅ Tests work perfectly when run individually per service
- ⚠️ Module caching conflicts when running all tests together
- ✅ All services have comprehensive test coverage

### Known Issues
1. **Module Caching**: Run tests individually per service (recommended)
2. **Batch Endpoints**: Need JSON body support (tests skipped)

### Next Steps
1. Fix batch encryption endpoints
2. Resolve module caching conflicts
3. Add end-to-end tests
4. Set up CI/CD pipeline

---

**Last Updated**: December 12, 2025  
**Status**: Comprehensive documentation complete

