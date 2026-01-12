"""
Demo Data Generator Package

This package provides comprehensive test data generation and demonstration capabilities
for the ResonaAI platform, including realistic conversations, emotion analysis,
cultural context, and voice analysis simulation.
"""

__version__ = "1.0.0"
__author__ = "ResonaAI Team"

# Import main classes for easier access
from .config import ConfigurationManager
from .models import DemoConfig, ServiceConfig, GenerationResult
from .storage.local_storage import LocalStorageManager

# Import main orchestrator classes from the main script
import sys
from pathlib import Path

# Add the parent directory to path to import from demo_data_generator.py
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

try:
    from demo_data_generator import DemoDataGenerator, DemoDataGeneratorCLI
    __all__ = [
        'ConfigurationManager',
        'DemoConfig', 
        'ServiceConfig',
        'GenerationResult',
        'LocalStorageManager',
        'DemoDataGenerator',
        'DemoDataGeneratorCLI'
    ]
except ImportError:
    # If import fails, just export the available classes
    __all__ = [
        'ConfigurationManager',
        'DemoConfig', 
        'ServiceConfig',
        'GenerationResult',
        'LocalStorageManager'
    ]