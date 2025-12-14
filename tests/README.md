# ResonaAI Testing Documentation

**Last Updated**: December 12, 2025  
**Status**: Comprehensive test coverage implemented

## Overview

This directory contains comprehensive test suites for the ResonaAI Voice-First Mental Health Support Platform. The testing infrastructure includes unit tests, integration tests, and service-level tests covering all microservices and core functionality.

## Test Status Summary

### Overall Test Coverage

| Category | Status | Coverage |
|----------|--------|----------|
| **Unit Tests** | ✅ Complete | 63+ test cases |
| **Integration Tests** | ✅ Complete | 3 test suites |
| **Service Tests** | ✅ Complete | 17 service test files |
| **End-to-End Tests** | ⚠️ Partial | Basic flows covered |
| **Performance Tests** | ⏳ Pending | Not yet implemented |
| **Security Tests** | ✅ Partial | Encryption service covered |

### Service Test Status

| Service | Test File | Test Cases | Status | Notes |
|---------|-----------|------------|--------|-------|
| **Encryption Service** | `services/encryption-service/test_encryption_service.py` | 15 | ✅ **13/15 passing** | 2 skipped (batch endpoints need JSON body) |
| **Dissonance Detector** | `services/dissonance-detector/test_dissonance_detector.py` | 7 | ✅ **Complete** | Works individually |
| **Baseline Tracker** | `services/baseline-tracker/test_baseline_tracker.py` | 9 | ✅ **Complete** | Works individually |
| **Conversation Engine** | `services/conversation-engine/test_conversation_engine.py` | 9 | ✅ **Complete** | Works individually |
| **Crisis Detection** | `services/crisis-detection/test_crisis_detection.py` | 10 | ✅ **Complete** | Works individually |
| **Consent Management** | `services/consent-management/test_consent_management.py` | 13 | ✅ **Complete** | Works individually |
| **API Gateway** | `services/api-gateway/test_auth.py`<br>`services/api-gateway/test_routing.py` | Multiple | ✅ **Complete** | Auth and routing tests |
| **Auth Service** | `services/auth_service/test_auth_service.py` | Multiple | ✅ **Complete** | Authentication tests |

### Core Component Tests

| Component | Test File | Status |
|-----------|-----------|--------|
| **API Tests** | `test_api.py` | ✅ Complete |
| **Audio Processor** | `test_audio_processor.py` | ✅ Complete |
| **Emotion Detector** | `test_emotion_detector.py` | ✅ Complete |
| **Streaming Processor** | `test_streaming_processor.py` | ✅ Complete |

### Integration Tests

| Integration Test | Test File | Status |
|------------------|-----------|--------|
| **Auth Flow** | `integration/test_auth_flow.py` | ✅ Complete |
| **Crisis Detection** | `integration/test_crisis_detection.py` | ✅ Complete |
| **Frontend-Backend Integration** | `integration/test_frontend_backend_integration.py` | ✅ Complete |
| **Speech Processing** | `integration/test_speech_processing.py` | ✅ Complete |

## Test Structure

```
tests/
├── __init__.py                          # Test package marker
├── conftest.py                          # Shared fixtures and configuration
├── README.md                            # This file
├── TEST_EXECUTION_GUIDE.md              # How to run tests
├── TEST_STATUS_REPORT.md                # Detailed test status
├── PROJECT_OVERVIEW.md                  # Project overview and architecture
│
├── test_api.py                          # Core API endpoint tests
├── test_audio_processor.py              # Audio processing tests
├── test_emotion_detector.py             # Emotion detection tests
├── test_streaming_processor.py          # Streaming functionality tests
│
├── integration/                         # Integration tests
│   ├── __init__.py
│   ├── test_auth_flow.py                # Authentication flow tests
│   ├── test_crisis_detection.py         # Crisis detection integration
│   └── test_speech_processing.py        # Speech processing integration
│
├── services/                            # Service-specific tests
│   ├── __init__.py
│   ├── api-gateway/
│   │   ├── test_auth.py                 # API Gateway auth tests
│   │   └── test_routing.py              # API Gateway routing tests
│   ├── auth_service/
│   │   └── test_auth_service.py         # Auth service tests
│   ├── baseline-tracker/
│   │   └── test_baseline_tracker.py     # Baseline tracking tests
│   ├── consent-management/
│   │   └── test_consent_management.py   # Consent management tests
│   ├── conversation-engine/
│   │   └── test_conversation_engine.py  # Conversation engine tests
│   ├── crisis-detection/
│   │   └── test_crisis_detection.py     # Crisis detection tests
│   ├── dissonance-detector/
│   │   └── test_dissonance_detector.py  # Dissonance detection tests
│   └── encryption-service/
│       └── test_encryption_service.py   # Encryption service tests
│
└── utils/                               # Test utilities
    ├── __init__.py
    └── test_helpers.py                  # Helper functions for tests
```

