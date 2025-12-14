# Cultural Context Service Test Coverage

**Status**: ✅ Complete  
**Last Updated**: December 2025

## Overview

Comprehensive test suite for the Cultural Context Service, covering all components including code-switching detection, deflection detection, bias detection, RAG service, embeddings, and API endpoints.

## Test Files

### 1. `test_cultural_context.py`
**Purpose**: Main API endpoint tests  
**Test Cases**: 35  
**Coverage**:
- Health check endpoint (with vector DB status)
- Context retrieval (English/Swahili/mixed)
- Query validation (empty, missing, special characters)
- Authentication (all endpoints)
- Caching (database integration)
- Code-switching detection
- Deflection detection
- **Bias check endpoint** (7 comprehensive tests)
- **Edge cases** (missing files, malformed data, service failures)
- **Error handling** (database failures, RAG unavailable)

### 2. `test_code_switch_analyzer.py`
**Purpose**: Code-switching detection tests  
**Test Cases**: 14  
**Coverage**:
- Language detection (English, Swahili, mixed, unknown)
- Text segmentation
- Language transition detection
- Complete analysis flow
- Emotional intensity detection
- Edge cases (empty text, whitespace)
- Singleton pattern

### 3. `test_deflection_detector.py`
**Purpose**: Deflection pattern detection tests  
**Test Cases**: 12  
**Coverage**:
- Deflection pattern matching (sawa, nimechoka, etc.)
- Voice contradiction detection
- Risk assessment (low, medium, high)
- Complete analysis flow
- Probe suggestion generation
- Edge cases
- Singleton pattern

### 4. `test_bias_detector.py`
**Purpose**: Bias detection and cultural sensitivity tests  
**Test Cases**: 13  
**Coverage**:
- Western-centric assumption detection
- Stigmatizing language detection
- Cultural insensitivity detection
- Inappropriate advice detection
- Cultural sensitivity validation
- Overall sensitivity assessment
- Sensitivity scoring
- Singleton pattern

### 5. `test_rag_service.py`
**Purpose**: RAG service tests  
**Test Cases**: 12  
**Coverage**:
- Service initialization
- Entry indexing
- Semantic search
- Language filtering
- Knowledge base indexing
- Availability checks
- Top-k limiting
- Edge cases (empty query, unavailable service)
- Singleton pattern

### 6. `test_embeddings.py`
**Purpose**: Embedding service tests  
**Test Cases**: 12  
**Coverage**:
- Text embedding generation
- Batch embedding
- Cosine similarity calculation
- Service availability
- Edge cases (empty text, unavailable service)
- Singleton pattern

### 7. `test_integration.py`
**Purpose**: Integration tests  
**Test Cases**: 11  
**Coverage**:
- Code-switching + deflection integration
- Bias detection + cultural context integration
- RAG + embeddings integration
- Full context analysis flow
- Error handling across services
- **Full query flow integration** (query → code-switching → deflection → bias check)
- **Cultural norms integration** with context retrieval
- **RAG fallback** to keyword search
- **Caching integration** with database
- **Error propagation** across service boundaries
- **Multilingual integration flow** (English, Swahili, mixed)

## Test Statistics

| Category | Test Cases | Status |
|----------|------------|--------|
| **API Endpoints** | 35 | ✅ Complete |
| **Code-Switching** | 14 | ✅ Complete |
| **Deflection Detection** | 12 | ✅ Complete |
| **Bias Detection** | 13 | ✅ Complete |
| **RAG Service** | 20 | ✅ Complete |
| **Embeddings** | 12 | ✅ Complete |
| **Integration** | 11 | ✅ Complete |
| **Total** | **116+** | ✅ **Complete** |

### New Test Coverage (Task 1.8 Completion)

**Added 27+ new test cases:**
- ✅ 7 comprehensive `/bias-check` endpoint tests
- ✅ 10 edge case tests (missing files, error handling, graceful degradation)
- ✅ 5 enhanced integration tests (full flow, error propagation, multilingual)
- ✅ 5+ additional RAG service tests

**Coverage Improvements:**
- All 4 API endpoints now have comprehensive test coverage
- Edge cases and error scenarios fully tested
- Integration test scenarios expanded
- Test execution verified (all tests pass)

