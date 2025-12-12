"""
Refresh Token service for long-lived authentication sessions
"""

import secrets
import hashlib
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import jwt
import uuid

from database import RefreshToken, User

logger = logging.getLogger(__name__)


class RefreshTokenService:
    """
    Refresh Token service for maintaining long-lived sessions
    Implements token rotation for security
    """
    
    # Token settings
    REFRESH_TOKEN_BYTES = 32  # 256 bits
    REFRESH_TOKEN_EXPIRY_DAYS = 30
    ACCESS_TOKEN_EXPIRY_MINUTES = 15  # Short-lived access tokens
    
    def __init__(self, jwt_secret: str, jwt_algorithm: str = "HS256"):
        """
        Initialize refresh token service
        
        Args:
            jwt_secret: Secret key for JWT signing
            jwt_algorithm: JWT algorithm (default: HS256)
        """
        self.jwt_secret = jwt_secret
        self.jwt_algorithm = jwt_algorithm
    
    def generate_refresh_token(self) -> str:
        """
        Generate a cryptographically secure refresh token
        
        Returns:
            Refresh token string
        """
        return secrets.token_urlsafe(self.REFRESH_TOKEN_BYTES)
    
    def hash_token(self, token: str) -> str:
        """
        Hash a refresh token for storage
        
        Args:
            token: Plain text token
            
        Returns:
            Hashed token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def verify_token(self, token: str, stored_hash: str) -> bool:
        """
        Verify a refresh token against its stored hash
        
        Args:
            token: Token to verify
            stored_hash: Stored hash value
            
        Returns:
            True if token is valid
        """
        return self.hash_token(token) == stored_hash
    
    def create_refresh_token(
        self,
        db: Session,
        user_id: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Tuple[RefreshToken, str]:
        """
        Create a new refresh token for a user
        
        Args:
            db: Database session
            user_id: User ID
            device_info: Optional device/browser information
            ip_address: Optional IP address
            
        Returns:
            Tuple of (RefreshToken model, plain_token)
        """
        # Generate token
        plain_token = self.generate_refresh_token()
        token_hash = self.hash_token(plain_token)
        
        # Calculate expiration
        expires_at = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRY_DAYS)
        
        # Create refresh token record
        refresh_token = RefreshToken(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            token_hash=token_hash,
            expires_at=expires_at,
            device_info=device_info,
            ip_address=ip_address
        )
        
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        
        logger.info(f"Refresh token created for user: {user_id}")
        
        return refresh_token, plain_token
    
    def validate_refresh_token(self, db: Session, token: str) -> Optional[RefreshToken]:
        """
        Validate a refresh token
        
        Args:
            db: Database session
            token: Refresh token to validate
            
        Returns:
            RefreshToken if valid, None otherwise
        """
        if not token:
            return None
        
        token_hash = self.hash_token(token)
        
        # Find token by hash
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False
        ).first()
        
        if not refresh_token:
            return None
        
        # Check expiration
        if refresh_token.expires_at < datetime.utcnow():
            logger.warning(f"Refresh token expired for user: {refresh_token.user_id}")
            return None
        
        return refresh_token
    
    def rotate_refresh_token(
        self,
        db: Session,
        old_token: str,
        device_info: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Optional[Tuple[RefreshToken, str]]:
        """
        Rotate a refresh token (revoke old, create new)
        Implements token rotation for security
        
        Args:
            db: Database session
            old_token: Current refresh token
            device_info: Optional device info
            ip_address: Optional IP address
            
        Returns:
            Tuple of (new RefreshToken, new plain_token) or None
        """
        # Validate old token
        old_refresh_token = self.validate_refresh_token(db, old_token)
        if not old_refresh_token:
            return None
        
        # Revoke old token
        old_refresh_token.revoked = True
        old_refresh_token.revoked_at = datetime.utcnow()
        
        # Create new token
        new_token, plain_token = self.create_refresh_token(
            db,
            str(old_refresh_token.user_id),
            device_info,
            ip_address
        )
        
        logger.info(f"Refresh token rotated for user: {old_refresh_token.user_id}")
        
        return new_token, plain_token
    
    def revoke_refresh_token(self, db: Session, token: str) -> bool:
        """
        Revoke a specific refresh token
        
        Args:
            db: Database session
            token: Refresh token to revoke
            
        Returns:
            True if revoked successfully
        """
        token_hash = self.hash_token(token)
        
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
        
        if not refresh_token:
            return False
        
        refresh_token.revoked = True
        refresh_token.revoked_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Refresh token revoked for user: {refresh_token.user_id}")
        
        return True
    
    def revoke_all_user_tokens(self, db: Session, user_id: str) -> int:
        """
        Revoke all refresh tokens for a user (logout from all devices)
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of tokens revoked
        """
        try:
            user_uuid = uuid.UUID(user_id)
            
            tokens = db.query(RefreshToken).filter(
                RefreshToken.user_id == user_uuid,
                RefreshToken.revoked == False
            ).all()
            
            count = 0
            for token in tokens:
                token.revoked = True
                token.revoked_at = datetime.utcnow()
                count += 1
            
            db.commit()
            
            logger.info(f"Revoked {count} refresh tokens for user: {user_id}")
            
            return count
            
        except ValueError:
            return 0
    
    def get_user_sessions(self, db: Session, user_id: str) -> list:
        """
        Get all active sessions (refresh tokens) for a user
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            List of active RefreshToken records
        """
        try:
            user_uuid = uuid.UUID(user_id)
            
            return db.query(RefreshToken).filter(
                RefreshToken.user_id == user_uuid,
                RefreshToken.revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            ).all()
            
        except ValueError:
            return []
    
    def generate_access_token(self, user: User) -> Tuple[str, int]:
        """
        Generate a short-lived access token
        
        Args:
            user: User object
            
        Returns:
            Tuple of (access_token, expires_in_seconds)
        """
        expires_at = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRY_MINUTES)
        
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "role": getattr(user, 'role', 'user'),
            "exp": expires_at
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        return token, self.ACCESS_TOKEN_EXPIRY_MINUTES * 60
    
    def cleanup_expired_tokens(self, db: Session) -> int:
        """
        Clean up expired refresh tokens
        
        Args:
            db: Database session
            
        Returns:
            Number of tokens deleted
        """
        result = db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        
        if result > 0:
            logger.info(f"Cleaned up {result} expired refresh tokens")
        
        return result


# Factory function to create service with settings
def create_refresh_token_service(jwt_secret: str, jwt_algorithm: str = "HS256") -> RefreshTokenService:
    """Create a RefreshTokenService instance"""
    return RefreshTokenService(jwt_secret, jwt_algorithm)

