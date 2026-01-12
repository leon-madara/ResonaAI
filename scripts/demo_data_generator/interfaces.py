"""
Core Interfaces for Demo Data Generator

This module defines abstract base classes and protocols that establish
the contracts for all components in the demo data generator system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Protocol
from .models import (
    ConversationThread, ConversationScenarioType, EmotionResult, 
    CulturalScenario, CulturalScenarioType, SwahiliPattern,
    AudioFeatures, VoiceTruthGap, DissonanceResult, DeflectionResult,
    UserProfile, BaselineData, DemoConfig, GenerationResult,
    ValidationResult, EmotionalProgression, ServiceConfig, ProcessInfo
)


class DataGeneratorInterface(ABC):
    """Base interface for all data generators"""
    
    @abstractmethod
    def generate(self, config: DemoConfig) -> GenerationResult:
        """Generate data according to configuration"""
        pass
    
    @abstractmethod
    def validate_output(self, data: Any) -> bool:
        """Validate generated data meets quality standards"""
        pass


class ConversationGeneratorInterface(DataGeneratorInterface):
    """Interface for conversation generation"""
    
    @abstractmethod
    def generate_conversation_thread(self, scenario: ConversationScenarioType, user_id: str) -> ConversationThread:
        """Generate a complete conversation thread"""
        pass
    
    @abstractmethod
    def create_emotional_arc(self, start_emotion: str, target_emotion: str, steps: int) -> EmotionalProgression:
        """Create realistic emotional progression"""
        pass
    
    @abstractmethod
    def add_cultural_context(self, conversation: ConversationThread) -> ConversationThread:
        """Add cultural context to conversation"""
        pass


class EmotionGeneratorInterface(DataGeneratorInterface):
    """Interface for emotion data generation"""
    
    @abstractmethod
    def generate_emotion_analysis(self, text: str, context: Optional[Dict] = None) -> EmotionResult:
        """Generate emotion analysis for text"""
        pass
    
    @abstractmethod
    def create_dissonance_pattern(self, text_emotion: str, voice_emotion: str) -> DissonanceResult:
        """Create voice-truth dissonance pattern"""
        pass
    
    @abstractmethod
    def generate_baseline_data(self, user_id: str, sessions: int) -> BaselineData:
        """Generate baseline emotional and voice patterns"""
        pass


class CulturalGeneratorInterface(DataGeneratorInterface):
    """Interface for cultural context generation"""
    
    @abstractmethod
    def generate_swahili_patterns(self, count: int) -> List[SwahiliPattern]:
        """Generate Swahili language patterns"""
        pass
    
    @abstractmethod
    def create_cultural_scenario(self, scenario_type: CulturalScenarioType) -> CulturalScenario:
        """Create cultural scenario"""
        pass
    
    @abstractmethod
    def simulate_deflection_detection(self, conversation: str) -> DeflectionResult:
        """Simulate cultural deflection detection"""
        pass


class VoiceGeneratorInterface(DataGeneratorInterface):
    """Interface for voice analysis simulation"""
    
    @abstractmethod
    def simulate_audio_features(self, text: str, emotion: str) -> AudioFeatures:
        """Simulate audio feature extraction"""
        pass
    
    @abstractmethod
    def generate_voice_truth_gap(self, text_content: str, emotional_state: str) -> VoiceTruthGap:
        """Generate voice-truth gap analysis"""
        pass
    
    @abstractmethod
    def create_prosodic_features(self, speech_pattern: Dict[str, Any]) -> Dict[str, float]:
        """Create prosodic feature data"""
        pass


class UserGeneratorInterface(DataGeneratorInterface):
    """Interface for user profile generation"""
    
    @abstractmethod
    def generate_user_profile(self, user_id: str) -> UserProfile:
        """Generate diverse user profile"""
        pass
    
    @abstractmethod
    def ensure_demographic_diversity(self, profiles: List[UserProfile]) -> bool:
        """Validate demographic diversity in generated profiles"""
        pass


class StorageInterface(ABC):
    """Interface for data storage operations"""
    
    @abstractmethod
    def save_data(self, data_type: str, data: Dict[str, Any]) -> bool:
        """Save data to storage"""
        pass
    
    @abstractmethod
    def load_data(self, data_type: str) -> Optional[Dict[str, Any]]:
        """Load data from storage"""
        pass
    
    @abstractmethod
    def clear_all_data(self) -> bool:
        """Clear all stored data"""
        pass
    
    @abstractmethod
    def validate_data_integrity(self) -> ValidationResult:
        """Validate integrity of stored data"""
        pass
    
    @abstractmethod
    def list_data_types(self) -> List[str]:
        """List available data types in storage"""
        pass


class APIServerInterface(ABC):
    """Interface for mock API server"""
    
    @abstractmethod
    def start_server(self, config: ServiceConfig) -> bool:
        """Start the mock API server"""
        pass
    
    @abstractmethod
    def stop_server(self) -> bool:
        """Stop the mock API server"""
        pass
    
    @abstractmethod
    def register_endpoints(self) -> None:
        """Register all API endpoints"""
        pass
    
    @abstractmethod
    def simulate_processing_delay(self, endpoint: str) -> float:
        """Simulate realistic processing delays"""
        pass
    
    @abstractmethod
    def get_server_info(self) -> ProcessInfo:
        """Get server process information"""
        pass


class FrontendLauncherInterface(ABC):
    """Interface for frontend launcher"""
    
    @abstractmethod
    def setup_environment(self, frontend_path: str) -> bool:
        """Setup frontend environment and dependencies"""
        pass
    
    @abstractmethod
    def start_frontend(self, config: ServiceConfig) -> ProcessInfo:
        """Start frontend development server"""
        pass
    
    @abstractmethod
    def configure_api_endpoints(self, mock_api_url: str) -> bool:
        """Configure frontend to use mock API"""
        pass
    
    @abstractmethod
    def open_browser(self, url: str) -> bool:
        """Open browser to demo URL"""
        pass
    
    @abstractmethod
    def stop_frontend(self) -> bool:
        """Stop frontend server"""
        pass


class DemoOrchestratorInterface(ABC):
    """Interface for main demo orchestrator"""
    
    @abstractmethod
    def generate_all_data(self, config: DemoConfig) -> GenerationResult:
        """Generate all required demo data"""
        pass
    
    @abstractmethod
    def start_demo(self, config: ServiceConfig) -> List[ProcessInfo]:
        """Start complete demo environment"""
        pass
    
    @abstractmethod
    def stop_demo(self) -> bool:
        """Stop all demo services"""
        pass
    
    @abstractmethod
    def get_demo_status(self) -> Dict[str, Any]:
        """Get current demo status"""
        pass
    
    @abstractmethod
    def cleanup_demo(self) -> bool:
        """Clean up demo data and processes"""
        pass


# Protocol for dependency injection

class ConfigurationProvider(Protocol):
    """Protocol for configuration providers"""
    
    def get_demo_config(self) -> DemoConfig:
        """Get demo configuration"""
        ...
    
    def get_service_config(self) -> ServiceConfig:
        """Get service configuration"""
        ...
    
    def update_config(self, **kwargs) -> None:
        """Update configuration parameters"""
        ...


class LoggerProvider(Protocol):
    """Protocol for logging providers"""
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        ...
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        ...
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message"""
        ...
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        ...


