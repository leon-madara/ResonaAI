"""
Data Management Service
Handles data deletion (Right to Erasure) and data portability (Export)
GDPR and Kenya DPA compliant
"""

import json
import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import jwt

from config import settings
from models import (
    DeletionRequest, DeletionResponse, DeletionStatusResponse,
    CancelDeletionRequest, DeletionStatus,
    ExportRequest, ExportResponse, ExportStatusResponse, ExportStatus, ExportFormat,
    DataSummary
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database models for deletion and export tracking
class DeletionRequestRecord(Base):
    """Track deletion requests"""
    __tablename__ = "deletion_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    tables_affected = Column(JSONB, nullable=True)
    records_deleted = Column(Integer, default=0)
    requested_by = Column(UUID(as_uuid=True), nullable=True)


class ExportRequestRecord(Base):
    """Track export requests"""
    __tablename__ = "export_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    status = Column(String(20), nullable=False, default="pending")
    format = Column(String(10), nullable=False, default="json")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    file_path = Column(Text, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    encrypted = Column(Boolean, default=True)
    options = Column(JSONB, nullable=True)


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Data Management Service",
    description="Service for data deletion and export (GDPR/DPA compliance)",
    version="1.0.0"
)

# Security
security = HTTPBearer()


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_from_token(credentials: HTTPAuthorizationCredentials) -> Optional[str]:
    """Extract user ID from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("user_id")
    except jwt.InvalidTokenError:
        return None


def get_user_role_from_token(credentials: HTTPAuthorizationCredentials) -> str:
    """Extract user role from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload.get("role", "user")
    except jwt.InvalidTokenError:
        return "user"


# Tables to delete data from (in order of foreign key dependencies)
USER_DATA_TABLES = [
    "messages",
    "conversations",
    "consent_records",
    "user_baselines",
    "session_deviations",
    "user_interfaces",
    "risk_assessments",
    "sync_queue",
    "refresh_tokens",
    "api_keys",
    "audit_logs",
    "user_profiles",
]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "data-management"
    }


# ============================================
# Data Deletion Endpoints
# ============================================

@app.post("/deletion/request", response_model=DeletionResponse)
async def request_deletion(
    request: DeletionRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Request deletion of user data (Right to Erasure)
    
    By default, deletion is scheduled after a grace period (21 days per Kenya DPA).
    Users can cancel during this period.
    """
    try:
        requesting_user = get_user_from_token(credentials)
        user_role = get_user_role_from_token(credentials)
        
        if not requesting_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check authorization
        if request.user_id != requesting_user and user_role not in ("admin", "system"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user's data"
            )
        
        if not request.confirm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Deletion must be confirmed. Set 'confirm' to true."
            )
        
        # Calculate schedule
        grace_period_days = 0 if (request.immediate and user_role == "admin") else settings.DELETION_GRACE_PERIOD_DAYS
        scheduled_at = datetime.utcnow() + timedelta(days=grace_period_days)
        
        # Create deletion request
        deletion_record = DeletionRequestRecord(
            id=uuid.uuid4(),
            user_id=uuid.UUID(request.user_id),
            status="scheduled",
            reason=request.reason,
            scheduled_at=scheduled_at,
            requested_by=uuid.UUID(requesting_user)
        )
        
        db.add(deletion_record)
        db.commit()
        db.refresh(deletion_record)
        
        logger.info(f"Deletion request created for user {request.user_id}, scheduled for {scheduled_at}")
        
        # If immediate, process in background
        if request.immediate and user_role == "admin":
            background_tasks.add_task(process_deletion, str(deletion_record.id), db)
        
        return DeletionResponse(
            request_id=str(deletion_record.id),
            user_id=request.user_id,
            status=DeletionStatus.SCHEDULED,
            scheduled_at=scheduled_at,
            grace_period_ends=scheduled_at,
            message=f"Deletion scheduled for {scheduled_at.isoformat()}. You can cancel before this date."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deletion request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Deletion request failed"
        )


@app.get("/deletion/status/{request_id}", response_model=DeletionStatusResponse)
async def get_deletion_status(
    request_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get status of a deletion request"""
    try:
        requesting_user = get_user_from_token(credentials)
        user_role = get_user_role_from_token(credentials)
        
        deletion_record = db.query(DeletionRequestRecord).filter(
            DeletionRequestRecord.id == uuid.UUID(request_id)
        ).first()
        
        if not deletion_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deletion request not found"
            )
        
        # Check authorization
        if str(deletion_record.user_id) != requesting_user and user_role not in ("admin", "system"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this deletion request"
            )
        
        can_cancel = deletion_record.status == "scheduled" and \
                     deletion_record.scheduled_at > datetime.utcnow()
        
        return DeletionStatusResponse(
            request_id=str(deletion_record.id),
            user_id=str(deletion_record.user_id),
            status=DeletionStatus(deletion_record.status),
            created_at=deletion_record.created_at,
            scheduled_at=deletion_record.scheduled_at,
            completed_at=deletion_record.completed_at,
            tables_affected=deletion_record.tables_affected or [],
            records_deleted=deletion_record.records_deleted,
            can_cancel=can_cancel
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get deletion status failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get deletion status failed"
        )


