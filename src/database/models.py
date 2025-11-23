"""
SQLAlchemy ORM Models for Pattern Storage

Maps to the PostgreSQL schema defined in migrations/001_initial_schema.sql
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, TIMESTAMP,
    Text, ForeignKey, CheckConstraint, UniqueConstraint, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# ============================================================================
# USER MODEL
# ============================================================================

class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    anonymous_id = Column(String(64), unique=True, nullable=False)
    email_hash = Column(String(256))
    phone_hash = Column(String(256))
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_active = Column(TIMESTAMP, server_default=func.now())
    account_status = Column(String(20), default='active')
    data_retention_days = Column(Integer, default=90)
    consent_research = Column(Boolean, default=False)
    consent_emergency_contact = Column(Boolean, default=False)
    timezone = Column(String(50), default='Africa/Nairobi')

    # Relationships
    voice_sessions = relationship('VoiceSession', back_populates='user', cascade='all, delete-orphan')
    patterns = relationship('UserPattern', back_populates='user', cascade='all, delete-orphan')
    baselines = relationship('VoiceBaseline', back_populates='user', cascade='all, delete-orphan')
    configs = relationship('InterfaceConfig', back_populates='user', cascade='all, delete-orphan')
    changes = relationship('InterfaceChange', back_populates='user', cascade='all, delete-orphan')
    alerts = relationship('RiskAlert', back_populates='user', cascade='all, delete-orphan')
    pattern_history = relationship('PatternHistory', back_populates='user', cascade='all, delete-orphan')

    __table_args__ = (
        CheckConstraint("account_status IN ('active', 'suspended', 'deleted')"),
    )

    def __repr__(self):
        return f"<User(anonymous_id='{self.anonymous_id}', status='{self.account_status}')>"

# ============================================================================
# VOICE SESSION MODEL
# ============================================================================

class VoiceSession(Base):
    __tablename__ = 'voice_sessions'

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    session_start = Column(TIMESTAMP, nullable=False, server_default=func.now())
    session_end = Column(TIMESTAMP)
    duration_seconds = Column(Integer)
    voice_emotion = Column(String(50))
    emotion_confidence = Column(Float)
    voice_features = Column(JSONB)
    transcript_encrypted = Column(Text)
    transcript_language = Column(String(10))
    processed = Column(Boolean, default=False)
    patterns_extracted = Column(Boolean, default=False)
    delete_after = Column(TIMESTAMP, server_default=func.now() + func.make_interval(0, 0, 0, 7))

    # Relationships
    user = relationship('User', back_populates='voice_sessions')

    __table_args__ = (
        CheckConstraint(
            "voice_emotion IN ('neutral', 'happy', 'sad', 'angry', 'fear', 'surprise', "
            "'disgust', 'hopeless', 'resigned', 'numb')"
        ),
        CheckConstraint("emotion_confidence >= 0 AND emotion_confidence <= 1"),
    )

    def __repr__(self):
        return f"<VoiceSession(session_id='{self.session_id}', emotion='{self.voice_emotion}')>"

# ============================================================================
# USER PATTERN MODEL
# ============================================================================

class UserPattern(Base):
    __tablename__ = 'user_patterns'

    pattern_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    generated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    sessions_analyzed = Column(Integer, nullable=False)
    data_confidence = Column(Float, nullable=False)

    # Emotional patterns
    primary_emotions = Column(ARRAY(String(50)))
    emotion_distribution = Column(JSONB)
    temporal_patterns = Column(JSONB)
    trajectory = Column(String(20))
    trajectory_confidence = Column(Float)
    variability_score = Column(Float)
    recent_shift = Column(String(200))

    # Cultural context
    primary_language = Column(String(20))
    code_switching = Column(Boolean)
    code_switching_pattern = Column(Text)
    deflection_phrases = Column(ARRAY(String(50)))
    deflection_frequency = Column(Float)
    stoicism_level = Column(String(20))
    cultural_stressors = Column(ARRAY(String(50)))
    communication_style = Column(String(50))

    # Triggers
    triggers = Column(JSONB)
    trigger_count = Column(Integer)
    most_severe_trigger = Column(String(50))
    trigger_combinations = Column(JSONB)

    # Coping
    effective_strategies = Column(JSONB)
    ineffective_strategies = Column(JSONB)
    untried_suggestions = Column(ARRAY(String(50)))
    coping_consistency = Column(Float)
    primary_coping_style = Column(String(50))

    # Current state
    current_dissonance = Column(JSONB)
    current_risk_level = Column(String(20))
    current_risk_score = Column(Float)
    current_risk_factors = Column(ARRAY(Text))

    # Mental health profile
    primary_concerns = Column(ARRAY(String(50)))
    current_state = Column(String(20))
    support_needs = Column(ARRAY(String(50)))
    identified_strengths = Column(ARRAY(Text))
    identified_challenges = Column(ARRAY(Text))

    # Metadata
    is_current = Column(Boolean, default=True)

    # Relationships
    user = relationship('User', back_populates='patterns')
    configs = relationship('InterfaceConfig', back_populates='pattern')
    alerts = relationship('RiskAlert', back_populates='pattern')
    history = relationship('PatternHistory', back_populates='pattern')

    __table_args__ = (
        CheckConstraint(
            "trajectory IN ('improving', 'declining', 'stable', 'volatile', 'insufficient_data')"
        ),
        CheckConstraint("current_risk_level IN ('low', 'medium', 'high', 'critical')"),
        CheckConstraint(
            "current_state IN ('crisis', 'struggling', 'managing', 'stable', 'improving')"
        ),
        CheckConstraint("data_confidence >= 0 AND data_confidence <= 1"),
        UniqueConstraint('user_id', name='uq_user_current_pattern', postgresql_where=(is_current == True)),
    )

    def __repr__(self):
        return f"<UserPattern(user_id='{self.user_id}', version={self.version}, risk='{self.current_risk_level}')>"

# ============================================================================
# VOICE BASELINE MODEL
# ============================================================================

class VoiceBaseline(Base):
    __tablename__ = 'voice_baselines'

    baseline_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    established_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    sessions_analyzed = Column(Integer, nullable=False)
    baseline_established = Column(Boolean, default=False)

    # Prosodic baseline
    typical_pitch_mean = Column(Float)
    typical_pitch_std = Column(Float)
    typical_pitch_range = Column(Float)

    # Energy baseline
    typical_energy_mean = Column(Float)
    typical_energy_std = Column(Float)

    # Temporal baseline
    typical_speech_rate = Column(Float)
    typical_pause_ratio = Column(Float)

    # Emotional baseline
    typical_prosody_variance = Column(Float)
    typical_emotion_distribution = Column(JSONB)

    # Personal stress markers
    stress_markers = Column(JSONB)

    # Metadata
    is_current = Column(Boolean, default=True)

    # Relationships
    user = relationship('User', back_populates='baselines')

    __table_args__ = (
        CheckConstraint("sessions_analyzed >= 0"),
        UniqueConstraint('user_id', name='uq_user_current_baseline', postgresql_where=(is_current == True)),
    )

    def __repr__(self):
        return f"<VoiceBaseline(user_id='{self.user_id}', version={self.version}, established={self.baseline_established})>"

# ============================================================================
# INTERFACE CONFIG MODEL
# ============================================================================

class InterfaceConfig(Base):
    __tablename__ = 'interface_configs'

    config_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    pattern_id = Column(UUID(as_uuid=True), ForeignKey('user_patterns.pattern_id'), nullable=False)
    version = Column(String(20), nullable=False)
    generated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # UI configuration (encrypted)
    ui_config_encrypted = Column(Text, nullable=False)

    # Metadata
    theme = Column(String(50))
    primary_components = Column(ARRAY(String(50)))
    hidden_components = Column(ARRAY(String(50)))
    crisis_prominence = Column(String(20))

    # Deployment
    deployed = Column(Boolean, default=False)
    deployed_at = Column(TIMESTAMP)

    # User feedback
    user_rating = Column(Integer)
    user_feedback = Column(Text)

    # Metadata
    is_current = Column(Boolean, default=True)

    # Relationships
    user = relationship('User', back_populates='configs')
    pattern = relationship('UserPattern', back_populates='configs')
    changes = relationship('InterfaceChange', back_populates='config')

    __table_args__ = (
        CheckConstraint("theme IN ('anxiety', 'depression', 'crisis', 'stable', 'balanced')"),
        CheckConstraint("crisis_prominence IN ('hidden', 'sidebar', 'card', 'top', 'modal')"),
        CheckConstraint("user_rating >= 1 AND user_rating <= 5"),
        UniqueConstraint('user_id', name='uq_user_current_config', postgresql_where=(is_current == True)),
    )

    def __repr__(self):
        return f"<InterfaceConfig(user_id='{self.user_id}', version='{self.version}', theme='{self.theme}')>"

# ============================================================================
# INTERFACE CHANGE MODEL
# ============================================================================

class InterfaceChange(Base):
    __tablename__ = 'interface_changes'

    change_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    config_id = Column(UUID(as_uuid=True), ForeignKey('interface_configs.config_id'), nullable=False)
    change_type = Column(String(50), nullable=False)
    component_affected = Column(String(100))
    reason = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    shown_to_user = Column(Boolean, default=False)
    user_acknowledged = Column(Boolean, default=False)
    user_rating = Column(Integer)
    user_feedback = Column(Text)

    # Relationships
    user = relationship('User', back_populates='changes')
    config = relationship('InterfaceConfig', back_populates='changes')

    __table_args__ = (
        CheckConstraint(
            "change_type IN ('risk_escalation', 'risk_de_escalation', 'feature_added', "
            "'feature_hidden', 'theme_changed', 'language_adapted', 'cultural_adjustment', "
            "'baseline_established', 'trigger_detected', 'coping_identified')"
        ),
        CheckConstraint("user_rating >= 1 AND user_rating <= 5"),
    )

    def __repr__(self):
        return f"<InterfaceChange(change_type='{self.change_type}', component='{self.component_affected}')>"

# ============================================================================
# RISK ALERT MODEL
# ============================================================================

class RiskAlert(Base):
    __tablename__ = 'risk_alerts'

    alert_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    pattern_id = Column(UUID(as_uuid=True), ForeignKey('user_patterns.pattern_id'))
    risk_level = Column(String(20), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_factors = Column(ARRAY(Text), nullable=False)
    risk_interpretation = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    alert_sent = Column(Boolean, default=False)
    alert_sent_at = Column(TIMESTAMP)
    counselor_id = Column(UUID(as_uuid=True))
    counselor_notified = Column(Boolean, default=False)
    counselor_responded = Column(Boolean, default=False)
    counselor_response = Column(Text)
    counselor_response_at = Column(TIMESTAMP)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(TIMESTAMP)
    resolution_notes = Column(Text)

    # Relationships
    user = relationship('User', back_populates='alerts')
    pattern = relationship('UserPattern', back_populates='alerts')

    __table_args__ = (
        CheckConstraint("risk_level IN ('high', 'critical')"),
        CheckConstraint("risk_score >= 0 AND risk_score <= 1"),
    )

    def __repr__(self):
        return f"<RiskAlert(user_id='{self.user_id}', level='{self.risk_level}', resolved={self.resolved})>"

# ============================================================================
# PATTERN HISTORY MODEL
# ============================================================================

class PatternHistory(Base):
    __tablename__ = 'pattern_history'

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    pattern_id = Column(UUID(as_uuid=True), ForeignKey('user_patterns.pattern_id'), nullable=False)
    snapshot_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    version = Column(Integer, nullable=False)

    # Key metrics
    emotional_trajectory = Column(String(20))
    risk_level = Column(String(20))
    risk_score = Column(Float)
    dissonance_score = Column(Float)
    coping_consistency = Column(Float)
    baseline_deviation = Column(Float)

    # Compressed full pattern
    full_pattern_compressed = Column(JSONB)

    # Relationships
    user = relationship('User', back_populates='pattern_history')
    pattern = relationship('UserPattern', back_populates='history')

    def __repr__(self):
        return f"<PatternHistory(user_id='{self.user_id}', version={self.version}, risk='{self.risk_level}')>"

# ============================================================================
# ENCRYPTION KEYS MODEL
# ============================================================================

class EncryptionKey(Base):
    __tablename__ = 'encryption_keys'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    public_key = Column(Text, nullable=False)
    private_key_encrypted = Column(Text, nullable=False)
    salt = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    rotated_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<EncryptionKey(user_id='{self.user_id}')>"
