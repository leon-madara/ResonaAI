"""
Encrypted Storage Service
Integrates with Encryption Service for secure data storage and retrieval
"""

import logging
import httpx
import json
import base64
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models.encrypted_models import UserProfile, Conversation, Message, SyncQueue, CrisisEvent
from config import settings

logger = logging.getLogger(__name__)


class EncryptedStorageService:
    """Service for encrypted data storage and retrieval"""
    
    def __init__(self, encryption_service_url: Optional[str] = None):
        """
        Initialize encrypted storage service
        
        Args:
            encryption_service_url: URL of the encryption service (defaults to ENCRYPTION_SERVICE_URL)
        """
        self.encryption_service_url = encryption_service_url or getattr(
            settings, 'ENCRYPTION_SERVICE_URL', 'http://encryption-service:8000'
        )
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def _encrypt_data(self, data: str, key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt data using encryption service
        
        Args:
            data: Plain text data to encrypt
            key_id: Optional key ID for encryption
            
        Returns:
            Encryption result with encrypted_data
        """
        try:
            response = await self.client.post(
                f"{self.encryption_service_url}/encrypt",
                json={"data": data, "key_id": key_id}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", {})
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise
    
    async def _decrypt_data(self, encrypted_data: str, key_id: Optional[str] = None) -> str:
        """
        Decrypt data using encryption service
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            key_id: Optional key ID for decryption
            
        Returns:
            Decrypted plain text data
        """
        try:
            response = await self.client.post(
                f"{self.encryption_service_url}/decrypt",
                json={"encrypted_data": encrypted_data, "key_id": key_id}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("data", "")
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise
    
    async def _reencrypt_data(self, encrypted_data: str) -> Dict[str, Any]:
        """
        Re-encrypt data using encryption service
        
        Args:
            encrypted_data: Base64 encoded encrypted data to re-encrypt
            
        Returns:
            Re-encryption result with new encrypted_data
        """
        try:
            response = await self.client.post(
                f"{self.encryption_service_url}/re-encrypt",
                json={"encrypted_data": encrypted_data}
            )
            response.raise_for_status()
            result = response.json()
            return result.get("result", {})
        except Exception as e:
            logger.error(f"Re-encryption failed: {str(e)}")
            raise
    
    async def save_user_profile(
        self,
        db: Session,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> UserProfile:
        """
        Save encrypted user profile
        
        Args:
            db: Database session
            user_id: User ID
            profile_data: Profile data dictionary to encrypt
            
        Returns:
            UserProfile model instance
        """
        # Encrypt profile data
        profile_json = json.dumps(profile_data)
        encryption_result = await self._encrypt_data(profile_json, key_id=f"user:{user_id}")
        encrypted_b64 = encryption_result.get("encrypted_data", "")
        
        # Convert base64 to bytes for BYTEA storage
        encrypted_bytes = base64.b64decode(encrypted_b64.encode('utf-8'))
        
        # Get or create profile
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            profile.encrypted_data = encrypted_bytes
            profile.updated_at = datetime.now(timezone.utc)
        else:
            profile = UserProfile(
                user_id=user_id,
                encrypted_data=encrypted_bytes
            )
            db.add(profile)
        
        db.commit()
        db.refresh(profile)
        return profile
    
    async def get_user_profile(
        self,
        db: Session,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get and decrypt user profile
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Decrypted profile data dictionary or None
        """
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return None
        
        # Convert BYTEA to base64
        encrypted_b64 = base64.b64encode(profile.encrypted_data).decode('utf-8')
        
        # Decrypt
        decrypted_json = await self._decrypt_data(encrypted_b64, key_id=f"user:{user_id}")
        return json.loads(decrypted_json)
    
    async def save_message(
        self,
        db: Session,
        conversation_id: str,
        message_type: str,
        content: str,
        emotion_data: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Save encrypted message
        
        Args:
            db: Database session
            conversation_id: Conversation ID
            message_type: 'user' or 'ai'
            content: Message content to encrypt
            emotion_data: Optional emotion data
            
        Returns:
            Message model instance
        """
        # Encrypt message content
        encryption_result = await self._encrypt_data(content, key_id=f"conversation:{conversation_id}")
        encrypted_b64 = encryption_result.get("encrypted_data", "")
        
        # Convert base64 to bytes for BYTEA storage
        encrypted_bytes = base64.b64decode(encrypted_b64.encode('utf-8'))
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            message_type=message_type,
            encrypted_content=encrypted_bytes,
            emotion_data=emotion_data
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    
    async def get_message(
        self,
        db: Session,
        message_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get and decrypt message
        
        Args:
            db: Database session
            message_id: Message ID
            
        Returns:
            Decrypted message data dictionary or None
        """
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return None
        
        # Convert BYTEA to base64
        encrypted_b64 = base64.b64encode(message.encrypted_content).decode('utf-8')
        
        # Decrypt
        decrypted_content = await self._decrypt_data(
            encrypted_b64,
            key_id=f"conversation:{message.conversation_id}"
        )
        
        return {
            "id": str(message.id),
            "conversation_id": str(message.conversation_id),
            "message_type": message.message_type,
            "content": decrypted_content,
            "emotion_data": message.emotion_data,
            "created_at": message.created_at.isoformat()
        }
    
    async def enqueue_sync_operation(
        self,
        db: Session,
        user_id: str,
        operation_type: str,
        operation_data: Dict[str, Any]
    ) -> SyncQueue:
        """
        Enqueue encrypted sync operation
        
        Args:
            db: Database session
            user_id: User ID
            operation_type: Type of operation
            operation_data: Operation data to encrypt
            
        Returns:
            SyncQueue model instance
        """
        # Encrypt operation data
        operation_json = json.dumps(operation_data)
        encryption_result = await self._encrypt_data(operation_json, key_id=f"user:{user_id}")
        encrypted_b64 = encryption_result.get("encrypted_data", "")
        
        # Convert base64 to bytes for BYTEA storage
        encrypted_bytes = base64.b64decode(encrypted_b64.encode('utf-8'))
        
        # Create sync queue entry
        sync_entry = SyncQueue(
            user_id=user_id,
            operation_type=operation_type,
            encrypted_data=encrypted_bytes,
            status='pending'
        )
        db.add(sync_entry)
        db.commit()
        db.refresh(sync_entry)
        return sync_entry
    
    async def get_sync_operation(
        self,
        db: Session,
        sync_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get and decrypt sync operation
        
        Args:
            db: Database session
            sync_id: Sync operation ID
            
        Returns:
            Decrypted operation data dictionary or None
        """
        sync_entry = db.query(SyncQueue).filter(SyncQueue.id == sync_id).first()
        if not sync_entry:
            return None
        
        # Convert BYTEA to base64
        encrypted_b64 = base64.b64encode(sync_entry.encrypted_data).decode('utf-8')
        
        # Decrypt
        decrypted_json = await self._decrypt_data(encrypted_b64, key_id=f"user:{sync_entry.user_id}")
        return json.loads(decrypted_json)
    
    async def _reencrypt_user_profiles(self, db: Session, batch_size: int = 100) -> Dict[str, int]:
        """
        Re-encrypt all user profiles
        
        Args:
            db: Database session
            batch_size: Number of records to process per batch
            
        Returns:
            Dictionary with counts of processed and failed records
        """
        processed = 0
        failed = 0
        
        try:
            # Get all user profiles in batches
            offset = 0
            while True:
                profiles = db.query(UserProfile).offset(offset).limit(batch_size).all()
                if not profiles:
                    break
                
                for profile in profiles:
                    try:
                        # Convert BYTEA to base64
                        encrypted_b64 = base64.b64encode(profile.encrypted_data).decode('utf-8')
                        
                        # Re-encrypt with new key
                        reencrypt_result = await self._reencrypt_data(encrypted_b64)
                        new_encrypted_b64 = reencrypt_result.get("encrypted_data", "")
                        
                        # Convert base64 back to bytes
                        new_encrypted_bytes = base64.b64decode(new_encrypted_b64.encode('utf-8'))
                        
                        # Update profile
                        profile.encrypted_data = new_encrypted_bytes
                        profile.updated_at = datetime.now(timezone.utc)
                        
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to re-encrypt user profile {profile.user_id}: {str(e)}")
                        failed += 1
                
                # Commit batch
                db.commit()
                offset += batch_size
                
                logger.info(f"Re-encrypted {processed} user profiles, {failed} failed")
            
            return {"processed": processed, "failed": failed}
            
        except Exception as e:
            logger.error(f"Error re-encrypting user profiles: {str(e)}")
            db.rollback()
            raise
    
    async def _reencrypt_messages(self, db: Session, batch_size: int = 100) -> Dict[str, int]:
        """
        Re-encrypt all messages
        
        Args:
            db: Database session
            batch_size: Number of records to process per batch
            
        Returns:
            Dictionary with counts of processed and failed records
        """
        processed = 0
        failed = 0
        
        try:
            # Get all messages in batches
            offset = 0
            while True:
                messages = db.query(Message).offset(offset).limit(batch_size).all()
                if not messages:
                    break
                
                for message in messages:
                    try:
                        # Convert BYTEA to base64
                        encrypted_b64 = base64.b64encode(message.encrypted_content).decode('utf-8')
                        
                        # Re-encrypt with new key
                        reencrypt_result = await self._reencrypt_data(encrypted_b64)
                        new_encrypted_b64 = reencrypt_result.get("encrypted_data", "")
                        
                        # Convert base64 back to bytes
                        new_encrypted_bytes = base64.b64decode(new_encrypted_b64.encode('utf-8'))
                        
                        # Update message
                        message.encrypted_content = new_encrypted_bytes
                        
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to re-encrypt message {message.id}: {str(e)}")
                        failed += 1
                
                # Commit batch
                db.commit()
                offset += batch_size
                
                logger.info(f"Re-encrypted {processed} messages, {failed} failed")
            
            return {"processed": processed, "failed": failed}
            
        except Exception as e:
            logger.error(f"Error re-encrypting messages: {str(e)}")
            db.rollback()
            raise
    
    async def _reencrypt_sync_queue(self, db: Session, batch_size: int = 100) -> Dict[str, int]:
        """
        Re-encrypt all sync queue entries
        
        Args:
            db: Database session
            batch_size: Number of records to process per batch
            
        Returns:
            Dictionary with counts of processed and failed records
        """
        processed = 0
        failed = 0
        
        try:
            # Get all sync queue entries in batches
            offset = 0
            while True:
                sync_entries = db.query(SyncQueue).offset(offset).limit(batch_size).all()
                if not sync_entries:
                    break
                
                for sync_entry in sync_entries:
                    try:
                        # Convert BYTEA to base64
                        encrypted_b64 = base64.b64encode(sync_entry.encrypted_data).decode('utf-8')
                        
                        # Re-encrypt with new key
                        reencrypt_result = await self._reencrypt_data(encrypted_b64)
                        new_encrypted_b64 = reencrypt_result.get("encrypted_data", "")
                        
                        # Convert base64 back to bytes
                        new_encrypted_bytes = base64.b64decode(new_encrypted_b64.encode('utf-8'))
                        
                        # Update sync entry
                        sync_entry.encrypted_data = new_encrypted_bytes
                        
                        processed += 1
                    except Exception as e:
                        logger.error(f"Failed to re-encrypt sync queue entry {sync_entry.id}: {str(e)}")
                        failed += 1
                
                # Commit batch
                db.commit()
                offset += batch_size
                
                logger.info(f"Re-encrypted {processed} sync queue entries, {failed} failed")
            
            return {"processed": processed, "failed": failed}
            
        except Exception as e:
            logger.error(f"Error re-encrypting sync queue: {str(e)}")
            db.rollback()
            raise
    
    async def rotate_key_and_reencrypt_data(
        self,
        db: Session,
        admin_token: str,
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Rotate encryption key and re-encrypt all existing data
        
        This is a critical operation that:
        1. Rotates the master encryption key
        2. Re-encrypts all data in user_profiles, messages, and sync_queue tables
        3. Handles errors with rollback capability
        
        Args:
            db: Database session
            admin_token: Admin authentication token for key rotation
            batch_size: Number of records to process per batch
            
        Returns:
            Dictionary with rotation status and re-encryption results
        """
        try:
            # Step 1: Rotate the encryption key
            logger.info("Starting key rotation...")
            rotate_response = await self.client.post(
                f"{self.encryption_service_url}/rotate-key",
                json={"admin_token": admin_token}
            )
            rotate_response.raise_for_status()
            rotation_result = rotate_response.json()
            
            if not rotation_result.get("success"):
                raise Exception("Key rotation failed")
            
            rotation_record = rotation_result.get("rotation_record", {})
            logger.info(f"Key rotated successfully: {rotation_record.get('timestamp')}")
            
            # Step 2: Re-encrypt all data in batches
            logger.info("Starting data re-encryption...")
            
            try:
                # Re-encrypt user profiles
                profile_results = await self._reencrypt_user_profiles(db, batch_size)
                
                # Re-encrypt messages
                message_results = await self._reencrypt_messages(db, batch_size)
                
                # Re-encrypt sync queue
                sync_results = await self._reencrypt_sync_queue(db, batch_size)
            finally:
                # Clear old key from encryption service after re-encryption
                try:
                    clear_response = await self.client.post(
                        f"{self.encryption_service_url}/clear-old-key",
                        json={}
                    )
                    clear_response.raise_for_status()
                except Exception as e:
                    logger.warning(f"Failed to clear old key: {str(e)}")
            
            # Calculate totals
            total_processed = (
                profile_results["processed"] +
                message_results["processed"] +
                sync_results["processed"]
            )
            total_failed = (
                profile_results["failed"] +
                message_results["failed"] +
                sync_results["failed"]
            )
            
            result = {
                "success": True,
                "rotation_record": rotation_record,
                "reencryption_results": {
                    "user_profiles": profile_results,
                    "messages": message_results,
                    "sync_queue": sync_results,
                    "total_processed": total_processed,
                    "total_failed": total_failed
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if total_failed > 0:
                logger.warning(f"Key rotation completed with {total_failed} failures")
            else:
                logger.info(f"Key rotation completed successfully: {total_processed} records re-encrypted")
            
            return result
            
        except Exception as e:
            logger.error(f"Key rotation and re-encryption failed: {str(e)}")
            db.rollback()
            raise
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global service instance
_encrypted_storage_service: Optional[EncryptedStorageService] = None


def get_encrypted_storage_service() -> EncryptedStorageService:
    """Get or create encrypted storage service instance"""
    global _encrypted_storage_service
    if _encrypted_storage_service is None:
        _encrypted_storage_service = EncryptedStorageService()
    return _encrypted_storage_service

