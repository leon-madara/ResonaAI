# Backlog: Cultural Context Service

**Status**: 🔴 5% Complete (Infrastructure Only)  
**Priority**: ⭐⭐⭐⭐⭐ CRITICAL  
**Estimated Effort**: 2-3 weeks  
**Blocking**: Core differentiator not functional

---

## Overview

**THE CRITICAL GAP** - Service to recognize Swahili deflections, code-switching, and cultural communication patterns specific to East Africa. Currently only infrastructure references exist - no actual implementation.

This is essential for ResonaAI's unique value proposition of understanding East African cultural context.

---

## What Exists (Infrastructure Only)

### ✅ API Gateway Route
- Route configured: `GET /cultural/context`
- Service URL: `http://cultural-context:8000`
- Status: Route exists but service doesn't

### ✅ Docker Compose Configuration
- Service definition exists
- Port mapping: 8007:8000
- Environment variables configured
- Dependencies configured
- **Problem**: Service directory doesn't exist

---

## What's Missing (Implementation)

### ❌ Service Directory Structure
```
services/cultural-context/              ❌ DOES NOT EXIST
├── main.py                             ❌ FastAPI app
├── config.py                           ❌ Configuration
├── Dockerfile                          ❌ Container config
├── requirements.txt                    ❌ Dependencies
├── models/
│   └── cultural_models.py              ❌ Data models
├── services/
│   ├── deflection_detector.py         ❌ Swahili deflections
│   ├── code_switch_analyzer.py        ❌ Language switching
│   └── stoicism_detector.py            ❌ Cultural patterns
└── data/
    ├── swahili_patterns.json           ❌ Pattern database
    └── cultural_norms.json            ❌ Cultural knowledge
```

### ❌ Core Functionality

**Deflection Patterns to Detect**:
- "nimechoka" → emotional exhaustion/giving up
- "sawa" → polite deflection (may not be okay)
- "sijui" → avoidance/uncertainty
- "tutaona" → fatalistic avoidance

**Code-Switching Analysis**:
- English → Swahili (increased emotional intensity)
- Swahili → English (emotional distance)
- Context-based switching patterns

**Stoicism Detection**:
- Cultural norm of not burdening others
- Short sessions despite distress
- Avoidance of direct emotional expression

---

## Implementation Plan

### Phase 1: Service Structure (Week 1)
- [ ] Create service directory structure
- [ ] Create FastAPI application with health check
- [ ] Create configuration and Docker setup
- [ ] Create data models

### Phase 2: Data Collection (Week 1-2)
- [ ] Research Swahili deflection patterns
- [ ] Create pattern databases (JSON files)
- [ ] Validate patterns with cultural consultants
- [ ] Document cultural meanings

### Phase 3: Core Implementation (Week 2-3)
- [ ] Implement deflection detector
- [ ] Implement code-switching analyzer
- [ ] Implement stoicism detector
- [ ] Write comprehensive tests

### Phase 4: Integration (Week 3)
- [ ] Integrate with speech processing
- [ ] Integrate with emotion analysis
- [ ] End-to-end testing
- [ ] Documentation

---

## Success Criteria

- ✅ Swahili deflection detection: 80%+ accuracy
- ✅ Code-switching recognition: 75%+ accuracy
- ✅ Stoicism pattern detection: 70%+ accuracy
- ✅ Service integrated with API Gateway
- ✅ Cultural sensitivity validated by consultants

---

## Dependencies

**Available**:
- ✅ Speech Processing Service (for transcript)
- ✅ Emotion Analysis Service (for voice emotion)
- ✅ API Gateway (for routing)
- ✅ Database infrastructure

**Needed**:
- Cultural consultant for pattern validation
- Swahili language expertise
- East African cultural knowledge

---

## Impact

**Without This Service**:
- ❌ Cannot understand cultural deflections
- ❌ Missing core differentiator
- ❌ No cultural sensitivity
- ❌ Generic responses instead of culturally-aware

**With This Service**:
- ✅ Understands "nimechoka" means more than "tired"
- ✅ Detects cultural communication patterns
- ✅ Provides culturally-appropriate responses
- ✅ Differentiates from generic mental health apps

---

## Next Steps

1. **Create Service Directory** (30 minutes)
2. **Research Cultural Patterns** (2-3 days)
3. **Implement Core Detection** (1-2 weeks)
4. **Validate with Consultants** (3-5 days)
5. **Integration Testing** (2-3 days)

This is the **highest priority** item blocking production readiness.