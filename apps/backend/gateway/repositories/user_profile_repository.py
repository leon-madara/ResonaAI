"""
User Profile Repository
Handles database operations for encrypted user profiles
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from models.encrypted_models import UserProfile
from services.encrypted_storage import get_encrypted_storage_service

logger = logging.getLogger(__name__)


class UserProfileRepository:
    """Repository for user profile database operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.encrypted_storage = get_encrypted_storage_service()
    
    async def save_profile(
        self,
        user_id: UUID,
        profile_data: Dict[str, Any]
    ) -> UserProfile:
        """
        Save encrypted user profile
        
        Args:
            user_id: User ID
            profile_data: Profile data dictionary to encrypt
            
        Returns:
            UserProfile model instance
        """
        return await self.encrypted_storage.save_user_profile(
            self.db,
            str(user_id),
            profile_data
        )
    
    async def get_profile(
        self,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get and decrypt user profile
        
        Args:
            user_id: User ID
            
        Returns:
            Decrypted profile data dictionary or None
        """
        return await self.encrypted_storage.get_user_profile(
            self.db,
            str(user_id)
        )
    
    def profile_exists(self, user_id: UUID) -> bool:
        """
        Check if profile exists for user
        
        Args:
            user_id: User ID
            
        Returns:
            True if profile exists
        """
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        return profile is not None

