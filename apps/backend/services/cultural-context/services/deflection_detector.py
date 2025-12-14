"""
Deflection detector with pattern matching and voice contradiction detection
Detects Swahili deflection patterns and correlates with voice analysis
"""

import json
import os
import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DeflectionMatch:
    """Represents a detected deflection pattern"""
    pattern: str
    pattern_type: str
    severity: str
    cultural_meaning: str
    interpretation: str
    probe_suggestions: List[str]
    confidence: float
    position: int
    context: str


@dataclass
class VoiceContradiction:
    """Represents a voice contradiction indicator"""
    indicator_type: str
    description: str
    severity_multiplier: float
    detected: bool
    confidence: float


class DeflectionDetector:
    """
    Detector for Swahili deflection patterns and voice contradictions.
    
    Detects:
    - Swahili deflection phrases
    - Cultural meaning of deflections
    - Voice contradictions (when voice tone contradicts words)
    - Severity assessment
    - Probe suggestions
    """
    
    def __init__(self, patterns_path: Optional[str] = None):
        """
        Initialize deflection detector.
        
        Args:
            patterns_path: Path to swahili_patterns.json file
        """
        if patterns_path is None:
            # Default paths
            default_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "data",
                "swahili_patterns.json"
            )
            mount_path = "/app/data/cultural-knowledge-base/swahili_patterns.json"
            
            if os.path.exists(mount_path):
                patterns_path = mount_path
            elif os.path.exists(default_path):
                patterns_path = default_path
            else:
                logger.warning(f"Swahili patterns file not found at {default_path} or {mount_path}")
                patterns_path = default_path
        
        self.patterns = self._load_patterns(patterns_path)
        self.voice_contradictions = self.patterns.get("voice_contradiction_indicators", [])
        
        # Build regex patterns for fast matching
        self.pattern_regexes = {}
        for pattern_data in self.patterns.get("patterns", []):
            pattern_text = pattern_data.get("pattern", "")
            # Create case-insensitive regex
            self.pattern_regexes[pattern_text] = re.compile(
                r'\b' + re.escape(pattern_text) + r'\b',
                re.IGNORECASE
            )
    
    def _load_patterns(self, path: str) -> Dict[str, Any]:
        """Load Swahili patterns from JSON file"""
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                logger.warning(f"Patterns file not found: {path}")
                return {"patterns": [], "voice_contradiction_indicators": []}
        except Exception as e:
            logger.error(f"Failed to load patterns from {path}: {e}")
            return {"patterns": [], "voice_contradiction_indicators": []}
    
    def detect_deflections(self, text: str, language: str = "auto") -> List[DeflectionMatch]:
        """
        Detect deflection patterns in text.
        
        Args:
            text: Text to analyze
            language: Language code ('en', 'sw', or 'auto')
            
        Returns:
            List of detected deflection matches
        """
        if not text or not text.strip():
            return []
        
        text_lower = text.lower()
        matches = []
        
        # Check each pattern
        for pattern_data in self.patterns.get("patterns", []):
            pattern_text = pattern_data.get("pattern", "")
            pattern_type = pattern_data.get("type", "unknown")
            
            # Check if pattern matches
            if pattern_text in self.pattern_regexes:
                regex = self.pattern_regexes[pattern_text]
                for match in regex.finditer(text_lower):
                    # Check if pattern type matches language preference
                    if language != "auto":
                        # Filter by language if specified
                        if pattern_type == "deflection" and language == "sw":
                            # Prefer Swahili patterns
                            pass
                        elif pattern_type != "deflection" and language == "en":
                            # Prefer English patterns
                            continue
                    
                    # Get context around match
                    start = max(0, match.start() - 30)
                    end = min(len(text), match.end() + 30)
                    context = text[start:end]
                    
                    # Calculate confidence based on context
                    confidence = self._calculate_confidence(
                        pattern_text,
                        context,
                        pattern_data
                    )
                    
                    matches.append(DeflectionMatch(
                        pattern=pattern_text,
                        pattern_type=pattern_type,
                        severity=pattern_data.get("severity", "low"),
                        cultural_meaning=pattern_data.get("cultural_meaning", ""),
                        interpretation=pattern_data.get("interpretation", ""),
                        probe_suggestions=pattern_data.get("probe_suggestions", []),
                        confidence=confidence,
                        position=match.start(),
                        context=context
                    ))
        
        # Sort by position
        matches.sort(key=lambda x: x.position)
        
        return matches
    
    def detect_voice_contradictions(self,
                                   text: str,
                                   voice_emotion: Optional[str] = None,
                                   voice_features: Optional[Dict[str, Any]] = None) -> List[VoiceContradiction]:
        """
        Detect voice contradictions (when voice tone contradicts words).
        
        Args:
            text: Text that was spoken
            voice_emotion: Detected voice emotion (e.g., 'sad', 'anxious', 'tired')
            voice_features: Voice features dict (pitch, energy, etc.)
            
        Returns:
            List of detected voice contradictions
        """
        contradictions = []
        
        if not voice_emotion:
            return contradictions
        
        text_lower = text.lower()
        
        # Check each contradiction indicator
        for indicator in self.voice_contradictions:
            indicator_type = indicator.get("indicator", "")
            description = indicator.get("description", "")
            
            detected = False
            confidence = 0.0
            
            # Check for specific contradiction patterns
            if "sad_voice_saying_okay" in indicator_type:
                # Sad voice saying okay/fine
                if voice_emotion in ["sad", "depressed", "hopeless"]:
                    if any(word in text_lower for word in ["sawa", "sijambo", "okay", "fine", "it's okay"]):
                        detected = True
                        confidence = 0.8
            
            elif "tired_voice_saying_fine" in indicator_type:
                # Tired voice saying fine
                if voice_emotion in ["tired", "exhausted", "fatigued"]:
                    if any(word in text_lower for word in ["sawa", "sijambo", "fine", "okay", "it's fine"]):
                        detected = True
                        confidence = 0.75
            
            elif "anxious_voice_saying_normal" in indicator_type:
                # Anxious voice saying normal
                if voice_emotion in ["anxious", "worried", "fearful"]:
                    if "ni hali ya kawaida" in text_lower or "it's normal" in text_lower:
                        detected = True
                        confidence = 0.7
            
            if detected:
                contradictions.append(VoiceContradiction(
                    indicator_type=indicator_type,
                    description=description,
                    severity_multiplier=indicator.get("severity_multiplier", 1.0),
                    detected=True,
                    confidence=confidence
                ))
        
        return contradictions
    
    def assess_risk(self,
                   deflections: List[DeflectionMatch],
                   contradictions: List[VoiceContradiction],
                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess risk level based on deflections and contradictions.
        
        Args:
            deflections: List of detected deflections
            contradictions: List of voice contradictions
            context: Additional context (e.g., previous deflections, session history)
            
        Returns:
            Risk assessment dictionary
        """
        if not deflections and not contradictions:
            return {
                "risk_level": "low",
                "risk_score": 0.0,
                "factors": [],
                "interpretation": "No deflections or contradictions detected."
            }
        
        # Base risk from deflections
        risk_factors = []
        base_score = 0.0
        
        # Count deflections by severity
        severity_counts = {"low": 0, "medium": 0, "high": 0}
        for deflection in deflections:
            severity = deflection.severity
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if severity == "high":
                base_score += 0.3
                risk_factors.append(f"High-severity deflection: {deflection.pattern}")
            elif severity == "medium":
                base_score += 0.15
                risk_factors.append(f"Medium-severity deflection: {deflection.pattern}")
            else:
                base_score += 0.05
        
        # Apply contradiction multipliers
        contradiction_multiplier = 1.0
        for contradiction in contradictions:
            if contradiction.detected:
                contradiction_multiplier *= contradiction.severity_multiplier
                risk_factors.append(f"Voice contradiction: {contradiction.description}")
        
        final_score = min(1.0, base_score * contradiction_multiplier)
        
        # Determine risk level
        if final_score >= 0.7:
            risk_level = "high"
        elif final_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Generate interpretation
        interpretation = self._generate_risk_interpretation(
            risk_level,
            severity_counts,
            contradictions,
            deflections
        )
        
        return {
            "risk_level": risk_level,
            "risk_score": final_score,
            "factors": risk_factors,
            "interpretation": interpretation,
            "severity_breakdown": severity_counts,
            "contradiction_count": len(contradictions)
        }
    
    def analyze(self,
                text: str,
                language: str = "auto",
                voice_emotion: Optional[str] = None,
                voice_features: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete deflection analysis.
        
        Args:
            text: Text to analyze
            language: Language code
            voice_emotion: Detected voice emotion
            voice_features: Voice features
            
        Returns:
            Complete analysis dictionary
        """
        deflections = self.detect_deflections(text, language)
        contradictions = self.detect_voice_contradictions(text, voice_emotion, voice_features)
        risk_assessment = self.assess_risk(deflections, contradictions)
        
        # Get probe suggestions
        probe_suggestions = []
        for deflection in deflections:
            probe_suggestions.extend(deflection.probe_suggestions[:2])  # Top 2 per deflection
        
        # Remove duplicates while preserving order
        seen = set()
        unique_probes = []
        for probe in probe_suggestions:
            if probe not in seen:
                seen.add(probe)
                unique_probes.append(probe)
        
        return {
            "deflection_detected": len(deflections) > 0,
            "deflection_count": len(deflections),
            "deflections": [
                {
                    "pattern": d.pattern,
                    "type": d.pattern_type,
                    "severity": d.severity,
                    "cultural_meaning": d.cultural_meaning,
                    "interpretation": d.interpretation,
                    "confidence": d.confidence,
                    "position": d.position,
                    "context": d.context
                }
                for d in deflections
            ],
            "voice_contradictions": [
                {
                    "type": c.indicator_type,
                    "description": c.description,
                    "detected": c.detected,
                    "confidence": c.confidence,
                    "severity_multiplier": c.severity_multiplier
                }
                for c in contradictions
            ],
            "contradiction_count": len(contradictions),
            "risk_assessment": risk_assessment,
            "probe_suggestions": unique_probes[:5],  # Top 5 suggestions
            "recommended_action": self._get_recommended_action(deflections, contradictions, risk_assessment)
        }
    
    def _calculate_confidence(self, pattern: str, context: str, pattern_data: Dict[str, Any]) -> float:
        """Calculate confidence in pattern match"""
        # Base confidence
        confidence = 0.7
        
        # Increase confidence if pattern appears in emotional context
        emotional_words = ["feel", "feeling", "emotion", "sad", "tired", "worried", "anxious"]
        if any(word in context.lower() for word in emotional_words):
            confidence += 0.1
        
        # Increase confidence if pattern is repeated
        pattern_count = context.lower().count(pattern.lower())
        if pattern_count > 1:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _generate_risk_interpretation(self,
                                     risk_level: str,
                                     severity_counts: Dict[str, int],
                                     contradictions: List[VoiceContradiction],
                                     deflections: List[DeflectionMatch]) -> str:
        """Generate risk interpretation"""
        if risk_level == "high":
            return (
                f"High risk detected: {severity_counts.get('high', 0)} high-severity deflections, "
                f"{len(contradictions)} voice contradictions. "
                "The user may be hiding significant distress. Immediate gentle probing recommended."
            )
        elif risk_level == "medium":
            return (
                f"Medium risk detected: {severity_counts.get('medium', 0)} medium-severity deflections, "
                f"{len(contradictions)} voice contradictions. "
                "The user may not be fully ready to discuss their feelings. Patient, gentle approach recommended."
            )
        else:
            return (
                f"Low risk: {len(deflections)} deflections detected, mostly low-severity. "
                "Continue with supportive, non-pressuring approach."
            )
    
    def _get_recommended_action(self,
                                deflections: List[DeflectionMatch],
                                contradictions: List[VoiceContradiction],
                                risk_assessment: Dict[str, Any]) -> str:
        """Get recommended action based on analysis"""
        risk_level = risk_assessment.get("risk_level", "low")
        
        if risk_level == "high":
            return "Immediate gentle probing recommended. Acknowledge contradictions and offer safe space."
        elif risk_level == "medium":
            return "Patient, gentle approach. Don't push, but offer opportunities to open up."
        else:
            return "Continue supportive approach. Respect user's pace and boundaries."


# Global instance
_detector: Optional[DeflectionDetector] = None


def get_deflection_detector(patterns_path: Optional[str] = None) -> DeflectionDetector:
    """Get or create deflection detector instance"""
    global _detector
    if _detector is None:
        _detector = DeflectionDetector(patterns_path)
    return _detector

