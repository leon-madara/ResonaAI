"""
Core Data Models for Demo Data Generator

This module defines all Pydantic models used throughout the demo data generator
system for type safety and data validation.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator


class EmotionType(str, Enum):
    """Seven-emotion model used in ResonaAI"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"


class CrisisLevel(str, Enum):
    """Crisis severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConversationScenarioType(str, Enum):
    """Types of conversation scenarios"""
    ACADEMIC_PRESSURE = "academic_pressure"
    FAMILY_ISSUES = "family_issues"
    RELATIONSHIP_PROBLEMS = "relationship_problems"
    FINANCIAL_STRESS = "financial_stress"
    HEALTH_CONCERNS = "health_concerns"
    CAREER_ANXIETY = "career_anxiety"
    CULTURAL_CONFLICT = "cultural_conflict"


class CulturalScenarioType(str, Enum):
    """Types of cultural scenarios"""
    TRADITIONAL_VS_MODERN = "traditional_vs_modern"
    FAMILY_PRESSURE = "family_pressure"
    GENDER_EXPECTATIONS = "gender_expectations"
    RELIGIOUS_CONFLICT = "religious_conflict"
    LANGUAGE_IDENTITY = "language_identity"


class SpeakerType(str, Enum):
    """Types of speakers in conversations"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Core Data Models

class EmotionResult(BaseModel):
    """Emotion analysis result"""
    detected: EmotionType
    confidence: float = Field(ge=0.0, le=1.0)
    voice_truth_gap: Optional[float] = Field(None, ge=0.0, le=1.0)
    features: Optional[Dict[str, float]] = None


class CulturalContext(BaseModel):
    """Cultural context information"""
    patterns: List[str] = Field(default_factory=list)
    deflection_detected: bool = False
    cultural_significance: str = Field(default="low")  # low, medium, high
    language_switches: List[str] = Field(default_factory=list)


class Message(BaseModel):
    """Individual message in a conversation"""
    id: str
    timestamp: datetime
    speaker: SpeakerType
    text: str
    emotion: EmotionResult
    cultural_context: Optional[CulturalContext] = None


class EmotionalProgression(BaseModel):
    """Emotional arc progression through a conversation"""
    start_emotion: EmotionType
    progression: List[EmotionType]
    end_emotion: EmotionType
    crisis_level: CrisisLevel


class ConversationThread(BaseModel):
    """Complete conversation thread"""
    id: str
    user_id: str
    scenario: ConversationScenarioType
    messages: List[Message]
    emotional_arc: EmotionalProgression
    duration_minutes: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)


class VoicePatterns(BaseModel):
    """Voice pattern baseline data"""
    average_pitch: float
    speech_rate: float
    emotional_baseline: EmotionType
    stress_indicators: List[str] = Field(default_factory=list)


class EmotionalPatterns(BaseModel):
    """Emotional pattern baseline data"""
    dominant_emotions: List[EmotionType]
    crisis_triggers: List[str] = Field(default_factory=list)
    coping_mechanisms: List[str] = Field(default_factory=list)


class BaselineData(BaseModel):
    """User baseline data"""
    voice_patterns: VoicePatterns
    emotional_patterns: EmotionalPatterns


class SessionHistory(BaseModel):
    """Individual session history record"""
    session_id: str
    date: datetime
    duration_minutes: int
    emotional_state: EmotionType
    topics_discussed: List[str]
    crisis_level: CrisisLevel
    intervention_needed: bool = False


class UserProfile(BaseModel):
    """User profile with demographics and baseline data"""
    id: str
    age: int = Field(ge=13, le=100)
    gender: str
    location: str
    primary_language: str
    secondary_language: Optional[str] = None
    cultural_background: str
    education_level: str
    occupation: str
    baseline_data: BaselineData
    session_history: List[SessionHistory] = Field(default_factory=list)