## Quick Start

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/services/encryption-service/test_encryption_service.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov=services --cov-report=html

# Run integration tests only
pytest tests/integration/

# Run service tests only
pytest tests/services/
```

### Running Tests Individually (Recommended)

Due to module caching conflicts when running all services together, it's recommended to run tests per service:

```bash
# Encryption Service (13/15 passing)
pytest tests/services/encryption-service/ -v

# Dissonance Detector
pytest tests/services/dissonance-detector/ -v

# Baseline Tracker
pytest tests/services/baseline-tracker/ -v

# Conversation Engine
pytest tests/services/conversation-engine/ -v

# Crisis Detection
pytest tests/services/crisis-detection/ -v

# Consent Management
pytest tests/services/consent-management/ -v

# API Gateway
pytest tests/services/api-gateway/ -v
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

- **Test Discovery**: Automatically finds `test_*.py` files
- **Coverage**: Configured for 80% minimum coverage
- **Markers**: Defined for `asyncio`, `slow`, `integration`, `unit`
- **Output**: Verbose mode with short traceback format

### Shared Fixtures (`conftest.py`)

Available fixtures:
- `test_db` - In-memory SQLite database session
- `test_user` - Test user with authentication
- `auth_token` - JWT token for authenticated requests
- `api_gateway_client` - Test client for API Gateway
- `mock_redis` - Mock Redis client
- `mock_http_client` - Mock HTTP client
- `sample_audio_file` - Sample audio file for testing

## Test Coverage Details

### Encryption Service Tests (13/15 passing)

**Coverage Areas**:
- ✅ Health check endpoint
- ✅ Data encryption/decryption
- ✅ Roundtrip encryption validation
- ✅ Invalid data handling
- ✅ Missing data validation
- ✅ Key rotation (with admin token validation)
- ✅ Invalid token handling
- ✅ User-specific key generation
- ✅ Key information retrieval
- ✅ End-to-end message encryption
- ✅ End-to-end message decryption
- ✅ Wrong password handling (security test)
- ⏸️ Batch encryption (skipped - endpoint needs JSON body support)
- ⏸️ Batch decryption (skipped - endpoint needs JSON body support)

**Key Test Scenarios**:
- Roundtrip encryption/decryption
- Key rotation with admin token validation
- User-specific key derivation
- Wrong password rejection
- Invalid data handling

### Dissonance Detector Tests (7 tests)

**Coverage Areas**:
- ✅ Health check endpoint
- ✅ Dissonance analysis (high/low scenarios)
- ✅ Missing fields validation
- ✅ Authentication/authorization tests
- ✅ Low dissonance (authentic) scenarios
- ✅ Error handling
- ✅ Timestamp handling

**Key Test Scenarios**:
- Defensive concealment detection (positive text, negative emotion)
- Authentic responses (low dissonance)
- Missing field validation
- Authentication requirements

### Baseline Tracker Tests (9 tests)

**Coverage Areas**:
- ✅ Health check endpoint
- ✅ Baseline update with voice features
- ✅ Baseline update with emotion data
- ✅ Baseline update with both data types
- ✅ Missing user_id validation
- ✅ Authentication tests
- ✅ Baseline retrieval
- ✅ Deviation detection
- ✅ Error handling

**Key Test Scenarios**:
- Voice fingerprint creation
- Emotion baseline calculation
- Deviation detection from baseline
- Missing data handling

### Conversation Engine Tests (9 tests)

**Coverage Areas**:
- ✅ Health check endpoint
- ✅ Empathetic response generation
- ✅ Crisis intervention responses
- ✅ Cultural context integration
- ✅ Conversation ID handling
- ✅ Missing message validation
- ✅ Authentication tests
- ✅ Error handling
- ✅ Supportive response generation
- ✅ Dissonance context integration

**Key Test Scenarios**:
- Empathetic response generation
- Crisis intervention triggering
- Cultural context usage
- Conversation ID management

### Crisis Detection Tests (10 tests)

**Coverage Areas**:
- ✅ Health check endpoint
- ✅ Crisis detection (low/medium/high/critical risk)
- ✅ Multi-source detection (all data types)
- ✅ Missing transcript validation
- ✅ Authentication tests
- ✅ Crisis escalation
- ✅ Different escalation types
- ✅ Error handling
- ✅ Risk level classification

**Key Test Scenarios**:
- Low/medium/high/critical risk detection
- Escalation to emergency services
- Multi-method detection (keywords, emotion, dissonance, baseline)
- Missing data handling

### Consent Management Tests (13 tests)

