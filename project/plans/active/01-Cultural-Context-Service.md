# In Progress: Cultural Context Service

## Status: 🟡 5% Complete (Infrastructure Only)

**Last Updated**: December 12, 2025  
**Priority**: ⭐⭐⭐ MEDIUM-HIGH

---

## Overview

Service to recognize Swahili deflections, code-switching, and cultural communication patterns specific to East Africa. Currently only infrastructure references exist - no actual implementation.

---

## What Exists (Infrastructure Only)

### ✅ API Gateway Route
**Location**: `services/api-gateway/main.py` lines 230-233

**Implementation**:
```python
@app.get("/cultural/context")
async def get_cultural_context(
    request: Request, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Route to cultural context service"""
    return await route_to_service("cultural_context", "/context", request, credentials)
```

**Status**: ✅ Route exists and is functional  
**Service URL**: `http://cultural-context:8000` (configured in SERVICE_URLS)

**What This Means**:
- ✅ API Gateway can receive requests to `/cultural/context`
- ✅ Request will be forwarded to `http://cultural-context:8000/context`
- ❌ Service at that URL doesn't exist (will return 503/connection error)

### ✅ Docker Compose Configuration
**Location**: `docker-compose.yml` lines 151-170

**Configuration**:
```yaml
cultural-context:
  build:
    context: ./services/cultural-context      # ❌ Directory doesn't exist
    dockerfile: Dockerfile                    # ❌ File doesn't exist
  ports:
    - "8007:8000"                             ✅ Port configured
  environment:
    - DATABASE_URL=...                        ✅ Configured
    - REDIS_URL=...                           ✅ Configured
    - PINECONE_API_KEY=${PINECONE_API_KEY}    ✅ Configured (for RAG)
    - PINECONE_ENVIRONMENT=...                ✅ Configured
  depends_on:
    - postgres                                ✅ Dependency configured
    - redis                                   ✅ Dependency configured
  volumes:
    - ./logs:/app/logs                        ✅ Volume configured
    - ./data/cultural-knowledge-base:/app/data/cultural-knowledge-base  ✅ Volume configured
```

**Status**: ✅ Configuration exists but service directory missing

**What This Means**:
- ✅ Docker Compose knows about the service
- ✅ Environment variables configured
- ✅ Dependencies configured
- ✅ Volumes configured
- ❌ Service directory `./services/cultural-context/` doesn't exist
- ❌ Dockerfile doesn't exist
- ❌ Service won't build or run

### ✅ Architecture Documentation
**Location**: `architecture/system-design.md` lines 181-195

**Documented Features**:
- ✅ Cultural knowledge base management
- ✅ Retrieval-augmented generation (RAG)
- ✅ Bias detection and mitigation
- ✅ Local resource integration
- ✅ Cultural advisory board feedback

**Technology Stack Documented**:
- ✅ Python with FastAPI
- ✅ Vector database (Pinecone/Weaviate)
- ✅ Embedding models for semantic search
- ✅ PostgreSQL for cultural data
- ✅ Analytics for bias monitoring

---

## What's Missing (Implementation)

### ❌ Service Directory Structure
**Status**: Completely missing

**Required Structure**:
```
services/cultural-context/              ❌ DOES NOT EXIST
├── __init__.py                         ❌
├── main.py                             ❌
├── config.py                           ❌
├── Dockerfile                          ❌
├── requirements.txt                    ❌
├── models/
│   └── cultural_models.py              ❌
├── services/
│   ├── deflection_detector.py         ❌
│   ├── code_switch_analyzer.py        ❌
│   └── stoicism_detector.py            ❌
└── data/
    ├── swahili_patterns.json           ❌
    └── cultural_norms.json            ❌
```

### ❌ Main Application
**File**: `services/cultural-context/main.py`  
**Status**: Not created

**Required Endpoints**:
- ❌ `GET /health` - Health check
- ❌ `POST /analyze/deflections` - Detect cultural deflections
- ❌ `POST /analyze/code-switching` - Analyze language switching
- ❌ `POST /analyze/stoicism` - Detect stoic patterns
- ❌ `GET /context` - Get cultural context (called by API Gateway)

### ❌ Deflection Detector
**File**: `services/cultural-context/services/deflection_detector.py`  
**Status**: Not created

**Required Functionality**:
- ❌ Swahili phrase pattern matching
- ❌ Cultural meaning interpretation
- ❌ Voice contradiction detection
- ❌ Severity assessment
- ❌ Suggested probe generation

**Patterns to Detect**:
- ❌ "nimechoka" → emotional exhaustion
- ❌ "sawa" → polite deflection
- ❌ "ni hali ya kawaida" → resigned acceptance
- ❌ "sijui" → avoidance/uncertainty
- ❌ "tutaona" → fatalistic avoidance

### ❌ Code-Switching Analyzer
**File**: `services/cultural-context/services/code_switch_analyzer.py`  
**Status**: Not created

