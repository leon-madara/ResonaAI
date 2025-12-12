"""
Cloud Key Management Integration
Supports AWS KMS and Azure Key Vault with local fallback
"""

import os
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


class KeyManagementProvider(ABC):
    """Abstract base class for key management providers"""
    
    @abstractmethod
    async def generate_data_key(self, key_id: str) -> Dict[str, bytes]:
        """Generate a data encryption key"""
        pass
    
    @abstractmethod
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data using the KMS"""
        pass
    
    @abstractmethod
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data using the KMS"""
        pass
    
    @abstractmethod
    async def rotate_key(self, key_id: str) -> str:
        """Rotate a key (create new version)"""
        pass
    
    @abstractmethod
    async def get_key_metadata(self, key_id: str) -> Dict[str, Any]:
        """Get key metadata"""
        pass


class LocalKeyManagement(KeyManagementProvider):
    """
    Local key management fallback
    Uses file-based key storage for development and fallback scenarios
    """
    
    def __init__(self, key_directory: str = "/app/keys"):
        self.key_directory = key_directory
        os.makedirs(key_directory, exist_ok=True)
    
    async def generate_data_key(self, key_id: str) -> Dict[str, bytes]:
        """Generate a local data encryption key"""
        from cryptography.fernet import Fernet
        
        key = Fernet.generate_key()
        
        # Store key
        key_path = os.path.join(self.key_directory, f"{key_id}.key")
        with open(key_path, 'wb') as f:
            f.write(key)
        os.chmod(key_path, 0o600)
        
        return {
            "plaintext_key": key,
            "encrypted_key": key  # In local mode, no envelope encryption
        }
    
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt using local key"""
        from cryptography.fernet import Fernet
        
        key_path = os.path.join(self.key_directory, f"{key_id}.key")
        
        if not os.path.exists(key_path):
            await self.generate_data_key(key_id)
        
        with open(key_path, 'rb') as f:
            key = f.read()
        
        fernet = Fernet(key)
        return fernet.encrypt(plaintext)
    
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt using local key"""
        from cryptography.fernet import Fernet
        
        key_path = os.path.join(self.key_directory, f"{key_id}.key")
        
        if not os.path.exists(key_path):
            raise ValueError(f"Key {key_id} not found")
        
        with open(key_path, 'rb') as f:
            key = f.read()
        
        fernet = Fernet(key)
        return fernet.decrypt(ciphertext)
    
    async def rotate_key(self, key_id: str) -> str:
        """Rotate local key"""
        new_key_id = f"{key_id}_v{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        await self.generate_data_key(new_key_id)
        
        logger.info(f"Rotated key {key_id} to {new_key_id}")
        return new_key_id
    
    async def get_key_metadata(self, key_id: str) -> Dict[str, Any]:
        """Get local key metadata"""
        key_path = os.path.join(self.key_directory, f"{key_id}.key")
        
        if not os.path.exists(key_path):
            return {"exists": False}
        
        stat = os.stat(key_path)
        return {
            "exists": True,
            "key_id": key_id,
            "provider": "local",
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
        }


class AWSKMSProvider(KeyManagementProvider):
    """
    AWS Key Management Service integration
    
    Requires environment variables:
    - AWS_ACCESS_KEY_ID
    - AWS_SECRET_ACCESS_KEY
    - AWS_REGION
    - AWS_KMS_KEY_ID (CMK ARN or alias)
    """
    
    def __init__(self, region: str = None, key_id: str = None):
        self.region = region or os.getenv("AWS_REGION", "af-south-1")
        self.default_key_id = key_id or os.getenv("AWS_KMS_KEY_ID")
        self._client = None
    
    def _get_client(self):
        """Get boto3 KMS client"""
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client('kms', region_name=self.region)
            except ImportError:
                raise ImportError("boto3 is required for AWS KMS. Install with: pip install boto3")
        return self._client
    
    async def generate_data_key(self, key_id: str = None) -> Dict[str, bytes]:
        """Generate a data key using AWS KMS"""
        client = self._get_client()
        
        response = client.generate_data_key(
            KeyId=key_id or self.default_key_id,
            KeySpec='AES_256'
        )
        
        return {
            "plaintext_key": response['Plaintext'],
            "encrypted_key": response['CiphertextBlob']
        }
    
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data using AWS KMS"""
        client = self._get_client()
        
        response = client.encrypt(
            KeyId=key_id or self.default_key_id,
            Plaintext=plaintext
        )
        
        return response['CiphertextBlob']
    
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data using AWS KMS"""
        client = self._get_client()
        
        response = client.decrypt(
            CiphertextBlob=ciphertext
        )
        
        return response['Plaintext']
    
    async def rotate_key(self, key_id: str = None) -> str:
        """Enable automatic key rotation for AWS KMS key"""
        client = self._get_client()
        
        client.enable_key_rotation(
            KeyId=key_id or self.default_key_id
        )
        
        logger.info(f"Enabled automatic rotation for AWS KMS key")
        return key_id or self.default_key_id
    
    async def get_key_metadata(self, key_id: str = None) -> Dict[str, Any]:
        """Get AWS KMS key metadata"""
        client = self._get_client()
        
        response = client.describe_key(
            KeyId=key_id or self.default_key_id
        )
        
        metadata = response['KeyMetadata']
        return {
            "exists": True,
            "key_id": metadata['KeyId'],
            "arn": metadata['Arn'],
            "provider": "aws_kms",
            "key_state": metadata['KeyState'],
            "key_usage": metadata['KeyUsage'],
            "created_at": metadata['CreationDate'].isoformat() if metadata.get('CreationDate') else None,
            "rotation_enabled": metadata.get('KeyRotationEnabled', False)
        }


