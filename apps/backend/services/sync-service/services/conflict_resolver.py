"""
Conflict resolution for sync service.

Default policy (documented here to keep the service self-contained):
- **conversation_sync**:
  - Insert-only per message ID (idempotent). If a message ID already exists, we do not overwrite content.
  - Rationale: messages are append-only; overwriting can corrupt history.
- **emotion_data_sync**:
  - Insert-only (idempotent via dedupe key). Do not overwrite existing emotion_history records.
- **baseline_update**:
  - Last-write-wins by `updated_at` / `timestamp` when present; otherwise keep remote.
  - Rationale: baseline is a mutable aggregate; most recent update should win.
- **user_preference_sync**:
  - Last-write-wins by `updated_at` / `timestamp` when present; otherwise keep remote.

If clients need different behavior, they can pass a different `strategy` in payload
and/or `user_preference` to override within the supported set.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Resolve conflicts in sync operations"""
    
    def __init__(self):
        """Initialize conflict resolver"""
        self.strategies = {
            "last_write_wins": self._last_write_wins,
            "timestamp_based": self._timestamp_based,
            "user_preference": self._user_preference,
        }
    
    def resolve(
        self,
        local_data: Dict[str, Any],
        remote_data: Dict[str, Any],
        strategy: str = "last_write_wins",
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resolve conflict between local and remote data.
        
        Args:
            local_data: Local version of data
            remote_data: Remote version of data
            strategy: Resolution strategy
            user_preference: Optional user preference
            
        Returns:
            Resolved data
        """
        if strategy not in self.strategies:
            logger.warning(f"Unknown strategy {strategy}, using last_write_wins")
            strategy = "last_write_wins"
        
        resolver = self.strategies[strategy]
        return resolver(local_data, remote_data, user_preference)
    
    def _last_write_wins(
        self,
        local_data: Dict[str, Any],
        remote_data: Dict[str, Any],
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Last write wins strategy"""
        local_timestamp = local_data.get("updated_at") or local_data.get("timestamp")
        remote_timestamp = remote_data.get("updated_at") or remote_data.get("timestamp")
        
        if local_timestamp and remote_timestamp:
            # Compare timestamps
            if isinstance(local_timestamp, str):
                local_ts = datetime.fromisoformat(local_timestamp.replace('Z', '+00:00'))
            else:
                local_ts = local_timestamp
            
            if isinstance(remote_timestamp, str):
                remote_ts = datetime.fromisoformat(remote_timestamp.replace('Z', '+00:00'))
            else:
                remote_ts = remote_timestamp
            
            return remote_data if remote_ts > local_ts else local_data
        
        # Default to remote if timestamps unavailable
        return remote_data
    
    def _timestamp_based(
        self,
        local_data: Dict[str, Any],
        remote_data: Dict[str, Any],
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """Timestamp-based resolution (same as last_write_wins)"""
        return self._last_write_wins(local_data, remote_data, user_preference)
    
    def _user_preference(
        self,
        local_data: Dict[str, Any],
        remote_data: Dict[str, Any],
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """User preference-based resolution"""
        if user_preference == "local":
            return local_data
        elif user_preference == "remote":
            return remote_data
        else:
            # Fallback to last_write_wins
            return self._last_write_wins(local_data, remote_data, user_preference)


# Global instance
_conflict_resolver: Optional[ConflictResolver] = None


def get_conflict_resolver() -> ConflictResolver:
    """Get or create conflict resolver instance"""
    global _conflict_resolver
    if _conflict_resolver is None:
        _conflict_resolver = ConflictResolver()
    return _conflict_resolver