**Coverage Areas**:
- ✅ Health check endpoint
- ✅ Consent creation
- ✅ Consent retrieval
- ✅ Consent revocation
- ✅ Consent checking (active/inactive)
- ✅ Consent types listing
- ✅ Authentication tests
- ✅ Missing fields validation
- ✅ Multiple consents creation
- ✅ Consent versioning

**Key Test Scenarios**:
- Multiple consent types
- Consent versioning
- Revocation workflow
- Active/inactive consent checking

## Known Issues & Limitations

### Module Caching Conflicts

**Issue**: When running all service tests together, Python's module caching causes conflicts between services using relative imports.

**Status**: ⚠️ Known limitation

**Workaround**: 
- Run tests individually per service (recommended)
- Use `pytest-xdist` for isolated test execution
- Consider refactoring services to use absolute imports

**Impact**: Low - All tests work perfectly when run individually

### Batch Endpoint Parameter Handling

**Issue**: Batch encryption/decryption endpoints expect lists but FastAPI has limitations with query parameters for lists.

**Status**: ⏸️ Deferred

**Solution Required**: 
- Update endpoints to accept JSON body instead of query parameters
- Update tests to use JSON body format

**Impact**: Medium - Batch operations currently skipped in tests

## Test Execution Best Practices

1. **Run Tests Individually**: Run tests per service to avoid module caching conflicts
2. **Use Virtual Environment**: Always run tests in a virtual environment
3. **Check Coverage**: Regularly run tests with coverage to identify gaps
4. **Fix Failing Tests First**: Address failing tests before adding new features
5. **Write Tests Before Code**: Follow TDD principles when possible
6. **Mock External Dependencies**: Mock external services (GPT, databases, etc.)
7. **Clean Up Resources**: Ensure proper cleanup in test fixtures

## Dependencies

### Required Test Packages

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
fastapi[all]
cryptography
sqlalchemy
redis
transformers
scikit-learn
PyJWT
```

### Installation

```bash
pip install -r requirements.txt
```

## Continuous Integration

### Recommended CI/CD Setup

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    pytest tests/services/encryption-service/ -v
    pytest tests/services/dissonance-detector/ -v
    pytest tests/services/baseline-tracker/ -v
    pytest tests/services/conversation-engine/ -v
    pytest tests/services/crisis-detection/ -v
    pytest tests/services/consent-management/ -v

- name: Generate Coverage Report
  run: pytest --cov=src --cov=services --cov-report=xml
```

## Next Steps

### Immediate Priorities

1. **Fix Batch Endpoints** (Priority: Medium)
   - Update encryption service batch endpoints to accept JSON body
   - Update tests to use JSON body instead of query parameters

2. **Resolve Module Caching** (Priority: Low)
   - Consider using pytest-xdist for isolated execution
   - Or refactor services to use absolute imports

### Short-term Enhancements

1. **Increase Test Coverage**
   - Add more edge case tests
   - Add integration tests between services
   - Add performance benchmarks

2. **End-to-End Tests**
   - Create E2E test suite for complete user flows
   - Test service-to-service communication
   - Test API Gateway routing

3. **Test Automation**
   - Set up CI/CD test execution
   - Add test coverage reporting
   - Add test result notifications

### Long-term Improvements

1. **Performance Testing**
   - Load testing for all endpoints
   - Stress testing for critical services
   - Response time benchmarks

2. **Security Testing**
   - Vulnerability scanning
   - Penetration testing
   - Security audit tests

3. **Test Documentation**
   - Test execution guides
   - Test maintenance procedures
   - Coverage reports

## Related Documentation

- [Test Execution Guide](TEST_EXECUTION_GUIDE.md) - Detailed guide on running tests
- [Test Status Report](TEST_STATUS_REPORT.md) - Detailed test status and metrics
- [Project Overview](PROJECT_OVERVIEW.md) - Complete project architecture and design
- [System Design](../../architecture/system-design.md) - System architecture documentation
- [Testing Documentation](../../Completed/06-Testing.md) - Testing completion status

## Contributing

When adding new tests:

1. Follow the existing test structure and patterns
2. Use appropriate fixtures from `conftest.py`
3. Mock external dependencies
4. Include error handling tests
5. Add authentication tests for protected endpoints
6. Document test scenarios in docstrings
7. Run tests individually to verify they work

## Support

For questions or issues with tests:
- Check [TEST_EXECUTION_GUIDE.md](TEST_EXECUTION_GUIDE.md) for common issues
- Review [TEST_STATUS_REPORT.md](TEST_STATUS_REPORT.md) for known limitations
- Open an issue on GitHub for bugs or feature requests

---

**Last Updated**: December 12, 2025  
**Test Coverage**: 63+ test cases across 17 test files  
**Status**: ✅ Comprehensive coverage implemented

