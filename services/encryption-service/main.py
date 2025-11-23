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
from typing import Dict, Any, Optional
from datetime import datetime
import json

from config import settings
from models.encryption_models import EncryptionRequest, DecryptionRequest, KeyRotationRequest

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
    
    def rotate_key(self, new_key: Optional[bytes] = None) -> Dict[str, Any]:
        """Rotate encryption key"""
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
            
            logger.info("Encryption key rotated successfully")
            return rotation_record
            
        except Exception as e:
            logger.error(f"Key rotation failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Key rotation failed")
    
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

@app.post("/rotate-key")
async def rotate_key(request: KeyRotationRequest):
    """Rotate encryption key"""
    try:
        # Verify admin credentials
        if not request.admin_token or request.admin_token != settings.ADMIN_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        result = encryption_manager.rotate_key()
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
