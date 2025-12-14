"""
User service for authentication and user management
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime, timezone
import uuid

from ..database import User
from ..utils.password import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email address.
    
    Args:
        db: Database session
        email: User email address
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    email: str,
    password: str,
    phone: Optional[str] = None,
    is_anonymous: bool = False
) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session
        email: User email address
        password: Plain text password (will be hashed)
        phone: Optional phone number
        is_anonymous: Whether user is anonymous
        
    Returns:
        Created User object
        
    Raises:
        ValueError: If email already exists
    """
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise ValueError(f"User with email {email} already exists")
    
    # Hash password
    password_hash = hash_password(password)
    
    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email,
        phone=phone,
        password_hash=password_hash,
        is_anonymous=is_anonymous,
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc),
        role='user'
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def verify_user_credentials(db: Session, email: str, password: str) -> Optional[User]:
    """
    Verify user credentials and return user if valid.
    
    Args:
        db: Database session
        email: User email address
        password: Plain text password
        
    Returns:
        User object if credentials are valid, None otherwise
    """
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    
    # Check if user has a password hash
    if not user.password_hash:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last active timestamp
    user.last_active = datetime.now(timezone.utc)
    db.commit()
    
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password.
    Alias for verify_user_credentials for backward compatibility.
    
    Args:
        db: Database session
        email: User email address
        password: Plain text password
        
    Returns:
        User object if authenticated, None otherwise
    """
    return verify_user_credentials(db, email, password)

