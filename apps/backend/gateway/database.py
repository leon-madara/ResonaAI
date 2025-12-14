"""
Database connection and models for API Gateway
"""

from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer, Float, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime, timezone
import os
import uuid
from sqlalchemy.pool import StaticPool

from config import settings

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Lazy engine/session creation:
# - Avoid importing postgres drivers during test collection
# - Allow tests to set DATABASE_URL/env before first DB access
_engine = None
_SessionLocal = None


def get_engine():
    """Get (or create) the SQLAlchemy engine."""
    global _engine
    if _engine is not None:
        return _engine

    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        _engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def get_sessionmaker():
    """Get (or create) the sessionmaker bound to the engine."""
    global _SessionLocal
    if _SessionLocal is not None:
        return _SessionLocal
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

# Base class for models
Base = declarative_base()


# Association table for user roles (many-to-many)
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)


class User(Base):
    """User model with MFA and RBAC support"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Email is nullable to support anonymous users (system design allows anonymous users).
    # API endpoints may still require email for registration/login.
    email = Column(String(255), unique=True, nullable=True, index=True)
    phone = Column(String(20), nullable=True, index=True)
    password_hash = Column(Text, nullable=True)  # Nullable for existing users, will be set on first login
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    consent_version = Column(String(10), nullable=True)
    data_retention_until = Column(DateTime, nullable=True)
    is_anonymous = Column(Boolean, default=True, nullable=False)
    
    # MFA fields
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(Text, nullable=True)  # Encrypted TOTP secret
    mfa_backup_codes = Column(ARRAY(Text), nullable=True)  # Hashed backup codes
    mfa_enabled_at = Column(DateTime, nullable=True)
    
    # Role (default: 'user')
    role = Column(String(50), default='user', nullable=False)
    
    # Relationships
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    refresh_tokens = relationship('RefreshToken', back_populates='user', cascade='all, delete-orphan')
    api_keys = relationship('APIKey', back_populates='user', cascade='all, delete-orphan')
    interface_evolution_logs = relationship('InterfaceEvolutionLog', back_populates='user', cascade='all, delete-orphan')
    dissonance_records = relationship('DissonanceRecord', back_populates='user', cascade='all, delete-orphan')
    profile = relationship('UserProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    conversations = relationship('Conversation', back_populates='user', cascade='all, delete-orphan')


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    permissions = Column(ARRAY(Text), nullable=False, default=[])
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='roles')


class RefreshToken(Base):
    """Refresh token model for token refresh mechanism"""
    __tablename__ = "refresh_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_hash = Column(Text, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    device_info = Column(Text, nullable=True)  # Optional device/browser info
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    
    # Relationships
    user = relationship('User', back_populates='refresh_tokens')


class APIKey(Base):
    """API Key model for service-to-service authentication"""
    __tablename__ = "api_keys"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    key_hash = Column(Text, nullable=False, unique=True)
    key_prefix = Column(String(8), nullable=False)  # First 8 chars for identification
    permissions = Column(ARRAY(Text), nullable=False, default=[])
    rate_limit = Column(Integer, default=100, nullable=False)  # Requests per minute
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship('User', back_populates='api_keys')


class AuditLog(Base):
    """Audit log model for security events"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    event_type = Column(String(50), nullable=False, index=True)  # login, logout, data_access, etc.
    event_action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=True)  # user, conversation, message, etc.
    resource_id = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    details = Column(JSONB, nullable=True)  # Additional event details
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    severity = Column(String(20), default='info', nullable=False)  # info, warning, error, critical


class InterfaceEvolutionLog(Base):
    """Interface evolution log model - tracks how interfaces evolve over time"""
    __tablename__ = "interface_evolution_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    version = Column(Integer, nullable=False, index=True)
    changes = Column(JSONB, nullable=False)  # Track interface changes
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='interface_evolution_logs')
    
    def __repr__(self):
        return f"<InterfaceEvolutionLog(user_id={self.user_id}, version={self.version})>"


class DissonanceRecord(Base):
    """Dissonance record model - stores dissonance detection results"""
    __tablename__ = "dissonance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False)
    transcript = Column(Text, nullable=True)
    stated_emotion = Column(String(50), nullable=True)
    actual_emotion = Column(String(50), nullable=True)
    dissonance_score = Column(Float(), nullable=False, index=True)
    interpretation = Column(String(100), nullable=True)
    risk_level = Column(String(20), nullable=True, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship('User', back_populates='dissonance_records')
    
    def __repr__(self):
        return f"<DissonanceRecord(user_id={self.user_id}, session_id={self.session_id}, score={self.dissonance_score})>"


def get_db() -> Session:
    """Get database session"""
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables (tables should already exist from init.sql)"""
    # Don't create tables here - they're managed by init.sql
    # This is just for reference
    pass


# Ensure all model modules are imported so their tables are registered on `Base.metadata`.
# Tests often call `Base.metadata.create_all()` for an in-memory SQLite database.
try:  # pragma: no cover
    from models import encrypted_models  # noqa: F401
    from models import mfa_models  # noqa: F401
    from models import rbac_models  # noqa: F401
    from models import api_key_models  # noqa: F401
except Exception:
    # In some environments, optional dependencies may not be installed; table registration
    # is best-effort for tests that rely on it.
    pass

