"""
Encryption Service for Mental Health Platform
Centralized encryption/decryption for sensitive data
"""

from fastapi import FastAPI, HTTPException
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import logging
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
import json

from config import settings
from models.encryption_models import (
    EncryptionRequest, DecryptionRequest, KeyRotationRequest,
    BatchEncryptRequest, BatchDecryptRequest, ReEncryptRequest
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Encryption Service",
    description="Centralized encryption/decryption service for sensitive data",
    version="1.0.0"
)

class EncryptionManager:
    """Manages encryption keys and operations"""
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)
        self.key_rotation_schedule = {}
    
    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        key_file = settings.MASTER_KEY_FILE
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            
            # Save key securely
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Set secure permissions
            os.chmod(key_file, 0o600)
            
            logger.info("Generated new master encryption key")
            return key
    
    def encrypt_data(self, data: str, key_id: Optional[str] = None) -> Dict[str, Any]:
        """Encrypt sensitive data"""
        try:
            # Convert string to bytes
            data_bytes = data.encode('utf-8')
            
            # Encrypt data
            encrypted_data = self.fernet.encrypt(data_bytes)
            
            # Encode for storage
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            return {
                "encrypted_data": encrypted_b64,
                "key_id": key_id or "default",
                "algorithm": "AES-256",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Encryption failed")
    
    def decrypt_data(self, encrypted_data: str, key_id: Optional[str] = None) -> str:
        """Decrypt sensitive data"""
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt data
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            
            # Convert back to string
            decrypted_data = decrypted_bytes.decode('utf-8')
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Decryption failed")
    
    def rotate_key(self, new_key: Optional[bytes] = None, keep_old_key: bool = False) -> Dict[str, Any]:
        """
        Rotate encryption key
        
        Args:
            new_key: New encryption key (generates new if None)
            keep_old_key: If True, keeps old key accessible for re-encryption
            
        Returns:
            Rotation record with old_key if keep_old_key=True
        """
        try:
            old_key = self.master_key
            
            if new_key is None:
                new_key = Fernet.generate_key()
            
            # Update encryption manager
            self.master_key = new_key
            self.fernet = Fernet(self.master_key)
            
            # Save new key
            with open(settings.MASTER_KEY_FILE, 'wb') as f:
                f.write(new_key)
            
            # Record rotation
            rotation_record = {
                "old_key_hash": hashlib.sha256(old_key).hexdigest(),
                "new_key_hash": hashlib.sha256(new_key).hexdigest(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Store old key temporarily if needed for re-encryption
            if keep_old_key:
                rotation_record["old_key"] = base64.b64encode(old_key).decode('utf-8')
                # Store old key temporarily (will be cleared after re-encryption)
                self._old_key = old_key
            else:
                self._old_key = None
            
            logger.info("Encryption key rotated successfully")
            return rotation_record
            
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Key rotation failed")
    
    def get_old_key(self) -> Optional[bytes]:
        """Get the old key if it was kept during rotation"""
        return getattr(self, '_old_key', None)
    
    def clear_old_key(self):
        """Clear the old key after re-encryption is complete"""
        if hasattr(self, '_old_key'):
            delattr(self, '_old_key')
    
    def generate_user_key(self, user_id: str, password: str) -> bytes:
        """Generate user-specific encryption key"""
        try:
            # Use PBKDF2 to derive key from password
            salt = user_id.encode('utf-8')  # Use user ID as salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
            return key
            
        except Exception as e:
            logger.error(f"User key generation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="User key generation failed")
    
    def reencrypt_data(
        self,
        encrypted_data: str,
        old_key: Optional[bytes] = None,
        new_key: Optional[bytes] = None
    ) -> Dict[str, Any]:
        """
        Re-encrypt data with a new key
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            old_key: Old encryption key (uses stored old key or current key if None)
            new_key: New encryption key (uses current master key if None)
            
        Returns:
            Re-encrypted data result
        """
        try:
            # Use stored old key if available, otherwise use current key
            if old_key is None:
                old_key = self.get_old_key() or self.master_key
            
            # Use current master key as new key if not provided
            if new_key is None:
                new_key = self.master_key
            
            # Create Fernet instances
            old_fernet = Fernet(old_key)
            new_fernet = Fernet(new_key)
            
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Decrypt with old key
            decrypted_bytes = old_fernet.decrypt(encrypted_bytes)
            
            # Encrypt with new key
            reencrypted_data = new_fernet.encrypt(decrypted_bytes)
            
            # Encode for storage
            reencrypted_b64 = base64.b64encode(reencrypted_data).decode('utf-8')
            
            return {
                "encrypted_data": reencrypted_b64,
                "algorithm": "AES-256",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Re-encryption failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Re-encryption failed")

# Initialize encryption manager
encryption_manager = EncryptionManager()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "encryption-service"
    }

@app.post("/encrypt")
async def encrypt_data(request: EncryptionRequest):
    """Encrypt sensitive data"""
    try:
        result = encryption_manager.encrypt_data(
            data=request.data,
            key_id=request.key_id
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Encryption request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Encryption request failed")

@app.post("/decrypt")
async def decrypt_data(request: DecryptionRequest):
    """Decrypt sensitive data"""
    try:
        decrypted_data = encryption_manager.decrypt_data(
            encrypted_data=request.encrypted_data,
            key_id=request.key_id
        )
        
        return {
            "success": True,
            "data": decrypted_data
        }
        
    except Exception as e:
        logger.error(f"Decryption request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Decryption request failed")

@app.post("/re-encrypt")
async def reencrypt_data(request: ReEncryptRequest):
    """Re-encrypt data with a new key"""
    try:
        result = encryption_manager.reencrypt_data(
            encrypted_data=request.encrypted_data,
            old_key=None,  # Uses stored old key or current master key
            new_key=None   # Uses current master key
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Re-encryption request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Re-encryption request failed")

@app.post("/clear-old-key")
async def clear_old_key():
    """Clear the old key after re-encryption is complete"""
    try:
        encryption_manager.clear_old_key()
        return {
            "success": True,
            "message": "Old key cleared"
        }
    except Exception as e:
        logger.error(f"Clear old key failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Clear old key failed")

@app.post("/rotate-key")
async def rotate_key(request: KeyRotationRequest):
    """Rotate encryption key"""
    try:
        # Verify admin credentials
        if not request.admin_token or request.admin_token != settings.ADMIN_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Keep old key for re-encryption workflow
        result = encryption_manager.rotate_key(keep_old_key=True)
        
        return {
            "success": True,
            "rotation_record": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Key rotation request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Key rotation request failed")

@app.post("/generate-user-key")
async def generate_user_key(user_id: str, password: str):
    """Generate user-specific encryption key"""
    try:
        key = encryption_manager.generate_user_key(user_id, password)
        
        return {
            "success": True,
            "key": base64.b64encode(key).decode('utf-8')
        }
        
    except Exception as e:
        logger.error(f"User key generation request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="User key generation request failed")

@app.get("/key-info")
async def get_key_info():
    """Get encryption key information (without exposing the key)"""
    return {
        "algorithm": "AES-256",
        "key_rotation_schedule": encryption_manager.key_rotation_schedule,
        "key_file_exists": os.path.exists(settings.MASTER_KEY_FILE)
    }


# ============================================
# End-to-End Message Encryption Endpoints
# ============================================

class MessageEncryptionManager:
    """
    Manages end-to-end encryption for messages
    Uses user-specific keys derived from their credentials
    """
    
    def __init__(self, base_manager: EncryptionManager):
        self.base_manager = base_manager
        self._user_keys_cache: Dict[str, bytes] = {}
    
    def get_user_fernet(self, user_id: str, user_key: bytes) -> Fernet:
        """Get Fernet instance for user-specific encryption"""
        return Fernet(user_key)
    
    def encrypt_message(
        self,
        message: str,
        user_id: str,
        user_key: bytes,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Encrypt a message with user-specific key
        
        Args:
            message: Plain text message
            user_id: User ID
            user_key: User's derived encryption key
            conversation_id: Optional conversation ID
            
        Returns:
            Encrypted message data
        """
        try:
            fernet = self.get_user_fernet(user_id, user_key)
            
            # Create message envelope
            envelope = {
                "content": message,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "conversation_id": conversation_id
            }
            
            # Encrypt envelope
            envelope_json = json.dumps(envelope)
            encrypted_data = fernet.encrypt(envelope_json.encode('utf-8'))
            encrypted_b64 = base64.b64encode(encrypted_data).decode('utf-8')
            
            return {
                "encrypted_content": encrypted_b64,
                "algorithm": "AES-256-Fernet",
                "key_id": f"user:{user_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Message encryption failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Message encryption failed")
    
    def decrypt_message(
        self,
        encrypted_content: str,
        user_id: str,
        user_key: bytes
    ) -> Dict[str, Any]:
        """
        Decrypt a message with user-specific key
        
        Args:
            encrypted_content: Base64 encoded encrypted data
            user_id: User ID
            user_key: User's derived encryption key
            
        Returns:
            Decrypted message envelope
        """
        try:
            fernet = self.get_user_fernet(user_id, user_key)
            
            # Decrypt
            encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
            decrypted_bytes = fernet.decrypt(encrypted_bytes)
            
            # Parse envelope
            envelope = json.loads(decrypted_bytes.decode('utf-8'))
            
            return envelope
            
        except Exception as e:
            logger.error(f"Message decryption failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Message decryption failed")
    
    def reencrypt_message(
        self,
        encrypted_content: str,
        old_user_key: bytes,
        new_user_key: bytes,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Re-encrypt a message with a new key (for key rotation)
        
        Args:
            encrypted_content: Currently encrypted content
            old_user_key: Old encryption key
            new_user_key: New encryption key
            user_id: User ID
            
        Returns:
            Re-encrypted message data
        """
        try:
            # Decrypt with old key
            envelope = self.decrypt_message(encrypted_content, user_id, old_user_key)
            
            # Re-encrypt with new key
            return self.encrypt_message(
                envelope["content"],
                user_id,
                new_user_key,
                envelope.get("conversation_id")
            )
            
        except Exception as e:
            logger.error(f"Message re-encryption failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Message re-encryption failed")


# Initialize message encryption manager
message_encryption_manager = MessageEncryptionManager(encryption_manager)


@app.post("/e2e/encrypt-message")
async def encrypt_message(
    message: str,
    user_id: str,
    password: str,
    conversation_id: Optional[str] = None
):
    """
    Encrypt a message with end-to-end encryption
    
    The message is encrypted with a key derived from the user's password.
    Only the user with the correct password can decrypt it.
    """
    try:
        # Generate user key from password
        user_key = encryption_manager.generate_user_key(user_id, password)
        
        # Encrypt message
        result = message_encryption_manager.encrypt_message(
            message=message,
            user_id=user_id,
            user_key=user_key,
            conversation_id=conversation_id
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"E2E message encryption failed: {str(e)}")
        raise HTTPException(status_code=500, detail="E2E message encryption failed")


@app.post("/e2e/decrypt-message")
async def decrypt_message(
    encrypted_content: str,
    user_id: str,
    password: str
):
    """
    Decrypt an end-to-end encrypted message
    
    Requires the user's password to derive the decryption key.
    """
    try:
        # Generate user key from password
        user_key = encryption_manager.generate_user_key(user_id, password)
        
        # Decrypt message
        envelope = message_encryption_manager.decrypt_message(
            encrypted_content=encrypted_content,
            user_id=user_id,
            user_key=user_key
        )
        
        return {
            "success": True,
            "message": envelope["content"],
            "timestamp": envelope.get("timestamp"),
            "conversation_id": envelope.get("conversation_id")
        }
        
    except Exception as e:
        logger.error(f"E2E message decryption failed: {str(e)}")
        raise HTTPException(status_code=500, detail="E2E message decryption failed")


@app.post("/e2e/batch-encrypt")
async def batch_encrypt_messages(request: BatchEncryptRequest):
    """Encrypt multiple messages at once"""
    try:
        user_key = encryption_manager.generate_user_key(request.user_id, request.password)
        
        results = []
        for message in request.messages:
            result = message_encryption_manager.encrypt_message(
                message=message,
                user_id=request.user_id,
                user_key=user_key,
                conversation_id=request.conversation_id
            )
            results.append(result)
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch encryption failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch encryption failed")


@app.post("/e2e/batch-decrypt")
async def batch_decrypt_messages(request: BatchDecryptRequest):
    """Decrypt multiple messages at once"""
    try:
        user_key = encryption_manager.generate_user_key(request.user_id, request.password)
        
        results = []
        for encrypted_content in request.encrypted_contents:
            envelope = message_encryption_manager.decrypt_message(
                encrypted_content=encrypted_content,
                user_id=request.user_id,
                user_key=user_key
            )
            results.append({
                "message": envelope["content"],
                "timestamp": envelope.get("timestamp"),
                "conversation_id": envelope.get("conversation_id")
            })
        
        return {
            "success": True,
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Batch decryption failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Batch decryption failed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
