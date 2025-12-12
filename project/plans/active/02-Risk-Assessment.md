# In Progress: Risk Assessment & Crisis Detection

## Status: 🟡 15% Complete (Infrastructure & References Only)

**Last Updated**: December 12, 2025  
**Priority**: ⭐⭐⭐⭐⭐ CRITICAL (Safety)

---

## Overview

Multi-layer risk assessment service that calculates risk from dissonance, baseline deviations, and patterns to enable crisis prevention. Currently only infrastructure references and consent management integration exist.

---

## What Exists (Infrastructure & References)

### ✅ API Gateway Route
**Location**: `services/api-gateway/main.py` lines 215-218

**Implementation**:
```python
@app.post("/crisis/detect")
async def detect_crisis(
    request: Request, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Route to crisis detection service"""
    return await route_to_service("crisis_detection", "/detect", request, credentials)
```

**Status**: ✅ Route exists and is functional  
**Service URL**: `http://crisis-detection:8000` (configured in SERVICE_URLS line 36)

**What This Means**:
- ✅ API Gateway can receive requests to `/crisis/detect`
- ✅ Request will be forwarded to `http://crisis-detection:8000/detect`
- ❌ Service at that URL doesn't exist (will return 503/connection error)

### ✅ Docker Compose Configuration
**Location**: `docker-compose.yml` lines 92-111

**Configuration**:
```yaml
crisis-detection:
  build:
    context: ./services/crisis-detection      # ❌ Directory doesn't exist
    dockerfile: Dockerfile                    # ❌ File doesn't exist
  ports:
    - "8004:8000"                             ✅ Port configured
  environment:
    - DATABASE_URL=...                        ✅ Configured
    - REDIS_URL=...                           ✅ Configured
    - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}    ✅ Configured (for alerts)
    - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}      ✅ Configured
  depends_on:
    - postgres                                ✅ Dependency configured
    - redis                                   ✅ Dependency configured
  volumes:
    - ./logs:/app/logs                        ✅ Volume configured
    - ./data/emergency-resources:/app/data/emergency-resources  ✅ Volume configured
```

**Status**: ✅ Configuration exists but service directory missing

**What This Means**:
- ✅ Docker Compose knows about the service
- ✅ Twilio credentials configured (for SMS/phone alerts)
- ✅ Emergency resources volume configured
- ❌ Service directory `./services/crisis-detection/` doesn't exist
- ❌ Dockerfile doesn't exist
- ❌ Service won't build or run

### ✅ Consent Management Integration
**Location**: `services/consent-management/main.py` lines 348-352

**Crisis Intervention Consent Type**:
```python
{
    "type": "crisis_intervention",
    "description": "Consent for crisis intervention and emergency contact",
    "required": True  ✅
}
```

**Status**: ✅ Consent type exists and is tracked

**What This Means**:
- ✅ Users can grant/revoke crisis intervention consent
- ✅ Consent is tracked in database
- ✅ Can check if user has consented to crisis intervention
- ❌ No actual crisis detection logic to use this consent

### ✅ Architecture Documentation
**Location**: `architecture/system-design.md` lines 133-147

**Documented Features**:
- ✅ Multi-layer crisis detection (keywords, sentiment, LLM)
- ✅ Risk assessment and scoring
- ✅ Escalation workflow management
- ✅ Emergency resource coordination
- ✅ Alert generation and routing

**Technology Stack Documented**:
- ✅ Python with FastAPI
- ✅ Pattern matching algorithms
- ✅ Machine learning classifiers
- ✅ PostgreSQL for crisis logs
- ✅ Real-time alerting system

---

## What's Missing (Implementation)

### ❌ Service Directory Structure
**Status**: Completely missing

