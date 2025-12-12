"""
Data Management models for deletion and export
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class DeletionStatus(str, Enum):
    """Status of a deletion request"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ExportStatus(str, Enum):
    """Status of a data export request"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    EXPIRED = "expired"
    FAILED = "failed"


class ExportFormat(str, Enum):
    """Available export formats"""
    JSON = "json"
    CSV = "csv"


class DeletionRequest(BaseModel):
    """Request to delete user data"""
    user_id: str = Field(..., description="User ID to delete data for")
    reason: Optional[str] = Field(default=None, description="Reason for deletion")
    immediate: bool = Field(default=False, description="Skip grace period (admin only)")
    confirm: bool = Field(default=False, description="Confirmation required")


class DeletionResponse(BaseModel):
    """Response for deletion request"""
    request_id: str
    user_id: str
    status: DeletionStatus
    scheduled_at: Optional[datetime]
    grace_period_ends: Optional[datetime]
    message: str


class DeletionStatusResponse(BaseModel):
    """Response for deletion status check"""
    request_id: str
    user_id: str
    status: DeletionStatus
    created_at: datetime
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    tables_affected: List[str]
    records_deleted: int
    can_cancel: bool


class CancelDeletionRequest(BaseModel):
    """Request to cancel a pending deletion"""
    request_id: str


class ExportRequest(BaseModel):
    """Request to export user data"""
    user_id: str = Field(..., description="User ID to export data for")
    format: ExportFormat = Field(default=ExportFormat.JSON)
    include_conversations: bool = Field(default=True)
    include_emotions: bool = Field(default=True)
    include_consents: bool = Field(default=True)
    include_baselines: bool = Field(default=True)
    include_sessions: bool = Field(default=True)
    encrypt: bool = Field(default=True, description="Encrypt the export file")


class ExportResponse(BaseModel):
    """Response for export request"""
    export_id: str
    user_id: str
    status: ExportStatus
    format: str
    estimated_size_bytes: Optional[int]
    download_url: Optional[str]
    expires_at: Optional[datetime]
    message: str


class ExportStatusResponse(BaseModel):
    """Response for export status check"""
    export_id: str
    user_id: str
    status: ExportStatus
    format: str
    created_at: datetime
    completed_at: Optional[datetime]
    download_url: Optional[str]
    expires_at: Optional[datetime]
    file_size_bytes: Optional[int]


class DataSummary(BaseModel):
    """Summary of user's data"""
    user_id: str
    created_at: datetime
    last_active: Optional[datetime]
    conversations_count: int
    messages_count: int
    consents_count: int
    baselines_count: int
    sessions_count: int
    total_records: int


class DeletionLog(BaseModel):
    """Log entry for deletion operations"""
    id: str
    user_id: str
    request_id: str
    table_name: str
    records_deleted: int
    deleted_at: datetime
    deleted_by: str  # User ID or 'system'

