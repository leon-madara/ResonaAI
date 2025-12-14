"""
Advanced content filtering algorithms for safety moderation
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class ContentFilter:
    """Advanced content filtering with ML-based classification"""
    
    def __init__(self):
        """Initialize content filter"""
        # Expanded crisis terms
        self.crisis_terms = [
            "suicide", "kill myself", "end it all", "better off dead",
            "self harm", "cut myself", "want to die", "no point living",
            "end my life", "take my life", "harm myself"
        ]
        
        # Medical advice terms
        self.medical_advice_terms = [
            "take these pills", "increase your dose", "stop your medication",
            "how to kill", "prescribe", "diagnosis", "you have", "you need medication"
        ]
        
        # Toxicity patterns
        self.toxicity_patterns = [
            r"\b(hate|kill|destroy|hurt)\s+(you|yourself|them)\b",
            r"\b(worthless|useless|pathetic|stupid)\b",
        ]
        
        # Unsafe advice patterns
        self.unsafe_advice_patterns = [
            r"you should (harm|hurt|kill|end)",
            r"try (suicide|self-harm|cutting)",
            r"the best way to (die|kill yourself)",
        ]
    
    def detect_crisis_signals(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detect crisis signals in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (detected, confidence, matched_terms)
        """
        text_lower = text.lower()
        matched_terms = []
        
        for term in self.crisis_terms:
            if term in text_lower:
                matched_terms.append(term)
        
        detected = len(matched_terms) > 0
        confidence = min(0.9, 0.5 + (len(matched_terms) * 0.1))
        
        return detected, confidence, matched_terms
    
    def detect_medical_advice(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Detect medical advice or prescribing language.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (detected, confidence, matched_terms)
        """
        text_lower = text.lower()
        matched_terms = []
        
        for term in self.medical_advice_terms:
            if term in text_lower:
                matched_terms.append(term)
        
        # Check regex patterns
        for pattern in self.unsafe_advice_patterns:
            if re.search(pattern, text_lower):
                matched_terms.append(f"pattern:{pattern}")
        
        detected = len(matched_terms) > 0
        confidence = min(0.95, 0.6 + (len(matched_terms) * 0.15))
        
        return detected, confidence, matched_terms
    
    def detect_toxicity(self, text: str) -> Tuple[bool, float]:
        """
        Detect toxic or harmful language.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (detected, confidence)
        """
        text_lower = text.lower()
        
        for pattern in self.toxicity_patterns:
            if re.search(pattern, text_lower):
                return True, 0.8
        
        return False, 0.0
    
    def calculate_risk_score(
        self,
        text: str,
        content_type: str = "response"
    ) -> Dict[str, Any]:
        """
        Calculate overall risk score for content.
        
        Args:
            text: Content to analyze
            content_type: "response" or "user_input"
            
        Returns:
            Dictionary with risk analysis
        """
        crisis_detected, crisis_confidence, crisis_terms = self.detect_crisis_signals(text)
        medical_detected, medical_confidence, medical_terms = self.detect_medical_advice(text)
        toxicity_detected, toxicity_confidence = self.detect_toxicity(text)
        
        # Calculate overall risk score (0-1)
        risk_factors = []
        if crisis_detected:
            risk_factors.append(crisis_confidence * 0.4)
        if medical_detected:
            risk_factors.append(medical_confidence * 0.5)
        if toxicity_detected:
            risk_factors.append(toxicity_confidence * 0.3)
        
        risk_score = sum(risk_factors) if risk_factors else 0.0
        risk_score = min(1.0, risk_score)
        
        # Determine action
        if content_type == "response":
            if medical_detected or (crisis_detected and risk_score > 0.7):
                action = "block"
            elif crisis_detected or toxicity_detected:
                action = "review"
            else:
                action = "allow"
        else:  # user_input
            if medical_detected:
                action = "review"
            elif crisis_detected:
                action = "review"  # Allow but flag
            else:
                action = "allow"
        
        return {
            "risk_score": risk_score,
            "crisis_detected": crisis_detected,
            "crisis_confidence": crisis_confidence,
            "crisis_terms": crisis_terms,
            "medical_advice_detected": medical_detected,
            "medical_confidence": medical_confidence,
            "medical_terms": medical_terms,
            "toxicity_detected": toxicity_detected,
            "toxicity_confidence": toxicity_confidence,
            "recommended_action": action,
        }


# Global instance
_content_filter: Optional[ContentFilter] = None


def get_content_filter() -> ContentFilter:
    """Get or create content filter instance"""
    global _content_filter
    if _content_filter is None:
        _content_filter = ContentFilter()
    return _content_filter