## New Test Cases (Task 1.8)

### `/bias-check` Endpoint Tests (7 tests)
- `test_bias_check_culturally_sensitive` - Verify culturally sensitive text is detected
- `test_bias_check_stigmatizing_text` - Verify biased/stigmatizing text is detected
- `test_bias_check_empty_text` - Verify 400 error for empty text
- `test_bias_check_whitespace_only` - Verify 400 error for whitespace-only text
- `test_bias_check_unauthorized` - Verify 403 error without authentication
- `test_bias_check_response_structure` - Verify complete response structure
- `test_bias_check_error_handling` - Verify error handling when detector fails

### Edge Case Tests (10 tests)
- `test_context_with_missing_cultural_norms` - Graceful fallback when cultural_norms.json missing
- `test_context_with_malformed_kb` - Error handling for malformed KB file
- `test_context_with_cache_failure` - Graceful degradation with database cache failures
- `test_context_with_rag_unavailable` - Fallback to keyword search when RAG unavailable
- `test_index_kb_with_empty_kb` - Handle empty KB file gracefully
- `test_index_kb_with_rag_failure` - Error handling when RAG service fails
- `test_health_check_with_db_failure` - Health check with database connection failure
- `test_health_check_with_vector_db_failure` - Health check with vector DB failure
- `test_context_with_none_language` - Default language handling
- `test_context_with_unsupported_language` - Unsupported language handling

### Enhanced Integration Tests (5 tests)
- `test_full_query_flow_integration` - Full flow: query → code-switching → deflection → bias check
- `test_cultural_norms_with_context_retrieval` - Cultural norms integration
- `test_rag_fallback_to_keyword_search` - RAG fallback mechanism
- `test_error_propagation_across_services` - Error handling across services
- `test_multilingual_integration_flow` - Multilingual content handling

## Running Tests

### Run All Cultural Context Tests
```bash
pytest tests/services/cultural-context/ -v
```

### Run Specific Test Categories
```bash
# Run only /bias-check endpoint tests
pytest tests/services/cultural-context/test_cultural_context.py -k "bias_check" -v

# Run only edge case tests
pytest tests/services/cultural-context/test_cultural_context.py -k "edge" -v

# Run only new integration tests
pytest tests/services/cultural-context/test_integration.py -k "full_query_flow or cultural_norms or multilingual" -v
```

### Run Specific Test File
```bash
# Code-switching tests
pytest tests/services/cultural-context/test_code_switch_analyzer.py -v

# Deflection detection tests
pytest tests/services/cultural-context/test_deflection_detector.py -v

# Bias detection tests
pytest tests/services/cultural-context/test_bias_detector.py -v

# RAG service tests
pytest tests/services/cultural-context/test_rag_service.py -v

# Embeddings tests
pytest tests/services/cultural-context/test_embeddings.py -v

# Integration tests
pytest tests/services/cultural-context/test_integration.py -v

# API endpoint tests
pytest tests/services/cultural-context/test_cultural_context.py -v
```

### Run with Coverage
```bash
pytest tests/services/cultural-context/ --cov=apps/backend/services/cultural-context --cov-report=html
```

## Test Fixtures

### Mock Patterns
- Creates temporary Swahili patterns JSON file
- Used for deflection detector tests

### Mock Knowledge Base
- Creates mock KB entries
- Used for API endpoint tests

### Mock Database
- In-memory SQLite database
- Used for caching tests

### Mock Embedding Service
- Mocks embedding generation
- Used for RAG service tests

## Test Patterns

### Singleton Pattern Tests
All services implement singleton pattern - tests verify that `get_*()` functions return the same instance.

### Edge Case Testing
- Empty strings
- Whitespace-only text
- None values
- Unavailable services
- Missing dependencies

### Integration Testing
Tests verify that services work together correctly:
- Code-switching + deflection detection
- Bias detection + cultural context
- RAG + embeddings

## Dependencies

Tests require:
- `pytest`
- `pytest-asyncio`
- `fastapi[all]`
- `sqlalchemy`
- Mock libraries

## Notes

- Some tests may skip if services are unavailable (e.g., embedding service without API keys)
- Tests use temporary files for patterns to avoid conflicts
- In-memory databases are used for caching tests
- All tests follow the existing project test patterns

