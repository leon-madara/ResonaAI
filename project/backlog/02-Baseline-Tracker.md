# Baseline Tracker - To Do

**Status**: ✅ COMPLETE (~90-100%)  
**Priority**: ⭐⭐⭐⭐ HIGH  
**Last Updated**: December 2024

## Overview

Build personal voice fingerprints for each user and detect deviations from their normal patterns. This enables detection of "different from THEIR normal" rather than just general patterns.

## What's Missing

```
services/baseline-tracker/        ❌ DOES NOT EXIST
└── (Should build personal voice fingerprints, detect deviations)

Database tables:
- user_baselines                  ❌ NOT CREATED
- session_deviations              ❌ NOT CREATED
```

## Impact

**Without This Service**:
- ❌ Can't detect "different from THEIR normal"
- ❌ Can't catch gradual decline
- ❌ No personal context for interpretation
- ❌ Missing personalized risk assessment

## Required Implementation

### Service Structure
```
services/baseline-tracker/
├── main.py                    # FastAPI service
├── config.py                  # Configuration
├── models/
│   └── baseline_models.py     # Data models
└── services/
    ├── baseline_builder.py    # Build user baselines
    └── deviation_detector.py  # Detect deviations
```

### Database Schema

```sql
CREATE TABLE user_baselines (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    baseline_type VARCHAR(50), -- 'emotion', 'pitch', 'energy', etc.
    baseline_value JSONB,
    session_count INTEGER,
    established_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, baseline_type)
);

CREATE TABLE session_deviations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    deviation_type VARCHAR(50),
    baseline_value JSONB,
    current_value JSONB,
    deviation_score FLOAT,
    detected_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Core Functionality

1. **Baseline Building**
   - Track user voice patterns over 3-5 sessions
   - Calculate average emotion distribution
   - Establish pitch, energy, rate baselines
   - Store baseline in database

2. **Deviation Detection**
   - Compare current session to user's baseline
   - Calculate deviation scores
   - Identify significant changes
   - Flag gradual decline patterns

3. **Personal Context**
   - Provide personal context for interpretation
   - Enable personalized risk assessment
   - Support adaptive interface generation

## Implementation Plan

### Phase 1: Database Setup (Week 4)
- [ ] Create database schema
- [ ] Set up migration scripts
- [ ] Create data models
- [ ] Test database operations

### Phase 2: Baseline Building (Week 4-5)
- [ ] Implement baseline calculation
- [ ] Track user sessions
- [ ] Store baselines in database
- [ ] Test with sample user data

### Phase 3: Deviation Detection (Week 5)
- [ ] Implement deviation calculation
- [ ] Compare current to baseline
- [ ] Calculate deviation scores
- [ ] Test deviation detection

### Phase 4: Integration (Week 5)
- [ ] Integrate with Dissonance Detector
- [ ] Connect to emotion detector
- [ ] End-to-end testing
- [ ] Documentation

## Timeline

**Estimated**: Weeks 4-5 (after Dissonance Detector)

## Dependencies

- Dissonance Detector (Gap 1) - Should be completed first
- Emotion Detector ✅ EXISTS
- Audio Processor ✅ EXISTS
- Database (PostgreSQL) ✅ EXISTS

## Success Criteria

- ✅ Baselines established after 3-5 sessions
- ✅ Deviation detection functional
- ✅ Personal context provided
- ✅ Integrated with other services
- ✅ Database schema created
- ✅ Unit tests passing

## Example Use Case

**User Baseline** (after 5 sessions):
```json
{
  "emotion_distribution": {
    "neutral": 0.60,
    "happy": 0.25,
    "sad": 0.10,
    "angry": 0.05
  },
  "average_pitch": 180.5,
  "average_energy": 0.65,
  "average_rate": 4.2
}
```

**Current Session**:
- Emotion: sad (0.85 confidence)
- Pitch: 150.0 (lower than baseline)
- Energy: 0.45 (lower than baseline)

**Deviation Detected**:
```json
{
  "deviation_score": 0.75,
  "significant_changes": [
    "emotion_shift_to_sad",
    "pitch_decrease",
    "energy_decrease"
  ],
  "interpretation": "significant_deviation_from_baseline",
  "risk": "medium"
}
```

## References

- See [DESIGN_CRITIQUE_AND_IMPROVEMENTS.md](../DESIGN_CRITIQUE_AND_IMPROVEMENTS.md) - Gap 2
- See [PROGRESS_REPORT.md](../PROGRESS_REPORT.md) - Gap 2

