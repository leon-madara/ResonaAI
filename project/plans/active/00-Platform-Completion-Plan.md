# ResonaAI Platform Completion Plan

**Status**: Active  
**Created**: December 12, 2025  
**Priority**: Critical  
**Estimated Duration**: 10-14 weeks

---

## Overview

This plan addresses all incomplete components of the ResonaAI mental health platform, prioritized by dependencies and criticality. The work is divided into 6 phases.

## Current State Summary

| Category | Status | Notes |
|----------|--------|-------|
| Infrastructure | 80% | Docker, K8s, monitoring complete |
| Core Services | 95% | Auth is mocked, STT partial |
| Voice Processing | 85% | Uses default classifier |
| Frontend | 60% | Pages missing - app crashes |
| Testing | 0% | Critical gap |
| Missing Services | 5-15% | Only Dockerfiles exist |

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                        COMPLETED                                │
├─────────────────────────────────────────────────────────────────┤
│ API Gateway (95%) │ Speech Processing (90%) │ Encryption (100%)│
│ Consent Mgmt (100%) │ Emotion Detector (85%)                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PHASE 1: FOUNDATION                          │
├─────────────────────────────────────────────────────────────────┤
│ Frontend Pages (0%) │ Real Auth (0%) │ DB Migrations (0%)      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               PHASE 2: CORE INNOVATION                          │
├─────────────────────────────────────────────────────────────────┤
│                   Dissonance Detector (0%)                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 3: PERSONALIZATION                           │
├─────────────────────────────────────────────────────────────────┤
│                   Baseline Tracker (0%)                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              PHASE 4: MICROSERVICES                             │
├─────────────────────────────────────────────────────────────────┤
│ Conversation Engine │ Crisis Detection │ Cultural Context      │
│ Safety Moderation │ Sync Service │ Emotion Analysis Service    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│            PHASE 5: ADVANCED FEATURES                           │
├─────────────────────────────────────────────────────────────────┤
│ Micro-Moment Detector │ Adaptive Interface Builder             │
└─────────────────────────────────────────────────────────────────┘

PHASE 6: TESTING (Runs in parallel with all phases)
```

---

## Phase 1: Foundation (Weeks 1-2)

### 1.1 Frontend Pages
**Status**: Not Started  
**Priority**: P0 - App crashes without these  
**Location**: `web-app/src/pages/`

| Page | Priority | Status |
|------|----------|--------|
| `LoginPage.tsx` | Critical | [ ] Not Started |
| `RegisterPage.tsx` | Critical | [ ] Not Started |
| `HomePage.tsx` | Critical | [ ] Not Started |
| `ChatPage.tsx` | Critical | [ ] Not Started |
| `ProfilePage.tsx` | Medium | [ ] Not Started |
| `SettingsPage.tsx` | Medium | [ ] Not Started |
| `ConsentPage.tsx` | High | [ ] Not Started |
| `CrisisPage.tsx` | High | [ ] Not Started |
| `OfflinePage.tsx` | Medium | [ ] Not Started |

**Utility Components** (`web-app/src/components/`):
- [ ] `Layout/Layout.tsx`
- [ ] `Auth/ProtectedRoute.tsx`
- [ ] `UI/LoadingSpinner.tsx`
- [ ] `UI/ErrorBoundary.tsx`

### 1.2 Real Authentication
**Status**: Not Started  
**Priority**: P0 - Security critical  
**Location**: `services/api-gateway/main.py`

Tasks:
- [ ] Add `password_hash` column to users table
- [ ] Implement bcrypt password hashing
- [ ] Add user lookup in `/auth/login`
- [ ] Add user creation in `/auth/register`
- [ ] Add email validation and duplicate checking

### 1.3 Database Migrations
**Status**: Not Started  
**Priority**: P1  

Tasks:
- [ ] Set up Alembic in services/
- [ ] Create migration for users table (add password_hash)
- [ ] Create migration for dissonance tracking
- [ ] Create migration for baseline tracking

---

## Phase 2: Core Innovation (Weeks 3-5)

### Dissonance Detector
**Status**: Not Started  
**Priority**: P1 - Core differentiator  
**Location**: `services/dissonance-detector/`

The core innovation - detect "I'm fine" + sad voice dissonance.

**Directory Structure to Create**:
```
services/dissonance-detector/
├── __init__.py
├── main.py                      # FastAPI endpoints
├── config.py                    # Settings
├── Dockerfile
├── requirements.txt
├── models/
│   └── dissonance_models.py    # Pydantic models
└── services/
    ├── sentiment_analyzer.py   # Text sentiment (transformers)
    └── dissonance_calculator.py # Gap calculation
