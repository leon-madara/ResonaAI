# Database Schema for Pattern Storage

**Privacy-Preserving, Scalable, Optimized for Adaptive Interface Generation**

---

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core Tables](#core-tables)
3. [Privacy Architecture](#privacy-architecture)
4. [Indexes & Performance](#indexes--performance)
5. [Migrations](#migrations)
6. [Queries](#queries)

---

## Schema Overview

### Design Principles

1. **Privacy-First**:
   - Raw audio NEVER stored
   - Transcripts encrypted or deleted
   - Patterns anonymized
   - User IDs hashed

2. **Pattern-Optimized**:
   - Denormalized for fast pattern retrieval
   - Optimized for overnight builder queries
   - Minimal joins for interface generation

3. **Temporal**:
   - All data timestamped
   - Historical tracking for baselines
   - Pattern evolution over time

4. **Scalable**:
   - Partitioned by date
   - Archived old sessions
   - Efficient indexes

---

## Core Tables

### 1. users

Core user table (minimal PII)

```sql
CREATE TABLE users (
    -- Primary key
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Anonymous identifier (for external references)
    anonymous_id VARCHAR(64) UNIQUE NOT NULL,

    -- Account info (encrypted)
    email_hash VARCHAR(256),  -- Hashed, not plaintext
    phone_hash VARCHAR(256),  -- Hashed, not plaintext

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    account_status VARCHAR(20) DEFAULT 'active',

    -- Privacy settings
    data_retention_days INT DEFAULT 90,
    consent_research BOOLEAN DEFAULT FALSE,
    consent_emergency_contact BOOLEAN DEFAULT FALSE,

    -- Timezone for overnight builds
    timezone VARCHAR(50) DEFAULT 'Africa/Nairobi',

    CONSTRAINT valid_status CHECK (account_status IN ('active', 'suspended', 'deleted'))
);

CREATE INDEX idx_users_anonymous ON users(anonymous_id);
CREATE INDEX idx_users_last_active ON users(last_active);
```

---

### 2. voice_sessions

Individual voice sessions (temporary, deleted after processing)

```sql
CREATE TABLE voice_sessions (
    -- Primary key
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Timestamp
    session_start TIMESTAMP NOT NULL DEFAULT NOW(),
    session_end TIMESTAMP,
    duration_seconds INT,

    -- Voice analysis results (from existing emotion detector)
    voice_emotion VARCHAR(50),
    emotion_confidence FLOAT,
    voice_features JSONB,  -- Prosodic, spectral, temporal features

    -- Transcription (encrypted, deleted after pattern extraction)
    transcript_encrypted TEXT,  -- AES-256 encrypted
    transcript_language VARCHAR(10),

    -- Processing status
    processed BOOLEAN DEFAULT FALSE,
    patterns_extracted BOOLEAN DEFAULT FALSE,

    -- Cleanup (sessions auto-deleted after pattern extraction)
    delete_after TIMESTAMP DEFAULT NOW() + INTERVAL '7 days',

    CONSTRAINT valid_emotion CHECK (
        voice_emotion IN ('neutral', 'happy', 'sad', 'angry', 'fear',
                          'surprise', 'disgust', 'hopeless', 'resigned', 'numb')
    )
);

CREATE INDEX idx_sessions_user ON voice_sessions(user_id, session_start DESC);
CREATE INDEX idx_sessions_delete ON voice_sessions(delete_after) WHERE NOT processed;
CREATE INDEX idx_sessions_processing ON voice_sessions(processed, patterns_extracted);

-- Auto-delete processed sessions after 7 days
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM voice_sessions
    WHERE delete_after < NOW()
      AND patterns_extracted = TRUE;
END;
$$ LANGUAGE plpgsql;
```

---

### 3. user_patterns

**Core table**: Anonymized patterns for interface generation

```sql
CREATE TABLE user_patterns (
    -- Primary key
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Version tracking (patterns evolve over time)
    version INT NOT NULL DEFAULT 1,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sessions_analyzed INT NOT NULL,
    data_confidence FLOAT NOT NULL,  -- 0-1

    -- === EMOTIONAL PATTERNS ===
    primary_emotions VARCHAR(50)[],  -- Array of primary emotions
    emotion_distribution JSONB,      -- {emotion: percentage}
    temporal_patterns JSONB,         -- {time_of_day: typical_emotion}
    trajectory VARCHAR(20),           -- improving/declining/stable
    trajectory_confidence FLOAT,
    variability_score FLOAT,
    recent_shift VARCHAR(200),

    -- === CULTURAL CONTEXT ===
    primary_language VARCHAR(20),
    code_switching BOOLEAN,
    code_switching_pattern TEXT,
    deflection_phrases VARCHAR(50)[],
    deflection_frequency FLOAT,
    stoicism_level VARCHAR(20),
    cultural_stressors VARCHAR(50)[],
    communication_style VARCHAR(50),

    -- === TRIGGERS ===
    triggers JSONB,  -- [{topic, severity, frequency, voice_markers}]
    trigger_count INT,
    most_severe_trigger VARCHAR(50),
    trigger_combinations JSONB,

    -- === COPING ===
    effective_strategies JSONB,  -- [{name, effectiveness, evidence}]
    ineffective_strategies JSONB,
    untried_suggestions VARCHAR(50)[],
    coping_consistency FLOAT,
    primary_coping_style VARCHAR(50),

    -- === CURRENT STATE (from latest session) ===
    current_dissonance JSONB,  -- Latest dissonance result
    current_risk_level VARCHAR(20),
    current_risk_score FLOAT,
    current_risk_factors TEXT[],

    -- === MENTAL HEALTH PROFILE ===
    primary_concerns VARCHAR(50)[],
    current_state VARCHAR(20),
    support_needs VARCHAR(50)[],
    identified_strengths TEXT[],
    identified_challenges TEXT[],

    -- Metadata
    is_current BOOLEAN DEFAULT TRUE,  -- Only one current version per user

    CONSTRAINT valid_trajectory CHECK (
        trajectory IN ('improving', 'declining', 'stable', 'volatile', 'insufficient_data')
    ),
    CONSTRAINT valid_risk CHECK (
        current_risk_level IN ('low', 'medium', 'high', 'critical')
    ),
    CONSTRAINT valid_state CHECK (
        current_state IN ('crisis', 'struggling', 'managing', 'stable', 'improving')
    )
);

-- Unique constraint: only one current pattern per user
CREATE UNIQUE INDEX idx_patterns_current ON user_patterns(user_id)
WHERE is_current = TRUE;

-- Indexes for pattern retrieval
CREATE INDEX idx_patterns_user_version ON user_patterns(user_id, version DESC);
CREATE INDEX idx_patterns_generated ON user_patterns(generated_at DESC);
CREATE INDEX idx_patterns_risk ON user_patterns(current_risk_level)
WHERE current_risk_level IN ('high', 'critical');

-- Index for overnight builder (fetch current patterns)
CREATE INDEX idx_patterns_overnight_build ON user_patterns(user_id, is_current)
WHERE is_current = TRUE;
```

---

### 4. voice_baselines

User's personal voice baseline (their "normal")

```sql
CREATE TABLE voice_baselines (
    -- Primary key
    baseline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,

    -- Version tracking
    version INT NOT NULL DEFAULT 1,
    established_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sessions_analyzed INT NOT NULL,
    baseline_established BOOLEAN DEFAULT FALSE,

    -- === PROSODIC BASELINE ===
    typical_pitch_mean FLOAT,
    typical_pitch_std FLOAT,
    typical_pitch_range FLOAT,

    -- === ENERGY BASELINE ===
    typical_energy_mean FLOAT,
    typical_energy_std FLOAT,

    -- === TEMPORAL BASELINE ===
    typical_speech_rate FLOAT,
    typical_pause_ratio FLOAT,

    -- === EMOTIONAL BASELINE ===
    typical_prosody_variance FLOAT,
    typical_emotion_distribution JSONB,

    -- === PERSONAL STRESS MARKERS ===
    stress_markers JSONB,  -- {faster_when_anxious: true, quieter_when_sad: true}

    -- Metadata
    is_current BOOLEAN DEFAULT TRUE,

    CONSTRAINT baseline_sessions CHECK (sessions_analyzed >= 0)
);

-- Only one current baseline per user
CREATE UNIQUE INDEX idx_baselines_current ON voice_baselines(user_id)
WHERE is_current = TRUE;

CREATE INDEX idx_baselines_user_version ON voice_baselines(user_id, version DESC);
CREATE INDEX idx_baselines_established ON voice_baselines(baseline_established);
```

---

### 5. interface_configs

Generated UI configurations (output of overnight builder)

```sql
CREATE TABLE interface_configs (
    -- Primary key
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_id UUID NOT NULL REFERENCES user_patterns(pattern_id),

    -- Version tracking
    version VARCHAR(20) NOT NULL,  -- e.g., "2.4"
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- === UI CONFIGURATION (encrypted for privacy) ===
    ui_config_encrypted TEXT NOT NULL,  -- JSON config, AES-256 encrypted

    -- === METADATA (unencrypted for queries) ===
    theme VARCHAR(50),  -- 'anxiety', 'depression', 'crisis', 'stable'
    primary_components VARCHAR(50)[],  -- Components shown
    hidden_components VARCHAR(50)[],   -- Components hidden
    crisis_prominence VARCHAR(20),     -- 'hidden', 'sidebar', 'top', 'modal'

    -- Deployment status
    deployed BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP,

    -- User feedback
    user_rating INT,  -- 1-5, did they like this interface?
    user_feedback TEXT,

    -- Metadata
    is_current BOOLEAN DEFAULT TRUE,

    CONSTRAINT valid_theme CHECK (
        theme IN ('anxiety', 'depression', 'crisis', 'stable', 'balanced')
    ),
    CONSTRAINT valid_prominence CHECK (
        crisis_prominence IN ('hidden', 'sidebar', 'card', 'top', 'modal')
    )
);

-- Only one current config per user
CREATE UNIQUE INDEX idx_configs_current ON interface_configs(user_id)
WHERE is_current = TRUE;

CREATE INDEX idx_configs_user_version ON interface_configs(user_id, generated_at DESC);
CREATE INDEX idx_configs_pattern ON interface_configs(pattern_id);
CREATE INDEX idx_configs_deployed ON interface_configs(deployed, deployed_at);
```

---

### 6. interface_changes

Change log (transparency: what changed and why)

```sql
CREATE TABLE interface_changes (
    -- Primary key
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    config_id UUID NOT NULL REFERENCES interface_configs(config_id),

    -- Change details
    change_type VARCHAR(50) NOT NULL,  -- e.g., 'risk_escalation', 'feature_hidden'
    component_affected VARCHAR(100),
    reason TEXT NOT NULL,  -- Why this change was made

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    shown_to_user BOOLEAN DEFAULT FALSE,

    -- User feedback
    user_acknowledged BOOLEAN DEFAULT FALSE,
    user_rating INT,  -- Did they like this change?
    user_feedback TEXT,

    CONSTRAINT valid_change_type CHECK (
        change_type IN (
            'risk_escalation', 'risk_de_escalation',
            'feature_added', 'feature_hidden',
            'theme_changed', 'language_adapted',
            'cultural_adjustment', 'baseline_established',
            'trigger_detected', 'coping_identified'
        )
    )
);

CREATE INDEX idx_changes_user ON interface_changes(user_id, created_at DESC);
CREATE INDEX idx_changes_config ON interface_changes(config_id);
CREATE INDEX idx_changes_unshown ON interface_changes(shown_to_user)
WHERE shown_to_user = FALSE;
```

---

### 7. risk_alerts

Crisis alerts for counselors

```sql
CREATE TABLE risk_alerts (
    -- Primary key
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_id UUID REFERENCES user_patterns(pattern_id),

    -- Alert details
    risk_level VARCHAR(20) NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_factors TEXT[] NOT NULL,
    risk_interpretation TEXT NOT NULL,

    -- Alert status
    created_at TIMESTAMP DEFAULT NOW(),
    alert_sent BOOLEAN DEFAULT FALSE,
    alert_sent_at TIMESTAMP,

    -- Counselor response
    counselor_id UUID,  -- References counselors table (not shown here)
    counselor_notified BOOLEAN DEFAULT FALSE,
    counselor_responded BOOLEAN DEFAULT FALSE,
    counselor_response TEXT,
    counselor_response_at TIMESTAMP,

    -- Resolution
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,

    CONSTRAINT valid_risk CHECK (
        risk_level IN ('high', 'critical')  -- Only high/critical generate alerts
    ),
    CONSTRAINT risk_score_range CHECK (risk_score >= 0 AND risk_score <= 1)
);

CREATE INDEX idx_alerts_user ON risk_alerts(user_id, created_at DESC);
CREATE INDEX idx_alerts_unresolved ON risk_alerts(resolved, created_at)
WHERE NOT resolved;
CREATE INDEX idx_alerts_critical ON risk_alerts(risk_level, created_at)
WHERE risk_level = 'critical';
CREATE INDEX idx_alerts_counselor ON risk_alerts(counselor_id, counselor_responded)
WHERE counselor_id IS NOT NULL;
```

---

### 8. pattern_history

Historical patterns (for tracking evolution)

```sql
CREATE TABLE pattern_history (
    -- Primary key
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_id UUID NOT NULL REFERENCES user_patterns(pattern_id),

    -- Snapshot metadata
    snapshot_at TIMESTAMP NOT NULL DEFAULT NOW(),
    version INT NOT NULL,

    -- Key metrics (for charting evolution)
    emotional_trajectory VARCHAR(20),
    risk_level VARCHAR(20),
    risk_score FLOAT,
    dissonance_score FLOAT,
    coping_consistency FLOAT,
    baseline_deviation FLOAT,

    -- Compressed full pattern (for detailed analysis)
    full_pattern_compressed JSONB  -- Compressed JSONB for storage efficiency
);

-- Partition by month for performance
CREATE INDEX idx_history_user_time ON pattern_history(user_id, snapshot_at DESC);
CREATE INDEX idx_history_risk ON pattern_history(risk_level, snapshot_at)
WHERE risk_level IN ('high', 'critical');

-- Query for evolution tracking
CREATE INDEX idx_history_trajectory ON pattern_history(user_id, snapshot_at, emotional_trajectory);
```

---

## Privacy Architecture

### Data Lifecycle

```
1. Voice Session Created
   ├─ Audio: NEVER stored (processed in-memory only)
   ├─ Transcript: Encrypted immediately (AES-256)
   └─ Features: Extracted and stored

2. Pattern Analysis (within 24 hours)
   ├─ Patterns extracted from sessions
   ├─ Patterns anonymized
   └─ Original session deleted

3. Interface Generation (overnight)
   ├─ Patterns read (anonymized)
   ├─ UI config generated
   └─ Config encrypted before storage

4. Data Retention
   ├─ Patterns: Kept for user-specified period (default 90 days)
   ├─ Baselines: Kept until user deletes account
   └─ Configs: Kept for 30 days
```

### Encryption Strategy

```sql
-- Encryption keys table (separate, access-controlled)
CREATE TABLE encryption_keys (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    public_key TEXT NOT NULL,
    private_key_encrypted TEXT NOT NULL,  -- User's password-derived key
    salt VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    rotated_at TIMESTAMP
);

-- Only the user can decrypt their own data
-- Server never has access to unencrypted transcripts/configs
```

### Anonymization Rules

```sql
-- Anonymized patterns (what's stored)
✅ Emotion distribution: {sad: 0.6, neutral: 0.4}
✅ Trigger topics: ["family", "work"]
✅ Coping effectiveness: [{"name": "breathing", "score": 0.8}]
✅ Risk level: "medium"

❌ Raw transcripts: DELETED or ENCRYPTED
❌ Audio files: NEVER STORED
❌ Identifiable voice prints: NOT STORED
❌ Specific personal details: NOT STORED
```

---

## Indexes & Performance

### Query Patterns

```sql
-- 1. Overnight Builder: Fetch all users needing rebuild
CREATE INDEX idx_overnight_rebuild ON user_patterns(user_id, is_current)
WHERE is_current = TRUE;

-- 2. Risk Monitoring: Find high-risk users
CREATE INDEX idx_risk_monitoring ON user_patterns(current_risk_level, generated_at DESC)
WHERE current_risk_level IN ('high', 'critical');

-- 3. User Login: Fetch current config
CREATE INDEX idx_user_login ON interface_configs(user_id, is_current)
WHERE is_current = TRUE AND deployed = TRUE;

-- 4. Pattern Evolution: Track changes over time
CREATE INDEX idx_pattern_evolution ON pattern_history(user_id, snapshot_at DESC);

-- 5. Cleanup: Delete old sessions
CREATE INDEX idx_cleanup_sessions ON voice_sessions(delete_after)
WHERE patterns_extracted = TRUE;
```

### Partitioning Strategy

```sql
-- Partition voice_sessions by month (auto-cleanup old data)
CREATE TABLE voice_sessions_2025_01 PARTITION OF voice_sessions
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE voice_sessions_2025_02 PARTITION OF voice_sessions
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- ... etc.

-- Partition pattern_history by quarter
CREATE TABLE pattern_history_2025_q1 PARTITION OF pattern_history
FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

-- ... etc.
```

---

## Sample Queries

### Query 1: Get Current Patterns for User

```sql
-- Fetch patterns for interface generation
SELECT
    p.user_id,
    p.primary_emotions,
    p.emotion_distribution,
    p.temporal_patterns,
    p.trajectory,
    p.primary_language,
    p.code_switching,
    p.stoicism_level,
    p.triggers,
    p.effective_strategies,
    p.current_risk_level,
    p.current_risk_score,
    p.primary_concerns,
    p.current_state,
    p.support_needs,
    b.typical_pitch_mean,
    b.typical_energy_mean,
    b.stress_markers,
    b.baseline_established
FROM user_patterns p
LEFT JOIN voice_baselines b ON p.user_id = b.user_id AND b.is_current = TRUE
WHERE p.user_id = :user_id
  AND p.is_current = TRUE;
```

### Query 2: Overnight Builder - All Users Needing Rebuild

```sql
-- Get all users with activity in last 24 hours
SELECT DISTINCT
    u.user_id,
    u.anonymous_id,
    u.timezone,
    p.pattern_id,
    p.sessions_analyzed,
    COUNT(s.session_id) as new_sessions
FROM users u
INNER JOIN user_patterns p ON u.user_id = p.user_id AND p.is_current = TRUE
LEFT JOIN voice_sessions s ON u.user_id = s.user_id
    AND s.session_start > NOW() - INTERVAL '24 hours'
    AND s.processed = TRUE
WHERE u.account_status = 'active'
  AND u.last_active > NOW() - INTERVAL '24 hours'
GROUP BY u.user_id, u.anonymous_id, u.timezone, p.pattern_id, p.sessions_analyzed
HAVING COUNT(s.session_id) > 0;  -- Only users with new activity
```

### Query 3: Risk Monitoring - High Risk Users

```sql
-- Find users needing immediate attention
SELECT
    u.anonymous_id,
    p.current_risk_level,
    p.current_risk_score,
    p.current_risk_factors,
    p.current_dissonance->>'risk_interpretation' as interpretation,
    p.generated_at,
    a.alert_sent,
    a.counselor_responded
FROM user_patterns p
INNER JOIN users u ON p.user_id = u.user_id
LEFT JOIN risk_alerts a ON p.user_id = a.user_id AND NOT a.resolved
WHERE p.is_current = TRUE
  AND p.current_risk_level IN ('high', 'critical')
  AND u.account_status = 'active'
ORDER BY p.current_risk_score DESC, p.generated_at DESC;
```

### Query 4: Pattern Evolution - Track User's Journey

```sql
-- Visualize user's emotional trajectory over time
SELECT
    snapshot_at,
    emotional_trajectory,
    risk_level,
    risk_score,
    dissonance_score,
    coping_consistency
FROM pattern_history
WHERE user_id = :user_id
  AND snapshot_at > NOW() - INTERVAL '90 days'
ORDER BY snapshot_at ASC;
```

### Query 5: Interface Change Log for Transparency

```sql
-- Show user what changed and why
SELECT
    change_type,
    component_affected,
    reason,
    created_at
FROM interface_changes
WHERE user_id = :user_id
  AND shown_to_user = FALSE
ORDER BY created_at DESC
LIMIT 10;
```

---

## Next Steps

1. **Create Migration Files** - SQL scripts to create all tables
2. **Build ORM Models** - SQLAlchemy models for Python
3. **Implement Storage Service** - Pattern storage/retrieval
4. **Add Privacy Layer** - Encryption/anonymization
5. **Create Queries** - Optimized queries for overnight builder

Ready to proceed with migrations and ORM models?
