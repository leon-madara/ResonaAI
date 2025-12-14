"""
Sync Repository
Handles database operations for sync queue
"""

import logging
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, timezone

from models.encrypted_models import SyncQueue
from services.encrypted_storage import get_encrypted_storage_service

logger = logging.getLogger(__name__)


class SyncRepository:
    """Repository for sync queue database operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.encrypted_storage = get_encrypted_storage_service()
    
    async def enqueue_operation(
        self,
        user_id: UUID,
        operation_type: str,
        operation_data: dict
    ) -> SyncQueue:
        """
        Enqueue a sync operation
        
        Args:
            user_id: User ID
            operation_type: Type of operation
            operation_data: Operation data dictionary
            
        Returns:
            SyncQueue model instance
        """
        return await self.encrypted_storage.enqueue_sync_operation(
            self.db,
            str(user_id),
            operation_type,
            operation_data
        )
    
    def get_sync_operation(self, sync_id: UUID) -> Optional[SyncQueue]:
        """Get sync operation by ID"""
        return self.db.query(SyncQueue).filter(SyncQueue.id == sync_id).first()
    
    def get_pending_operations(
        self,
        limit: int = 100
    ) -> List[SyncQueue]:
        """
        Get pending sync operations
        
        Args:
            limit: Maximum number of operations
            
        Returns:
            List of pending SyncQueue instances
        """
        return (
            self.db.query(SyncQueue)
            .filter(SyncQueue.status == 'pending')
            .order_by(SyncQueue.created_at)
            .limit(limit)
            .all()
        )
    
    def get_user_operations(
        self,
        user_id: UUID,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[SyncQueue]:
        """
        Get user's sync operations
        
        Args:
            user_id: User ID
            status: Optional status filter
            limit: Maximum number of operations
            
        Returns:
            List of SyncQueue instances
        """
        query = self.db.query(SyncQueue).filter(SyncQueue.user_id == user_id)
        
        if status:
            query = query.filter(SyncQueue.status == status)
        
        return query.order_by(desc(SyncQueue.created_at)).limit(limit).all()
    
    def mark_processing(self, sync_id: UUID) -> bool:
        """
        Mark sync operation as processing
        
        Args:
            sync_id: Sync operation ID
            
        Returns:
            True if successful
        """
        sync_op = self.get_sync_operation(sync_id)
        if not sync_op:
            return False
        
        sync_op.status = 'processing'
        sync_op.processed_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    def mark_completed(self, sync_id: UUID) -> bool:
        """
        Mark sync operation as completed
        
        Args:
            sync_id: Sync operation ID
            
        Returns:
            True if successful
        """
        sync_op = self.get_sync_operation(sync_id)
        if not sync_op:
            return False
        
        sync_op.status = 'completed'
        sync_op.processed_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    def mark_failed(self, sync_id: UUID) -> bool:
        """
        Mark sync operation as failed
        
        Args:
            sync_id: Sync operation ID
            
        Returns:
            True if successful
        """
        sync_op = self.get_sync_operation(sync_id)
        if not sync_op:
            return False
        
        sync_op.status = 'failed'
        sync_op.retry_count += 1
        sync_op.processed_at = datetime.now(timezone.utc)
        self.db.commit()
        return True
    
    async def get_operation_data(self, sync_id: UUID) -> Optional[dict]:
        """
        Get and decrypt operation data
        
        Args:
            sync_id: Sync operation ID
            
        Returns:
            Decrypted operation data dictionary or None
        """
        try:
            return await self.encrypted_storage.get_sync_operation(self.db, str(sync_id))
        except Exception as e:
            logger.error(f"Failed to decrypt sync operation {sync_id}: {e}")
            return None

