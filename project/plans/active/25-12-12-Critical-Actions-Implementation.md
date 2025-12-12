# Plan: Critical Actions Implementation

**Date**: December 12, 2025  
**Status**: In Progress  
**Priority**: High

## Overview

Implementing critical actions identified in PROJECT_RULES_AND_STATUS.md:
1. Create missing test files (Safety Moderation, Sync Service, Cultural Context)
2. Complete Cultural Context Service implementation
3. Fix Encryption Service batch endpoints (2 tests skipped)
4. Replace mock authentication with real implementation

## Objectives

- [ ] Create test files for 3 services missing test coverage
- [ ] Complete Cultural Context Service implementation (Swahili patterns, code-switching)
- [ ] Fix Encryption Service batch endpoints to accept JSON body
- [ ] Replace mock authentication endpoints with real database-backed auth

## Implementation Steps

### Phase 1: Create Missing Test Files

1. **Safety Moderation Service Tests**
   - Create `tests/services/safety-moderation/test_safety_moderation.py`
   - Test health check endpoint
   - Test content validation endpoint
   - Test crisis term detection
   - Test unsafe advice detection
   - Test content type handling (response vs user_input)
   - Test authentication requirements
   - Test error handling

2. **Sync Service Tests**
   - Create `tests/services/sync-service/test_sync_service.py`
   - Test health check endpoint
   - Test data upload endpoint
   - Test sync queue operations
   - Test database integration
   - Test authentication requirements
   - Test error handling

3. **Cultural Context Service Tests**
   - Create `tests/services/cultural-context/test_cultural_context.py`
   - Test health check endpoint
   - Test context retrieval endpoint
   - Test knowledge base loading
   - Test caching functionality
   - Test language filtering
   - Test authentication requirements
   - Test error handling

### Phase 2: Fix Encryption Service Batch Endpoints

1. **Update Batch Encrypt Endpoint**
   - Change from query parameters to JSON body
   - Create Pydantic model for batch request
   - Update endpoint to accept JSON body
   - Update test to use JSON body

2. **Update Batch Decrypt Endpoint**
   - Change from query parameters to JSON body
   - Create Pydantic model for batch request
   - Update endpoint to accept JSON body
   - Update test to use JSON body

3. **Remove Skip Markers from Tests**
   - Update test_batch_encrypt_messages to use JSON body
   - Update test_batch_decrypt_messages to use JSON body
   - Verify all tests pass

### Phase 3: Complete Cultural Context Service

1. **Enhance Swahili Pattern Database**
   - Add Swahili deflection patterns to kb.json
   - Add code-switching patterns
   - Add emotional expressions in Swahili
   - Add cultural context entries

2. **Implement Code-Switching Detection**
   - Add code-switching analyzer function
   - Detect English-Swahili code-switching
   - Detect emotional intensity markers
   - Integrate with context retrieval

3. **Implement Deflection Detection**
   - Add deflection pattern matcher
   - Detect Swahili polite deflections ("sawa", "nimechoka")
   - Detect emotional exhaustion markers
   - Integrate with context retrieval

### Phase 4: Replace Mock Authentication

1. **Update Login Endpoint**
   - Replace mock implementation with real authenticate_user call
   - Use database session from dependency
   - Return real JWT tokens
   - Handle authentication errors properly

2. **Update Register Endpoint**
   - Replace mock implementation with real create_user call
   - Use database session from dependency
   - Return real user data
   - Handle validation errors properly

3. **Update Tests**
   - Update API Gateway auth tests to use real database
   - Test password hashing
   - Test user creation
   - Test authentication flow

## Files to Create/Modify

### New Files
- `tests/services/safety-moderation/test_safety_moderation.py`
- `tests/services/sync-service/test_sync_service.py`
- `tests/services/cultural-context/test_cultural_context.py`

### Modified Files
- `services/encryption-service/main.py` - Update batch endpoints
- `services/encryption-service/models/encryption_models.py` - Add batch request models
- `tests/services/encryption-service/test_encryption_service.py` - Update batch tests
- `services/cultural-context/main.py` - Add code-switching and deflection detection
- `services/cultural-context/data/kb.json` - Add Swahili patterns
- `services/api-gateway/main.py` - Replace mock auth endpoints

## Testing Strategy

### Unit Tests
- Each service gets comprehensive test coverage
- All endpoints tested
- Error handling tested
- Authentication tested

### Integration Tests
- Test service-to-service communication
- Test database integration
- Test authentication flow

## Dependencies

- ✅ Database schema exists (users table with password_hash)
- ✅ Auth service functions exist (authenticate_user, create_user)
- ✅ Test fixtures exist (conftest.py)
- ✅ Services are implemented

## Timeline

- **Phase 1**: 2-3 hours (Create test files)
- **Phase 2**: 1 hour (Fix batch endpoints)
- **Phase 3**: 2-3 hours (Complete Cultural Context)
- **Phase 4**: 1-2 hours (Replace mock auth)

**Total**: 6-9 hours

## Risks & Mitigation

### Risk 1: Test file structure mismatch
- **Mitigation**: Follow existing test patterns from other services

### Risk 2: Batch endpoint changes break existing code
- **Mitigation**: Update both endpoint and tests together

### Risk 3: Cultural Context patterns incomplete
- **Mitigation**: Start with MVP patterns, can expand later

### Risk 4: Real auth breaks existing tests
- **Mitigation**: Update tests to use real database fixtures

## Success Criteria

- [ ] All 3 missing test files created and passing
- [ ] Encryption Service batch endpoints accept JSON body
- [ ] All batch tests passing (no skips)
- [ ] Cultural Context Service has Swahili patterns and code-switching
- [ ] API Gateway uses real authentication (no mocks)
- [ ] All tests passing

## Next Steps After Completion

1. Update PROJECT_RULES_AND_STATUS.md with new status
2. Update TEST_STATUS_REPORT.md
3. Create progress report

