"""
Risk Calculator Service
Calculates risk scores from multiple detection methods
"""

import logging
from typing import Dict, Optional, List
import re

logger = logging.getLogger(__name__)


class RiskCalculator:
    """Calculate risk scores from multiple sources"""
    
    def __init__(self, thresholds: Dict[str, float], crisis_keywords: List[str]):
        self.thresholds = thresholds
        self.crisis_keywords = [kw.lower() for kw in crisis_keywords]
    
    def calculate_risk(
        self,
        transcript: Optional[str] = None,
        emotion_data: Optional[Dict] = None,
        dissonance_data: Optional[Dict] = None,
        baseline_data: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate overall risk score
        
        Returns:
            {
                "risk_level": "high",
                "risk_score": 0.75,
                "crisis_detected": True,
                "detection_methods": ["keyword", "dissonance"],
                "escalation_required": True,
                "recommended_action": "immediate_human_review"
            }
        """
        detection_methods = []
        risk_scores = []
        
        # Keyword detection
        if transcript:
            keyword_risk = self._detect_keywords(transcript)
            if keyword_risk > 0:
                detection_methods.append("keyword")
                risk_scores.append(keyword_risk)
        
        # Emotion-based detection
        if emotion_data:
            emotion_risk = self._detect_emotion_risk(emotion_data)
            if emotion_risk > 0:
                detection_methods.append("emotion")
                risk_scores.append(emotion_risk)
        
        # Dissonance-based detection
        if dissonance_data:
            dissonance_risk = self._detect_dissonance_risk(dissonance_data)
            if dissonance_risk > 0:
                detection_methods.append("dissonance")
                risk_scores.append(dissonance_risk)
        
        # Baseline deviation detection
        if baseline_data:
            baseline_risk = self._detect_baseline_risk(baseline_data)
            if baseline_risk > 0:
                detection_methods.append("baseline_deviation")
                risk_scores.append(baseline_risk)
        
        # Calculate overall risk (weighted average, with higher weights for more severe indicators)
        if risk_scores:
            # Weight keyword detection more heavily
            weighted_scores = []
            for i, score in enumerate(risk_scores):
                method = detection_methods[i] if i < len(detection_methods) else "unknown"
                weight = 1.5 if method == "keyword" else 1.0
                weighted_scores.append(score * weight)
            
            overall_risk = sum(weighted_scores) / sum([1.5 if m == "keyword" else 1.0 for m in detection_methods])
        else:
            overall_risk = 0.0
        
        # Determine risk level
        risk_level = self._get_risk_level(overall_risk)
        
        # Determine if escalation is required
        escalation_required = risk_level in ["high", "critical"]
        
        # Recommended action
        if risk_level == "critical":
            recommended_action = "immediate_emergency_contact"
        elif risk_level == "high":
            recommended_action = "immediate_human_review"
        elif risk_level == "medium":
            recommended_action = "human_review_queue"
        else:
            recommended_action = "monitor"
        
        return {
            "risk_level": risk_level,
            "risk_score": overall_risk,
            "crisis_detected": overall_risk >= self.thresholds["medium"],
            "detection_methods": detection_methods,
            "escalation_required": escalation_required,
            "recommended_action": recommended_action
        }
    
    def _detect_keywords(self, text: str) -> float:
        """Detect crisis keywords in text"""
        text_lower = text.lower()
        matches = sum(1 for keyword in self.crisis_keywords if keyword in text_lower)
        
        if matches > 0:
            # More matches = higher risk
            return min(0.9, 0.5 + (matches * 0.2))
        return 0.0
    
    def _detect_emotion_risk(self, emotion_data: Dict) -> float:
        """Detect risk from emotion data"""
        emotion = emotion_data.get("emotion", "neutral").lower()
        confidence = emotion_data.get("confidence", 0.5)
        
        high_risk_emotions = ["sad", "angry", "fear", "anxious"]
        if emotion in high_risk_emotions:
            return 0.3 * confidence
        return 0.0
    
    def _detect_dissonance_risk(self, dissonance_data: Dict) -> float:
        """Detect risk from dissonance data"""
        dissonance_level = dissonance_data.get("dissonance_level", "low")
        interpretation = dissonance_data.get("interpretation", "")
        
        if dissonance_level == "high" and interpretation == "defensive_concealment":
            return 0.6
        elif dissonance_level == "high":
            return 0.4
        elif dissonance_level == "medium":
            return 0.2
        return 0.0
    
    def _detect_baseline_risk(self, baseline_data: Dict) -> float:
        """Detect risk from baseline deviation"""
        deviation_detected = baseline_data.get("deviation_detected", False)
        deviation_score = baseline_data.get("deviation_score", 0.0)
        
        if deviation_detected:
            return min(0.5, deviation_score)
        return 0.0
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Get risk level from score"""
        if risk_score >= self.thresholds["critical"]:
            return "critical"
        elif risk_score >= self.thresholds["high"]:
            return "high"
        elif risk_score >= self.thresholds["medium"]:
            return "medium"
        else:
            return "low"

