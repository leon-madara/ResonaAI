"""
Emotion detection using pre-trained models and feature-based classification
"""

import numpy as np
import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, Any, Tuple, Optional
import logging
from loguru import logger
from datetime import datetime

from .config import settings
from .models import EmotionResult, AudioFeatures, EmotionPrediction

class EmotionDetector:
    """Emotion detection using multiple approaches"""
    
    def __init__(self):
        self.model_name = settings.MODEL_NAME
        self.emotion_labels = settings.EMOTION_LABELS
        self.min_confidence = settings.MIN_CONFIDENCE
        
        # Model components
        self.wav2vec2_processor = None
        self.wav2vec2_model = None
        self.emotion_classifier = None
        self.feature_scaler = None
        
        # Feature weights for ensemble
        self.feature_weights = {
            'wav2vec2': 0.4,
            'mfcc': 0.2,
            'spectral': 0.2,
            'prosodic': 0.2
        }
    
    async def load_models(self):
        """Load pre-trained models"""
        try:
            logger.info("Loading emotion detection models...")
            
            # Load Wav2Vec2 model
            await self._load_wav2vec2_model()
            
            # Load emotion classifier
            await self._load_emotion_classifier()
            
            logger.info("All models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    async def _load_wav2vec2_model(self):
        """Load Wav2Vec2 model for feature extraction"""
        try:
            logger.info(f"Loading Wav2Vec2 model: {self.model_name}")
            
            self.wav2vec2_processor = Wav2Vec2Processor.from_pretrained(self.model_name)
            self.wav2vec2_model = Wav2Vec2Model.from_pretrained(self.model_name)
            
            # Set to evaluation mode
            self.wav2vec2_model.eval()
            
            logger.info("Wav2Vec2 model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading Wav2Vec2 model: {str(e)}")
            raise
    
    async def _load_emotion_classifier(self):
        """Load emotion classification model"""
        try:
            model_path = settings.EMOTION_MODEL_PATH
            
            if os.path.exists(model_path):
                logger.info(f"Loading emotion classifier from {model_path}")
                model_data = joblib.load(model_path)
                self.emotion_classifier = model_data['classifier']
                self.feature_scaler = model_data['scaler']
            else:
                logger.warning(f"Emotion classifier not found at {model_path}, using default model")
                await self._create_default_classifier()
            
            logger.info("Emotion classifier loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading emotion classifier: {str(e)}")
            await self._create_default_classifier()
    
    async def _create_default_classifier(self):
        """Create a default emotion classifier"""
        logger.info("Creating default emotion classifier")
        
        # Create a simple Random Forest classifier
        self.emotion_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            max_depth=10
        )
        
        # Create a standard scaler
        self.feature_scaler = StandardScaler()
        
        # Train with dummy data (in production, this would be pre-trained)
        dummy_features = np.random.randn(1000, 50)  # 50 features
        dummy_labels = np.random.choice(self.emotion_labels, 1000)
        
        scaled_features = self.feature_scaler.fit_transform(dummy_features)
        self.emotion_classifier.fit(scaled_features, dummy_labels)
        
        logger.info("Default emotion classifier created")
    
    async def detect_emotion(self, audio: np.ndarray) -> EmotionResult:
        """
        Detect emotion from audio
        
        Args:
            audio: Preprocessed audio array
            
        Returns:
            EmotionResult with detected emotion and confidence
        """
        try:
            start_time = datetime.now()
            
            # Extract features
            features = await self._extract_all_features(audio)
            
            # Predict emotion
            emotion_prediction = await self._predict_emotion(features)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = EmotionResult(
                emotion=emotion_prediction.emotion,
                confidence=emotion_prediction.confidence,
                timestamp=datetime.now(),
                features=features,
                processing_time=processing_time
            )
            
            logger.info(f"Emotion detected: {result.emotion} (confidence: {result.confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error detecting emotion: {str(e)}")
            raise
    
    async def _extract_all_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract all features for emotion detection"""
        features = {}
        
        # Wav2Vec2 features
        # Always include the key (tests and downstream code expect it).
        # If the model isn't loaded, `_extract_wav2vec2_features` returns a zero vector.
        features['wav2vec2'] = await self._extract_wav2vec2_features(audio)
        
        # Traditional audio features
        features['mfcc'] = self._extract_mfcc_features(audio)
        features['spectral'] = self._extract_spectral_features(audio)
        features['prosodic'] = self._extract_prosodic_features(audio)
        features['temporal'] = self._extract_temporal_features(audio)
        features['statistical'] = self._extract_statistical_features(audio)
        
        return features
    
    async def _extract_wav2vec2_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract Wav2Vec2 features"""
        try:
            # Ensure audio is in the right format
            if len(audio.shape) == 1:
                audio = audio.reshape(1, -1)
            
            # Process audio
            inputs = self.wav2vec2_processor(
                audio.flatten(), 
                sampling_rate=settings.SAMPLE_RATE, 
                return_tensors="pt"
            )
            
            # Extract features
            with torch.no_grad():
                outputs = self.wav2vec2_model(**inputs)
                features = outputs.last_hidden_state.mean(dim=1).numpy()
            
            return features.flatten()
            
        except Exception as e:
            logger.error(f"Error extracting Wav2Vec2 features: {str(e)}")
            return np.zeros(768)  # Default Wav2Vec2 feature size
    
    def _extract_mfcc_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract MFCC features"""
        try:
            import librosa
            mfcc = librosa.feature.mfcc(
                y=audio, 
                sr=settings.SAMPLE_RATE, 
                n_mfcc=settings.MFCC_FEATURES
            )
            return mfcc.mean(axis=1)  # Average over time
        except Exception as e:
            logger.error(f"Error extracting MFCC features: {str(e)}")
            return np.zeros(settings.MFCC_FEATURES)
    
    def _extract_spectral_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract spectral features"""
        try:
            import librosa
            features = []
            
            # Spectral centroid
            features.append(np.mean(librosa.feature.spectral_centroid(y=audio, sr=settings.SAMPLE_RATE)))
            
            # Spectral rolloff
            features.append(np.mean(librosa.feature.spectral_rolloff(y=audio, sr=settings.SAMPLE_RATE)))
            
            # Spectral bandwidth
            features.append(np.mean(librosa.feature.spectral_bandwidth(y=audio, sr=settings.SAMPLE_RATE)))
            
            # Zero crossing rate
            features.append(np.mean(librosa.feature.zero_crossing_rate(audio)))
            
            return np.array(features)
        except Exception as e:
            logger.error(f"Error extracting spectral features: {str(e)}")
            return np.zeros(4)
    
    def _extract_prosodic_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract prosodic features"""
        try:
            import librosa
            features = []
            
            # Fundamental frequency
            f0, voiced_flag, _ = librosa.pyin(
                audio, 
                fmin=librosa.note_to_hz('C2'), 
                fmax=librosa.note_to_hz('C7'),
                sr=settings.SAMPLE_RATE
            )
            
            f0_voiced = f0[voiced_flag]
            if len(f0_voiced) > 0:
                features.extend([np.mean(f0_voiced), np.std(f0_voiced)])
            else:
                features.extend([0.0, 0.0])
            
            # Energy
            rms = librosa.feature.rms(y=audio)
            features.append(np.mean(rms))
            features.append(np.std(rms))
            
            return np.array(features)
        except Exception as e:
            logger.error(f"Error extracting prosodic features: {str(e)}")
            return np.zeros(4)
    
    def _extract_temporal_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract temporal features"""
        try:
            features = []
            
            # Duration
            features.append(len(audio) / settings.SAMPLE_RATE)
            
            # Basic statistics
            features.extend([np.mean(audio), np.std(audio), np.var(audio)])
            
            return np.array(features)
        except Exception as e:
            logger.error(f"Error extracting temporal features: {str(e)}")
            return np.zeros(4)
    
    def _extract_statistical_features(self, audio: np.ndarray) -> np.ndarray:
        """Extract statistical features"""
        try:
            features = []
            
            # Percentiles
            features.extend([
                np.percentile(audio, 25),
                np.percentile(audio, 50),
                np.percentile(audio, 75),
                np.percentile(audio, 90)
            ])
            
            # Skewness and kurtosis
            mean = np.mean(audio)
            std = np.std(audio)
            if std > 0:
                features.append(np.mean(((audio - mean) / std) ** 3))  # Skewness
                features.append(np.mean(((audio - mean) / std) ** 4) - 3)  # Kurtosis
            else:
                features.extend([0.0, 0.0])
            
            return np.array(features)
        except Exception as e:
            logger.error(f"Error extracting statistical features: {str(e)}")
            return np.zeros(6)
    
    async def _predict_emotion(self, features: Dict[str, Any]) -> EmotionPrediction:
        """Predict emotion using ensemble approach"""
        try:
            # Combine features
            combined_features = self._combine_features(features)
            
            # Scale features
            if self.feature_scaler is not None:
                scaled_features = self.feature_scaler.transform(combined_features.reshape(1, -1))
            else:
                scaled_features = combined_features.reshape(1, -1)
            
            # Predict probabilities
            if self.emotion_classifier is not None:
                probabilities = self.emotion_classifier.predict_proba(scaled_features)[0]
            else:
                # Fallback to random probabilities
                probabilities = np.random.dirichlet(np.ones(len(self.emotion_labels)))
            
            # Create probability dictionary
            prob_dict = dict(zip(self.emotion_labels, probabilities))
            
            # Get predicted emotion and confidence
            predicted_idx = np.argmax(probabilities)
            predicted_emotion = self.emotion_labels[predicted_idx]
            confidence = probabilities[predicted_idx]
            
            # Apply confidence threshold
            if confidence < self.min_confidence:
                predicted_emotion = "neutral"
                confidence = 0.5
            
            return EmotionPrediction(
                emotion=predicted_emotion,
                confidence=confidence,
                probabilities=prob_dict,
                features_used=list(features.keys())
            )
            
        except Exception as e:
            logger.error(f"Error predicting emotion: {str(e)}")
            # Return neutral as fallback
            return EmotionPrediction(
                emotion="neutral",
                confidence=0.5,
                probabilities={emotion: 1.0/len(self.emotion_labels) for emotion in self.emotion_labels},
                features_used=[]
            )
    
    def _combine_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Combine all features into a single vector"""
        combined = []
        
        # Add features in order of importance
        for feature_type in ['wav2vec2', 'mfcc', 'spectral', 'prosodic', 'temporal', 'statistical']:
            if feature_type in features:
                if isinstance(features[feature_type], np.ndarray):
                    combined.extend(features[feature_type])
                elif isinstance(features[feature_type], dict):
                    combined.extend(features[feature_type].values())
                elif isinstance(features[feature_type], list):
                    combined.extend(features[feature_type])
        
        return np.array(combined)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded models"""
        return {
            "wav2vec2_model": self.model_name,
            "emotion_classifier": "RandomForest" if self.emotion_classifier else None,
            "feature_scaler": "StandardScaler" if self.feature_scaler else None,
            "supported_emotions": self.emotion_labels,
            "feature_weights": self.feature_weights,
            "min_confidence": self.min_confidence
        }
