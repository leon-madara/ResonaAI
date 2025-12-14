-- Mental Health Platform Database Initialization
-- Based on system design architecture

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. User Data Management
-- ============================================

-- Users table with privacy controls
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(20),
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    consent_version VARCHAR(10),
    data_retention_until TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT true
);

-- Encrypted user profiles
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    encrypted_data BYTEA NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users table
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL;
CREATE INDEX idx_users_last_active ON users(last_active);
CREATE INDEX idx_users_data_retention ON users(data_retention_until) WHERE data_retention_until IS NOT NULL;

-- ============================================
-- 2. Conversation Management
-- ============================================

-- Conversation sessions
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    emotion_summary JSONB,
    crisis_detected BOOLEAN DEFAULT false,
    escalated_to_human BOOLEAN DEFAULT false
);

-- Encrypted conversation messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('user', 'ai')),
    encrypted_content BYTEA NOT NULL,
    emotion_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for conversations
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_started_at ON conversations(started_at);
CREATE INDEX idx_conversations_crisis ON conversations(crisis_detected) WHERE crisis_detected = true;
CREATE INDEX idx_conversations_emotion_summary ON conversations USING GIN (emotion_summary);

-- Indexes for messages
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_type ON messages(message_type);
CREATE INDEX idx_messages_emotion_data ON messages USING GIN (emotion_data);

-- ============================================
-- 3. Offline Sync Management
-- ============================================

-- Sync queue for offline operations
CREATE TABLE sync_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    operation_type VARCHAR(50) NOT NULL,
    encrypted_data BYTEA NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0
);

-- Indexes for sync queue
CREATE INDEX idx_sync_queue_user_id ON sync_queue(user_id);
CREATE INDEX idx_sync_queue_status ON sync_queue(status);
CREATE INDEX idx_sync_queue_created_at ON sync_queue(created_at);
CREATE INDEX idx_sync_queue_pending ON sync_queue(status, created_at) WHERE status = 'pending';

-- User preferences (offline-first UI/UX settings; stored as JSON for MVP)
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    preferences JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_preferences_updated_at ON user_preferences(updated_at);

-- ============================================
-- 4. Crisis Management
-- ============================================

-- Crisis detection logs
CREATE TABLE crisis_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    detection_method VARCHAR(50) NOT NULL,
    escalation_required BOOLEAN DEFAULT false,
    human_reviewed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for crisis events
CREATE INDEX idx_crisis_events_user_id ON crisis_events(user_id);
CREATE INDEX idx_crisis_events_conversation_id ON crisis_events(conversation_id);
CREATE INDEX idx_crisis_events_risk_level ON crisis_events(risk_level);
CREATE INDEX idx_crisis_events_escalation ON crisis_events(escalation_required) WHERE escalation_required = true;
CREATE INDEX idx_crisis_events_created_at ON crisis_events(created_at);
CREATE INDEX idx_crisis_events_unreviewed ON crisis_events(human_reviewed, created_at) WHERE human_reviewed = false;

-- ============================================
-- 5. Additional Tables for Service Functionality
-- ============================================

-- Emotion analysis history
CREATE TABLE emotion_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    emotion_type VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5, 4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    voice_emotion JSONB,
    text_sentiment JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_emotion_history_user_id ON emotion_history(user_id);
CREATE INDEX idx_emotion_history_conversation_id ON emotion_history(conversation_id);
CREATE INDEX idx_emotion_history_created_at ON emotion_history(created_at);

-- Cultural context cache
CREATE TABLE cultural_context_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context_key VARCHAR(255) NOT NULL UNIQUE,
    context_data JSONB NOT NULL,
    language VARCHAR(10),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

CREATE INDEX idx_cultural_context_key ON cultural_context_cache(context_key);
CREATE INDEX idx_cultural_context_language ON cultural_context_cache(language);
CREATE INDEX idx_cultural_context_expires ON cultural_context_cache(expires_at) WHERE expires_at IS NOT NULL;

-- Safety moderation logs
CREATE TABLE moderation_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    moderation_type VARCHAR(50) NOT NULL,
    action_taken VARCHAR(50) NOT NULL,
    flagged_content TEXT,
    confidence_score DECIMAL(5, 4),
    human_reviewed BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_moderation_logs_message_id ON moderation_logs(message_id);
CREATE INDEX idx_moderation_logs_unreviewed ON moderation_logs(human_reviewed) WHERE human_reviewed = false;
CREATE INDEX idx_moderation_logs_created_at ON moderation_logs(created_at);

-- ============================================
-- 6. Functions and Triggers
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for user_profiles
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger for cultural_context_cache
CREATE TRIGGER update_cultural_context_cache_updated_at BEFORE UPDATE ON cultural_context_cache
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to clean up expired cultural context cache
CREATE OR REPLACE FUNCTION cleanup_expired_cultural_context()
RETURNS void AS $$
BEGIN
    DELETE FROM cultural_context_cache WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ language 'plpgsql';

-- ============================================
-- 7. Initial Data (Optional)
-- ============================================

-- Grant permissions (adjust as needed for your setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

