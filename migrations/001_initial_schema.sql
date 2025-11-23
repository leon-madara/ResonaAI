-- Migration 001: Initial Schema for Pattern Storage
-- Privacy-preserving, optimized for adaptive interface generation

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. USERS TABLE
-- ============================================================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    anonymous_id VARCHAR(64) UNIQUE NOT NULL,
    email_hash VARCHAR(256),
    phone_hash VARCHAR(256),
    created_at TIMESTAMP DEFAULT NOW(),
    last_active TIMESTAMP DEFAULT NOW(),
    account_status VARCHAR(20) DEFAULT 'active',
    data_retention_days INT DEFAULT 90,
    consent_research BOOLEAN DEFAULT FALSE,
    consent_emergency_contact BOOLEAN DEFAULT FALSE,
    timezone VARCHAR(50) DEFAULT 'Africa/Nairobi',

    CONSTRAINT valid_status CHECK (account_status IN ('active', 'suspended', 'deleted'))
);

CREATE INDEX idx_users_anonymous ON users(anonymous_id);
CREATE INDEX idx_users_last_active ON users(last_active);
CREATE INDEX idx_users_status ON users(account_status) WHERE account_status = 'active';

-- ============================================================================
-- 2. VOICE SESSIONS TABLE (temporary, auto-deleted)
-- ============================================================================

CREATE TABLE voice_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_start TIMESTAMP NOT NULL DEFAULT NOW(),
    session_end TIMESTAMP,
    duration_seconds INT,
    voice_emotion VARCHAR(50),
    emotion_confidence FLOAT,
    voice_features JSONB,
    transcript_encrypted TEXT,
    transcript_language VARCHAR(10),
    processed BOOLEAN DEFAULT FALSE,
    patterns_extracted BOOLEAN DEFAULT FALSE,
    delete_after TIMESTAMP DEFAULT NOW() + INTERVAL '7 days',

    CONSTRAINT valid_emotion CHECK (
        voice_emotion IN ('neutral', 'happy', 'sad', 'angry', 'fear',
                          'surprise', 'disgust', 'hopeless', 'resigned', 'numb')
    ),
    CONSTRAINT valid_confidence CHECK (emotion_confidence >= 0 AND emotion_confidence <= 1)
);

CREATE INDEX idx_sessions_user ON voice_sessions(user_id, session_start DESC);
CREATE INDEX idx_sessions_delete ON voice_sessions(delete_after) WHERE NOT processed;
CREATE INDEX idx_sessions_processing ON voice_sessions(processed, patterns_extracted);
CREATE INDEX idx_sessions_unprocessed ON voice_sessions(user_id, processed) WHERE NOT processed;

-- Auto-cleanup function
CREATE OR REPLACE FUNCTION cleanup_old_sessions()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM voice_sessions
    WHERE delete_after < NOW()
      AND patterns_extracted = TRUE;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Schedule cleanup (run daily)
COMMENT ON FUNCTION cleanup_old_sessions() IS 'Auto-delete processed sessions after retention period';

-- ============================================================================
-- 3. USER PATTERNS TABLE (core anonymized patterns)
-- ============================================================================

CREATE TABLE user_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    version INT NOT NULL DEFAULT 1,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sessions_analyzed INT NOT NULL,
    data_confidence FLOAT NOT NULL,

    -- Emotional patterns
    primary_emotions VARCHAR(50)[],
    emotion_distribution JSONB,
    temporal_patterns JSONB,
    trajectory VARCHAR(20),
    trajectory_confidence FLOAT,
    variability_score FLOAT,
    recent_shift VARCHAR(200),

    -- Cultural context
    primary_language VARCHAR(20),
    code_switching BOOLEAN,
    code_switching_pattern TEXT,
    deflection_phrases VARCHAR(50)[],
    deflection_frequency FLOAT,
    stoicism_level VARCHAR(20),
    cultural_stressors VARCHAR(50)[],
    communication_style VARCHAR(50),

    -- Triggers
    triggers JSONB,
    trigger_count INT,
    most_severe_trigger VARCHAR(50),
    trigger_combinations JSONB,

    -- Coping
    effective_strategies JSONB,
    ineffective_strategies JSONB,
    untried_suggestions VARCHAR(50)[],
    coping_consistency FLOAT,
    primary_coping_style VARCHAR(50),

    -- Current state
    current_dissonance JSONB,
    current_risk_level VARCHAR(20),
    current_risk_score FLOAT,
    current_risk_factors TEXT[],

    -- Mental health profile
    primary_concerns VARCHAR(50)[],
    current_state VARCHAR(20),
    support_needs VARCHAR(50)[],
    identified_strengths TEXT[],
    identified_challenges TEXT[],

    -- Metadata
    is_current BOOLEAN DEFAULT TRUE,

    CONSTRAINT valid_trajectory CHECK (
        trajectory IN ('improving', 'declining', 'stable', 'volatile', 'insufficient_data')
    ),
    CONSTRAINT valid_risk CHECK (
        current_risk_level IN ('low', 'medium', 'high', 'critical')
    ),
    CONSTRAINT valid_state CHECK (
        current_state IN ('crisis', 'struggling', 'managing', 'stable', 'improving')
    ),
    CONSTRAINT valid_confidence CHECK (data_confidence >= 0 AND data_confidence <= 1)
);