**Required Structure**:
```
services/
├── crisis-detection/                    ❌ DOES NOT EXIST
│   ├── __init__.py                      ❌
│   ├── main.py                          ❌
│   ├── config.py                        ❌
│   ├── Dockerfile                       ❌
│   ├── requirements.txt                 ❌
│   ├── models/
│   │   └── crisis_models.py             ❌
│   └── services/
│       ├── risk_calculator.py           ❌
│       ├── crisis_detector.py           ❌
│       └── escalation_manager.py       ❌
│
└── risk-assessment/                     ❌ DOES NOT EXIST (separate service or combined?)
    ├── __init__.py                      ❌
    ├── main.py                          ❌
    └── services/
        ├── risk_calculator.py           ❌
        └── suicide_risk_detector.py      ❌
```

**Note**: Architecture shows both "crisis-detection" and potentially "risk-assessment" as separate services. Need to clarify if they should be combined or separate.

### ❌ Risk Calculator
**File**: `services/risk-assessment/services/risk_calculator.py`  
**Status**: Not created

**Required Functionality**:
- ❌ Multi-signal risk scoring
- ❌ Dissonance-based risk assessment
- ❌ Baseline deviation risk
- ❌ Pattern-based risk
- ❌ Micro-moment risk
- ❌ Cultural context risk
- ❌ Weighted risk factors
- ❌ Risk level classification (low, medium, medium-high, high, critical)

