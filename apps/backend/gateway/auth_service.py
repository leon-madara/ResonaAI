"""
Authentication service for user management
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import User
from datetime import datetime
import uuid
import re

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


from typing import Tuple

def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    return True, ""


from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        user_uuid = uuid.UUID(user_id)
        return db.query(User).filter(User.id == user_uuid).first()
    except ValueError:
        return None


def create_user(
    db: Session,
    email: str,
    password: str,
    consent_version: str,
    is_anonymous: bool = True
) -> User:
    """Create a new user"""
    # Validate email
    if not validate_email(email):
        raise ValueError("Invalid email format")
    
    # Validate password
    is_valid, error_msg = validate_password(password)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Hash password
    password_hash = get_password_hash(password)
    
    # Create user
    user = User(
        id=uuid.uuid4(),
        email=email.lower(),
        password_hash=password_hash,
        consent_version=consent_version,
        is_anonymous=is_anonymous,
        created_at=datetime.utcnow(),
        last_active=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user"""
    user = get_user_by_email(db, email)
    if not user:
        return None
    
    # Check if user has a password hash (for existing users without passwords)
    if not user.password_hash:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    # Update last active
    user.last_active = datetime.utcnow()
    db.commit()
    
    return user


def update_user_password(db: Session, user_id: str, new_password: str) -> bool:
    """Update user password"""
    user = get_user_by_id(db, user_id)
    if not user:
        return False
    
    # Validate password
    is_valid, error_msg = validate_password(new_password)
    if not is_valid:
        raise ValueError(error_msg)
    
    # Hash and update password
    user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return True

