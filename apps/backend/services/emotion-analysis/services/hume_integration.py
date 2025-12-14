"""
Hume AI integration for emotion analysis
"""

import os
import logging
import requests
from typing import Dict, Any, Optional, List
import base64

logger = logging.getLogger(__name__)

HUME_API_KEY = os.getenv("HUME_API_KEY")
HUME_API_URL = os.getenv("HUME_API_URL", "https://api.hume.ai/v0/stream/models")


class HumeIntegration:
    """Integration with Hume AI for emotion analysis"""
    
    def __init__(self):
        """Initialize Hume AI integration"""
        self.api_key = HUME_API_KEY
        self.api_url = HUME_API_URL
        self.available = bool(self.api_key)
        
        if not self.available:
            logger.warning("Hume AI API key not configured")
    
    def analyze_audio(
        self,
        audio_data: bytes,
        audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Analyze emotion from audio using Hume AI.
        
        Args:
            audio_data: Audio file bytes
            audio_format: Audio format (wav, mp3, etc.)
            
        Returns:
            Dictionary with emotion analysis results
        """
        if not self.available:
            raise ValueError("Hume AI not configured")
        
        try:
            # Encode audio to base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            # Prepare request
            headers = {
                "X-Hume-Api-Key": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "models": {
                    "language": {},
                    "prosody": {},
                    "face": {}
                },
                "raw_text": False,
                "audio": {
                    "encoding": audio_format,
                    "sample_rate": 16000
                }
            }
            
            # Send request
            response = requests.post(
                f"{self.api_url}/prosody",
                headers=headers,
                json=payload,
                files={"file": audio_data},
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Hume AI API error: {response.status_code} - {response.text}")
                raise Exception(f"Hume AI API error: {response.status_code}")
            
            result = response.json()
            
            # Extract emotion data
            emotions = self._extract_emotions(result)
            
            return {
                "emotion": emotions.get("primary_emotion", "neutral"),
                "confidence": emotions.get("confidence", 0.0),
                "probabilities": emotions.get("probabilities", {}),
                "raw_response": result,
                "source": "hume_ai"
            }
            
        except Exception as e:
            logger.error(f"Hume AI analysis failed: {e}")
            raise
    
    def _extract_emotions(self, hume_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract emotion data from Hume AI response.
        
        Args:
            hume_response: Raw Hume AI API response
            
        Returns:
            Dictionary with extracted emotion data
        """
        emotions = {
            "probabilities": {},
            "primary_emotion": "neutral",
            "confidence": 0.0
        }
        
        try:
            # Parse Hume AI response structure
            # Response format may vary, this is a generic parser
            if "predictions" in hume_response:
                for prediction in hume_response["predictions"]:
                    if "emotions" in prediction:
                        for emotion_data in prediction["emotions"]:
                            emotion_name = emotion_data.get("name", "").lower()
                            score = emotion_data.get("score", 0.0)
                            emotions["probabilities"][emotion_name] = score
                    
                    # Prosody model provides overall emotion
                    if "prosody" in prediction:
                        prosody = prediction["prosody"]
                        if "emotions" in prosody:
                            for emotion_data in prosody["emotions"]:
                                emotion_name = emotion_data.get("name", "").lower()
                                score = emotion_data.get("score", 0.0)
                                emotions["probabilities"][emotion_name] = score
            
            # Find primary emotion (highest score)
            if emotions["probabilities"]:
                primary_emotion = max(
                    emotions["probabilities"].items(),
                    key=lambda x: x[1]
                )
                emotions["primary_emotion"] = primary_emotion[0]
                emotions["confidence"] = primary_emotion[1]
        
        except Exception as e:
            logger.warning(f"Failed to extract emotions from Hume response: {e}")
        
        return emotions
    
    def is_available(self) -> bool:
        """Check if Hume AI is available"""
        return self.available


# Global instance
_hume_integration: Optional[HumeIntegration] = None


def get_hume_integration() -> HumeIntegration:
    """Get or create Hume AI integration instance"""
    global _hume_integration
    if _hume_integration is None:
        _hume_integration = HumeIntegration()
    return _hume_integration

