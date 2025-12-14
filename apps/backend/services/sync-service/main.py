"""
Sync Service
Main FastAPI application for offline data synchronization
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel
import os
import json
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from workers.sync_tasks import process_sync_operation
from services.validator import get_data_validator
from services.conflict_resolver import get_conflict_resolver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

class SyncRequest(BaseModel):
    user_id: str
    data: Dict[str, Any]
    operation_type: str

class SyncResponse(BaseModel):
    sync_id: str
    status: str
    message: str
    timestamp: datetime
    stored: bool = False
    encrypted: bool = False


def _get_env(name: str, default: str) -> str:
    """Get environment variable with default."""
    return os.getenv(name, default)


# Database wiring (simple, service-local)
DATABASE_URL = _get_env("DATABASE_URL", "postgresql://postgres:password@postgres:5432/mental_health")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _enqueue_sync_operation(user_id: str, operation_type: str, payload: Dict[str, Any]) -> str:
    """
    Enqueue an offline operation into the `sync_queue` table.

    Notes:
    - The system design expects encrypted payloads. MVP stores JSON bytes directly.
      This must be replaced with encryption-service integration before production.
    """
    sync_id = str(uuid.uuid4())
    payload_bytes = json.dumps(payload).encode("utf-8")

    db = SessionLocal()
    try:
        # Use database-agnostic SQL (works with both PostgreSQL and SQLite)
        db.execute(
            text(
                """
                INSERT INTO sync_queue (id, user_id, operation_type, encrypted_data, status, created_at, retry_count)
                VALUES (:id, :user_id, :operation_type, :encrypted_data, 'pending', CURRENT_TIMESTAMP, 0)
                """
            ),
            {
                "id": sync_id,
                "user_id": user_id,
                "operation_type": operation_type,
                "encrypted_data": payload_bytes,
            },
        )
        db.commit()
        return sync_id
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Sync Service...")
    yield
    logger.info("Shutting down Sync Service...")

app = FastAPI(title="Sync Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    # Best-effort DB ping
    db_ok = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.warning(f"DB health check failed: {e}")

    return {"status": "healthy", "service": "sync-service", "db_connected": db_ok}

@app.post("/upload", response_model=SyncResponse)
async def upload_data(
    request: SyncRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload offline data for synchronization"""
    try:
        # Validate data
        validator = get_data_validator()
        is_valid, error, warnings = validator.validate(
            user_id=request.user_id,
            operation_type=request.operation_type,
            data=request.data
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error or "Validation failed"
            )
        
        if warnings:
            logger.warning(f"Validation warnings for sync {request.user_id}: {warnings}")
        
        # Enqueue operation
        sync_id = _enqueue_sync_operation(
            user_id=request.user_id,
            operation_type=request.operation_type,
            payload=request.data,
        )
        
        # Trigger background processing
        try:
            process_sync_operation.delay(
                sync_id=sync_id,
                user_id=request.user_id,
                operation_type=request.operation_type,
                payload=request.data
            )
            logger.info(f"Sync operation {sync_id} queued for background processing")
        except Exception as e:
            logger.warning(f"Failed to queue Celery task (will process on next poll): {e}")
            # Operation is still queued in database, will be picked up by worker
        
        return SyncResponse(
            sync_id=sync_id,
            status="queued",
            message="Data queued for synchronization",
            timestamp=datetime.now(timezone.utc),
            stored=True,
            encrypted=False,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enqueue sync operation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue sync operation",
        )


@app.get("/sync/status/{sync_id}")
async def get_sync_status(
    sync_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get sync operation status"""
    db = SessionLocal()
    try:
        row = db.execute(
            text("""
                SELECT id, status, created_at, processed_at, retry_count
                FROM sync_queue
                WHERE id = :id
            """),
            {"id": sync_id}
        ).fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sync operation not found"
            )
        
        return {
            "sync_id": str(row.id),
            "status": row.status,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "processed_at": row.processed_at.isoformat() if row.processed_at else None,
            "retry_count": row.retry_count,
        }
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)

