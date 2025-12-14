"""
Hallucination detection for AI responses
"""

import logging
import re
from typing import Dict, List, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class HallucinationDetector:
    """Detect hallucinations and factual inconsistencies in AI responses"""
    
    def __init__(self):
        """Initialize hallucination detector"""
        # Patterns that indicate uncertainty or hallucination
        self.uncertainty_patterns = [
            r"\b(might|may|could|possibly|perhaps|maybe)\s+(be|have|need)",
            r"\b(i think|i believe|i assume|i guess)",
            r"\b(not sure|uncertain|unclear)",
        ]
        
        # Contradictory statements
        self.contradiction_patterns = [
            (r"\b(always|never)\b", r"\b(sometimes|occasionally)\b"),
            (r"\b(all|every)\b", r"\b(some|few)\b"),
        ]
        
        # Medical claims that should be flagged
        self.medical_claim_patterns = [
            r"\b(you have|you are diagnosed with|you need|you must take)\s+[a-z]+\s+(disease|disorder|syndrome|condition)",
            r"\b(cure|treat|heal)\s+[a-z]+\s+(with|using)\s+[a-z]+",
        ]
        
        # Factual claims that need verification
        self.factual_claim_patterns = [
            r"\b(studies show|research proves|science says|doctors say)\b",
            r"\b(it is (known|proven|established))\s+that",
        ]
    
    def detect_uncertainty(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect uncertainty markers in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (detected, matched_patterns)
        """
        text_lower = text.lower()
        matched = []
        
        for pattern in self.uncertainty_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                matched.extend(matches)
        
        return len(matched) > 0, matched
    
    def detect_contradictions(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect contradictory statements.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (detected, contradictions)
        """
        text_lower = text.lower()
        contradictions = []
        
        for pattern1, pattern2 in self.contradiction_patterns:
            has_pattern1 = bool(re.search(pattern1, text_lower))
            has_pattern2 = bool(re.search(pattern2, text_lower))
            
            if has_pattern1 and has_pattern2:
                contradictions.append(f"{pattern1} vs {pattern2}")
        
        return len(contradictions) > 0, contradictions
    
    def detect_medical_claims(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect unverified medical claims.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (detected, claims)
        """
        text_lower = text.lower()
        claims = []
        
        for pattern in self.medical_claim_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                claims.extend(matches)
        
        return len(claims) > 0, claims
    
    def detect_factual_claims(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect factual claims that need verification.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (detected, claims)
        """
        text_lower = text.lower()
        claims = []
        
        for pattern in self.factual_claim_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                claims.extend(matches)
        
        return len(claims) > 0, claims
    
    def check_against_knowledge_base(
        self,
        text: str,
        knowledge_base: Optional[List[str]] = None
    ) -> Tuple[bool, float]:
        """
        Check if text contradicts known facts from knowledge base.
        
        Args:
            text: Text to check
            knowledge_base: Optional list of known facts
            
        Returns:
            Tuple of (contradiction_detected, confidence)
        """
        # This is a placeholder - in production, would check against actual KB
        # For now, return low confidence
        return False, 0.0
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive hallucination analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with hallucination analysis
        """
        uncertainty_detected, uncertainty_matches = self.detect_uncertainty(text)
        contradiction_detected, contradictions = self.detect_contradictions(text)
        medical_claims_detected, medical_claims = self.detect_medical_claims(text)
        factual_claims_detected, factual_claims = self.detect_factual_claims(text)
        
        # Calculate hallucination score (0-1)
        score = 0.0
        issues = []
        
        if uncertainty_detected:
            score += 0.2
            issues.append("uncertainty_detected")
        
        if contradiction_detected:
            score += 0.4
            issues.append("contradiction_detected")
        
        if medical_claims_detected:
            score += 0.5
            issues.append("unverified_medical_claim")
        
        if factual_claims_detected:
            score += 0.3
            issues.append("unverified_factual_claim")
        
        score = min(1.0, score)
        
        return {
            "hallucination_score": score,
            "uncertainty_detected": uncertainty_detected,
            "uncertainty_matches": uncertainty_matches,
            "contradiction_detected": contradiction_detected,
            "contradictions": contradictions,
            "medical_claims_detected": medical_claims_detected,
            "medical_claims": medical_claims,
            "factual_claims_detected": factual_claims_detected,
            "factual_claims": factual_claims,
            "issues": issues,
            "needs_review": score > 0.5,
        }


# Global instance
_hallucination_detector: Optional[HallucinationDetector] = None


def get_hallucination_detector() -> HallucinationDetector:
    """Get or create hallucination detector instance"""
    global _hallucination_detector
    if _hallucination_detector is None:
        _hallucination_detector = HallucinationDetector()
    return _hallucination_detector

