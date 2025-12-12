# Test Execution Guide

**Last Updated**: December 12, 2025

## Overview

This guide provides detailed instructions for running tests in the ResonaAI platform. Due to module caching conflicts when running all services together, tests are designed to run individually per service.

## Prerequisites

### Required Software

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Required Packages

Install test dependencies:

```bash
pip install -r requirements.txt
```

Key test packages:
- `pytest==7.4.3`
- `pytest-asyncio==0.21.1`
- `pytest-cov==4.1.0`
- `fastapi[all]`
- `cryptography`
- `sqlalchemy`
- `redis`
- `transformers`
- `scikit-learn`
- `PyJWT`

## Test Execution Methods

### Method 1: Run All Tests (May Have Conflicts)

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=src --cov=services --cov-report=html
```

**Note**: This may encounter module caching conflicts. If you see import errors, use Method 2.

### Method 2: Run Tests Per Service (Recommended)

Run tests individually per service to avoid module caching conflicts:

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

# Auth Service
pytest tests/services/auth_service/ -v
```

### Method 3: Run Specific Test Files

```bash
# Run specific test file
pytest tests/services/encryption-service/test_encryption_service.py -v

# Run specific test class
pytest tests/services/encryption-service/test_encryption_service.py::TestEncryptionService -v

# Run specific test method
pytest tests/services/encryption-service/test_encryption_service.py::TestEncryptionService::test_health_check -v
```

### Method 4: Run by Test Type

```bash
# Run only integration tests
pytest tests/integration/ -v

# Run only unit tests (core components)
pytest tests/test_*.py -v

# Run only service tests
pytest tests/services/ -v
```

### Method 5: Run with Markers

```bash
# Run only slow tests
pytest -m slow -v

# Run only integration tests
pytest -m integration -v

# Run only unit tests
pytest -m unit -v

# Run async tests
pytest -m asyncio -v
```

## Test Execution Scripts

### Using the Test Runner Script

A helper script is available for running tests:

```bash
# Run all service tests individually
python scripts/run_tests.py

# Run specific service
python scripts/run_tests.py --service encryption-service

# Run with coverage
python scripts/run_tests.py --coverage
```

## Common Test Execution Scenarios

### Scenario 1: Quick Test Run

```bash
# Run encryption service tests (fastest, most complete)
pytest tests/services/encryption-service/ -v
```

### Scenario 2: Full Test Suite

```bash
# Run all services individually
for service in encryption-service dissonance-detector baseline-tracker conversation-engine crisis-detection consent-management; do
    echo "Testing $service..."
    pytest tests/services/$service/ -v
done
```

### Scenario 3: Test with Coverage

```bash
# Run with HTML coverage report
pytest tests/services/encryption-service/ --cov=services/encryption-service --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Scenario 4: Debug Failing Tests

```bash
# Run with detailed output
pytest tests/services/encryption-service/ -vv

# Run with print statements visible
pytest tests/services/encryption-service/ -s

# Run with pdb debugger on failure
pytest tests/services/encryption-service/ --pdb
```

### Scenario 5: Run Tests in Parallel

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/services/encryption-service/ -n 4
```

## Troubleshooting

### Issue 1: Module Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError` when running all tests together

**Cause**: Python's module caching conflicts with relative imports

**Solution**:
1. Run tests individually per service (recommended)
2. Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
3. Use pytest-xdist for isolated execution

### Issue 2: Database Connection Errors

**Symptoms**: Database connection errors in tests

**Cause**: Tests may be trying to connect to real database

**Solution**:
- Tests use in-memory SQLite by default
- Ensure `conftest.py` fixtures are being used
- Check that `TEST_DATABASE_URL` is set correctly

### Issue 3: Missing Dependencies

**Symptoms**: `ImportError` for specific packages

**Cause**: Missing test dependencies

**Solution**:
```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio pytest-cov
```

### Issue 4: Authentication Token Errors

**Symptoms**: `401 Unauthorized` errors in tests

**Cause**: Test fixtures not generating valid tokens

**Solution**:
- Ensure `conftest.py` is in the test directory
- Check that `TEST_JWT_SECRET_KEY` matches service configuration
- Verify token generation in fixtures

### Issue 5: Redis Connection Errors

**Symptoms**: Redis connection errors in API Gateway tests

**Cause**: Tests trying to connect to real Redis

**Solution**:
- Tests use mocked Redis by default
- Ensure `mock_redis` fixture is being used
- Check that Redis is mocked in test setup

## Test Output Interpretation

### Successful Test Run

```
tests/services/encryption-service/test_encryption_service.py::TestEncryptionService::test_health_check PASSED
tests/services/encryption-service/test_encryption_service.py::TestEncryptionService::test_encrypt_data PASSED
...
======================== 13 passed, 2 skipped in 2.34s ========================
```

### Failed Test

```
tests/services/encryption-service/test_encryption_service.py::TestEncryptionService::test_encrypt_data FAILED
...
AssertionError: assert response.status_code == 200
...
======================== 1 failed, 12 passed in 2.45s ========================
```

### Skipped Test

```
tests/services/encryption-service/test_encryption_service.py::TestEncryptionService::test_batch_encrypt_messages SKIPPED
...
======================== 13 passed, 2 skipped in 2.34s ========================
```

## Best Practices

### 1. Run Tests Before Committing

```bash
# Run relevant service tests before committing
pytest tests/services/your-service/ -v
```

### 2. Run Tests in CI/CD

Set up automated test execution in your CI/CD pipeline:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: |
    pytest tests/services/encryption-service/ -v
    pytest tests/services/dissonance-detector/ -v
    # ... other services
```

### 3. Monitor Test Coverage

```bash
# Generate coverage report
pytest --cov=src --cov=services --cov-report=term-missing

# Aim for 80%+ coverage
pytest --cov=src --cov=services --cov-report=term-missing --cov-fail-under=80
```

### 4. Fix Failing Tests First

Always fix failing tests before adding new features or tests.

### 5. Write Tests for New Features

When adding new features:
1. Write tests first (TDD approach)
2. Run tests to verify they fail initially
3. Implement feature
4. Run tests to verify they pass
5. Refactor if needed

## Performance Considerations

### Test Execution Time

- **Individual Service**: ~1-2 seconds per service
- **All Services**: ~10-15 seconds (if no conflicts)
- **With Coverage**: ~20-30 seconds per service

### Optimization Tips

1. Use `pytest-xdist` for parallel execution
2. Run only relevant tests during development
3. Use markers to skip slow tests: `pytest -m "not slow"`
4. Cache test results when possible

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: |
          pytest tests/services/encryption-service/ -v
          pytest tests/services/dissonance-detector/ -v
          pytest tests/services/baseline-tracker/ -v
          pytest tests/services/conversation-engine/ -v
          pytest tests/services/crisis-detection/ -v
          pytest tests/services/consent-management/ -v
      - name: Generate coverage
        run: pytest --cov=src --cov=services --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test Status Report](TEST_STATUS_REPORT.md)
- [Project Overview](PROJECT_OVERVIEW.md)

---

**Last Updated**: December 12, 2025