-- Unique constraint: only one current pattern per user
CREATE UNIQUE INDEX idx_patterns_current ON user_patterns(user_id) WHERE is_current = TRUE;

CREATE INDEX idx_patterns_user_version ON user_patterns(user_id, version DESC);
CREATE INDEX idx_patterns_generated ON user_patterns(generated_at DESC);
CREATE INDEX idx_patterns_risk ON user_patterns(current_risk_level) WHERE current_risk_level IN ('high', 'critical');
CREATE INDEX idx_patterns_overnight_build ON user_patterns(user_id, is_current) WHERE is_current = TRUE;

-- ============================================================================
-- 4. VOICE BASELINES TABLE
-- ============================================================================

CREATE TABLE voice_baselines (
    baseline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    version INT NOT NULL DEFAULT 1,
    established_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sessions_analyzed INT NOT NULL,
    baseline_established BOOLEAN DEFAULT FALSE,

    -- Prosodic baseline
    typical_pitch_mean FLOAT,
    typical_pitch_std FLOAT,
    typical_pitch_range FLOAT,

    -- Energy baseline
    typical_energy_mean FLOAT,
    typical_energy_std FLOAT,

    -- Temporal baseline
    typical_speech_rate FLOAT,
    typical_pause_ratio FLOAT,

    -- Emotional baseline
    typical_prosody_variance FLOAT,
    typical_emotion_distribution JSONB,

    -- Personal stress markers
    stress_markers JSONB,

    -- Metadata
    is_current BOOLEAN DEFAULT TRUE,

    CONSTRAINT baseline_sessions CHECK (sessions_analyzed >= 0)
);

-- Only one current baseline per user
CREATE UNIQUE INDEX idx_baselines_current ON voice_baselines(user_id) WHERE is_current = TRUE;

CREATE INDEX idx_baselines_user_version ON voice_baselines(user_id, version DESC);
CREATE INDEX idx_baselines_established ON voice_baselines(baseline_established);

-- ============================================================================
-- 5. INTERFACE CONFIGS TABLE
-- ============================================================================

CREATE TABLE interface_configs (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_id UUID NOT NULL REFERENCES user_patterns(pattern_id),
    version VARCHAR(20) NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- UI configuration (encrypted)
    ui_config_encrypted TEXT NOT NULL,

    -- Metadata (unencrypted for queries)
    theme VARCHAR(50),
    primary_components VARCHAR(50)[],
    hidden_components VARCHAR(50)[],
    crisis_prominence VARCHAR(20),

    -- Deployment
    deployed BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP,

    -- User feedback
    user_rating INT,
    user_feedback TEXT,

    -- Metadata
    is_current BOOLEAN DEFAULT TRUE,

    CONSTRAINT valid_theme CHECK (
        theme IN ('anxiety', 'depression', 'crisis', 'stable', 'balanced')
    ),
    CONSTRAINT valid_prominence CHECK (
        crisis_prominence IN ('hidden', 'sidebar', 'card', 'top', 'modal')
    ),
    CONSTRAINT valid_rating CHECK (user_rating >= 1 AND user_rating <= 5)
);

-- Only one current config per user
CREATE UNIQUE INDEX idx_configs_current ON interface_configs(user_id) WHERE is_current = TRUE;

CREATE INDEX idx_configs_user_version ON interface_configs(user_id, generated_at DESC);
CREATE INDEX idx_configs_pattern ON interface_configs(pattern_id);
CREATE INDEX idx_configs_deployed ON interface_configs(deployed, deployed_at);

-- ============================================================================
-- 6. INTERFACE CHANGES TABLE
-- ============================================================================

