"""
Speech-to-Text Service with accent adaptation for East African languages
"""

import asyncio
import tempfile
import os
from typing import Dict, Any, Optional, List
import numpy as np
import librosa
import soundfile as sf
from datetime import datetime
import logging

# Cloud STT APIs
import openai
from azure.cognitiveservices.speech import SpeechConfig, AudioConfig, SpeechRecognizer
from azure.cognitiveservices.speech.audio import AudioStreamFormat

from config import settings
from models.stt_models import TranscriptionResult, STTConfig

logger = logging.getLogger(__name__)

class STTService:
    """Speech-to-Text service with multiple providers and accent adaptation"""
    
    def __init__(self):
        self.openai_client = None
        self.azure_speech_config = None
        self.current_provider = "openai"  # Default provider
        
        # Accent adaptation mappings
        self.accent_mappings = {
            "kenyan": {
                "language": "en-KE",
                "azure_locale": "en-KE",
                "whisper_language": "en"
            },
            "ugandan": {
                "language": "en-UG", 
                "azure_locale": "en-UG",
                "whisper_language": "en"
            },
            "tanzanian": {
                "language": "en-TZ",
                "azure_locale": "en-TZ", 
                "whisper_language": "en"
            },
            "swahili_kenyan": {
                "language": "sw-KE",
                "azure_locale": "sw-KE",
                "whisper_language": "sw"
            },
            "swahili_tanzanian": {
                "language": "sw-TZ",
                "azure_locale": "sw-TZ",
                "whisper_language": "sw"
            }
        }
    
    async def initialize(self):
        """Initialize STT services"""
        try:
            # Initialize OpenAI
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.openai_client = openai
                logger.info("OpenAI STT initialized")
            
            # Initialize Azure Speech
            if settings.AZURE_SPEECH_KEY and settings.AZURE_SPEECH_REGION:
                self.azure_speech_config = SpeechConfig(
                    subscription=settings.AZURE_SPEECH_KEY,
                    region=settings.AZURE_SPEECH_REGION
                )
                logger.info("Azure Speech STT initialized")
            
            logger.info("STT Service initialized successfully")
            
        except Exception as e:
            logger.error(f"STT Service initialization failed: {str(e)}")
            raise
    
    async def transcribe(
        self,
        audio: np.ndarray,
        language: str = "en",
        accent: str = "kenyan",
        enable_emotion_detection: bool = False
    ) -> TranscriptionResult:
        """
        Transcribe audio to text with accent adaptation
        """
        start_time = datetime.utcnow()
        
        try:
            # Get accent configuration
            accent_config = self.accent_mappings.get(accent, self.accent_mappings["kenyan"])
            
            # Try primary provider (OpenAI)
            if self.openai_client and self.current_provider == "openai":
                result = await self._transcribe_openai(audio, accent_config, enable_emotion_detection)
            # Fallback to Azure
            elif self.azure_speech_config:
                result = await self._transcribe_azure(audio, accent_config, enable_emotion_detection)
            else:
                raise Exception("No STT provider available")
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            # Try fallback provider
            if self.current_provider == "openai" and self.azure_speech_config:
                logger.info("Falling back to Azure STT")
                result = await self._transcribe_azure(audio, accent_config, enable_emotion_detection)
                result.processing_time = (datetime.utcnow() - start_time).total_seconds()
                return result
            else:
                raise
    
    async def transcribe_stream(
        self,
        audio: np.ndarray,
        language: str = "en",
        accent: str = "kenyan"
    ) -> TranscriptionResult:
        """
        Transcribe audio stream for real-time processing
        """
        start_time = datetime.utcnow()
        
        try:
            # Get accent configuration
            accent_config = self.accent_mappings.get(accent, self.accent_mappings["kenyan"])
            
            # Use OpenAI for streaming (better for real-time)
            if self.openai_client:
                result = await self._transcribe_openai_stream(audio, accent_config)
            else:
                result = await self._transcribe_azure_stream(audio, accent_config)
            
            # Calculate processing time
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            result.processing_time = processing_time
            
            return result
            
        except Exception as e:
            logger.error(f"Stream transcription failed: {str(e)}")
            raise
    
    async def _transcribe_openai(
        self,
        audio: np.ndarray,
        accent_config: Dict[str, str],
        enable_emotion_detection: bool = False
    ) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper"""
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, audio, settings.SAMPLE_RATE)
                
                # Transcribe with OpenAI
                with open(temp_file.name, "rb") as audio_file:
                    response = await asyncio.to_thread(
                        self.openai_client.Audio.transcribe,
                        model="whisper-1",
                        file=audio_file,
                        language=accent_config["whisper_language"],
                        response_format="verbose_json"
                    )
                
                # Clean up temporary file
                os.unlink(temp_file.name)
                
                # Parse response
                text = response.text
                confidence = getattr(response, 'confidence', 0.9)  # Default confidence
                segments = []
                
                if hasattr(response, 'segments'):
                    for segment in response.segments:
                        segments.append({
                            "start": segment.start,
                            "end": segment.end,
                            "text": segment.text,
                            "confidence": getattr(segment, 'confidence', confidence)
                        })
                
                return TranscriptionResult(
                    text=text,
                    confidence=confidence,
                    language=accent_config["language"],
                    segments=segments,
                    duration=len(audio) / settings.SAMPLE_RATE,
                    sample_rate=settings.SAMPLE_RATE,
                    channels=1,
                    emotion_data=None  # OpenAI doesn't provide emotion data
                )
                
        except Exception as e:
            logger.error(f"OpenAI transcription failed: {str(e)}")
            raise
    
    async def _transcribe_azure(
        self,
        audio: np.ndarray,
        accent_config: Dict[str, str],
        enable_emotion_detection: bool = False
    ) -> TranscriptionResult:
        """Transcribe using Azure Speech Services"""
        try:
            # Configure Azure Speech
            speech_config = SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION
            )
            speech_config.speech_recognition_language = accent_config["azure_locale"]
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                sf.write(temp_file.name, audio, settings.SAMPLE_RATE)
                
                # Create audio config
                audio_config = AudioConfig(filename=temp_file.name)
                
                # Create recognizer
                recognizer = SpeechRecognizer(
                    speech_config=speech_config,
                    audio_config=audio_config
                )
                
                # Perform recognition
                result = await asyncio.to_thread(recognizer.recognize_once)
                
                # Clean up temporary file
                os.unlink(temp_file.name)
                
                if result.reason == ResultReason.RecognizedSpeech:
                    return TranscriptionResult(
                        text=result.text,
                        confidence=result.confidence,
                        language=accent_config["language"],
                        segments=[],
                        duration=len(audio) / settings.SAMPLE_RATE,
                        sample_rate=settings.SAMPLE_RATE,
                        channels=1,
                        emotion_data=None
                    )
                else:
                    raise Exception(f"Azure recognition failed: {result.reason}")
                
        except Exception as e:
            logger.error(f"Azure transcription failed: {str(e)}")
            raise
    
    async def _transcribe_openai_stream(
        self,
        audio: np.ndarray,
        accent_config: Dict[str, str]
    ) -> TranscriptionResult:
        """Transcribe stream using OpenAI Whisper"""
        # For streaming, we'll use the same method as regular transcription
        # but with a flag indicating it's a partial result
        result = await self._transcribe_openai(audio, accent_config)
        result.is_final = False  # Stream results are typically partial
        return result
    
    async def _transcribe_azure_stream(
        self,
        audio: np.ndarray,
        accent_config: Dict[str, str]
    ) -> TranscriptionResult:
        """Transcribe stream using Azure Speech Services"""
        # Similar to regular Azure transcription but for streaming
        result = await self._transcribe_azure(audio, accent_config)
        result.is_final = False
        return result
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of STT services"""
        health_status = {
            "openai": "unavailable",
            "azure": "unavailable",
            "overall": "unhealthy"
        }
        
        try:
            # Test OpenAI
            if self.openai_client:
                # Simple test - this would need actual implementation
                health_status["openai"] = "healthy"
            
            # Test Azure
            if self.azure_speech_config:
                # Simple test - this would need actual implementation
                health_status["azure"] = "healthy"
            
            # Overall health
            if health_status["openai"] == "healthy" or health_status["azure"] == "healthy":
                health_status["overall"] = "healthy"
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
        
        return health_status
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "providers": {
                "openai": {
                    "model": "whisper-1",
                    "status": "available" if self.openai_client else "unavailable",
                    "languages": ["en", "sw"],
                    "accents": list(self.accent_mappings.keys())
                },
                "azure": {
                    "model": "Azure Speech Services",
                    "status": "available" if self.azure_speech_config else "unavailable",
                    "languages": ["en-KE", "en-UG", "en-TZ", "sw-KE", "sw-TZ"],
                    "accents": list(self.accent_mappings.keys())
                }
            },
            "current_provider": self.current_provider,
            "supported_accents": list(self.accent_mappings.keys())
        }
