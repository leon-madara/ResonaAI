# ResonaAI: Quick Reference Guide

**Last Updated**: December 12, 2025  
**Purpose**: Quick reference for project rules, test standards, and implementation status

---

## Test-Based Project Rules (Quick Reference)

### ✅ All Services MUST Have:
1. FastAPI application (`main.py`)
2. Health check endpoint (`GET /health`)
3. Test file: `tests/services/[service-name]/test_[service_name].py`
4. Minimum 5 test cases (health, main functionality, error handling, validation, auth)
5. Error handling comprehensive
6. Input validation implemented
7. CORS middleware configured
8. Dockerfile for containerization

### ✅ Test Execution Standards:
- Run tests individually per service: `pytest tests/services/[service-name]/ -v`
- All tests must pass before deployment
- Minimum 80% test coverage required
- Tests use fixtures from `conftest.py`
- Tests mock external dependencies

---

## Service Status Quick Look

| Service | Tests | Implementation | Status |
|---------|-------|----------------|--------|
| API Gateway | ✅ | 🟡 95% (mock auth) | 🟡 |
| Speech Processing | ✅ | ✅ 100% | ✅ |
| Emotion Analysis | ✅ | ✅ 100% | ✅ |
| Conversation Engine | ✅ | ✅ 100% | ✅ |
| Crisis Detection | ✅ | ✅ 100% | ✅ |
| Safety Moderation | ❌ | ✅ 100% | 🟡 |
| Sync Service | ❌ | ✅ 100% | 🟡 |
| Cultural Context | ❌ | 🔴 5% | 🔴 |
| Encryption Service | ✅ 13/15 | ✅ 100% | 🟡 |
| Dissonance Detector | ✅ | ✅ 100% | ✅ |
| Baseline Tracker | ✅ | ✅ 100% | ✅ |
| Consent Management | ✅ | ✅ 100% | ✅ |

**Legend**: ✅ Complete | 🟡 Partial | 🔴 Incomplete

---

## Critical Actions Required

### 🔴 High Priority
1. **Create Missing Test Files**
   - `tests/services/safety-moderation/test_safety_moderation.py`
   - `tests/services/sync-service/test_sync_service.py`
   - `tests/services/cultural-context/test_cultural_context.py`

2. **Complete Cultural Context Service**
   - Implement Swahili pattern database
   - Implement code-switching detection
   - Implement deflection detection

### 🟡 Medium Priority
3. **Fix Encryption Service Batch Endpoints**
   - Update endpoints to accept JSON body
   - Update tests to use JSON body

4. **Replace Mock Authentication**
   - Implement real user database integration
   - Implement password hashing (bcrypt)

---

## Test Execution Commands

```bash
# Run all service tests individually (recommended)
pytest tests/services/encryption-service/ -v
pytest tests/services/dissonance-detector/ -v
pytest tests/services/baseline-tracker/ -v
pytest tests/services/conversation-engine/ -v
pytest tests/services/crisis-detection/ -v
pytest tests/services/consent-management/ -v

# Run with coverage
pytest tests/services/[service-name]/ --cov=services/[service-name] --cov-report=html

# Run integration tests
pytest tests/integration/ -v
```

---

## Quality Gate Checklist

Before marking a service as "Complete":
- [ ] All tests passing (or skipped with documented reason)
- [ ] Test coverage ≥ 80%
- [ ] Health check endpoint functional
- [ ] Error handling comprehensive
- [ ] Input validation implemented
- [ ] Authentication middleware integrated (if applicable)
- [ ] CORS middleware configured
- [ ] Proper logging implemented
- [ ] Docker container builds successfully
- [ ] Service integrates with API Gateway

---

## Documentation References

- **System Design**: `architecture/system-design.md`
- **Test Standards**: `tests/README.md`, `tests/TEST_STATUS_REPORT.md`
- **Full Status Mapping**: `architecture/PROJECT_RULES_AND_STATUS.md`
- **Completed Work**: `Completed/07-Documentation.md`
- **In Progress**: `In Progress/README.md`
- **To Do**: `project/backlog/README.md`

---

**Quick Status**: 9/12 services complete with tests | 2 services need tests | 1 service incomplete

