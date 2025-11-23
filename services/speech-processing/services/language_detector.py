"""
Language Detection Service for East African languages
"""

import numpy as np
import librosa
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from config import settings
from models.stt_models import LanguageDetectionResult

logger = logging.getLogger(__name__)

class LanguageDetector:
    """Language detection service for audio"""
    
    def __init__(self):
        self.supported_languages = ["en", "sw"]  # English and Swahili
        self.language_models = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize language detection models"""
        try:
            # Load language detection models
            # For now, we'll use a simple approach based on audio features
            # In production, this would load pre-trained models
            
            self.language_models = {
                "en": {
                    "name": "English",
                    "features": self._get_english_features(),
                    "weight": 1.0
                },
                "sw": {
                    "name": "Swahili", 
                    "features": self._get_swahili_features(),
                    "weight": 1.0
                }
            }
            
            self.initialized = True
            logger.info("Language Detector initialized successfully")
            
        except Exception as e:
            logger.error(f"Language Detector initialization failed: {str(e)}")
            raise
    
    async def detect_language(
        self,
        audio: np.ndarray,
        sample_rate: int = None
    ) -> LanguageDetectionResult:
        """
        Detect language from audio
        """
        if not self.initialized:
            await self.initialize()
        
        start_time = datetime.utcnow()
        
        try:
            if sample_rate is None:
                sample_rate = settings.SAMPLE_RATE
            
            # Extract audio features
            features = self._extract_language_features(audio, sample_rate)
            
            # Calculate language probabilities
            language_scores = {}
            for lang_code, lang_model in self.language_models.items():
                score = self._calculate_language_score(features, lang_model)
                language_scores[lang_code] = score
            
            # Get best language
            best_language = max(language_scores, key=language_scores.get)
            confidence = language_scores[best_language]
            
            # Get alternatives
            alternatives = []
            for lang_code, score in language_scores.items():
                if lang_code != best_language:
                    alternatives.append({
                        "language": lang_code,
                        "name": self.language_models[lang_code]["name"],
                        "confidence": score
                    })
            
            # Sort alternatives by confidence
            alternatives.sort(key=lambda x: x["confidence"], reverse=True)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            return LanguageDetectionResult(
                language=best_language,
                name=self.language_models[best_language]["name"],
                confidence=confidence,
                alternatives=alternatives,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Language detection failed: {str(e)}")
            # Return default result
            return LanguageDetectionResult(
                language="en",
                name="English",
                confidence=0.5,
                alternatives=[],
                processing_time=(datetime.utcnow() - start_time).total_seconds()
            )
    
    def _extract_language_features(self, audio: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Extract features for language detection"""
        try:
            features = {}
            
            # Basic audio features
            features["duration"] = len(audio) / sample_rate
            features["rms_energy"] = np.sqrt(np.mean(audio**2))
            features["zero_crossing_rate"] = np.mean(librosa.feature.zero_crossing_rate(audio))
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            features["spectral_centroid_mean"] = np.mean(spectral_centroids)
            features["spectral_centroid_std"] = np.std(spectral_centroids)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=13)
            for i in range(13):
                features[f"mfcc_{i}_mean"] = np.mean(mfccs[i])
                features[f"mfcc_{i}_std"] = np.std(mfccs[i])
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=sample_rate)
            for i in range(12):
                features[f"chroma_{i}_mean"] = np.mean(chroma[i])
            
            # Spectral rolloff
            rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
            features["spectral_rolloff_mean"] = np.mean(rolloff)
            features["spectral_rolloff_std"] = np.std(rolloff)
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return {}
    
    def _calculate_language_score(self, features: Dict[str, float], lang_model: Dict[str, Any]) -> float:
        """Calculate language score based on features"""
        try:
            if not features:
                return 0.5  # Default score
            
            # Simple scoring based on feature similarity
            # In production, this would use a trained classifier
            score = 0.5  # Base score
            
            # Adjust score based on known language characteristics
            lang_code = None
            for code, model in self.language_models.items():
                if model == lang_model:
                    lang_code = code
                    break
            
            if lang_code == "en":
                # English characteristics
                if "spectral_centroid_mean" in features:
                    if 1000 <= features["spectral_centroid_mean"] <= 3000:
                        score += 0.2
                if "zero_crossing_rate" in features:
                    if 0.05 <= features["zero_crossing_rate"] <= 0.15:
                        score += 0.2
            
            elif lang_code == "sw":
                # Swahili characteristics (would need actual data to tune)
                if "spectral_centroid_mean" in features:
                    if 800 <= features["spectral_centroid_mean"] <= 2500:
                        score += 0.2
                if "zero_crossing_rate" in features:
                    if 0.04 <= features["zero_crossing_rate"] <= 0.12:
                        score += 0.2
            
            return min(1.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Score calculation failed: {str(e)}")
            return 0.5
    
    def _get_english_features(self) -> Dict[str, Any]:
        """Get typical English language features"""
        return {
            "spectral_centroid_range": (1000, 3000),
            "zero_crossing_rate_range": (0.05, 0.15),
            "mfcc_patterns": "english_mfcc_patterns"
        }
    
    def _get_swahili_features(self) -> Dict[str, Any]:
        """Get typical Swahili language features"""
        return {
            "spectral_centroid_range": (800, 2500),
            "zero_crossing_rate_range": (0.04, 0.12),
            "mfcc_patterns": "swahili_mfcc_patterns"
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of language detection service"""
        return {
            "status": "healthy" if self.initialized else "unhealthy",
            "supported_languages": self.supported_languages,
            "models_loaded": len(self.language_models)
        }
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about language detection models"""
        return {
            "supported_languages": self.supported_languages,
            "models": {
                lang_code: {
                    "name": model["name"],
                    "status": "loaded" if self.initialized else "not_loaded"
                }
                for lang_code, model in self.language_models.items()
            },
            "initialized": self.initialized
        }
