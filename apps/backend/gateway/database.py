"""
Database connection and models for API Gateway
"""

from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import os
import uuid

from config import settings

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, nullable=False)
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


def get_db() -> Session:
    """Get database session"""
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

