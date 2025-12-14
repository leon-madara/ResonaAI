"""
Data integrity validation for sync service
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import json
import uuid

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate data integrity for sync operations"""
    
    def __init__(self):
        """Initialize data validator"""
        self.required_fields = {
            "conversation_sync": ["conversation_id", "messages"],
            "emotion_data_sync": ["emotion_data"],
            "baseline_update": ["baseline_data"],
            "user_preference_sync": ["preferences"],
        }
    
    def validate_structure(
        self,
        operation_type: str,
        data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate data structure.
        
        Args:
            operation_type: Type of operation
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if operation_type not in self.required_fields:
            return False, f"Unknown operation type: {operation_type}"
        
        required = self.required_fields[operation_type]
        missing = [field for field in required if field not in data]
        
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        return True, None
    
    def validate_user_permissions(
        self,
        user_id: str,
        operation_type: str,
        data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate user has permission for operation.
        
        Args:
            user_id: User ID
            operation_type: Type of operation
            data: Operation data
            
        Returns:
            Tuple of (has_permission, error_message)
        """
        # Validate UUID format (system design uses UUID user IDs).
        try:
            uuid.UUID(str(user_id))
        except Exception:
            return False, "Invalid user_id (must be a UUID)"

        # Check if user_id matches in data (if present)
        if "user_id" in data and data["user_id"] != user_id:
            return False, "User ID mismatch"
        
        # Additional permission checks can be added here
        return True, None
    
    def validate_data_consistency(
        self,
        operation_type: str,
        data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Validate data consistency.
        
        Args:
            operation_type: Type of operation
            data: Data to validate
            
        Returns:
            Tuple of (is_consistent, error_message, warnings)
        """
        warnings = []
        
        if operation_type == "conversation_sync":
            messages = data.get("messages", [])
            if not isinstance(messages, list):
                return False, "Messages must be a list", warnings
            
            # Check message structure
            for i, msg in enumerate(messages):
                if not isinstance(msg, dict):
                    warnings.append(f"Message {i} is not a dictionary")
                elif "content" not in msg:
                    warnings.append(f"Message {i} missing content")
        
        elif operation_type == "emotion_data_sync":
            emotion_data = data.get("emotion_data", [])
            if not isinstance(emotion_data, list):
                return False, "Emotion data must be a list", warnings
        
        elif operation_type == "baseline_update":
            baseline_data = data.get("baseline_data")
            if not isinstance(baseline_data, dict):
                return False, "Baseline data must be a dictionary", warnings
        
        elif operation_type == "user_preference_sync":
            preferences = data.get("preferences", {})
            if not isinstance(preferences, dict):
                return False, "Preferences must be a dictionary", warnings
        
        return True, None, warnings
    
    def validate(
        self,
        user_id: str,
        operation_type: str,
        data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], List[str]]:
        """
        Comprehensive validation.
        
        Args:
            user_id: User ID
            operation_type: Type of operation
            data: Data to validate
            
        Returns:
            Tuple of (is_valid, error_message, warnings)
        """
        # Structure validation
        is_valid, error = self.validate_structure(operation_type, data)
        if not is_valid:
            return False, error, []
        
        # Permission validation
        has_permission, error = self.validate_user_permissions(user_id, operation_type, data)
        if not has_permission:
            return False, error, []
        
        # Consistency validation
        is_consistent, error, warnings = self.validate_data_consistency(operation_type, data)
        if not is_consistent:
            return False, error, warnings
        
        return True, None, warnings


# Global instance
_data_validator: Optional[DataValidator] = None


def get_data_validator() -> DataValidator:
    """Get or create data validator instance"""
    global _data_validator
    if _data_validator is None:
        _data_validator = DataValidator()
    return _data_validator

