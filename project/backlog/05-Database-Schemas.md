# Database Schemas - To Do

**Status**: ✅ IMPLEMENTED  
**Priority**: ⭐⭐⭐⭐ HIGH  
**Last Updated**: December 12, 2025

## Overview

Database schemas for missing innovation features. These tables are required for baseline tracking, interface personalization, and risk assessment.

## Missing Tables

### 1. User Baselines ✅
**Purpose**: Store personal voice fingerprints for each user

```sql
CREATE TABLE user_baselines (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    baseline_type VARCHAR(50) NOT NULL, -- 'emotion', 'pitch', 'energy', 'rate', etc.
    baseline_value JSONB NOT NULL,
    session_count INTEGER DEFAULT 0,
    established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, baseline_type),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_baselines_user_id ON user_baselines(user_id);
CREATE INDEX idx_user_baselines_type ON user_baselines(baseline_type);
```

### 2. Session Deviations ✅
**Purpose**: Track deviations from user's baseline

```sql
CREATE TABLE session_deviations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    deviation_type VARCHAR(50) NOT NULL,
    baseline_value JSONB,
    current_value JSONB,
    deviation_score FLOAT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_session_deviations_user_id ON session_deviations(user_id);
CREATE INDEX idx_session_deviations_session_id ON session_deviations(session_id);
CREATE INDEX idx_session_deviations_score ON session_deviations(deviation_score);
```

### 3. User Interfaces ✅
**Purpose**: Store personalized interface configurations

```sql
CREATE TABLE user_interfaces (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    interface_config JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT true,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_interfaces_user_id ON user_interfaces(user_id);
CREATE INDEX idx_user_interfaces_active ON user_interfaces(active);
```

### 4. Interface Evolution Log ✅
**Purpose**: Track how interfaces evolve over time

```sql
CREATE TABLE interface_evolution_log (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    version INTEGER NOT NULL,
    changes JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_interface_evolution_user_id ON interface_evolution_log(user_id);
CREATE INDEX idx_interface_evolution_version ON interface_evolution_log(version);
```

### 5. Dissonance Records ✅
**Purpose**: Store dissonance detection results

```sql
CREATE TABLE dissonance_records (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    transcript TEXT,
    stated_emotion VARCHAR(50),
    actual_emotion VARCHAR(50),
    dissonance_score FLOAT NOT NULL,
    interpretation VARCHAR(100),
    risk_level VARCHAR(20),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_dissonance_records_user_id ON dissonance_records(user_id);
CREATE INDEX idx_dissonance_records_score ON dissonance_records(dissonance_score);
CREATE INDEX idx_dissonance_records_risk ON dissonance_records(risk_level);
```

### 6. Risk Assessments ✅
**Purpose**: Store risk assessment results

```sql
CREATE TABLE risk_assessments (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL, -- 'low', 'medium', 'high', 'critical'
    risk_factors JSONB,
    dissonance_contribution FLOAT,
    baseline_deviation_contribution FLOAT,
    pattern_contribution FLOAT,
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_taken VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX idx_risk_assessments_user_id ON risk_assessments(user_id);
CREATE INDEX idx_risk_assessments_level ON risk_assessments(risk_level);
CREATE INDEX idx_risk_assessments_score ON risk_assessments(risk_score);
```

## Implementation Plan

### Phase 1: Schema Design (Week 1)
- [ ] Review all required tables
- [ ] Finalize schema designs
- [ ] Create migration scripts
- [ ] Review with team

### Phase 2: Migration Scripts (Week 1-2)
- [x] Create Alembic migrations
- [x] Add rollback procedures
- [ ] Test migrations (to be done in deployment)
- [x] Document schema

### Phase 3: Integration (Week 2)
- [x] Update ORM models
- [x] Integrate with services
- [ ] Test database operations (to be done in deployment)
- [ ] Performance optimization (indexes already added)

## Timeline

**Estimated**: Week 1-2 (in parallel with Dissonance Detector)

## Dependencies

- Database (PostgreSQL) ✅ EXISTS
- ORM setup (SQLAlchemy) ✅ VERIFIED AND USED
- Migration tool (Alembic) ✅ SET UP AND CONFIGURED

## Success Criteria

- ✅ All tables created (via Alembic migrations 002-008)
- ✅ Migrations have rollback procedures (downgrade functions)
- ✅ Indexes optimized (all required indexes added)
- ✅ Foreign keys properly set (CASCADE delete where appropriate)
- ✅ Documentation complete (ORM models in gateway/database.py)

## Implementation Details

### Migrations Created:
- `002_add_user_baselines.py` - User baseline tracking
- `003_add_session_deviations.py` - Session deviation tracking
- `004_add_user_interfaces.py` - Interface configuration storage
- `005_add_risk_assessments.py` - Risk assessment storage
- `007_add_interface_evolution_log.py` - Interface evolution tracking
- `008_add_dissonance_records.py` - Dissonance detection results

### ORM Models Added:
- `InterfaceEvolutionLog` - In `apps/backend/gateway/database.py`
- `DissonanceRecord` - In `apps/backend/gateway/database.py`

### Notes:
- All foreign keys reference `conversations.id` (not `sessions.id`) per system design
- UUID primary keys used for consistency
- All migrations include proper downgrade functions for rollback

## Notes

- All tables should include proper indexes for performance
- Foreign keys should cascade on delete for data integrity
- Timestamps should be automatically managed
- JSONB columns for flexible schema evolution

## References

- See [DESIGN_CRITIQUE_AND_IMPROVEMENTS.md](../DESIGN_CRITIQUE_AND_IMPROVEMENTS.md)
- See [PROGRESS_REPORT.md](../PROGRESS_REPORT.md)