**Required Functionality**:
- ❌ Language switching detection
- ❌ Emotional intensity correlation
- ❌ Pattern recognition (English ↔ Swahili)
- ❌ Context analysis
- ❌ Interpretation generation

**Patterns to Detect**:
- ❌ English → Swahili (increased emotional intensity)
- ❌ Swahili → English (emotional distance)
- ❌ Code-switching frequency
- ❌ Context-based switching

### ❌ Stoicism Detector
**File**: `services/cultural-context/services/stoicism_detector.py`  
**Status**: Not created

**Required Functionality**:
- ❌ Cultural stoicism indicators
- ❌ Session pattern analysis
- ❌ Deflection with voice contradiction
- ❌ Avoidance pattern detection
- ❌ Recommended approach generation

**Indicators to Detect**:
- ❌ Short sessions despite distress
- ❌ Deflection phrases with voice contradiction
- ❌ Avoids direct emotional expression
- ❌ Family/community pressure patterns

### ❌ Data Files

#### Swahili Patterns JSON
**File**: `services/cultural-context/data/swahili_patterns.json`  
**Status**: Not created

**Required Content**:
```json
{
  "deflections": {
    "nimechoka": {
      "literal": "I am tired",
      "cultural_signal": "emotional_exhaustion_giving_up",
      "severity": "high",
      "probe_suggestion": "When you say 'nimechoka' with that tone..."
    },
    "sawa": {
      "literal": "okay/fine",
      "cultural_signal": "polite_deflection",
      "severity": "medium"
    }
  },
  "stress_expressions": {
    "niko na wasiwasi": {
      "meaning": "I have worries",
      "intensity": "moderate"
    }
  }
}
```

#### Cultural Norms JSON
**File**: `services/cultural-context/data/cultural_norms.json`  
**Status**: Not created

**Required Content**:
```json
{
  "stoicism": {
    "description": "Cultural norm of not burdening others",
    "indicators": [...],
    "response_strategy": "permission_based_disclosure"
  },
  "family_duty": {
    "description": "Strong family obligations",
    "indicators": [...]
  }
}
```

### ❌ Database Integration
**Status**: Not implemented

**Required**:
- ❌ Database models for cultural patterns
- ❌ Cultural knowledge base storage
- ❌ Pattern usage tracking
- ❌ Bias monitoring tables

### ❌ Vector Database Integration
**Status**: Not implemented

**Required**:
- ❌ Pinecone/Weaviate integration
- ❌ Embedding model setup
- ❌ Semantic search implementation
- ❌ RAG pipeline

---

## Integration Points

### Current Integration Status

#### ✅ API Gateway Integration
**Status**: Route exists, service missing

**Flow**:
1. ✅ Client calls `GET /cultural/context`
2. ✅ API Gateway receives request
3. ✅ API Gateway forwards to `http://cultural-context:8000/context`
4. ❌ Service doesn't exist → Connection error/503

#### ❌ Speech Processing Integration
**Status**: Not integrated

**Needed**:
- ❌ Get transcript from speech processing
- ❌ Get language detection results
- ❌ Pass to cultural context analyzer

#### ❌ Emotion Analysis Integration
**Status**: Not integrated

**Needed**:
- ❌ Get voice emotion from emotion detector
- ❌ Compare with cultural patterns
- ❌ Detect contradictions

#### ❌ Conversation Engine Integration
**Status**: Not integrated

**Needed**:
- ❌ Inject cultural context into responses
- ❌ Use cultural patterns for response generation
- ❌ Apply cultural sensitivity filters

---

## Docker Compose Analysis

### What's Configured
**File**: `docker-compose.yml` lines 151-170

**Configuration Details**:
- ✅ **Port**: 8007 (external) → 8000 (internal)
- ✅ **Build Context**: `./services/cultural-context`
- ✅ **Environment Variables**:
  - `DATABASE_URL` - PostgreSQL connection
  - `REDIS_URL` - Redis connection
  - `PINECONE_API_KEY` - Vector database API key
  - `PINECONE_ENVIRONMENT` - Vector database environment
- ✅ **Dependencies**: postgres, redis
- ✅ **Volumes**:
  - Logs: `./logs:/app/logs`
  - Cultural knowledge base: `./data/cultural-knowledge-base:/app/data/cultural-knowledge-base`

### What's Missing
- ❌ Service directory: `services/cultural-context/`
- ❌ Dockerfile
- ❌ requirements.txt
- ❌ All Python files
- ❌ Data files

**Impact**: Docker Compose will fail to build this service.

---

## Current Behavior

### When API Gateway Route is Called

**Scenario**: Client calls `GET /api/cultural/context`

