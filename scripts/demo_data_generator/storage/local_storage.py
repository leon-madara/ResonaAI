"""
Local Storage Manager for Demo Data Generator

This module provides local JSON file-based storage for all generated test data.
It implements the StorageInterface with methods for saving, loading, validating,
and managing structured JSON data files.
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging
from ..interfaces import StorageInterface
from ..models import ValidationResult


class LocalStorageManager(StorageInterface):
    """
    Local file-based storage manager for demo data.
    
    Manages structured JSON files for different data types including:
    - User profiles
    - Conversations
    - Cultural scenarios
    - Swahili patterns
    - Emotion data
    - Voice analysis data
    """
    
    def __init__(self, storage_path: str = "demo_data"):
        """
        Initialize local storage manager.
        
        Args:
            storage_path: Base directory for storing data files
        """
        self.storage_path = Path(storage_path)
        self.logger = logging.getLogger(__name__)
        
        # Data type to filename mapping
        self.data_files = {
            "users": "users.json",
            "conversations": "conversations.json", 
            "cultural_scenarios": "cultural_scenarios.json",
            "swahili_patterns": "swahili_patterns.json",
            "emotion_data": "emotion_data.json",
            "voice_data": "voice_data.json",
            "baseline_data": "baseline_data.json",
            "session_history": "session_history.json"
        }
        
        # Ensure storage directory exists
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self) -> None:
        """Create storage directory if it doesn't exist"""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Storage directory ensured: {self.storage_path}")
        except Exception as e:
            self.logger.error(f"Failed to create storage directory: {e}")
            raise
    
    def _get_file_path(self, data_type: str) -> Path:
        """Get full file path for a data type"""
        if data_type not in self.data_files:
            raise ValueError(f"Unknown data type: {data_type}. Available: {list(self.data_files.keys())}")
        
        return self.storage_path / self.data_files[data_type]
    
    def _validate_json_structure(self, data: Any) -> bool:
        """
        Validate that data can be serialized to JSON.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is JSON serializable
        """
        try:
            # First try without default parameter to catch non-serializable objects
            json.dumps(data)
            return True
        except (TypeError, ValueError) as e:
            self.logger.error(f"JSON validation failed: {e}")
            return False
    
    def _backup_existing_file(self, file_path: Path) -> Optional[Path]:
        """
        Create backup of existing file before overwriting.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Path to backup file if created, None otherwise
        """
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f".backup_{timestamp}.json")
        
        try:
            shutil.copy2(file_path, backup_path)
            self.logger.debug(f"Created backup: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.warning(f"Failed to create backup: {e}")
            return None
    
    def save_data(self, data_type: str, data: Dict[str, Any]) -> bool:
        """
        Save data to JSON file with validation and backup.
        
        Args:
            data_type: Type of data being saved
            data: Data dictionary to save
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            # Validate data structure
            if not self._validate_json_structure(data):
                self.logger.error(f"Invalid JSON structure for {data_type}")
                return False
            
            file_path = self._get_file_path(data_type)
            
            # Create backup if file exists
            self._backup_existing_file(file_path)
            
            # Handle incremental updates
            existing_data = {}
            if file_path.exists():
                try:
                    existing_data = self.load_data(data_type) or {}
                except Exception as e:
                    self.logger.warning(f"Could not load existing data for incremental update: {e}")
            
            # Merge with existing data for incremental updates
            if existing_data:
                # For list-based data, extend the lists
                for key, value in data.items():
                    if isinstance(value, list) and key in existing_data:
                        if isinstance(existing_data[key], list):
                            # Avoid duplicates by checking IDs if available
                            existing_ids = set()
                            if existing_data[key] and isinstance(existing_data[key][0], dict):
                                existing_ids = {item.get('id') for item in existing_data[key] if 'id' in item}
                            
                            for item in value:
                                if isinstance(item, dict) and 'id' in item:
                                    if item['id'] not in existing_ids:
                                        existing_data[key].append(item)
                                else:
                                    existing_data[key].append(item)
                        else:
                            existing_data[key] = value
                    else:
                        existing_data[key] = value
                
                final_data = existing_data
            else:
                final_data = data
            
            # Write to file with proper formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Successfully saved {data_type} data to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save {data_type} data: {e}")
            return False
    
    def load_data(self, data_type: str) -> Optional[Dict[str, Any]]:
        """
        Load data from JSON file.
        
        Args:
            data_type: Type of data to load
            
        Returns:
            Data dictionary if successful, None otherwise
        """
        try:
            file_path = self._get_file_path(data_type)
            
            if not file_path.exists():
                self.logger.debug(f"Data file does not exist: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"Successfully loaded {data_type} data from {file_path}")
            return data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {data_type} file: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load {data_type} data: {e}")
            return None
    
    def clear_all_data(self) -> bool:
        """
        Clear all stored data files and reset to clean state.
        
        Returns:
            True if all files cleared successfully, False otherwise
        """
        try:
            success = True
            cleared_files = []
            
            for data_type in self.data_files:
                file_path = self._get_file_path(data_type)
                
                if file_path.exists():
                    try:
                        file_path.unlink()
                        cleared_files.append(str(file_path))
                        self.logger.debug(f"Cleared file: {file_path}")
                    except Exception as e:
                        self.logger.error(f"Failed to clear {file_path}: {e}")
                        success = False
            
            # Also clear any backup files
            backup_pattern = "*.backup_*.json"
            for backup_file in self.storage_path.glob(backup_pattern):
                try:
                    backup_file.unlink()
                    cleared_files.append(str(backup_file))
                    self.logger.debug(f"Cleared backup file: {backup_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to clear backup {backup_file}: {e}")
            
            # Clear any temporary files
            temp_pattern = "*.tmp"
            for temp_file in self.storage_path.glob(temp_pattern):
                try:
                    temp_file.unlink()
                    cleared_files.append(str(temp_file))
                    self.logger.debug(f"Cleared temp file: {temp_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to clear temp {temp_file}: {e}")
            
            if success:
                self.logger.info(f"Successfully cleared all data files: {cleared_files}")
            else:
                self.logger.warning("Some files could not be cleared")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to clear data: {e}")
            return False
    
    def validate_data_integrity(self) -> ValidationResult:
        """
        Validate integrity of all stored data files.
        
        Returns:
            ValidationResult with validation details
        """
        try:
            corrupted_files = []
            missing_files = []
            validation_errors = []
            total_files_checked = 0
            
            for data_type, filename in self.data_files.items():
                file_path = self._get_file_path(data_type)
                total_files_checked += 1
                
                if not file_path.exists():
                    # Missing files are not necessarily errors for demo data
                    self.logger.debug(f"Data file missing: {file_path}")
                    continue
                
                try:
                    # Try to load and validate JSON
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Basic structure validation
                    if not isinstance(data, dict):
                        validation_errors.append(f"{filename}: Root element must be a dictionary")
                        corrupted_files.append(filename)
                        continue
                    
                    # Check for common required fields based on data type
                    if data_type == "users" and "users" in data:
                        for user in data["users"]:
                            if not isinstance(user, dict) or "id" not in user:
                                validation_errors.append(f"{filename}: Invalid user structure")
                                break
                    
                    elif data_type == "conversations" and "conversations" in data:
                        for conv in data["conversations"]:
                            if not isinstance(conv, dict) or "id" not in conv or "messages" not in conv:
                                validation_errors.append(f"{filename}: Invalid conversation structure")
                                break
                    
                    self.logger.debug(f"Validation passed for {filename}")
                    
                except json.JSONDecodeError as e:
                    validation_errors.append(f"{filename}: Invalid JSON - {e}")
                    corrupted_files.append(filename)
                except Exception as e:
                    validation_errors.append(f"{filename}: Validation error - {e}")
                    corrupted_files.append(filename)
            
            is_valid = len(corrupted_files) == 0 and len(validation_errors) == 0
            
            result = ValidationResult(
                valid=is_valid,
                total_files_checked=total_files_checked,
                corrupted_files=corrupted_files,
                missing_files=missing_files,
                validation_errors=validation_errors
            )
            
            if is_valid:
                self.logger.info("Data integrity validation passed")
            else:
                self.logger.warning(f"Data integrity issues found: {len(validation_errors)} errors")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Data integrity validation failed: {e}")
            return ValidationResult(
                valid=False,
                total_files_checked=0,
                corrupted_files=[],
                missing_files=[],
                validation_errors=[f"Validation process failed: {e}"]
            )
    
    def list_data_types(self) -> List[str]:
        """
        List all available data types.
        
        Returns:
            List of data type names
        """
        return list(self.data_files.keys())
    
    def get_file_info(self, data_type: str) -> Dict[str, Any]:
        """
        Get information about a data file.
        
        Args:
            data_type: Type of data file
            
        Returns:
            Dictionary with file information
        """
        try:
            file_path = self._get_file_path(data_type)
            
            if not file_path.exists():
                return {
                    "exists": False,
                    "path": str(file_path),
                    "size_bytes": 0,
                    "modified": None,
                    "record_count": 0
                }
            
            stat = file_path.stat()
            
            # Try to get record count
            record_count = 0
            try:
                data = self.load_data(data_type)
                if data:
                    # Count records in the main data arrays
                    for key, value in data.items():
                        if isinstance(value, list):
                            record_count += len(value)
            except Exception:
                pass
            
            return {
                "exists": True,
                "path": str(file_path),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "record_count": record_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get file info for {data_type}: {e}")
            return {
                "exists": False,
                "path": str(self._get_file_path(data_type)),
                "size_bytes": 0,
                "modified": None,
                "record_count": 0,
                "error": str(e)
            }
    
    def get_storage_summary(self) -> Dict[str, Any]:
        """
        Get summary of all stored data.
        
        Returns:
            Dictionary with storage summary
        """
        try:
            summary = {
                "storage_path": str(self.storage_path),
                "total_files": 0,
                "total_size_bytes": 0,
                "data_types": {},
                "last_modified": None
            }
            
            latest_modified = None
            
            for data_type in self.data_files:
                file_info = self.get_file_info(data_type)
                summary["data_types"][data_type] = file_info
                
                if file_info["exists"]:
                    summary["total_files"] += 1
                    summary["total_size_bytes"] += file_info["size_bytes"]
                    
                    if file_info["modified"]:
                        if latest_modified is None or file_info["modified"] > latest_modified:
                            latest_modified = file_info["modified"]
            
            summary["last_modified"] = latest_modified
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Failed to get storage summary: {e}")
            return {
                "storage_path": str(self.storage_path),
                "total_files": 0,
                "total_size_bytes": 0,
                "data_types": {},
                "last_modified": None,
                "error": str(e)
            }
    
    def reset_to_clean_state(self) -> bool:
        """
        Reset storage to completely clean state.
        
        This method:
        1. Clears all data files
        2. Validates clean state
        3. Recreates storage directory structure
        
        Returns:
            True if reset successful and clean state validated
        """
        try:
            # Clear all data
            if not self.clear_all_data():
                self.logger.error("Failed to clear all data during reset")
                return False
            
            # Validate clean state
            if not self.validate_clean_state():
                self.logger.error("Clean state validation failed after reset")
                return False
            
            # Ensure storage directory structure exists
            self._ensure_storage_directory()
            
            self.logger.info("Successfully reset to clean state")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reset to clean state: {e}")
            return False
    
    def validate_clean_state(self) -> bool:
        """
        Validate that storage is in clean state (no data files exist).
        
        Returns:
            True if storage is clean, False otherwise
        """
        try:
            # Check that no data files exist
            for data_type in self.data_files:
                file_path = self._get_file_path(data_type)
                if file_path.exists():
                    self.logger.debug(f"Clean state validation failed: {file_path} exists")
                    return False
            
            # Check for any backup files
            backup_files = list(self.storage_path.glob("*.backup_*.json"))
            if backup_files:
                self.logger.debug(f"Clean state validation failed: backup files exist: {backup_files}")
                return False
            
            # Check for any temporary files
            temp_files = list(self.storage_path.glob("*.tmp"))
            if temp_files:
                self.logger.debug(f"Clean state validation failed: temp files exist: {temp_files}")
                return False
            
            self.logger.debug("Clean state validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"Clean state validation error: {e}")
            return False
    
    def get_cleanup_report(self) -> Dict[str, Any]:
        """
        Generate a report of what would be cleaned up.
        
        Returns:
            Dictionary with cleanup report details
        """
        try:
            report = {
                "data_files": [],
                "backup_files": [],
                "temp_files": [],
                "total_files": 0,
                "total_size_bytes": 0,
                "storage_path": str(self.storage_path)
            }
            
            # Check data files
            for data_type in self.data_files:
                file_path = self._get_file_path(data_type)
                if file_path.exists():
                    stat = file_path.stat()
                    report["data_files"].append({
                        "type": data_type,
                        "path": str(file_path),
                        "size_bytes": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime)
                    })
                    report["total_files"] += 1
                    report["total_size_bytes"] += stat.st_size
            
            # Check backup files
            for backup_file in self.storage_path.glob("*.backup_*.json"):
                stat = backup_file.stat()
                report["backup_files"].append({
                    "path": str(backup_file),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
                report["total_files"] += 1
                report["total_size_bytes"] += stat.st_size
            
            # Check temp files
            for temp_file in self.storage_path.glob("*.tmp"):
                stat = temp_file.stat()
                report["temp_files"].append({
                    "path": str(temp_file),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                })
                report["total_files"] += 1
                report["total_size_bytes"] += stat.st_size
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate cleanup report: {e}")
            return {
                "data_files": [],
                "backup_files": [],
                "temp_files": [],
                "total_files": 0,
                "total_size_bytes": 0,
                "storage_path": str(self.storage_path),
                "error": str(e)
            }