class SwahiliPattern(BaseModel):
    """Swahili language pattern for cultural context"""
    id: str
    pattern: str
    language: str = "swahili"
    meaning: str
    emotional_weight: str  # low, medium, high
    cultural_significance: str
    deflection_indicator: bool = False
    crisis_level: CrisisLevel
    appropriate_responses: List[str] = Field(default_factory=list)


class CulturalScenario(BaseModel):
    """Cultural scenario definition"""
    id: str
    scenario_type: CulturalScenarioType
    title: str
    description: str
    cultural_elements: List[str]
    appropriate_responses: List[str]
    sensitivity_level: str  # low, medium, high


class AudioFeatures(BaseModel):
    """Simulated audio features"""
    mfcc: List[float] = Field(default_factory=list)
    spectral_features: Dict[str, float] = Field(default_factory=dict)
    prosodic_features: Dict[str, float] = Field(default_factory=dict)
    quality_metrics: Dict[str, float] = Field(default_factory=dict)


class VoiceTruthGap(BaseModel):
    """Voice-truth dissonance analysis"""
    text_emotion: EmotionType
    voice_emotion: EmotionType
    dissonance_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    indicators: List[str] = Field(default_factory=list)


class DissonanceResult(BaseModel):
    """Dissonance detection result"""
    detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    voice_truth_gap: VoiceTruthGap
    explanation: str


class DeflectionResult(BaseModel):
    """Cultural deflection detection result"""
    detected: bool
    confidence: float = Field(ge=0.0, le=1.0)
    patterns: List[str] = Field(default_factory=list)
    cultural_context: str
    suggested_response: str


# Configuration Models

class DemoConfig(BaseModel):
    """Configuration for demo data generation"""
    num_users: int = Field(default=10, ge=1, le=1000)
    conversations_per_user: int = Field(default=5, ge=1, le=50)
    cultural_scenarios: int = Field(default=20, ge=1, le=100)
    swahili_patterns: int = Field(default=50, ge=1, le=500)
    output_directory: str = Field(default="demo_data")
    include_crisis_scenarios: bool = True
    crisis_scenario_percentage: float = Field(default=0.1, ge=0.0, le=1.0)
    emotional_diversity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    cultural_authenticity_check: bool = True


class GenerationResult(BaseModel):
    """Result of data generation process"""
    success: bool
    users_generated: int
    conversations_generated: int
    cultural_scenarios_generated: int
    swahili_patterns_generated: int
    output_directory: str
    generation_time_seconds: float
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Result of data validation process"""
    valid: bool
    total_files_checked: int
    corrupted_files: List[str] = Field(default_factory=list)
    missing_files: List[str] = Field(default_factory=list)
    validation_errors: List[str] = Field(default_factory=list)


# API Response Models

class APIResponse(BaseModel):
    """Base API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationResponse(APIResponse):
    """API response for conversation requests"""
    conversation: Optional[ConversationThread] = None


class EmotionAnalysisResponse(APIResponse):
    """API response for emotion analysis requests"""
    emotion_result: Optional[EmotionResult] = None


class CulturalAnalysisResponse(APIResponse):
    """API response for cultural analysis requests"""
    cultural_context: Optional[CulturalContext] = None
    deflection_result: Optional[DeflectionResult] = None


class VoiceAnalysisResponse(APIResponse):
    """API response for voice analysis requests"""
    audio_features: Optional[AudioFeatures] = None
    dissonance_result: Optional[DissonanceResult] = None


# Service Configuration Models

class ServiceConfig(BaseModel):
    """Configuration for demo services"""
    mock_api_port: int = Field(default=8001, ge=1024, le=65535)
    frontend_port: int = Field(default=3000, ge=1024, le=65535)
    auto_open_browser: bool = True
    processing_delay_ms: int = Field(default=500, ge=0, le=5000)
    enable_websockets: bool = True
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])


class ProcessInfo(BaseModel):
    """Information about running processes"""
    process_id: int
    name: str
    port: int
    status: str  # running, stopped, error
    start_time: datetime
    url: Optional[str] = None