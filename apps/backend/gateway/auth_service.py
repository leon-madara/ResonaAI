"""
Authentication service for user management
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from database import User
from datetime import datetime, timezone
import uuid
import re
import base64
import hashlib
import hmac
import os

try:
    import bcrypt  # type: ignore
except Exception:  # pragma: no cover
    bcrypt = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.

    Uses bcrypt when available; falls back to PBKDF2-HMAC-SHA256 when bcrypt is
    not installed (primarily for local test environments).
    """
    try:
        if bcrypt is not None and hashed_password.startswith("$2"):
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )

        # PBKDF2 fallback format: pbkdf2_sha256$<iters>$<salt_b64>$<hash_b64>
        if hashed_password.startswith("pbkdf2_sha256$"):
            parts = hashed_password.split("$")
            if len(parts) != 4:
                return False
            _, iters_s, salt_b64, hash_b64 = parts
            iters = int(iters_s)
            salt = base64.b64decode(salt_b64.encode("utf-8"))
            expected = base64.b64decode(hash_b64.encode("utf-8"))
            derived = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iters, dklen=len(expected))
            return hmac.compare_digest(derived, expected)

        # Unknown format
        return False
    except (ValueError, TypeError):
        return False


def get_password_hash(password: str) -> str:
    """Hash a password.

    Uses bcrypt when available; otherwise uses PBKDF2-HMAC-SHA256.
    """
    if bcrypt is not None:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    # PBKDF2 fallback
    iters = 200_000
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iters, dklen=32)
    return "pbkdf2_sha256$%d$%s$%s" % (
        iters,
        base64.b64encode(salt).decode("utf-8"),
        base64.b64encode(derived).decode("utf-8"),
    )


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
        created_at=datetime.now(timezone.utc),
        last_active=datetime.now(timezone.utc)
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
    user.last_active = datetime.now(timezone.utc)
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

