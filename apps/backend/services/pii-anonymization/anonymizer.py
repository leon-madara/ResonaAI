"""
PII Anonymization core logic
Implements detection, anonymization, and tokenization
"""

import re
import hashlib
import secrets
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from config import PII_PATTERNS, ANONYMIZATION_METHODS
from models import PIIDetection, AnonymizationMethod

logger = logging.getLogger(__name__)


class PIIAnonymizer:
    """
    PII (Personally Identifiable Information) Anonymizer
    Detects and anonymizes sensitive data in text
    """
    
    def __init__(self):
        """Initialize the anonymizer with compiled patterns"""
        self.patterns = {}
        self._compile_patterns()
        
        # Token storage for reversible anonymization
        self.token_store: Dict[str, Dict[str, str]] = {}
    
    def _compile_patterns(self):
        """Compile regex patterns for efficiency"""
        for pii_type, config in PII_PATTERNS.items():
            try:
                self.patterns[pii_type] = {
                    "regex": re.compile(config["pattern"]),
                    "description": config["description"]
                }
            except re.error as e:
                logger.error(f"Failed to compile pattern for {pii_type}: {e}")
    
    def detect_pii(
        self,
        text: str,
        pii_types: Optional[List[str]] = None
    ) -> List[PIIDetection]:
        """
        Detect PII in text
        
        Args:
            text: Text to scan
            pii_types: Specific PII types to detect (None for all)
            
        Returns:
            List of PIIDetection objects
        """
        detections = []
        
        patterns_to_check = self.patterns
        if pii_types:
            patterns_to_check = {
                k: v for k, v in self.patterns.items()
                if k in pii_types
            }
        
        for pii_type, config in patterns_to_check.items():
            regex = config["regex"]
            
            for match in regex.finditer(text):
                detection = PIIDetection(
                    pii_type=pii_type,
                    value=match.group(),
                    start_index=match.start(),
                    end_index=match.end(),
                    confidence=1.0
                )
                detections.append(detection)
        
        # Sort by start index
        detections.sort(key=lambda x: x.start_index)
        
        return detections
    
    def _generate_token(self, value: str, user_id: Optional[str] = None) -> str:
        """
        Generate a unique token for a value
        
        Args:
            value: Value to tokenize
            user_id: Optional user ID for user-specific tokens
            
        Returns:
            Token string
        """
        # Use a combination of random token and hash for uniqueness
        random_part = secrets.token_hex(4)
        hash_part = hashlib.sha256(value.encode()).hexdigest()[:8]
        
        token = f"[PII_{random_part}_{hash_part}]"
        
        return token
    
    def _hash_value(self, value: str, salt: str = "") -> str:
        """
        Hash a value for irreversible anonymization
        
        Args:
            value: Value to hash
            salt: Optional salt
            
        Returns:
            Hash string
        """
        salted = f"{salt}{value}"
        return f"[HASH_{hashlib.sha256(salted.encode()).hexdigest()[:16]}]"
    
    def _mask_value(self, value: str, pii_type: str, preserve_format: bool = True) -> str:
        """
        Mask a value
        
        Args:
            value: Value to mask
            pii_type: Type of PII
            preserve_format: Whether to preserve format
            
        Returns:
            Masked string
        """
        if not preserve_format:
            return f"[{pii_type.upper()}]"
        
        # Type-specific masking
        if pii_type == "email":
            # Mask email: j***@g***.com
            parts = value.split("@")
            if len(parts) == 2:
                local = parts[0][0] + "***"
                domain_parts = parts[1].split(".")
                domain = domain_parts[0][0] + "***." + domain_parts[-1]
                return f"{local}@{domain}"
        
        elif pii_type in ("phone", "phone_local"):
            # Mask phone: +254***XXX
            if len(value) >= 4:
                return value[:3] + "*" * (len(value) - 6) + value[-3:]
        
        elif pii_type == "credit_card":
            # Mask credit card: ****-****-****-1234
            return "**** **** **** " + value[-4:]
        
        elif pii_type == "ssn":
            # Mask SSN: ***-**-1234
            return "***-**-" + value[-4:]
        
        elif pii_type == "ip_address":
            # Mask IP: 192.168.***.***
            parts = value.split(".")
            if len(parts) == 4:
                return f"{parts[0]}.{parts[1]}.***.***"
        
        # Default masking
        if len(value) <= 3:
            return "*" * len(value)
        
        return value[0] + "*" * (len(value) - 2) + value[-1]
    
    def _redact_value(self, pii_type: str) -> str:
        """
        Redact a value completely
        
        Args:
            pii_type: Type of PII
            
        Returns:
            Redaction placeholder
        """
        return f"[{pii_type.upper()}_REDACTED]"
    
    def anonymize(
        self,
        text: str,
        method: AnonymizationMethod = AnonymizationMethod.MASKING,
        pii_types: Optional[List[str]] = None,
        preserve_format: bool = True,
        user_id: Optional[str] = None
    ) -> Tuple[str, List[PIIDetection], Optional[Dict[str, str]]]:
        """
        Anonymize PII in text
        
        Args:
            text: Text to anonymize
            method: Anonymization method
            pii_types: Specific PII types to detect
            preserve_format: Whether to preserve format in masking
            user_id: User ID for tokenization
            
        Returns:
            Tuple of (anonymized_text, detections, token_mappings)
        """
        # Detect PII
        detections = self.detect_pii(text, pii_types)
        
        if not detections:
            return text, [], None
        
        tokens = {} if method == AnonymizationMethod.TOKENIZATION else None
        
        # Process in reverse order to maintain indices
        anonymized = text
        for detection in reversed(detections):
            value = detection.value
            pii_type = detection.pii_type
            
            if method == AnonymizationMethod.TOKENIZATION:
                replacement = self._generate_token(value, user_id)
                tokens[replacement] = value
            elif method == AnonymizationMethod.HASHING:
                replacement = self._hash_value(value, user_id or "")
            elif method == AnonymizationMethod.MASKING:
                replacement = self._mask_value(value, pii_type, preserve_format)
            elif method == AnonymizationMethod.REDACTION:
                replacement = self._redact_value(pii_type)
            else:
                replacement = self._mask_value(value, pii_type, preserve_format)
            
            anonymized = (
                anonymized[:detection.start_index] +
                replacement +
                anonymized[detection.end_index:]
            )
        
        return anonymized, detections, tokens
    
    def deanonymize(
        self,
        text: str,
        tokens: Dict[str, str]
    ) -> Tuple[str, int]:
        """
        Reverse tokenization to restore original values
        
        Args:
            text: Anonymized text
            tokens: Token to value mappings
            
        Returns:
            Tuple of (original_text, tokens_replaced)
        """
        result = text
        tokens_replaced = 0
        
        for token, value in tokens.items():
            if token in result:
                result = result.replace(token, value)
                tokens_replaced += 1
        
        return result, tokens_replaced
    
    def anonymize_for_external_api(
        self,
        text: str,
        api_name: str = "openai"
    ) -> Tuple[str, Dict[str, str]]:
        """
        Anonymize text for sending to external APIs
        Uses tokenization for later restoration
        
        Args:
            text: Text to anonymize
            api_name: Name of external API (for logging)
            
        Returns:
            Tuple of (anonymized_text, token_mappings)
        """
        anonymized, detections, tokens = self.anonymize(
            text,
            method=AnonymizationMethod.TOKENIZATION,
            preserve_format=False
        )
        
        if detections:
            logger.info(
                f"Anonymized {len(detections)} PII instances before sending to {api_name}"
            )
        
        return anonymized, tokens or {}
    
    def restore_from_external_api(
        self,
        text: str,
        tokens: Dict[str, str]
    ) -> str:
        """
        Restore anonymized text from external API response
        
        Args:
            text: Response text with tokens
            tokens: Token mappings from original request
            
        Returns:
            Restored text
        """
        restored, count = self.deanonymize(text, tokens)
        
        if count > 0:
            logger.info(f"Restored {count} PII instances from external API response")
        
        return restored


# Global anonymizer instance
pii_anonymizer = PIIAnonymizer()


def get_anonymizer() -> PIIAnonymizer:
    """Get the global anonymizer instance"""
    return pii_anonymizer

