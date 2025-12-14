-- Migration 002: Complete Schema for All Required Tables
-- Ensures all tables from init.sql and additional required tables exist
-- This migration is idempotent - safe to run multiple times

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. USERS TABLE (enhance if exists, create if not)
-- ============================================================================

-- Check if users table exists with old schema (id) or new schema (user_id)
DO $$
BEGIN
    -- If table doesn't exist, create it
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            email VARCHAR(255) UNIQUE,
            phone VARCHAR(20),
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            consent_version VARCHAR(10),
            data_retention_until TIMESTAMP,
            is_anonymous BOOLEAN DEFAULT true,
            -- Additional fields for pattern storage schema compatibility
            anonymous_id VARCHAR(64) UNIQUE,
            email_hash VARCHAR(256),
            phone_hash VARCHAR(256),
            account_status VARCHAR(20) DEFAULT 'active',
            data_retention_days INT DEFAULT 90,
            consent_research BOOLEAN DEFAULT FALSE,
            consent_emergency_contact BOOLEAN DEFAULT FALSE,
            timezone VARCHAR(50) DEFAULT 'Africa/Nairobi',
            CONSTRAINT valid_status CHECK (account_status IN ('active', 'suspended', 'deleted'))
        );
    ELSE
        -- Add missing columns if they don't exist
        ALTER TABLE users ADD COLUMN IF NOT EXISTS anonymous_id VARCHAR(64) UNIQUE;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS email_hash VARCHAR(256);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_hash VARCHAR(256);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS account_status VARCHAR(20) DEFAULT 'active';
        ALTER TABLE users ADD COLUMN IF NOT EXISTS data_retention_days INT DEFAULT 90;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS consent_research BOOLEAN DEFAULT FALSE;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS consent_emergency_contact BOOLEAN DEFAULT FALSE;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Africa/Nairobi';
        
        -- Add constraint if it doesn't exist
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.table_constraints 
                WHERE constraint_name = 'valid_status' AND table_name = 'users'
            ) THEN
                ALTER TABLE users ADD CONSTRAINT valid_status 
                    CHECK (account_status IN ('active', 'suspended', 'deleted'));
            END IF;
        END $$;
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone) WHERE phone IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active);
CREATE INDEX IF NOT EXISTS idx_users_data_retention ON users(data_retention_until) WHERE data_retention_until IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_anonymous ON users(anonymous_id) WHERE anonymous_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_users_status ON users(account_status) WHERE account_status = 'active';

-- ============================================================================
-- 2. USER PROFILES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_profiles (
    user_id UUID PRIMARY KEY,
    encrypted_data BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_profiles_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE
);

-- Add trigger for updated_at
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 3. CONVERSATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    emotion_summary JSONB,
    crisis_detected BOOLEAN DEFAULT false,
    escalated_to_human BOOLEAN DEFAULT false,
    CONSTRAINT fk_conversations_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_started_at ON conversations(started_at);
CREATE INDEX IF NOT EXISTS idx_conversations_crisis ON conversations(crisis_detected) WHERE crisis_detected = true;
CREATE INDEX IF NOT EXISTS idx_conversations_emotion_summary ON conversations USING GIN (emotion_summary);

-- ============================================================================
-- 4. MESSAGES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'ai')),
    encrypted_content BYTEA NOT NULL,
    emotion_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_messages_conversation FOREIGN KEY (conversation_id) 
        REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_type ON messages(message_type);
CREATE INDEX IF NOT EXISTS idx_messages_emotion_data ON messages USING GIN (emotion_data);

-- ============================================================================
-- 5. SYNC QUEUE TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS sync_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    encrypted_data BYTEA NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    CONSTRAINT fk_sync_queue_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sync_queue_user_id ON sync_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);
CREATE INDEX IF NOT EXISTS idx_sync_queue_created_at ON sync_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_sync_queue_pending ON sync_queue(status, created_at) WHERE status = 'pending';

-- ============================================================================
-- 5b. USER PREFERENCES TABLE (offline-first UI settings)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID PRIMARY KEY,
    preferences JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_updated_at ON user_preferences(updated_at);

-- Add trigger for updated_at
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 6. CRISIS EVENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS crisis_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    conversation_id UUID,
    risk_level VARCHAR(20) NOT NULL 
        CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    detection_method VARCHAR(50) NOT NULL,
    escalation_required BOOLEAN DEFAULT false,
    human_reviewed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_crisis_events_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_crisis_events_conversation FOREIGN KEY (conversation_id) 
        REFERENCES conversations(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_crisis_events_user_id ON crisis_events(user_id);
CREATE INDEX IF NOT EXISTS idx_crisis_events_conversation_id ON crisis_events(conversation_id);
CREATE INDEX IF NOT EXISTS idx_crisis_events_risk_level ON crisis_events(risk_level);
CREATE INDEX IF NOT EXISTS idx_crisis_events_escalation ON crisis_events(escalation_required) WHERE escalation_required = true;
CREATE INDEX IF NOT EXISTS idx_crisis_events_created_at ON crisis_events(created_at);
CREATE INDEX IF NOT EXISTS idx_crisis_events_unreviewed ON crisis_events(human_reviewed, created_at) WHERE human_reviewed = false;

-- ============================================================================
-- 7. USER BASELINES TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_baselines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    baseline_type VARCHAR(50) NOT NULL,
    baseline_value JSONB NOT NULL,
    session_count INTEGER DEFAULT 0,
    established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_baselines_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT uq_user_baselines_user_type UNIQUE (user_id, baseline_type)
);

