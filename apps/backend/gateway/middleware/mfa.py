"""
Multi-Factor Authentication (MFA) service and middleware
TOTP-based authentication using pyotp with backup codes
"""

import pyotp
import secrets
import hashlib
import logging
from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class MFAService:
    """
    Multi-Factor Authentication service using TOTP (Time-based One-Time Password)
    Provides secure 2FA with backup codes
    """
    
    # TOTP settings
    TOTP_DIGITS = 6
    TOTP_INTERVAL = 30  # seconds
    TOTP_VALID_WINDOW = 1  # Allow 1 interval before/after for clock drift
    
    # Backup codes settings
    BACKUP_CODE_LENGTH = 8
    BACKUP_CODE_COUNT = 10
    
    # MFA token settings (temporary token for MFA flow)
    MFA_TOKEN_EXPIRY_MINUTES = 5
    
    def __init__(self, issuer: str = "ResonaAI"):
        """
        Initialize MFA service
        
        Args:
            issuer: The issuer name shown in authenticator apps
        """
        self.issuer = issuer
    
    def generate_secret(self) -> str:
        """
        Generate a new TOTP secret
        
        Returns:
            Base32 encoded secret string
        """
        return pyotp.random_base32()
    
    def generate_totp(self, secret: str) -> pyotp.TOTP:
        """
        Create a TOTP instance for the given secret
        
        Args:
            secret: Base32 encoded secret
            
        Returns:
            TOTP instance
        """
        return pyotp.TOTP(
            secret,
            digits=self.TOTP_DIGITS,
            interval=self.TOTP_INTERVAL
        )
    
    def get_provisioning_uri(self, secret: str, user_email: str) -> str:
        """
        Generate provisioning URI for QR code
        
        Args:
            secret: TOTP secret
            user_email: User's email address
            
        Returns:
            otpauth:// URI for QR code generation
        """
        totp = self.generate_totp(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer
        )
    
    def verify_code(self, secret: str, code: str) -> bool:
        """
        Verify a TOTP code
        
        Args:
            secret: User's TOTP secret
            code: 6-digit code to verify
            
        Returns:
            True if code is valid
        """
        if not secret or not code:
            return False
            
        try:
            totp = self.generate_totp(secret)
            return totp.verify(code, valid_window=self.TOTP_VALID_WINDOW)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    def generate_backup_codes(self) -> List[str]:
        """
        Generate a set of backup codes
        
        Returns:
            List of backup code strings
        """
        codes = []
        for _ in range(self.BACKUP_CODE_COUNT):
            # Generate random alphanumeric code
            code = secrets.token_hex(self.BACKUP_CODE_LENGTH // 2).upper()
            codes.append(code)
        return codes
    
    def hash_backup_code(self, code: str) -> str:
        """
        Hash a backup code for storage
        
        Args:
            code: Plain text backup code
            
        Returns:
            Hashed backup code
        """
        return hashlib.sha256(code.upper().encode()).hexdigest()
    
    def verify_backup_code(self, code: str, hashed_codes: List[str]) -> Tuple[bool, int]:
        """
        Verify a backup code against stored hashes
        
        Args:
            code: Backup code to verify
            hashed_codes: List of hashed backup codes
            
        Returns:
            Tuple of (is_valid, index_if_found)
        """
        hashed_input = self.hash_backup_code(code)
        
        for i, stored_hash in enumerate(hashed_codes):
            if stored_hash == hashed_input:
                return True, i
        
        return False, -1
    
    def generate_mfa_token(self, user_id: str, secret_key: str) -> str:
        """
        Generate a temporary MFA token for the login flow
        
        Args:
            user_id: User's ID
            secret_key: JWT secret key
            
        Returns:
            Temporary MFA token
        """
        import jwt
        
        payload = {
            "user_id": user_id,
            "type": "mfa_pending",
            "exp": datetime.utcnow() + timedelta(minutes=self.MFA_TOKEN_EXPIRY_MINUTES)
        }
        
        return jwt.encode(payload, secret_key, algorithm="HS256")
    
    def verify_mfa_token(self, token: str, secret_key: str) -> Optional[str]:
        """
        Verify a temporary MFA token
        
        Args:
            token: MFA token to verify
            secret_key: JWT secret key
            
        Returns:
            User ID if valid, None otherwise
        """
        import jwt
        
        try:
            payload = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            if payload.get("type") != "mfa_pending":
                return None
            
            return payload.get("user_id")
            
        except jwt.ExpiredSignatureError:
            logger.warning("MFA token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid MFA token: {e}")
            return None
    
    def is_mfa_required_for_role(self, role: str) -> bool:
        """
        Check if MFA is required for a given role
        Based on security-policies.yaml configuration
        
        Args:
            role: User's role (admin, counselor, user, system)
            
        Returns:
            True if MFA is required
        """
        # From security-policies.yaml:
        # mfa:
        #   required_for_admins: true
        #   required_for_counselors: true
        #   required_for_users: false
        
        mfa_required_roles = {"admin", "counselor"}
        return role.lower() in mfa_required_roles


# Global MFA service instance
mfa_service = MFAService()


def get_mfa_service() -> MFAService:
    """Get the MFA service instance"""
    return mfa_service

