"""
API Key authentication middleware for service-to-service communication
"""

import secrets
import hashlib
import logging
from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import APIKeyHeader
import uuid

from database import APIKey, get_db

logger = logging.getLogger(__name__)

# API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class APIKeyService:
    """
    API Key management service for service-to-service authentication
    """
    
    # API key settings
    KEY_LENGTH = 32  # 256 bits
    KEY_PREFIX_LENGTH = 8
    
    def generate_api_key(self) -> Tuple[str, str, str]:
        """
        Generate a new API key
        
        Returns:
            Tuple of (full_key, key_prefix, key_hash)
        """
        # Generate random key
        key = secrets.token_urlsafe(self.KEY_LENGTH)
        
        # Extract prefix for identification
        key_prefix = key[:self.KEY_PREFIX_LENGTH]
        
        # Hash for storage
        key_hash = self.hash_key(key)
        
        return key, key_prefix, key_hash
    
    def hash_key(self, key: str) -> str:
        """
        Hash an API key for storage
        
        Args:
            key: Plain text API key
            
        Returns:
            Hashed key
        """
        return hashlib.sha256(key.encode()).hexdigest()
    
    def verify_key(self, key: str, stored_hash: str) -> bool:
        """
        Verify an API key against its stored hash
        
        Args:
            key: API key to verify
            stored_hash: Stored hash value
            
        Returns:
            True if key is valid
        """
        return self.hash_key(key) == stored_hash
    
    def create_api_key(
        self,
        db: Session,
        name: str,
        user_id: Optional[str] = None,
        permissions: Optional[list] = None,
        rate_limit: int = 100,
        expires_in_days: Optional[int] = None
    ) -> Tuple[APIKey, str]:
        """
        Create a new API key
        
        Args:
            db: Database session
            name: Descriptive name for the key
            user_id: Optional user ID to associate with the key
            permissions: List of permissions
            rate_limit: Requests per minute
            expires_in_days: Days until expiration (None for no expiration)
            
        Returns:
            Tuple of (APIKey model, plain_key)
        """
        # Generate key
        plain_key, key_prefix, key_hash = self.generate_api_key()
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Create API key record
        api_key = APIKey(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id) if user_id else None,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            permissions=permissions or [],
            rate_limit=rate_limit,
            expires_at=expires_at
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        logger.info(f"API key created: {name} (prefix: {key_prefix})")
        
        return api_key, plain_key
    
    def get_api_key_by_id(self, db: Session, key_id: str) -> Optional[APIKey]:
        """Get API key by ID"""
        try:
            key_uuid = uuid.UUID(key_id)
            return db.query(APIKey).filter(APIKey.id == key_uuid).first()
        except ValueError:
            return None
    
    def get_api_keys_by_user(self, db: Session, user_id: str) -> list:
        """Get all API keys for a user"""
        try:
            user_uuid = uuid.UUID(user_id)
            return db.query(APIKey).filter(
                APIKey.user_id == user_uuid,
                APIKey.revoked == False
            ).all()
        except ValueError:
            return []
    
    def validate_api_key(self, db: Session, key: str) -> Optional[APIKey]:
        """
        Validate an API key
        
        Args:
            db: Database session
            key: API key to validate
            
        Returns:
            APIKey if valid, None otherwise
        """
        if not key or len(key) < self.KEY_PREFIX_LENGTH:
            return None
        
        # Extract prefix
        key_prefix = key[:self.KEY_PREFIX_LENGTH]
        
        # Find matching keys by prefix
        potential_keys = db.query(APIKey).filter(
            APIKey.key_prefix == key_prefix,
            APIKey.revoked == False
        ).all()
        
        # Verify against each potential key
        for api_key in potential_keys:
            if self.verify_key(key, api_key.key_hash):
                # Check expiration
                if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                    logger.warning(f"API key expired: {api_key.name}")
                    return None
                
                # Update last used
                api_key.last_used_at = datetime.utcnow()
                db.commit()
                
                return api_key
        
        return None
    
    def revoke_api_key(self, db: Session, key_id: str) -> bool:
        """
        Revoke an API key
        
        Args:
            db: Database session
            key_id: API key ID
            
        Returns:
            True if revoked successfully
        """
        api_key = self.get_api_key_by_id(db, key_id)
        if not api_key:
            return False
        
        api_key.revoked = True
        api_key.revoked_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"API key revoked: {api_key.name}")
        
        return True
    
    def update_api_key(
        self,
        db: Session,
        key_id: str,
        name: Optional[str] = None,
        permissions: Optional[list] = None,
        rate_limit: Optional[int] = None
    ) -> Optional[APIKey]:
        """
        Update an API key
        
        Args:
            db: Database session
            key_id: API key ID
            name: New name (optional)
            permissions: New permissions (optional)
            rate_limit: New rate limit (optional)
            
        Returns:
            Updated APIKey or None
        """
        api_key = self.get_api_key_by_id(db, key_id)
        if not api_key or api_key.revoked:
            return None
        
        if name is not None:
            api_key.name = name
        if permissions is not None:
            api_key.permissions = permissions
        if rate_limit is not None:
            api_key.rate_limit = rate_limit
        
        db.commit()
        db.refresh(api_key)
        
        return api_key


# Global API key service instance
api_key_service = APIKeyService()


def get_api_key_service() -> APIKeyService:
    """Get the API key service instance"""
    return api_key_service


async def get_api_key_auth(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[APIKey]:
    """
    Dependency to validate API key authentication
    
    Usage:
        @app.get("/api/data")
        async def get_data(api_key: APIKey = Depends(get_api_key_auth)):
            if not api_key:
                raise HTTPException(...)
    """
    if not api_key:
        return None
    
    validated_key = api_key_service.validate_api_key(db, api_key)
    return validated_key


async def require_api_key(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    Dependency to require API key authentication
    Raises 401 if key is missing or invalid
    
    Usage:
        @app.get("/api/data")
        async def get_data(api_key: APIKey = Depends(require_api_key)):
            ...
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    validated_key = api_key_service.validate_api_key(db, api_key)
    if not validated_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired API key"
        )
    
    return validated_key


class APIKeyRateLimiter:
    """
    Rate limiter for API key authenticated requests
    Uses Redis for distributed rate limiting
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def check_rate_limit(self, api_key: APIKey) -> bool:
        """
        Check if API key has exceeded its rate limit
        
        Args:
            api_key: APIKey model
            
        Returns:
            True if within rate limit
        """
        try:
            import time
            
            key = f"api_key_rate:{api_key.id}"
            window_size = 60  # 1 minute
            current_time = int(time.time())
            window_start = current_time - window_size
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiration
            pipe.expire(key, window_size)
            
            results = pipe.execute()
            current_requests = results[1]
            
            return current_requests < api_key.rate_limit
            
        except Exception as e:
            logger.error(f"API key rate limit check failed: {e}")
            # Allow request if Redis is unavailable
            return True

