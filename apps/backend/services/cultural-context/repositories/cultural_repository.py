"""
Cultural Repository
Handles database operations for cultural context cache
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timezone, timedelta

from models.database_models import CulturalContextCache

logger = logging.getLogger(__name__)


class CulturalRepository:
    """Repository for cultural context cache database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_cached_context(
        self,
        context_key: str
    ) -> Optional[CulturalContextCache]:
        """
        Get cached cultural context by key if not expired
        
        Args:
            context_key: Cache key
            
        Returns:
            CulturalContextCache instance if found and not expired, None otherwise
        """
        cache_entry = (
            self.db.query(CulturalContextCache)
            .filter(CulturalContextCache.context_key == context_key)
            .first()
        )
        
        if not cache_entry:
            return None
        
        # Check if expired
        if cache_entry.expires_at:
            expires_at = cache_entry.expires_at
            now = datetime.now(timezone.utc)
            # SQLite often returns naive datetimes; assume UTC.
            if getattr(expires_at, "tzinfo", None) is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < now:
                # Delete expired entry
                self.db.delete(cache_entry)
                self.db.commit()
                return None
        
        return cache_entry
    
    def cache_context(
        self,
        context_key: str,
        context_data: Dict[str, Any],
        language: Optional[str] = None,
        region: Optional[str] = None,
        expires_in_hours: int = 24
    ) -> CulturalContextCache:
        """
        Cache cultural context data
        
        Args:
            context_key: Cache key
            context_data: Context data to cache
            language: Optional language code
            region: Optional region
            expires_in_hours: Hours until expiration (default 24)
            
        Returns:
            CulturalContextCache model instance
        """
        try:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)
            
            # Check if entry exists
            existing = (
                self.db.query(CulturalContextCache)
                .filter(CulturalContextCache.context_key == context_key)
                .first()
            )
            
            if existing:
                # Update existing entry
                existing.context_data = context_data
                existing.language = language
                existing.region = region
                existing.expires_at = expires_at
                existing.updated_at = datetime.now(timezone.utc)
                self.db.commit()
                self.db.refresh(existing)
                logger.info(f"Updated cached context for key {context_key}")
                return existing
            else:
                # Create new entry
                cache_entry = CulturalContextCache(
                    context_key=context_key,
                    context_data=context_data,
                    language=language,
                    region=region,
                    expires_at=expires_at
                )
                self.db.add(cache_entry)
                self.db.commit()
                self.db.refresh(cache_entry)
                logger.info(f"Cached context for key {context_key}")
                return cache_entry
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error caching context: {e}")
            raise
    
    def delete_expired_entries(self) -> int:
        """
        Delete expired cache entries
        
        Returns:
            Number of entries deleted
        """
        try:
            now = datetime.now(timezone.utc)
            deleted = (
                self.db.query(CulturalContextCache)
                .filter(CulturalContextCache.expires_at < now)
                .delete()
            )
            self.db.commit()
            if deleted > 0:
                logger.info(f"Deleted {deleted} expired cache entries")
            return deleted
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting expired entries: {e}")
            raise
    
    def get_by_language(
        self,
        language: str,
        limit: int = 100
    ) -> List[CulturalContextCache]:
        """
        Get cached contexts by language
        
        Args:
            language: Language code
            limit: Maximum number of entries
            
        Returns:
            List of CulturalContextCache instances
        """
        return (
            self.db.query(CulturalContextCache)
            .filter(
                and_(
                    CulturalContextCache.language == language,
                    (CulturalContextCache.expires_at.is_(None)) |
                    (CulturalContextCache.expires_at > datetime.now(timezone.utc))
                )
            )
            .order_by(desc(CulturalContextCache.created_at))
            .limit(limit)
            .all()
        )
    
    def delete_context(self, context_key: str) -> bool:
        """
        Delete cached context by key
        
        Args:
            context_key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        cache_entry = (
            self.db.query(CulturalContextCache)
            .filter(CulturalContextCache.context_key == context_key)
            .first()
        )
        
        if not cache_entry:
            return False
        
        self.db.delete(cache_entry)
        self.db.commit()
        logger.info(f"Deleted cached context for key {context_key}")
        return True