**What Happens**:
1. ✅ Request reaches API Gateway
2. ✅ Authentication middleware validates token
3. ✅ Route handler executes
4. ✅ HTTP client attempts to call `http://cultural-context:8000/context`
5. ❌ Connection fails (service doesn't exist)
6. ❌ Returns 503 Service Unavailable or connection error

**Error Response**:
```json
{
  "error": "Service cultural_context not available",
  "status_code": 503
}
```

---

## Implementation Requirements

### Phase 1: Service Structure (Week 1)
**Estimated**: 2-3 days

**Tasks**:
1. Create `services/cultural-context/` directory
2. Create `main.py` with FastAPI app
3. Create `config.py` with settings
4. Create `Dockerfile`
5. Create `requirements.txt`
6. Create `models/cultural_models.py`
7. Create directory structure

**Deliverable**: Service skeleton that responds to health check

### Phase 2: Data Collection (Week 1-2)
**Estimated**: 3-5 days

**Tasks**:
1. Research Swahili deflection patterns
2. Create `swahili_patterns.json`
3. Create `cultural_norms.json`
4. Validate patterns with cultural consultants
5. Document pattern meanings

**Deliverable**: Complete data files with validated patterns

### Phase 3: Deflection Detector (Week 2)
**Estimated**: 3-4 days

**Tasks**:
1. Implement pattern matching
2. Implement cultural meaning mapping
3. Implement voice contradiction detection
4. Implement severity assessment
5. Implement probe suggestion generation
6. Write unit tests

**Deliverable**: Working deflection detection

### Phase 4: Code-Switching Analyzer (Week 2-3)
**Estimated**: 3-4 days

**Tasks**:
1. Implement language detection per segment
2. Implement switching pattern detection
3. Implement emotional intensity mapping
4. Implement context analysis
5. Write unit tests

**Deliverable**: Working code-switching analysis

### Phase 5: Stoicism Detector (Week 3)
**Estimated**: 2-3 days

**Tasks**:
1. Implement stoicism indicators
2. Implement session pattern analysis
3. Implement avoidance detection
4. Implement response strategy selection
5. Write unit tests

**Deliverable**: Working stoicism detection

### Phase 6: Integration (Week 3-4)
**Estimated**: 2-3 days

**Tasks**:
1. Integrate with API Gateway
2. Integrate with speech processing
3. Integrate with emotion analysis
4. End-to-end testing
5. Documentation

**Deliverable**: Fully integrated service

---

## Dependencies

### External Dependencies
**Status**: Not installed

**Required**:
- ❌ Pinecone client (for vector database)
- ❌ Sentence transformers (for embeddings)
- ❌ Language detection library
- ❌ NLP libraries for pattern matching

### Internal Dependencies
**Status**: Available

**Available**:
- ✅ Speech Processing Service (for transcript)
- ✅ Emotion Analysis Service (for voice emotion)
- ✅ API Gateway (for routing)
- ✅ PostgreSQL (for storage)
- ✅ Redis (for caching)

**Not Yet Available**:
- ❌ Dissonance Detector (for dissonance patterns)
- ❌ Baseline Tracker (for user patterns)

---

## Success Metrics

### Target Metrics
- ✅ Swahili deflection detection: **0%** → Target: **80%+**
- ✅ Code-switching recognition: **0%** → Target: **75%+**
- ✅ Stoicism pattern detection: **0%** → Target: **70%+**
- ✅ Cultural sensitivity score: **N/A** → Target: **85%+** (user feedback)

### Current Status
- Deflection detection: **0%** (not implemented)
- Code-switching: **0%** (not implemented)
- Stoicism detection: **0%** (not implemented)
- User feedback: **N/A** (no users yet)

---

## Blockers

### Current Blockers
1. **No service implementation** - Directory doesn't exist
2. **No data files** - Pattern databases missing
3. **No cultural consultant** - Patterns need validation
4. **No training data** - Need examples for testing

### Dependencies
- Can be built independently (no blocking dependencies)
- Can run in parallel with other services
- Needs speech processing for transcript (available)
- Needs emotion analysis for voice emotion (available)

---

## Estimated Completion

**Total Effort**: 1.5-2 weeks  
**Team**: 1 NLP engineer + 1 cultural consultant (part-time)  
**Lines of Code**: ~600-800 lines + data files  
**Complexity**: Medium (pattern matching, cultural knowledge base)

**Timeline**: Weeks 8-9 (after Micro-Moment Detector, can run in parallel)

---

## Next Immediate Steps

1. **Create Service Directory** (30 minutes)
   ```bash
   mkdir -p services/cultural-context/{models,services,data}
   ```

2. **Create Basic FastAPI App** (2 hours)
   - `main.py` with health check
   - `config.py` with settings
   - `Dockerfile`
   - `requirements.txt`

3. **Create Data Files** (1 day)
   - Research Swahili patterns
   - Create JSON files
   - Validate with consultant

4. **Implement Deflection Detector** (3-4 days)
   - Pattern matching
   - Cultural meaning mapping
   - Voice contradiction detection

---

## References

- **Design Spec**: `DESIGN_CRITIQUE_AND_IMPROVEMENTS.md` - Gap 4
- **Architecture**: `architecture/system-design.md` lines 181-195
- **Progress Report**: `PROGRESS_REPORT.md` - Gap 4
- **Missing Components**: `MISSING_COMPONENTS_REPORT.md` - Component 4
