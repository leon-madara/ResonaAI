"""
Configuration Management for Demo Data Generator

This module provides configuration management with environment variable support,
validation, and default values for all demo parameters.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import Field, validator
from pydantic_settings import BaseSettings
from .models import DemoConfig, ServiceConfig


class DemoSettings(BaseSettings):
    """Demo configuration with environment variable support"""
    
    # Data Generation Settings
    num_users: int = Field(default=10, env="DEMO_NUM_USERS", ge=1, le=1000)
    conversations_per_user: int = Field(default=5, env="DEMO_CONVERSATIONS_PER_USER", ge=1, le=50)
    cultural_scenarios: int = Field(default=20, env="DEMO_CULTURAL_SCENARIOS", ge=1, le=100)
    swahili_patterns: int = Field(default=50, env="DEMO_SWAHILI_PATTERNS", ge=1, le=500)
    output_directory: str = Field(default="demo_data", env="DEMO_OUTPUT_DIR")
    include_crisis_scenarios: bool = Field(default=True, env="DEMO_INCLUDE_CRISIS")
    crisis_scenario_percentage: float = Field(default=0.1, env="DEMO_CRISIS_PERCENTAGE", ge=0.0, le=1.0)
    emotional_diversity_threshold: float = Field(default=0.8, env="DEMO_EMOTIONAL_DIVERSITY", ge=0.0, le=1.0)
    cultural_authenticity_check: bool = Field(default=True, env="DEMO_CULTURAL_CHECK")
    
    # Service Settings
    mock_api_port: int = Field(default=8001, env="DEMO_API_PORT", ge=1024, le=65535)
    frontend_port: int = Field(default=3000, env="DEMO_FRONTEND_PORT", ge=1024, le=65535)
    auto_open_browser: bool = Field(default=True, env="DEMO_AUTO_BROWSER")
    processing_delay_ms: int = Field(default=500, env="DEMO_PROCESSING_DELAY", ge=0, le=5000)
    enable_websockets: bool = Field(default=True, env="DEMO_ENABLE_WS")
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"], env="DEMO_CORS_ORIGINS")
    
    # Paths and Directories
    frontend_path: str = Field(default="apps/frontend", env="DEMO_FRONTEND_PATH")
    data_storage_path: str = Field(default="demo_data", env="DEMO_STORAGE_PATH")
    log_level: str = Field(default="INFO", env="DEMO_LOG_LEVEL")
    
    # Development Settings
    debug_mode: bool = Field(default=False, env="DEMO_DEBUG")
    verbose_logging: bool = Field(default=False, env="DEMO_VERBOSE")
    skip_browser_launch: bool = Field(default=False, env="DEMO_SKIP_BROWSER")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables
    
    @validator('output_directory', 'data_storage_path', 'frontend_path')
    def validate_paths(cls, v):
        """Ensure paths are valid and create directories if needed"""
        if not v:
            raise ValueError("Path cannot be empty")
        return v
    
    @validator('mock_api_port', 'frontend_port')
    def validate_ports_different(cls, v, values):
        """Ensure API and frontend ports are different"""
        if 'mock_api_port' in values and v == values['mock_api_port']:
            raise ValueError("Frontend and API ports must be different")
        return v
    
    def to_demo_config(self) -> DemoConfig:
        """Convert to DemoConfig model"""
        return DemoConfig(
            num_users=self.num_users,
            conversations_per_user=self.conversations_per_user,
            cultural_scenarios=self.cultural_scenarios,
            swahili_patterns=self.swahili_patterns,
            output_directory=self.output_directory,
            include_crisis_scenarios=self.include_crisis_scenarios,
            crisis_scenario_percentage=self.crisis_scenario_percentage,
            emotional_diversity_threshold=self.emotional_diversity_threshold,
            cultural_authenticity_check=self.cultural_authenticity_check
        )
    
    def to_service_config(self) -> ServiceConfig:
        """Convert to ServiceConfig model"""
        return ServiceConfig(
            mock_api_port=self.mock_api_port,
            frontend_port=self.frontend_port,
            auto_open_browser=self.auto_open_browser,
            processing_delay_ms=self.processing_delay_ms,
            enable_websockets=self.enable_websockets,
            cors_origins=[f"http://localhost:{self.frontend_port}"]
        )


class ConfigurationManager:
    """Manages configuration loading, validation, and updates"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._settings: Optional[DemoSettings] = None
        self._config_cache: Dict[str, Any] = {}
    
    def load_settings(self) -> DemoSettings:
        """Load settings from environment and config file"""
        if self._settings is None:
            if self.config_file and Path(self.config_file).exists():
                # Load from JSON config file
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                # Update environment with config file values
                for key, value in config_data.items():
                    if key.upper() not in os.environ:
                        os.environ[key.upper()] = str(value)
            
            self._settings = DemoSettings()
        
        return self._settings
    
    def get_demo_config(self) -> DemoConfig:
        """Get demo configuration"""
        settings = self.load_settings()
        return settings.to_demo_config()
    
    def get_service_config(self) -> ServiceConfig:
        """Get service configuration"""
        settings = self.load_settings()
        return settings.to_service_config()
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters"""
        settings = self.load_settings()
        
        # Update settings object
        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        # Clear cache to force reload
        self._config_cache.clear()
    
    def update_demo_config(self, demo_config: DemoConfig) -> None:
        """Update demo configuration"""
        settings = self.load_settings()
        
        # Update demo-related settings
        settings.num_users = demo_config.num_users
        settings.conversations_per_user = demo_config.conversations_per_user
        settings.cultural_scenarios = demo_config.cultural_scenarios
        settings.swahili_patterns = demo_config.swahili_patterns
        settings.output_directory = demo_config.output_directory
        settings.include_crisis_scenarios = demo_config.include_crisis_scenarios
        settings.crisis_scenario_percentage = demo_config.crisis_scenario_percentage
        settings.emotional_diversity_threshold = demo_config.emotional_diversity_threshold
        settings.cultural_authenticity_check = demo_config.cultural_authenticity_check
        
        # Clear cache to force reload
        self._config_cache.clear()
    
    def update_service_config(self, service_config: ServiceConfig) -> None:
        """Update service configuration"""
        settings = self.load_settings()
        
        # Update service-related settings
        settings.mock_api_port = service_config.mock_api_port
        settings.frontend_port = service_config.frontend_port
        settings.auto_open_browser = service_config.auto_open_browser
        settings.processing_delay_ms = service_config.processing_delay_ms
        settings.enable_websockets = service_config.enable_websockets
        settings.cors_origins = service_config.cors_origins
        
        # Clear cache to force reload
        self._config_cache.clear()
    
    def save_config(self, config_file: str) -> None:
        """Save current configuration to file"""
        settings = self.load_settings()
        config_data = settings.dict()
        
        # Ensure directory exists
        Path(config_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate current configuration and return validation results"""
        try:
            settings = self.load_settings()
            demo_config = settings.to_demo_config()
            service_config = settings.to_service_config()
            
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": [],
                "settings": settings.dict()
            }
            
            # Check for potential issues
            if demo_config.num_users * demo_config.conversations_per_user > 1000:
                validation_results["warnings"].append(
                    "Large number of conversations may take significant time to generate"
                )
            
            if service_config.mock_api_port == service_config.frontend_port:
                validation_results["errors"].append(
                    "API and frontend ports cannot be the same"
                )
                validation_results["valid"] = False
            
            # Check if output directory is writable
            output_path = Path(demo_config.output_directory)
            try:
                output_path.mkdir(parents=True, exist_ok=True)
                test_file = output_path / "test_write.tmp"
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                validation_results["errors"].append(
                    f"Output directory not writable: {e}"
                )
                validation_results["valid"] = False
            
            return validation_results
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Configuration validation failed: {e}"],
                "warnings": [],
                "settings": {}
            }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get information about the current environment"""
        return {
            "python_version": os.sys.version,
            "platform": os.name,
            "working_directory": os.getcwd(),
            "environment_variables": {
                key: value for key, value in os.environ.items() 
                if key.startswith("DEMO_")
            },
            "config_file": self.config_file,
            "config_file_exists": self.config_file and Path(self.config_file).exists()
        }


# Default configuration instances
default_config_manager = ConfigurationManager()


def get_demo_config() -> DemoConfig:
    """Get default demo configuration"""
    return default_config_manager.get_demo_config()


def get_service_config() -> ServiceConfig:
    """Get default service configuration"""
    return default_config_manager.get_service_config()


def create_config_manager(config_file: Optional[str] = None) -> ConfigurationManager:
    """Create a new configuration manager"""
    return ConfigurationManager(config_file)


# Configuration presets for different scenarios

QUICK_DEMO_CONFIG = {
    "num_users": 3,
    "conversations_per_user": 2,
    "cultural_scenarios": 5,
    "swahili_patterns": 10,
    "include_crisis_scenarios": False,
    "processing_delay_ms": 200
}

COMPREHENSIVE_DEMO_CONFIG = {
    "num_users": 20,
    "conversations_per_user": 10,
    "cultural_scenarios": 50,
    "swahili_patterns": 100,
    "include_crisis_scenarios": True,
    "crisis_scenario_percentage": 0.15,
    "processing_delay_ms": 800
}

DEVELOPMENT_CONFIG = {
    "num_users": 5,
    "conversations_per_user": 3,
    "cultural_scenarios": 10,
    "swahili_patterns": 20,
    "debug_mode": True,
    "verbose_logging": True,
    "processing_delay_ms": 100,
    "skip_browser_launch": True
}


def apply_preset(preset_name: str, config_manager: ConfigurationManager) -> None:
    """Apply a configuration preset"""
    presets = {
        "quick": QUICK_DEMO_CONFIG,
        "comprehensive": COMPREHENSIVE_DEMO_CONFIG,
        "development": DEVELOPMENT_CONFIG
    }
    
    if preset_name not in presets:
        raise ValueError(f"Unknown preset: {preset_name}. Available: {list(presets.keys())}")
    
    config_manager.update_config(**presets[preset_name])