class ProgressReporter(Protocol):
    """Protocol for progress reporting"""
    
    def start_task(self, task_name: str, total_steps: int) -> None:
        """Start a new task"""
        ...
    
    def update_progress(self, steps_completed: int, message: str = "") -> None:
        """Update task progress"""
        ...
    
    def complete_task(self, success: bool, message: str = "") -> None:
        """Complete current task"""
        ...


# Factory interfaces

class GeneratorFactory(ABC):
    """Factory for creating data generators"""
    
    @abstractmethod
    def create_conversation_generator(self) -> ConversationGeneratorInterface:
        """Create conversation generator"""
        pass
    
    @abstractmethod
    def create_emotion_generator(self) -> EmotionGeneratorInterface:
        """Create emotion generator"""
        pass
    
    @abstractmethod
    def create_cultural_generator(self) -> CulturalGeneratorInterface:
        """Create cultural generator"""
        pass
    
    @abstractmethod
    def create_voice_generator(self) -> VoiceGeneratorInterface:
        """Create voice generator"""
        pass
    
    @abstractmethod
    def create_user_generator(self) -> UserGeneratorInterface:
        """Create user generator"""
        pass


class ServiceFactory(ABC):
    """Factory for creating services"""
    
    @abstractmethod
    def create_storage(self, storage_path: str) -> StorageInterface:
        """Create storage service"""
        pass
    
    @abstractmethod
    def create_api_server(self, storage: StorageInterface) -> APIServerInterface:
        """Create API server"""
        pass
    
    @abstractmethod
    def create_frontend_launcher(self) -> FrontendLauncherInterface:
        """Create frontend launcher"""
        pass
    
    @abstractmethod
    def create_demo_orchestrator(self, 
                                generator_factory: GeneratorFactory,
                                storage: StorageInterface,
                                api_server: APIServerInterface,
                                frontend_launcher: FrontendLauncherInterface) -> DemoOrchestratorInterface:
        """Create demo orchestrator"""
        pass