```

**Key Endpoint**:
```
POST /analyze
Input: {transcript, voice_emotion}
Output: {dissonance_level, dissonance_score, interpretation, risk_level}
```

Tasks:
- [ ] Create service directory structure
- [ ] Implement FastAPI application
- [ ] Implement sentiment analyzer (transformers)
- [ ] Implement dissonance calculator
- [ ] Add API Gateway route
- [ ] Add Docker Compose configuration
- [ ] Write unit tests

---

## Phase 3: Personalization (Weeks 6-8)

### Baseline Tracker
**Status**: Not Started  
**Priority**: P2  
**Location**: `services/baseline-tracker/`
**Depends On**: Dissonance Detector

Tasks:
- [ ] Create service directory structure
- [ ] Implement personal voice fingerprint
- [ ] Implement emotional baseline calculation
- [ ] Implement deviation detection
- [ ] Implement historical pattern analysis

---

## Phase 4: Missing Microservices (Weeks 9-12)

### 4.1 Conversation Engine
**Status**: Dockerfile only  
**Location**: `services/conversation-engine/`

Tasks:
- [ ] GPT-4 integration with therapeutic prompts
- [ ] Emotion-conditioned response generation
- [ ] Conversation context management
- [ ] Cultural context injection

### 4.2 Crisis Detection
**Status**: Dockerfile only  
**Location**: `services/crisis-detection/`
**Depends On**: Dissonance Detector, Baseline Tracker

Tasks:
- [ ] Multi-layer crisis detection
- [ ] Risk scoring algorithm
- [ ] Escalation workflow
- [ ] Emergency resource coordination

### 4.3 Cultural Context Service
**Status**: Dockerfile only  
**Location**: `services/cultural-context/`

Tasks:
- [ ] Swahili deflection detection
- [ ] Code-switching recognition
- [ ] East African stoicism patterns
- [ ] RAG with vector database

### 4.4 Safety Moderation
**Status**: Dockerfile only  
**Location**: `services/safety-moderation/`

Tasks:
- [ ] Response validation
- [ ] Content filtering
- [ ] Hallucination detection
- [ ] Human review queue

### 4.5 Sync Service
**Status**: Dockerfile only  
**Location**: `services/sync-service/`

Tasks:
- [ ] Background job processing (Celery)
- [ ] Conflict resolution
- [ ] Data integrity validation
- [ ] Offline queue management

### 4.6 Emotion Analysis Service
**Status**: Code exists in src/, needs microservice wrapper  
**Location**: `services/emotion-analysis/`

Tasks:
- [ ] Wrap emotion_detector.py as microservice
- [ ] Add Hume AI integration
- [ ] Add Azure Cognitive Services integration

---

## Phase 5: Advanced Features (Weeks 13-14)

### 5.1 Micro-Moment Detector
**Status**: Not Started  
**Priority**: P4

Tasks:
- [ ] Voice tremor detection
- [ ] Sigh detection
- [ ] Voice crack detection

### 5.2 Adaptive Interface Builder
**Status**: Not Started  
**Priority**: P4
**Depends On**: All above services

Tasks:
- [ ] User pattern analysis
- [ ] Personalized UI generation

---

## Phase 6: Testing (Parallel with all phases)

**Current Coverage**: 0%  
**Target**: 80%+

### Test Categories

| Category | Status | Target |
|----------|--------|--------|
| Unit Tests | 0% | 80% |
| Integration Tests | 0% | 70% |
| E2E Tests | 0% | 60% |
| Security Tests | 0% | 90% |
| Performance Tests | 0% | Pass benchmarks |

### Files to Create
- [ ] `services/api-gateway/tests/`
- [ ] `services/dissonance-detector/tests/`
- [ ] `services/speech-processing/tests/`
- [ ] `web-app/src/__tests__/`

---

## Priority Summary

| Priority | Component | Weeks | Status |
|----------|-----------|-------|--------|
| P0 | Frontend Pages | 1-2 | Not Started |
| P0 | Real Auth | 1-2 | Not Started |
| P1 | Dissonance Detector | 3-5 | Not Started |
| P1 | Testing | Parallel | Not Started |
| P2 | Baseline Tracker | 6-8 | Not Started |
| P2 | Conversation Engine | 9-10 | Not Started |
| P2 | Crisis Detection | 10-12 | Not Started |
| P3 | Cultural Context | 9-10 | Not Started |
| P3 | Safety Moderation | 11-12 | Not Started |
| P4 | Sync Service | 12-13 | Not Started |
| P4 | Advanced Features | 13-14 | Not Started |

---

## Progress Log

| Date | Update |
|------|--------|
| Dec 12, 2025 | Plan created |

---

## Notes

- All phases can have testing run in parallel
- Phase 4 services can be developed in parallel after Phase 3
- Frontend work is independent of backend and can run in parallel