class AzureKeyVaultProvider(KeyManagementProvider):
    """
    Azure Key Vault integration
    
    Requires environment variables:
    - AZURE_TENANT_ID
    - AZURE_CLIENT_ID
    - AZURE_CLIENT_SECRET
    - AZURE_KEY_VAULT_URL
    """
    
    def __init__(self, vault_url: str = None):
        self.vault_url = vault_url or os.getenv("AZURE_KEY_VAULT_URL")
        self._client = None
        self._crypto_client = None
    
    def _get_client(self):
        """Get Azure Key Vault clients"""
        if self._client is None:
            try:
                from azure.identity import DefaultAzureCredential
                from azure.keyvault.keys import KeyClient
                from azure.keyvault.keys.crypto import CryptographyClient
                
                credential = DefaultAzureCredential()
                self._client = KeyClient(vault_url=self.vault_url, credential=credential)
            except ImportError:
                raise ImportError(
                    "Azure SDK is required. Install with: "
                    "pip install azure-identity azure-keyvault-keys"
                )
        return self._client
    
    def _get_crypto_client(self, key_name: str):
        """Get cryptography client for a key"""
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.keys.crypto import CryptographyClient
        
        credential = DefaultAzureCredential()
        key_client = self._get_client()
        key = key_client.get_key(key_name)
        
        return CryptographyClient(key, credential=credential)
    
    async def generate_data_key(self, key_id: str) -> Dict[str, bytes]:
        """Generate a data key using Azure Key Vault"""
        from cryptography.fernet import Fernet
        
        # Generate local key and encrypt with Azure
        local_key = Fernet.generate_key()
        encrypted_key = await self.encrypt(key_id, local_key)
        
        return {
            "plaintext_key": local_key,
            "encrypted_key": encrypted_key
        }
    
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data using Azure Key Vault"""
        from azure.keyvault.keys.crypto import EncryptionAlgorithm
        
        crypto_client = self._get_crypto_client(key_id)
        result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep_256, plaintext)
        
        return result.ciphertext
    
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data using Azure Key Vault"""
        from azure.keyvault.keys.crypto import EncryptionAlgorithm
        
        crypto_client = self._get_crypto_client(key_id)
        result = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep_256, ciphertext)
        
        return result.plaintext
    
    async def rotate_key(self, key_id: str) -> str:
        """Create a new version of an Azure Key Vault key"""
        key_client = self._get_client()
        
        # Get existing key to get its properties
        existing_key = key_client.get_key(key_id)
        
        # Create new version
        new_key = key_client.create_rsa_key(
            key_id,
            size=existing_key.key.key_size
        )
        
        logger.info(f"Created new version of Azure Key Vault key: {key_id}")
        return new_key.id
    
    async def get_key_metadata(self, key_id: str) -> Dict[str, Any]:
        """Get Azure Key Vault key metadata"""
        key_client = self._get_client()
        
        key = key_client.get_key(key_id)
        
        return {
            "exists": True,
            "key_id": key.id,
            "name": key.name,
            "provider": "azure_key_vault",
            "key_type": str(key.key_type),
            "enabled": key.properties.enabled,
            "created_at": key.properties.created_on.isoformat() if key.properties.created_on else None,
            "updated_at": key.properties.updated_on.isoformat() if key.properties.updated_on else None,
            "version": key.properties.version
        }


class KeyManagementService:
    """
    Unified key management service with fallback support
    
    Tries providers in order:
    1. AWS KMS (if configured)
    2. Azure Key Vault (if configured)
    3. Local key management (fallback)
    """
    
    def __init__(self):
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> KeyManagementProvider:
        """Initialize the appropriate KMS provider"""
        
        # Try AWS KMS
        if os.getenv("AWS_KMS_KEY_ID"):
            try:
                logger.info("Using AWS KMS for key management")
                return AWSKMSProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize AWS KMS: {e}")
        
        # Try Azure Key Vault
        if os.getenv("AZURE_KEY_VAULT_URL"):
            try:
                logger.info("Using Azure Key Vault for key management")
                return AzureKeyVaultProvider()
            except Exception as e:
                logger.warning(f"Failed to initialize Azure Key Vault: {e}")
        
        # Fallback to local
        logger.info("Using local key management (fallback)")
        return LocalKeyManagement()
    
    async def generate_data_key(self, key_id: str) -> Dict[str, bytes]:
        """Generate a data encryption key"""
        return await self.provider.generate_data_key(key_id)
    
    async def encrypt(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data"""
        return await self.provider.encrypt(key_id, plaintext)
    
    async def decrypt(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data"""
        return await self.provider.decrypt(key_id, ciphertext)
    
    async def rotate_key(self, key_id: str) -> str:
        """Rotate a key"""
        return await self.provider.rotate_key(key_id)
    
    async def get_key_metadata(self, key_id: str) -> Dict[str, Any]:
        """Get key metadata"""
        return await self.provider.get_key_metadata(key_id)
    
    def get_provider_type(self) -> str:
        """Get the current provider type"""
        if isinstance(self.provider, AWSKMSProvider):
            return "aws_kms"
        elif isinstance(self.provider, AzureKeyVaultProvider):
            return "azure_key_vault"
        else:
            return "local"


# Global instance
key_management_service = KeyManagementService()


def get_key_management_service() -> KeyManagementService:
    """Get the global key management service"""
    return key_management_service

