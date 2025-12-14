-- Migration 009: Moderation Tables
-- Creates tables for human review queue and moderation logging

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. MODERATION QUEUE TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS moderation_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('response', 'user_input')),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    validation_result JSONB NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_review', 'approved', 'rejected', 'resolved')),
    reviewer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    decision TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    reviewed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_moderation_queue_status ON moderation_queue(status);
CREATE INDEX idx_moderation_queue_priority ON moderation_queue(priority);
CREATE INDEX idx_moderation_queue_created_at ON moderation_queue(created_at);
CREATE INDEX idx_moderation_queue_user_id ON moderation_queue(user_id) WHERE user_id IS NOT NULL;

-- ============================================================================
-- 2. MODERATION LOGS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS moderation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    content_type VARCHAR(20) NOT NULL CHECK (content_type IN ('response', 'user_input')),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    validation_result JSONB NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('allow', 'block', 'review')),
    reviewer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_moderation_logs_action ON moderation_logs(action);
CREATE INDEX idx_moderation_logs_created_at ON moderation_logs(created_at);
CREATE INDEX idx_moderation_logs_user_id ON moderation_logs(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX idx_moderation_logs_reviewer_id ON moderation_logs(reviewer_id) WHERE reviewer_id IS NOT NULL;

-- ============================================================================
-- 3. MODERATION METRICS VIEW (for analytics)
-- ============================================================================

CREATE OR REPLACE VIEW moderation_metrics AS
SELECT
    DATE(created_at) as date,
    action,
    content_type,
    COUNT(*) as count,
    AVG((validation_result->>'risk_score')::float) as avg_risk_score,
    AVG((validation_result->>'hallucination_score')::float) as avg_hallucination_score
FROM moderation_logs
GROUP BY DATE(created_at), action, content_type;

COMMENT ON TABLE moderation_queue IS 'Queue for human review of flagged content';
COMMENT ON TABLE moderation_logs IS 'Log of all moderation decisions for analytics';
COMMENT ON VIEW moderation_metrics IS 'Aggregated moderation metrics for dashboard';