CREATE INDEX IF NOT EXISTS idx_user_baselines_user_id ON user_baselines(user_id);
CREATE INDEX IF NOT EXISTS idx_user_baselines_type ON user_baselines(baseline_type);

-- Add trigger for updated_at
DROP TRIGGER IF EXISTS update_user_baselines_updated_at ON user_baselines;
CREATE TRIGGER update_user_baselines_updated_at 
    BEFORE UPDATE ON user_baselines
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 8. SESSION DEVIATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS session_deviations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_id UUID NOT NULL,
    deviation_type VARCHAR(50) NOT NULL,
    baseline_value JSONB,
    current_value JSONB,
    deviation_score FLOAT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_session_deviations_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_session_deviations_conversation FOREIGN KEY (session_id) 
        REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_session_deviations_user_id ON session_deviations(user_id);
CREATE INDEX IF NOT EXISTS idx_session_deviations_session_id ON session_deviations(session_id);
CREATE INDEX IF NOT EXISTS idx_session_deviations_score ON session_deviations(deviation_score);

-- ============================================================================
-- 9. EMOTION HISTORY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS emotion_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    conversation_id UUID,
    message_id UUID,
    emotion_type VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5, 4) NOT NULL 
        CHECK (confidence_score >= 0 AND confidence_score <= 1),
    voice_emotion JSONB,
    text_sentiment JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_emotion_history_user FOREIGN KEY (user_id) 
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_emotion_history_conversation FOREIGN KEY (conversation_id) 
        REFERENCES conversations(id) ON DELETE SET NULL,
    CONSTRAINT fk_emotion_history_message FOREIGN KEY (message_id) 
        REFERENCES messages(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_emotion_history_user_id ON emotion_history(user_id);
CREATE INDEX IF NOT EXISTS idx_emotion_history_conversation_id ON emotion_history(conversation_id);
CREATE INDEX IF NOT EXISTS idx_emotion_history_created_at ON emotion_history(created_at);

-- ============================================================================
-- 10. CULTURAL CONTEXT CACHE TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS cultural_context_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context_key VARCHAR(255) NOT NULL UNIQUE,
    context_data JSONB NOT NULL,
    language VARCHAR(10),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cultural_context_key ON cultural_context_cache(context_key);
CREATE INDEX IF NOT EXISTS idx_cultural_context_language ON cultural_context_cache(language);
CREATE INDEX IF NOT EXISTS idx_cultural_context_expires ON cultural_context_cache(expires_at) WHERE expires_at IS NOT NULL;

-- Add trigger for updated_at
DROP TRIGGER IF EXISTS update_cultural_context_cache_updated_at ON cultural_context_cache;
CREATE TRIGGER update_cultural_context_cache_updated_at 
    BEFORE UPDATE ON cultural_context_cache
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- 11. MODERATION LOGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS moderation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID,
    moderation_type VARCHAR(50) NOT NULL,
    action_taken VARCHAR(50) NOT NULL,
    flagged_content TEXT,
    confidence_score DECIMAL(5, 4),
    human_reviewed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_moderation_logs_message FOREIGN KEY (message_id) 
        REFERENCES messages(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_moderation_logs_message_id ON moderation_logs(message_id);
CREATE INDEX IF NOT EXISTS idx_moderation_logs_unreviewed ON moderation_logs(human_reviewed) WHERE human_reviewed = false;
CREATE INDEX IF NOT EXISTS idx_moderation_logs_created_at ON moderation_logs(created_at);

-- ============================================================================
-- 12. HELPER FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to clean up expired cultural context cache
CREATE OR REPLACE FUNCTION cleanup_expired_cultural_context()
RETURNS void AS $$
BEGIN
    DELETE FROM cultural_context_cache WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ language 'plpgsql';

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE users IS 'User accounts with privacy controls and authentication';
COMMENT ON TABLE user_profiles IS 'Encrypted user profile data';
COMMENT ON TABLE conversations IS 'Conversation sessions between users and AI';
COMMENT ON TABLE messages IS 'Encrypted conversation messages';
COMMENT ON TABLE sync_queue IS 'Queue for offline sync operations';
COMMENT ON TABLE crisis_events IS 'Crisis detection and escalation logs';
COMMENT ON TABLE user_baselines IS 'Personal voice fingerprints and baseline patterns for each user';
COMMENT ON TABLE session_deviations IS 'Deviations from user baselines detected in sessions';
COMMENT ON TABLE emotion_history IS 'Historical emotion analysis data';
COMMENT ON TABLE cultural_context_cache IS 'Cached cultural context responses';
COMMENT ON TABLE moderation_logs IS 'Safety moderation and content filtering logs';

-- Migration complete
COMMENT ON SCHEMA public IS 'ResonaAI Complete Database Schema v2.0';