**Inputs Needed** (from other services):
- ❌ Dissonance data (from DissonanceDetector - doesn't exist yet)
- ❌ Baseline deviation (from BaselineTracker - doesn't exist yet)
- ❌ Patterns (from PatternAnalyzer - doesn't exist yet)
- ❌ Micro-moments (from MicroMomentDetector - doesn't exist yet)
- ❌ Cultural context (from CulturalContextService - doesn't exist yet)

**Output Required**:
```python
{
    'risk_level': 'high',  # low, medium, medium-high, high, critical
    'risk_score': 0.85,   # 0-1 scale
    'contributing_factors': [
        {
            'factor': 'high_dissonance',
            'weight': 0.4,
            'description': 'Claiming wellness but voice shows severe distress'
        },
        {
            'factor': 'baseline_deviation',
            'weight': 0.3,
            'description': 'Voice significantly different from normal'
        },
        {
            'factor': 'post_decision_calm',
            'weight': 0.9,
            'description': 'CRITICAL: Resolved tone after prolonged distress'
        }
    ],
    'crisis_indicators': [
        'post_decision_calm',
        'concealment_increasing',
        'hopelessness_language'
    ],
    'recommended_action': 'immediate_human_escalation',
    'urgency': 'critical'
}
```

### ❌ Crisis Detector
**File**: `services/crisis-detection/services/crisis_detector.py`  
**Status**: Not created

**Required Functionality**:
- ❌ Suicide risk detection
- ❌ Specific crisis pattern recognition
- ❌ Risk timeline analysis
- ❌ Confidence scoring
- ❌ Immediate action flags

**High-Risk Patterns to Detect**:
- ❌ Post-decision calm (resolved voice after prolonged distress)
- ❌ Increasing concealment (dissonance rising over time)
- ❌ Hopelessness language + flat affect
- ❌ Finality indicators ("I'm done", "what's the point")

**Timeline Analysis Required**:
```python
{
    'week_1': 'authentic_communication',
    'week_2': 'increasing_distress',
    'week_3': 'high_concealment',
    'week_4': 'post_decision_calm'  # RED FLAG
}
```

### ❌ Escalation Manager
**File**: `services/crisis-detection/services/escalation_manager.py`  
**Status**: Not created

**Required Functionality**:
- ❌ Crisis escalation protocol execution
- ❌ Real-time alert generation
- ❌ Counselor connection (<30s target)
- ❌ Emergency contact notification (if consented)
- ❌ Alert logging
- ❌ User support blocking (prevent exit without support)

**Escalation Flow Required**:
1. ❌ Alert user immediately
2. ❌ Connect to crisis counselor (<30s)
3. ❌ Notify emergency contact (if consented)
4. ❌ Log for follow-up
5. ❌ Prevent user exit without support

### ❌ Real-Time Alert System
**Status**: Not implemented

**Required**:
- ❌ WebSocket server for counselors
- ❌ Real-time alert broadcasting
- ❌ Counselor connection management
- ❌ Alert delivery tracking
- ❌ <30 second delivery target

**WebSocket Endpoint Needed**:
- ❌ `WebSocket /alerts/counselor/{counselor_id}`

### ❌ Database Schema
**Status**: Not created

**Required Tables**:

#### Risk Assessments Table
```sql
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES conversations(id),
    user_id_encrypted BYTEA,

    -- Risk scoring
    risk_level VARCHAR(20),
    risk_score FLOAT,
    contributing_factors JSONB,

    -- Crisis detection
    crisis_indicators JSONB,
    suicide_risk VARCHAR(20),

    -- Action taken
    recommended_action VARCHAR(100),
    escalated BOOLEAN DEFAULT FALSE,
    escalation_time TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Crisis Alerts Table
```sql
CREATE TABLE crisis_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_assessment_id UUID REFERENCES risk_assessments(id),
    user_id_encrypted BYTEA,

    -- Alert details
    severity VARCHAR(20),
    patterns_detected JSONB,

    -- Response tracking
    alert_sent_at TIMESTAMP,
    counselor_notified_at TIMESTAMP,
    counselor_id UUID,
    user_connected_at TIMESTAMP,

    -- Outcome
    resolution VARCHAR(100),
    resolved_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()
);
```

**Status**: ❌ Tables not created, no migration files

### ❌ Twilio Integration
**Status**: Not implemented

**Configuration Exists**:
- ✅ `TWILIO_ACCOUNT_SID` in docker-compose.yml
- ✅ `TWILIO_AUTH_TOKEN` in docker-compose.yml

**What's Missing**:
- ❌ Twilio client initialization
- ❌ SMS sending functionality
- ❌ Phone call functionality
- ❌ Emergency contact notification
- ❌ Error handling for Twilio API

---

## Integration Points

### Current Integration Status

#### ✅ API Gateway Integration
**Status**: Route exists, service missing

**Flow**:
1. ✅ Client calls `POST /crisis/detect`
2. ✅ API Gateway receives request
3. ✅ API Gateway forwards to `http://crisis-detection:8000/detect`
4. ❌ Service doesn't exist → Connection error/503

#### ✅ Consent Management Integration
**Status**: Consent type exists, logic missing

**What Exists**:
- ✅ Crisis intervention consent type
- ✅ Consent tracking
- ✅ Consent checking capability

**What's Missing**:
- ❌ Logic to check consent before escalation
- ❌ Emergency contact retrieval
- ❌ Consent-based notification logic

#### ❌ Dissonance Detector Integration
**Status**: Service doesn't exist

**Needed**:
- ❌ Get dissonance data from DissonanceDetector
- ❌ Use dissonance score in risk calculation
- ❌ Detect concealment patterns

**Blocking**: DissonanceDetector must be built first (Priority 1)

#### ❌ Baseline Tracker Integration
**Status**: Service doesn't exist

**Needed**:
- ❌ Get baseline deviation from BaselineTracker
- ❌ Use deviation in risk calculation
- ❌ Detect "different from normal" patterns

**Blocking**: BaselineTracker must be built first (Priority 2)

#### ❌ Pattern Analyzer Integration
**Status**: Service doesn't exist

**Needed**:
- ❌ Get pattern analysis
- ❌ Detect post-decision calm
- ❌ Track concealment trajectory

**Blocking**: Pattern Analyzer (part of Interface Builder or separate)

#### ❌ Micro-Moment Detector Integration
**Status**: Service doesn't exist

**Needed**:
- ❌ Get physiological signals
- ❌ Use tremor/sighs/breaks in risk calculation
- ❌ Detect involuntary stress signals

**Blocking**: MicroMomentDetector must be built (Priority 3)

#### ❌ Cultural Context Integration
**Status**: Service doesn't exist

**Needed**:
- ❌ Get cultural risk factors
- ❌ Use cultural patterns in risk assessment
- ❌ Adjust risk based on cultural context

**Blocking**: CulturalContextService must be built (Priority 4)

---

## Current Behavior

### When API Gateway Route is Called

**Scenario**: Client calls `POST /api/crisis/detect`

**What Happens**:
1. ✅ Request reaches API Gateway
2. ✅ Authentication middleware validates token
3. ✅ Route handler executes
4. ✅ HTTP client attempts to call `http://crisis-detection:8000/detect`
5. ❌ Connection fails (service doesn't exist)
6. ❌ Returns 503 Service Unavailable

**Error Response**:
```json
{
  "error": "Service crisis_detection not available",
  "status_code": 503
}
```

---

## Implementation Requirements

### Phase 1: Service Structure (Week 1)
**Estimated**: 2-3 days

**Tasks**:
1. Create `services/crisis-detection/` directory
2. Create `main.py` with FastAPI app
3. Create `config.py` with settings
4. Create `Dockerfile`
5. Create `requirements.txt`
6. Create database models
7. Create directory structure

**Deliverable**: Service skeleton that responds to health check

### Phase 2: Risk Calculator (Week 2)
**Estimated**: 4-5 days

**Tasks**:
1. Implement multi-signal risk scoring
2. Implement weighted factor calculation
3. Implement risk level classification
4. Integrate with DissonanceDetector (when available)
5. Integrate with BaselineTracker (when available)
6. Write unit tests

**Dependencies**: DissonanceDetector, BaselineTracker

**Deliverable**: Working risk calculator

### Phase 3: Crisis Detector (Week 2-3)
**Estimated**: 4-5 days

**Tasks**:
1. Implement suicide risk detection
2. Implement post-decision calm detection
3. Implement concealment trajectory tracking
4. Implement hopelessness detection
5. Implement timeline analysis
6. Write unit tests

**Dependencies**: DissonanceDetector, BaselineTracker, Pattern Analyzer

**Deliverable**: Working crisis detector

### Phase 4: Escalation Manager (Week 3)
**Estimated**: 3-4 days

**Tasks**:
1. Implement escalation protocol
2. Implement Twilio integration
3. Implement counselor connection
4. Implement emergency contact notification
5. Implement alert logging
6. Write unit tests

**Dependencies**: Twilio account, counselor dashboard

**Deliverable**: Working escalation system

### Phase 5: Real-Time Alerting (Week 3-4)
**Estimated**: 2-3 days

**Tasks**:
1. Implement WebSocket server
2. Implement counselor connection management
3. Implement alert broadcasting
4. Implement delivery tracking
5. Write integration tests

**Deliverable**: Real-time alert system

### Phase 6: Integration & Testing (Week 4)
**Estimated**: 2-3 days

**Tasks**:
1. Integrate with all required services
2. End-to-end testing
3. Clinical validation
4. Performance testing
5. Documentation

**Dependencies**: All other services complete

**Deliverable**: Fully integrated and validated system

---

## Dependencies

### External Dependencies
**Status**: Partially configured

**Required**:
- ✅ Twilio credentials (configured in docker-compose)
- ❌ Twilio Python SDK (not installed)
- ❌ WebSocket library (not installed)
- ❌ Clinical validation (needs mental health expert)

### Internal Dependencies
**Status**: Mostly missing

**Available**:
- ✅ API Gateway (for routing)
- ✅ PostgreSQL (for storage)
- ✅ Redis (for caching)
- ✅ Consent Management (for consent checking)

**Not Yet Available** (Blocking):
- ❌ Dissonance Detector (REQUIRED for dissonance-based risk)
- ❌ Baseline Tracker (REQUIRED for deviation-based risk)
- ❌ Pattern Analyzer (REQUIRED for pattern-based risk)
- ❌ Micro-Moment Detector (needed for physiological signals)
- ❌ Cultural Context Service (needed for cultural risk factors)

**Critical Path**: Must wait for DissonanceDetector and BaselineTracker

---

## Success Metrics

### Target Metrics
- ✅ Crisis detection rate: **0%** → Target: **95%+**
- ✅ False alarm rate: **N/A** → Target: **<5%**
- ✅ Alert delivery time: **N/A** → Target: **<30 seconds**
- ✅ Counselor connection time: **N/A** → Target: **<60 seconds**
- ✅ False negatives (missed crises): **N/A** → Target: **<1%** (CRITICAL)

### Current Status
- Crisis detection: **0%** (not implemented)
- Alert system: **0%** (not implemented)
- Escalation: **0%** (not implemented)
- Clinical validation: **0%** (not started)

---

## Safety Considerations

### Critical Requirements

**Must Err on Side of Caution**:
- ✅ False positives better than false negatives
- ✅ Multiple detection layers required
- ✅ Human-in-loop for high-risk cases
- ✅ Continuous monitoring required
- ✅ Clinical validation required before production

**Risk Thresholds** (Need Clinical Validation):
- ❌ Low risk threshold (not defined)
- ❌ Medium risk threshold (not defined)
- ❌ High risk threshold (not defined)
- ❌ Critical risk threshold (not defined)
- ❌ Suicide risk threshold (not defined)

**Escalation Protocols** (Need Definition):
- ❌ When to alert user
- ❌ When to contact counselor
- ❌ When to contact emergency services
- ❌ When to contact emergency contact
- ❌ Response time requirements

---

## Blockers

### Current Blockers
1. **No service implementation** - Directory doesn't exist
2. **Dependencies not available** - DissonanceDetector, BaselineTracker don't exist
3. **No clinical validation** - Risk thresholds need expert review
4. **No Twilio integration** - Alert system not implemented
5. **No database schema** - Risk tables don't exist

### Dependency Chain
```
Risk Assessment
  ├─ Requires: DissonanceDetector (Priority 1) ⚠️ BLOCKING
  ├─ Requires: BaselineTracker (Priority 2) ⚠️ BLOCKING
  ├─ Requires: Pattern Analyzer ⚠️ BLOCKING
  ├─ Requires: MicroMomentDetector (Priority 3)
  └─ Requires: CulturalContextService (Priority 4)
```

**Cannot Start**: Until DissonanceDetector and BaselineTracker are complete

---

## Estimated Completion

**Total Effort**: 2-3 weeks  
**Team**: 1 backend engineer + clinical advisor (ongoing)  
**Lines of Code**: ~800-1,200 lines  
**Complexity**: High (safety-critical, real-time alerts, clinical validation required)

**Timeline**: Weeks 15-16 (after DissonanceDetector and BaselineTracker)

---

## Next Immediate Steps

1. **Wait for Dependencies** (Priority: Wait)
   - DissonanceDetector must be built first
   - BaselineTracker must be built second
   - Then can start Risk Assessment

2. **Clinical Consultation** (Priority: Start Now)
   - Recruit mental health clinical advisor
   - Define risk thresholds
   - Define escalation protocols
   - Validate detection patterns

3. **Service Structure** (Priority: After Dependencies)
   - Create service directory
   - Set up FastAPI app
   - Create database models
   - Create Dockerfile

---

## References

- **Design Spec**: `DESIGN_CRITIQUE_AND_IMPROVEMENTS.md` - Gap 6
- **Architecture**: `architecture/system-design.md` lines 133-147
- **Progress Report**: `PROGRESS_REPORT.md` - Gap 6
- **Missing Components**: `MISSING_COMPONENTS_REPORT.md` - Component 6
