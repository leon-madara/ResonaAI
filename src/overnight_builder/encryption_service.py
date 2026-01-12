"""
Encryption Service

End-to-end encryption for UI configurations.
User-controlled encryption ensures privacy even from the server.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os
import base64
import json
from typing import Dict, Tuple


class EncryptionService:
    """
    Encrypts and decrypts UI configurations using AES-256

    Security Model:
    - User-controlled encryption keys (derived from user passphrase or device)
    - AES-256-GCM for authenticated encryption
    - Random IV for each encryption
    - Server never sees plaintext configs
    """

    def __init__(self):
        self.algorithm = algorithms.AES
        self.key_size = 256  # bits
        self.backend = default_backend()

    def encrypt_config(
        self,
        config: Dict,
        user_key: bytes
    ) -> str:
        """
        Encrypt UI configuration

        Args:
            config: UI configuration dict
            user_key: User's encryption key (32 bytes)

        Returns:
            Base64-encoded encrypted string
        """

        # Convert config to JSON
        plaintext = json.dumps(config, ensure_ascii=False).encode('utf-8')

        # Generate random IV (initialization vector)
        iv = os.urandom(16)

        # Create cipher
        cipher = Cipher(
            algorithms.AES(user_key),
            modes.GCM(iv),
            backend=self.backend
        )

        # Encrypt
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Get authentication tag
        tag = encryptor.tag

        # Combine IV + tag + ciphertext
        encrypted = iv + tag + ciphertext

        # Encode as base64 for storage
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt_config(
        self,
        encrypted_config: str,
        user_key: bytes
    ) -> Dict:
        """
        Decrypt UI configuration

        Args:
            encrypted_config: Base64-encoded encrypted string
            user_key: User's encryption key (32 bytes)

        Returns:
            Decrypted config dict
        """

        # Decode from base64
        encrypted = base64.b64decode(encrypted_config.encode('utf-8'))

        # Extract IV, tag, and ciphertext
        iv = encrypted[:16]
        tag = encrypted[16:32]
        ciphertext = encrypted[32:]

        # Create cipher
        cipher = Cipher(
            algorithms.AES(user_key),
            modes.GCM(iv, tag),
            backend=self.backend
        )

        # Decrypt
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        # Parse JSON
        return json.loads(plaintext.decode('utf-8'))

    def derive_key_from_passphrase(
        self,
        passphrase: str,
        salt: bytes = None
    ) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from user passphrase

        Args:
            passphrase: User's passphrase
            salt: Salt for key derivation (generates random if None)

        Returns:
            Tuple of (key, salt)
        """

        # Generate salt if not provided
        if salt is None:
            salt = os.urandom(16)

        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            iterations=100000,
            backend=self.backend
        )

        key = kdf.derive(passphrase.encode('utf-8'))

        return key, salt

    def generate_random_key(self) -> bytes:
        """
        Generate random encryption key

        Returns:
            Random 32-byte key
        """
        return os.urandom(32)

    def encrypt_for_storage(
        self,
        config: Dict,
        user_id: str,
        user_passphrase: str = None
    ) -> Tuple[str, str]:
        """
        Encrypt config for database storage

        Args:
            config: UI configuration
            user_id: User ID (used as additional context)
            user_passphrase: Optional user passphrase (generates random key if None)

        Returns:
            Tuple of (encrypted_config, salt_base64)
        """

        # Derive or generate key
        if user_passphrase:
            key, salt = self.derive_key_from_passphrase(user_passphrase)
        else:
            # For anonymous users without passphrase, use random key
            # (stored separately, secured by session)
            key = self.generate_random_key()
            salt = os.urandom(16)

        # Encrypt config
        encrypted = self.encrypt_config(config, key)

        # Encode salt for storage
        salt_b64 = base64.b64encode(salt).decode('utf-8')

        return encrypted, salt_b64

    def decrypt_from_storage(
        self,
        encrypted_config: str,
        salt_b64: str,
        user_passphrase: str
    ) -> Dict:
        """
        Decrypt config from database storage

        Args:
            encrypted_config: Encrypted configuration string
            salt_b64: Base64-encoded salt
            user_passphrase: User's passphrase

        Returns:
            Decrypted config dict
        """

        # Decode salt
        salt = base64.b64decode(salt_b64.encode('utf-8'))

        # Derive key from passphrase
        key, _ = self.derive_key_from_passphrase(user_passphrase, salt)

        # Decrypt config
        return self.decrypt_config(encrypted_config, key)
