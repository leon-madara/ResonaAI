"""
Sentiment Analyzer Service
Analyzes sentiment from transcript text using transformers
"""

import logging
from typing import Dict, Optional
from transformers import pipeline
import torch

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze sentiment from transcript text"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.sentiment_pipeline = None
        self.cache: Dict[str, Dict] = {}
        self._model_loaded = False
        
    async def load_model(self):
        """Load sentiment analysis model"""
        if self._model_loaded:
            return
            
        try:
            logger.info(f"Loading sentiment model: {self.model_name}")
            
            # Use device_map="auto" for GPU support if available
            device = 0 if torch.cuda.is_available() else -1
            
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                return_all_scores=True,
                device=device
            )
            self._model_loaded = True
            logger.info(f"Sentiment model loaded successfully on device {device}")
        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            raise
    
    async def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        
        Returns:
        {
            "label": "positive",  # or "negative", "neutral"
            "score": 0.85,
            "valence": 0.75  # -1 to 1
        }
        """
        if not self._model_loaded:
            await self.load_model()
        
        # Check cache
        cache_key = text.lower().strip()
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Analyze
            results = self.sentiment_pipeline(text)
            
            # Extract best result
            if isinstance(results, list) and len(results) > 0:
                scores = results[0] if isinstance(results[0], list) else results
                best_result = max(scores, key=lambda x: x['score'])
            else:
                # Fallback
                best_result = {"label": "neutral", "score": 0.5}
            
            # Map to valence (-1 to 1)
            label = best_result['label'].lower()
            score = best_result['score']
            
            if 'positive' in label or 'pos' in label:
                valence = score
            elif 'negative' in label or 'neg' in label:
                valence = -score
            else:  # neutral
                valence = 0.0
            
            result = {
                "label": label,
                "score": score,
                "valence": valence
            }
            
            # Cache result (with size limit)
            if len(self.cache) < 1000:
                self.cache[cache_key] = result
            else:
                # Remove oldest entry (simple FIFO)
                first_key = next(iter(self.cache))
                del self.cache[first_key]
                self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            # Return neutral as fallback
            return {
                "label": "neutral",
                "score": 0.5,
                "valence": 0.0
            }

