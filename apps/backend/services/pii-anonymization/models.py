"""
PII Anonymization models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AnonymizationMethod(str, Enum):
    """Available anonymization methods"""
    TOKENIZATION = "tokenization"
    HASHING = "hashing"
    MASKING = "masking"
    REDACTION = "redaction"


class PIIType(str, Enum):
    """Types of PII that can be detected"""
    EMAIL = "email"
    PHONE = "phone"
    PHONE_LOCAL = "phone_local"
    SSN = "ssn"
    NATIONAL_ID = "national_id_ke"
    CREDIT_CARD = "credit_card"
    IP_ADDRESS = "ip_address"
    DATE_OF_BIRTH = "date_of_birth"
    NAME = "name_pattern"
    CUSTOM = "custom"


class PIIDetection(BaseModel):
    """A detected PII instance"""
    pii_type: str
    value: str
    start_index: int
    end_index: int
    confidence: float = 1.0


class AnonymizeRequest(BaseModel):
    """Request to anonymize text"""
    text: str = Field(..., description="Text to anonymize")
    method: AnonymizationMethod = Field(default=AnonymizationMethod.MASKING, description="Anonymization method")
    pii_types: Optional[List[str]] = Field(default=None, description="Specific PII types to detect (None for all)")
    preserve_format: bool = Field(default=True, description="Preserve format for certain PII types")
    user_id: Optional[str] = Field(default=None, description="User ID for tokenization")


class AnonymizeResponse(BaseModel):
    """Response with anonymized text"""
    original_length: int
    anonymized_text: str
    pii_detected: List[PIIDetection]
    pii_count: int
    method: str
    processing_time_ms: float
    tokens: Optional[Dict[str, str]] = Field(default=None, description="Token mappings for reversible anonymization")


class DetectRequest(BaseModel):
    """Request to detect PII without anonymizing"""
    text: str = Field(..., description="Text to scan for PII")
    pii_types: Optional[List[str]] = Field(default=None, description="Specific PII types to detect")


class DetectResponse(BaseModel):
    """Response with detected PII"""
    text_length: int
    pii_detected: List[PIIDetection]
    pii_count: int
    contains_pii: bool


class DeanonymizeRequest(BaseModel):
    """Request to reverse tokenization"""
    text: str = Field(..., description="Anonymized text")
    tokens: Dict[str, str] = Field(..., description="Token mappings from original anonymization")


class DeanonymizeResponse(BaseModel):
    """Response with de-anonymized text"""
    text: str
    tokens_replaced: int


class BatchAnonymizeRequest(BaseModel):
    """Request to anonymize multiple texts"""
    texts: List[str] = Field(..., description="List of texts to anonymize")
    method: AnonymizationMethod = Field(default=AnonymizationMethod.MASKING)
    pii_types: Optional[List[str]] = None


class BatchAnonymizeResponse(BaseModel):
    """Response with batch anonymization results"""
    results: List[AnonymizeResponse]
    total_pii_count: int
    processing_time_ms: float


class AnonymizationAuditLog(BaseModel):
    """Audit log entry for anonymization operations"""
    id: str
    user_id: Optional[str]
    operation: str  # anonymize, detect, deanonymize
    pii_types_detected: List[str]
    pii_count: int
    method: str
    timestamp: datetime
    source_service: Optional[str]