CREATE TABLE interface_changes (
    change_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    config_id UUID NOT NULL REFERENCES interface_configs(config_id),
    change_type VARCHAR(50) NOT NULL,
    component_affected VARCHAR(100),
    reason TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    shown_to_user BOOLEAN DEFAULT FALSE,
    user_acknowledged BOOLEAN DEFAULT FALSE,
    user_rating INT,
    user_feedback TEXT,

    CONSTRAINT valid_change_type CHECK (
        change_type IN (
            'risk_escalation', 'risk_de_escalation',
            'feature_added', 'feature_hidden',
            'theme_changed', 'language_adapted',
            'cultural_adjustment', 'baseline_established',
            'trigger_detected', 'coping_identified'
        )
    ),
    CONSTRAINT valid_rating CHECK (user_rating >= 1 AND user_rating <= 5)
);

CREATE INDEX idx_changes_user ON interface_changes(user_id, created_at DESC);
CREATE INDEX idx_changes_config ON interface_changes(config_id);
CREATE INDEX idx_changes_unshown ON interface_changes(shown_to_user) WHERE shown_to_user = FALSE;

-- ============================================================================
-- 7. RISK ALERTS TABLE
-- ============================================================================

CREATE TABLE risk_alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_id UUID REFERENCES user_patterns(pattern_id),
    risk_level VARCHAR(20) NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_factors TEXT[] NOT NULL,
    risk_interpretation TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    alert_sent BOOLEAN DEFAULT FALSE,
    alert_sent_at TIMESTAMP,
    counselor_id UUID,
    counselor_notified BOOLEAN DEFAULT FALSE,
    counselor_responded BOOLEAN DEFAULT FALSE,
    counselor_response TEXT,
    counselor_response_at TIMESTAMP,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,

    CONSTRAINT valid_risk CHECK (risk_level IN ('high', 'critical')),
    CONSTRAINT risk_score_range CHECK (risk_score >= 0 AND risk_score <= 1)
);

CREATE INDEX idx_alerts_user ON risk_alerts(user_id, created_at DESC);
CREATE INDEX idx_alerts_unresolved ON risk_alerts(resolved, created_at) WHERE NOT resolved;
CREATE INDEX idx_alerts_critical ON risk_alerts(risk_level, created_at) WHERE risk_level = 'critical';
CREATE INDEX idx_alerts_counselor ON risk_alerts(counselor_id, counselor_responded) WHERE counselor_id IS NOT NULL;

-- ============================================================================
-- 8. PATTERN HISTORY TABLE (for evolution tracking)
-- ============================================================================

CREATE TABLE pattern_history (
    history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    pattern_id UUID NOT NULL REFERENCES user_patterns(pattern_id),
    snapshot_at TIMESTAMP NOT NULL DEFAULT NOW(),
    version INT NOT NULL,

    -- Key metrics for charting
    emotional_trajectory VARCHAR(20),
    risk_level VARCHAR(20),
    risk_score FLOAT,
    dissonance_score FLOAT,
    coping_consistency FLOAT,
    baseline_deviation FLOAT,

    -- Compressed full pattern
    full_pattern_compressed JSONB
);

CREATE INDEX idx_history_user_time ON pattern_history(user_id, snapshot_at DESC);
CREATE INDEX idx_history_risk ON pattern_history(risk_level, snapshot_at) WHERE risk_level IN ('high', 'critical');
CREATE INDEX idx_history_trajectory ON pattern_history(user_id, snapshot_at, emotional_trajectory);

-- ============================================================================
-- 9. ENCRYPTION KEYS TABLE (separate, access-controlled)
-- ============================================================================

CREATE TABLE encryption_keys (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    public_key TEXT NOT NULL,
    private_key_encrypted TEXT NOT NULL,
    salt VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    rotated_at TIMESTAMP
);

-- No indexes on encryption_keys (sensitive data, minimal queries)

-- ============================================================================
-- TRIGGERS & FUNCTIONS
-- ============================================================================

