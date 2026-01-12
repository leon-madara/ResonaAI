"""
Test setup and basic functionality of the demo data generator
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.demo_data_generator.models import (
    DemoConfig, ServiceConfig, EmotionType, CrisisLevel,
    ConversationScenarioType, UserProfile, ConversationThread
)
from scripts.demo_data_generator.config import ConfigurationManager, get_demo_config, get_service_config
from scripts.demo_data_generator.interfaces import DataGeneratorInterface


class TestSetup:
    """Test basic setup and imports"""
    
    def test_imports_work(self):
        """Test that all core imports work correctly"""
        # This test passes if imports don't raise exceptions
        assert DemoConfig is not None
        assert ServiceConfig is not None
        assert EmotionType is not None
        assert ConfigurationManager is not None
    
    def test_enum_values(self):
        """Test that enums have expected values"""
        # Test EmotionType enum
        assert EmotionType.NEUTRAL == "neutral"
        assert EmotionType.HAPPY == "happy"
        assert EmotionType.SAD == "sad"
        assert EmotionType.ANGRY == "angry"
        assert EmotionType.FEAR == "fear"
        assert EmotionType.SURPRISE == "surprise"
        assert EmotionType.DISGUST == "disgust"
        
        # Test CrisisLevel enum
        assert CrisisLevel.NONE == "none"
        assert CrisisLevel.LOW == "low"
        assert CrisisLevel.MEDIUM == "medium"
        assert CrisisLevel.HIGH == "high"
        assert CrisisLevel.CRITICAL == "critical"
    
    def test_demo_config_creation(self):
        """Test that DemoConfig can be created with defaults"""
        config = DemoConfig()
        
        assert config.num_users == 10
        assert config.conversations_per_user == 5
        assert config.cultural_scenarios == 20
        assert config.swahili_patterns == 50
        assert config.output_directory == "demo_data"
        assert config.include_crisis_scenarios is True
        assert config.crisis_scenario_percentage == 0.1
        assert config.emotional_diversity_threshold == 0.8
        assert config.cultural_authenticity_check is True
    
    def test_service_config_creation(self):
        """Test that ServiceConfig can be created with defaults"""
        config = ServiceConfig()
        
        assert config.mock_api_port == 8001
        assert config.frontend_port == 3000
        assert config.auto_open_browser is True
        assert config.processing_delay_ms == 500
        assert config.enable_websockets is True
        assert config.cors_origins == ["http://localhost:3000"]
    
    def test_configuration_manager(self):
        """Test that ConfigurationManager works"""
        manager = ConfigurationManager()
        
        demo_config = manager.get_demo_config()
        service_config = manager.get_service_config()
        
        assert isinstance(demo_config, DemoConfig)
        assert isinstance(service_config, ServiceConfig)
        
        # Test validation
        validation_result = manager.validate_configuration()
        assert isinstance(validation_result, dict)
        assert "valid" in validation_result
        assert "errors" in validation_result
        assert "warnings" in validation_result
    
    def test_config_functions(self):
        """Test global config functions"""
        demo_config = get_demo_config()
        service_config = get_service_config()
        
        assert isinstance(demo_config, DemoConfig)
        assert isinstance(service_config, ServiceConfig)
    
    def test_interface_is_abstract(self):
        """Test that DataGeneratorInterface is abstract"""
        with pytest.raises(TypeError):
            # Should not be able to instantiate abstract class
            DataGeneratorInterface()


class TestModels:
    """Test Pydantic models"""
    
    def test_demo_config_validation(self):
        """Test DemoConfig validation"""
        # Valid config
        config = DemoConfig(num_users=5, conversations_per_user=3)
        assert config.num_users == 5
        assert config.conversations_per_user == 3
        
        # Test validation constraints
        with pytest.raises(ValueError):
            DemoConfig(num_users=0)  # Should be >= 1
        
        with pytest.raises(ValueError):
            DemoConfig(num_users=2000)  # Should be <= 1000
        
        with pytest.raises(ValueError):
            DemoConfig(crisis_scenario_percentage=1.5)  # Should be <= 1.0
    
    def test_service_config_validation(self):
        """Test ServiceConfig validation"""
        # Valid config
        config = ServiceConfig(mock_api_port=8080, frontend_port=3001)
        assert config.mock_api_port == 8080
        assert config.frontend_port == 3001
        
        # Test port validation
        with pytest.raises(ValueError):
            ServiceConfig(mock_api_port=100)  # Should be >= 1024
        
        with pytest.raises(ValueError):
            ServiceConfig(frontend_port=70000)  # Should be <= 65535


if __name__ == "__main__":
    pytest.main([__file__])