@app.post("/deletion/cancel")
async def cancel_deletion(
    request: CancelDeletionRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Cancel a pending deletion request"""
    try:
        requesting_user = get_user_from_token(credentials)
        user_role = get_user_role_from_token(credentials)
        
        deletion_record = db.query(DeletionRequestRecord).filter(
            DeletionRequestRecord.id == uuid.UUID(request.request_id)
        ).first()
        
        if not deletion_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Deletion request not found"
            )
        
        # Check authorization
        if str(deletion_record.user_id) != requesting_user and user_role not in ("admin", "system"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to cancel this deletion request"
            )
        
        if deletion_record.status != "scheduled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel deletion with status: {deletion_record.status}"
            )
        
        if deletion_record.scheduled_at <= datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Grace period has ended. Deletion cannot be cancelled."
            )
        
        deletion_record.status = "cancelled"
        deletion_record.cancelled_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Deletion request {request.request_id} cancelled")
        
        return {"success": True, "message": "Deletion request cancelled"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cancel deletion failed"
        )


# ============================================
# Data Export Endpoints
# ============================================

@app.post("/export/request", response_model=ExportResponse)
async def request_export(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Request export of user data (Right to Data Portability)
    
    Exports data in machine-readable format (JSON or CSV).
    Download link expires after 24 hours.
    """
    try:
        requesting_user = get_user_from_token(credentials)
        user_role = get_user_role_from_token(credentials)
        
        if not requesting_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Check authorization
        if request.user_id != requesting_user and user_role not in ("admin", "system"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to export this user's data"
            )
        
        expires_at = datetime.utcnow() + timedelta(hours=settings.EXPORT_EXPIRY_HOURS)
        
        # Create export request
        export_record = ExportRequestRecord(
            id=uuid.uuid4(),
            user_id=uuid.UUID(request.user_id),
            status="pending",
            format=request.format.value,
            expires_at=expires_at,
            encrypted=request.encrypt,
            options={
                "include_conversations": request.include_conversations,
                "include_emotions": request.include_emotions,
                "include_consents": request.include_consents,
                "include_baselines": request.include_baselines,
                "include_sessions": request.include_sessions
            }
        )
        
        db.add(export_record)
        db.commit()
        db.refresh(export_record)
        
        # Process in background
        background_tasks.add_task(process_export, str(export_record.id))
        
        logger.info(f"Export request created for user {request.user_id}")
        
        return ExportResponse(
            export_id=str(export_record.id),
            user_id=request.user_id,
            status=ExportStatus.PENDING,
            format=request.format.value,
            estimated_size_bytes=None,
            download_url=None,
            expires_at=expires_at,
            message="Export request received. Processing in background."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export request failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export request failed"
        )


@app.get("/export/status/{export_id}", response_model=ExportStatusResponse)
async def get_export_status(
    export_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get status of an export request"""
    try:
        requesting_user = get_user_from_token(credentials)
        user_role = get_user_role_from_token(credentials)
        
        export_record = db.query(ExportRequestRecord).filter(
            ExportRequestRecord.id == uuid.UUID(export_id)
        ).first()
        
        if not export_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export request not found"
            )
        
        # Check authorization
        if str(export_record.user_id) != requesting_user and user_role not in ("admin", "system"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this export request"
            )
        
        download_url = None
        if export_record.status == "completed" and export_record.file_path:
            download_url = f"/export/download/{export_id}"
        
        return ExportStatusResponse(
            export_id=str(export_record.id),
            user_id=str(export_record.user_id),
            status=ExportStatus(export_record.status),
            format=export_record.format,
            created_at=export_record.created_at,
            completed_at=export_record.completed_at,
            download_url=download_url,
            expires_at=export_record.expires_at,
            file_size_bytes=export_record.file_size_bytes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get export status failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get export status failed"
        )


@app.get("/export/download/{export_id}")
async def download_export(
    export_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Download exported data file"""
    try:
        requesting_user = get_user_from_token(credentials)
        user_role = get_user_role_from_token(credentials)
        
        export_record = db.query(ExportRequestRecord).filter(
            ExportRequestRecord.id == uuid.UUID(export_id)
        ).first()
        
        if not export_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export request not found"
            )
        
        # Check authorization
        if str(export_record.user_id) != requesting_user and user_role not in ("admin", "system"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to download this export"
            )
        
        if export_record.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Export not ready. Status: {export_record.status}"
            )
        
        if export_record.expires_at and export_record.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Export has expired"
            )
        
        if not export_record.file_path or not os.path.exists(export_record.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export file not found"
            )
        
        filename = f"data_export_{export_record.user_id}.{export_record.format}"
        
        return FileResponse(
            export_record.file_path,
            filename=filename,
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download export failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Download export failed"
        )


