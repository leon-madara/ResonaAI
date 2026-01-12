"""
Tests for LocalStorageManager

This module contains unit tests for the local storage functionality
including save/load operations, data validation, and cleanup functionality.
"""

import pytest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.demo_data_generator.storage.local_storage import LocalStorageManager
from scripts.demo_data_generator.models import ValidationResult


class TestLocalStorageManager:
    """Test LocalStorageManager functionality"""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield LocalStorageManager(temp_dir)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return {
            "users": [
                {
                    "id": "user_001",
                    "name": "Test User",
                    "age": 25,
                    "location": "Nairobi",
                    "primary_language": "Swahili"
                },
                {
                    "id": "user_002", 
                    "name": "Another User",
                    "age": 30,
                    "location": "Mombasa",
                    "primary_language": "English"
                }
            ]
        }
    
    @pytest.fixture
    def sample_conversation_data(self):
        """Sample conversation data for testing"""
        return {
            "conversations": [
                {
                    "id": "conv_001",
                    "user_id": "user_001",
                    "scenario": "academic_pressure",
                    "messages": [
                        {
                            "id": "msg_001",
                            "timestamp": "2024-01-12T10:00:00Z",
                            "speaker": "user",
                            "text": "I'm feeling stressed about exams"
                        }
                    ]
                }
            ]
        }
    
    def test_initialization(self, temp_storage):
        """Test LocalStorageManager initialization"""
        assert temp_storage.storage_path.exists()
        assert len(temp_storage.data_files) == 8
        assert "users" in temp_storage.data_files
        assert "conversations" in temp_storage.data_files
    
    def test_save_and_load_data(self, temp_storage, sample_user_data):
        """Test basic save and load operations"""
        # Save data
        success = temp_storage.save_data("users", sample_user_data)
        assert success is True
        
        # Load data
        loaded_data = temp_storage.load_data("users")
        assert loaded_data is not None
        assert loaded_data == sample_user_data
        assert len(loaded_data["users"]) == 2
    
    def test_save_invalid_data_type(self, temp_storage):
        """Test saving with invalid data type"""
        success = temp_storage.save_data("invalid_type", {"test": "data"})
        assert success is False
    
    def test_load_nonexistent_data(self, temp_storage):
        """Test loading data that doesn't exist"""
        result = temp_storage.load_data("users")
        assert result is None
    
    def test_incremental_data_loading(self, temp_storage, sample_user_data):
        """Test incremental data updates"""
        # Save initial data
        temp_storage.save_data("users", sample_user_data)
        
        # Add more data
        additional_data = {
            "users": [
                {
                    "id": "user_003",
                    "name": "Third User", 
                    "age": 28,
                    "location": "Kisumu",
                    "primary_language": "Luo"
                }
            ]
        }
        
        success = temp_storage.save_data("users", additional_data)
        assert success is True
        
        # Load and verify merged data
        loaded_data = temp_storage.load_data("users")
        assert len(loaded_data["users"]) == 3
        
        # Check that all users are present
        user_ids = {user["id"] for user in loaded_data["users"]}
        assert user_ids == {"user_001", "user_002", "user_003"}
    
    def test_list_data_types(self, temp_storage):
        """Test listing available data types"""
        data_types = temp_storage.list_data_types()
        expected_types = [
            "users", "conversations", "cultural_scenarios", "swahili_patterns",
            "emotion_data", "voice_data", "baseline_data", "session_history"
        ]
        assert set(data_types) == set(expected_types)
    
    def test_get_file_info(self, temp_storage, sample_user_data):
        """Test getting file information"""
        # Test non-existent file
        info = temp_storage.get_file_info("users")
        assert info["exists"] is False
        assert info["size_bytes"] == 0
        assert info["record_count"] == 0
        
        # Save data and test existing file
        temp_storage.save_data("users", sample_user_data)
        info = temp_storage.get_file_info("users")
        assert info["exists"] is True
        assert info["size_bytes"] > 0
        assert info["record_count"] == 2  # 2 users in sample data
        assert isinstance(info["modified"], datetime)
    
    def test_validate_data_integrity(self, temp_storage, sample_user_data, sample_conversation_data):
        """Test data integrity validation"""
        # Test with no data
        result = temp_storage.validate_data_integrity()
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.total_files_checked == 8
        
        # Save valid data
        temp_storage.save_data("users", sample_user_data)
        temp_storage.save_data("conversations", sample_conversation_data)
        
        # Test with valid data
        result = temp_storage.validate_data_integrity()
        assert result.valid is True
        assert len(result.corrupted_files) == 0
        assert len(result.validation_errors) == 0
    
    def test_validate_data_integrity_corrupted_file(self, temp_storage):
        """Test data integrity validation with corrupted file"""
        # Create corrupted JSON file
        file_path = temp_storage._get_file_path("users")
        with open(file_path, 'w') as f:
            f.write("invalid json content {")
        
        result = temp_storage.validate_data_integrity()
        assert result.valid is False
        assert "users.json" in result.corrupted_files
        assert len(result.validation_errors) > 0
    
    def test_clear_all_data(self, temp_storage, sample_user_data, sample_conversation_data):
        """Test clearing all data"""
        # Save some data
        temp_storage.save_data("users", sample_user_data)
        temp_storage.save_data("conversations", sample_conversation_data)
        
        # Verify data exists
        assert temp_storage.load_data("users") is not None
        assert temp_storage.load_data("conversations") is not None
        
        # Clear all data
        success = temp_storage.clear_all_data()
        assert success is True
        
        # Verify data is cleared
        assert temp_storage.load_data("users") is None
        assert temp_storage.load_data("conversations") is None
    
    def test_validate_clean_state(self, temp_storage, sample_user_data):
        """Test clean state validation"""
        # Initially should be clean
        assert temp_storage.validate_clean_state() is True
        
        # Add data - should not be clean
        temp_storage.save_data("users", sample_user_data)
        assert temp_storage.validate_clean_state() is False
        
        # Clear data - should be clean again
        temp_storage.clear_all_data()
        assert temp_storage.validate_clean_state() is True
    
    def test_reset_to_clean_state(self, temp_storage, sample_user_data):
        """Test reset to clean state functionality"""
        # Add some data
        temp_storage.save_data("users", sample_user_data)
        assert temp_storage.validate_clean_state() is False
        
        # Reset to clean state
        success = temp_storage.reset_to_clean_state()
        assert success is True
        assert temp_storage.validate_clean_state() is True
    
    def test_get_cleanup_report(self, temp_storage, sample_user_data):
        """Test cleanup report generation"""
        # Test with no data
        report = temp_storage.get_cleanup_report()
        assert report["total_files"] == 0
        assert len(report["data_files"]) == 0
        
        # Add data and test report
        temp_storage.save_data("users", sample_user_data)
        report = temp_storage.get_cleanup_report()
        assert report["total_files"] == 1
        assert len(report["data_files"]) == 1
        assert report["data_files"][0]["type"] == "users"
        assert report["total_size_bytes"] > 0
    
    def test_get_storage_summary(self, temp_storage, sample_user_data, sample_conversation_data):
        """Test storage summary generation"""
        # Test with no data
        summary = temp_storage.get_storage_summary()
        assert summary["total_files"] == 0
        assert summary["total_size_bytes"] == 0
        assert summary["last_modified"] is None
        
        # Add data and test summary
        temp_storage.save_data("users", sample_user_data)
        temp_storage.save_data("conversations", sample_conversation_data)
        
        summary = temp_storage.get_storage_summary()
        assert summary["total_files"] == 2
        assert summary["total_size_bytes"] > 0
        assert summary["last_modified"] is not None
        assert len(summary["data_types"]) == 8  # All data types should be listed
    
    def test_backup_functionality(self, temp_storage, sample_user_data):
        """Test that backups are created when overwriting files"""
        # Save initial data
        temp_storage.save_data("users", sample_user_data)
        
        # Modify and save again (should create backup)
        # Use different data structure to avoid incremental merging
        modified_data = {
            "users": [
                {
                    "id": "user_004",  # Different ID to avoid merging
                    "name": "Modified User",
                    "age": 26,
                    "location": "Nairobi",
                    "primary_language": "Swahili"
                }
            ]
        }
        
        temp_storage.save_data("users", modified_data)
        
        # Check that backup files exist
        backup_files = list(temp_storage.storage_path.glob("*.backup_*.json"))
        assert len(backup_files) > 0
        
        # Verify current data includes both original and new data (due to incremental loading)
        current_data = temp_storage.load_data("users")
        assert len(current_data["users"]) == 3  # 2 original + 1 new
        
        # Check that the new user is present
        user_ids = {user["id"] for user in current_data["users"]}
        assert "user_004" in user_ids
    
    def test_json_serialization_validation(self, temp_storage):
        """Test JSON serialization validation"""
        # Test with non-serializable data
        invalid_data = {
            "users": [
                {
                    "id": "user_001",
                    "function": lambda x: x  # Functions are not JSON serializable
                }
            ]
        }
        
        success = temp_storage.save_data("users", invalid_data)
        assert success is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])