-- Trigger: Archive old pattern when new one becomes current
CREATE OR REPLACE FUNCTION archive_old_pattern()
RETURNS TRIGGER AS $$
BEGIN
    -- Mark previous current pattern as not current
    UPDATE user_patterns
    SET is_current = FALSE
    WHERE user_id = NEW.user_id
      AND pattern_id != NEW.pattern_id
      AND is_current = TRUE;

    -- Create history snapshot
    INSERT INTO pattern_history (
        user_id, pattern_id, version,
        emotional_trajectory, risk_level, risk_score,
        dissonance_score, coping_consistency,
        full_pattern_compressed
    )
    SELECT
        NEW.user_id,
        NEW.pattern_id,
        NEW.version,
        NEW.trajectory,
        NEW.current_risk_level,
        NEW.current_risk_score,
        (NEW.current_dissonance->>'dissonance_score')::FLOAT,
        NEW.coping_consistency,
        to_jsonb(NEW)
    WHERE NEW.is_current = TRUE;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_pattern_on_new
    AFTER INSERT ON user_patterns
    FOR EACH ROW
    EXECUTE FUNCTION archive_old_pattern();

-- Trigger: Archive old baseline when new one becomes current
CREATE OR REPLACE FUNCTION archive_old_baseline()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE voice_baselines
    SET is_current = FALSE
    WHERE user_id = NEW.user_id
      AND baseline_id != NEW.baseline_id
      AND is_current = TRUE;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_baseline_on_new
    AFTER INSERT ON voice_baselines
    FOR EACH ROW
    EXECUTE FUNCTION archive_old_baseline();

-- Trigger: Archive old config when new one becomes current
CREATE OR REPLACE FUNCTION archive_old_config()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE interface_configs
    SET is_current = FALSE
    WHERE user_id = NEW.user_id
      AND config_id != NEW.config_id
      AND is_current = TRUE;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER archive_config_on_new
    AFTER INSERT ON interface_configs
    FOR EACH ROW
    EXECUTE FUNCTION archive_old_config();

-- Trigger: Create risk alert when high risk detected
CREATE OR REPLACE FUNCTION create_risk_alert()
RETURNS TRIGGER AS $$
BEGIN
    -- Only create alert for high/critical risk
    IF NEW.current_risk_level IN ('high', 'critical') AND NEW.is_current = TRUE THEN
        INSERT INTO risk_alerts (
            user_id,
            pattern_id,
            risk_level,
            risk_score,
            risk_factors,
            risk_interpretation
        )
        VALUES (
            NEW.user_id,
            NEW.pattern_id,
            NEW.current_risk_level,
            NEW.current_risk_score,
            NEW.current_risk_factors,
            NEW.current_dissonance->>'risk_interpretation'
        );
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER create_alert_on_high_risk
    AFTER INSERT ON user_patterns
    FOR EACH ROW
    EXECUTE FUNCTION create_risk_alert();

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function: Get current patterns for user
CREATE OR REPLACE FUNCTION get_user_current_patterns(p_user_id UUID)
RETURNS TABLE (
    patterns JSONB,
    baseline JSONB,
    config JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        to_jsonb(p.*) as patterns,
        to_jsonb(b.*) as baseline,
        to_jsonb(c.*) as config
    FROM user_patterns p
    LEFT JOIN voice_baselines b ON p.user_id = b.user_id AND b.is_current = TRUE
    LEFT JOIN interface_configs c ON p.user_id = c.user_id AND c.is_current = TRUE
    WHERE p.user_id = p_user_id
      AND p.is_current = TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- COMMENTS (documentation)
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts with minimal PII, privacy-first design';
COMMENT ON TABLE voice_sessions IS 'Temporary storage for sessions, auto-deleted after pattern extraction';
COMMENT ON TABLE user_patterns IS 'Core anonymized patterns for interface generation';
COMMENT ON TABLE voice_baselines IS 'Personal voice baselines for deviation detection';
COMMENT ON TABLE interface_configs IS 'Generated UI configurations, encrypted for privacy';
COMMENT ON TABLE interface_changes IS 'Change log for transparency (what changed and why)';
COMMENT ON TABLE risk_alerts IS 'Crisis alerts for counselor intervention';
COMMENT ON TABLE pattern_history IS 'Historical patterns for evolution tracking';
COMMENT ON TABLE encryption_keys IS 'User encryption keys for E2E encryption';

-- ============================================================================
-- GRANT PERMISSIONS (adjust as needed)
-- ============================================================================

-- Create application role
CREATE ROLE resona_app;

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO resona_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO resona_app;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO resona_app;

-- Restrict access to encryption_keys (only specific functions should access)
REVOKE ALL ON encryption_keys FROM resona_app;
GRANT SELECT ON encryption_keys TO resona_app;  -- Read-only for app

-- Migration complete
COMMENT ON SCHEMA public IS 'ResonaAI Pattern Storage Schema v1.0';