@app.get("/data/summary/{user_id}", response_model=DataSummary)
async def get_data_summary(
    user_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get summary of user's data before deletion or export"""
    try:
        requesting_user = get_user_from_token(credentials)
        user_role = get_user_role_from_token(credentials)
        
        # Check authorization
        if user_id != requesting_user and user_role not in ("admin", "system"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this user's data"
            )
        
        # Query counts from each table
        user_uuid = uuid.UUID(user_id)
        
        # This is a simplified version - in production, query actual tables
        conversations_count = 0
        messages_count = 0
        consents_count = 0
        baselines_count = 0
        sessions_count = 0
        
        try:
            from sqlalchemy import text
            
            conversations_result = db.execute(
                text("SELECT COUNT(*) FROM conversations WHERE user_id = :uid"),
                {"uid": user_uuid}
            )
            conversations_count = conversations_result.scalar() or 0
            
            messages_result = db.execute(
                text("SELECT COUNT(*) FROM messages m JOIN conversations c ON m.conversation_id = c.id WHERE c.user_id = :uid"),
                {"uid": user_uuid}
            )
            messages_count = messages_result.scalar() or 0
            
            consents_result = db.execute(
                text("SELECT COUNT(*) FROM consent_records WHERE user_id = :uid"),
                {"uid": user_uuid}
            )
            consents_count = consents_result.scalar() or 0
            
        except Exception as e:
            logger.warning(f"Error querying data counts: {e}")
        
        total_records = conversations_count + messages_count + consents_count + baselines_count + sessions_count
        
        return DataSummary(
            user_id=user_id,
            created_at=datetime.utcnow(),  # Would get from users table
            last_active=None,
            conversations_count=conversations_count,
            messages_count=messages_count,
            consents_count=consents_count,
            baselines_count=baselines_count,
            sessions_count=sessions_count,
            total_records=total_records
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get data summary failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Get data summary failed"
        )


# ============================================
# Background Tasks
# ============================================

async def process_deletion(request_id: str, db: Session):
    """Process a deletion request (background task)"""
    try:
        deletion_record = db.query(DeletionRequestRecord).filter(
            DeletionRequestRecord.id == uuid.UUID(request_id)
        ).first()
        
        if not deletion_record:
            logger.error(f"Deletion record not found: {request_id}")
            return
        
        deletion_record.status = "in_progress"
        db.commit()
        
        user_uuid = deletion_record.user_id
        tables_affected = []
        total_deleted = 0
        
        from sqlalchemy import text
        
        # Delete from each table
        for table in USER_DATA_TABLES:
            try:
                if table == "messages":
                    # Special handling for messages (through conversations)
                    result = db.execute(
                        text(f"DELETE FROM {table} WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = :uid)"),
                        {"uid": user_uuid}
                    )
                else:
                    result = db.execute(
                        text(f"DELETE FROM {table} WHERE user_id = :uid"),
                        {"uid": user_uuid}
                    )
                
                if result.rowcount > 0:
                    tables_affected.append(table)
                    total_deleted += result.rowcount
                    
            except Exception as e:
                logger.warning(f"Error deleting from {table}: {e}")
        
        # Finally delete the user
        try:
            db.execute(
                text("DELETE FROM users WHERE id = :uid"),
                {"uid": user_uuid}
            )
            tables_affected.append("users")
            total_deleted += 1
        except Exception as e:
            logger.error(f"Error deleting user: {e}")
        
        db.commit()
        
        deletion_record.status = "completed"
        deletion_record.completed_at = datetime.utcnow()
        deletion_record.tables_affected = tables_affected
        deletion_record.records_deleted = total_deleted
        db.commit()
        
        logger.info(f"Deletion completed for user {user_uuid}: {total_deleted} records from {len(tables_affected)} tables")
        
    except Exception as e:
        logger.error(f"Deletion processing failed: {e}")
        if deletion_record:
            deletion_record.status = "failed"
            db.commit()


async def process_export(export_id: str):
    """Process an export request (background task)"""
    db = SessionLocal()
    try:
        export_record = db.query(ExportRequestRecord).filter(
            ExportRequestRecord.id == uuid.UUID(export_id)
        ).first()
        
        if not export_record:
            logger.error(f"Export record not found: {export_id}")
            return
        
        export_record.status = "processing"
        db.commit()
        
        user_uuid = export_record.user_id
        options = export_record.options or {}
        
        # Collect user data
        export_data = {
            "export_id": export_id,
            "user_id": str(user_uuid),
            "exported_at": datetime.utcnow().isoformat(),
            "format_version": "1.0"
        }
        
        from sqlalchemy import text
        
        # Export user profile
        try:
            user_result = db.execute(
                text("SELECT * FROM users WHERE id = :uid"),
                {"uid": user_uuid}
            )
            user_row = user_result.fetchone()
            if user_row:
                export_data["profile"] = dict(user_row._mapping)
                # Remove sensitive fields
                export_data["profile"].pop("password_hash", None)
                export_data["profile"].pop("mfa_secret", None)
                export_data["profile"].pop("mfa_backup_codes", None)
        except Exception as e:
            logger.warning(f"Error exporting user profile: {e}")
        
        # Export conversations and messages
        if options.get("include_conversations", True):
            try:
                conv_result = db.execute(
                    text("SELECT * FROM conversations WHERE user_id = :uid"),
                    {"uid": user_uuid}
                )
                conversations = [dict(row._mapping) for row in conv_result]
                export_data["conversations"] = conversations
            except Exception as e:
                logger.warning(f"Error exporting conversations: {e}")
        
        # Export consent records
        if options.get("include_consents", True):
            try:
                consent_result = db.execute(
                    text("SELECT * FROM consent_records WHERE user_id = :uid"),
                    {"uid": user_uuid}
                )
                consents = [dict(row._mapping) for row in consent_result]
                export_data["consents"] = consents
            except Exception as e:
                logger.warning(f"Error exporting consents: {e}")
        
        # Save to file
        os.makedirs(settings.EXPORT_STORAGE_PATH, exist_ok=True)
        file_path = os.path.join(
            settings.EXPORT_STORAGE_PATH,
            f"export_{export_id}.json"
        )
        
        # Convert datetime objects to strings for JSON serialization
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, uuid.UUID):
                return str(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=json_serializer)
        
        file_size = os.path.getsize(file_path)
        
        export_record.status = "completed"
        export_record.completed_at = datetime.utcnow()
        export_record.file_path = file_path
        export_record.file_size_bytes = file_size
        db.commit()
        
        logger.info(f"Export completed for user {user_uuid}: {file_size} bytes")
        
    except Exception as e:
        logger.error(f"Export processing failed: {e}")
        if export_record:
            export_record.status = "failed"
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )

