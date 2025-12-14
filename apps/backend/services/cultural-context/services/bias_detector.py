"""
Bias detection algorithms and cultural sensitivity validation
Detects potential biases in AI responses and validates cultural sensitivity
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BiasDetection:
    """Represents a detected bias"""
    bias_type: str
    severity: str
    description: str
    detected_pattern: str
    suggestion: str
    confidence: float


@dataclass
class CulturalSensitivityCheck:
    """Represents a cultural sensitivity validation"""
    check_type: str
    passed: bool
    issue: Optional[str]
    suggestion: Optional[str]


class BiasDetector:
    """
    Detector for biases and cultural insensitivity in AI responses.
    
    Detects:
    - Western-centric assumptions
    - Stigmatizing language
    - Cultural insensitivity
    - Inappropriate advice
    - Language that may alienate users
    """
    
    def __init__(self):
        """Initialize bias detector with patterns"""
        # Western-centric assumptions
        self.western_assumptions = [
            r'\b(individual therapy|psychotherapy|counseling|medication)\b.*\b(only|best|should)\b',
            r'\b(western|american|european)\b.*\b(approach|method|treatment)\b',
            r'\b(you should|you must|you need to)\b.*\b(see a therapist|take medication|get professional help)\b',
        ]
        
        # Stigmatizing language
        self.stigmatizing_patterns = [
            r'\b(crazy|insane|mental|psycho|nuts)\b',
            r'\b(just|simply|easily)\b.*\b(get over|move on|snap out of)\b',
            r'\b(weak|strong|tough)\b.*\b(handle|deal with)\b',
            r'\b(shouldn\'t|should not|don\'t)\b.*\b(feel|think|worry)\b',
        ]
        
        # Cultural insensitivity
        self.cultural_insensitivity = [
            r'\b(your culture|your tradition|your beliefs)\b.*\b(wrong|backward|primitive)\b',
            r'\b(you people|your kind|those people)\b',
            r'\b(modern|civilized|developed)\b.*\b(way|approach|method)\b',
        ]
        
        # Inappropriate advice
        self.inappropriate_advice = [
            r'\b(just|simply|easily)\b.*\b(pray|believe|have faith)\b',
            r'\b(ignore|dismiss|forget about)\b.*\b(family|community|tradition)\b',
            r'\b(you must|you have to|you need to)\b.*\b(leave|abandon|cut off)\b.*\b(family|community)\b',
        ]
        
        # Language that may alienate
        self.alienating_language = [
            r'\b(we|us|our)\b.*\b(always|never|all)\b',
            r'\b(you don\'t|you can\'t|you won\'t)\b.*\b(understand|know|appreciate)\b',
            r'\b(typical|normal|usual)\b.*\b(for people like you|in your situation)\b',
        ]
        
        # Compile regex patterns
        self.patterns = {
            "western_assumptions": [re.compile(p, re.IGNORECASE) for p in self.western_assumptions],
            "stigmatizing": [re.compile(p, re.IGNORECASE) for p in self.stigmatizing_patterns],
            "cultural_insensitivity": [re.compile(p, re.IGNORECASE) for p in self.cultural_insensitivity],
            "inappropriate_advice": [re.compile(p, re.IGNORECASE) for p in self.inappropriate_advice],
            "alienating": [re.compile(p, re.IGNORECASE) for p in self.alienating_language],
        }
        
        # Positive patterns (what we want to see)
        self.positive_patterns = [
            r'\b(respect|honor|acknowledge|validate)\b.*\b(culture|tradition|belief|community)\b',
            r'\b(understand|appreciate|recognize)\b.*\b(context|background|experience)\b',
            r'\b(valid|normal|understandable)\b.*\b(feeling|emotion|response)\b',
            r'\b(community|family|support network)\b.*\b(important|valuable|helpful)\b',
        ]
        
        self.positive_regex = [re.compile(p, re.IGNORECASE) for p in self.positive_patterns]
    
    def detect_biases(self, text: str) -> List[BiasDetection]:
        """
        Detect biases in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of detected biases
        """
        if not text or not text.strip():
            return []
        
        text_lower = text.lower()
        detections = []
        
        # Check each bias type
        for bias_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text_lower)
                if matches:
                    # Determine severity
                    severity = self._determine_severity(bias_type, matches)
                    
                    # Get description and suggestion
                    description, suggestion = self._get_bias_info(bias_type)
                    
                    detections.append(BiasDetection(
                        bias_type=bias_type,
                        severity=severity,
                        description=description,
                        detected_pattern=str(matches[0]) if matches else "",
                        suggestion=suggestion,
                        confidence=0.8  # High confidence for pattern matches
                    ))
        
        return detections
    
    def validate_cultural_sensitivity(self, text: str, context: Optional[Dict[str, Any]] = None) -> List[CulturalSensitivityCheck]:
        """
        Validate cultural sensitivity of text.
        
        Args:
            text: Text to validate
            context: Additional context (user language, region, etc.)
            
        Returns:
            List of sensitivity checks
        """
        checks = []
        
        # Check 1: Respects cultural context
        respects_culture = any(pattern.search(text) for pattern in self.positive_regex)
        checks.append(CulturalSensitivityCheck(
            check_type="cultural_respect",
            passed=respects_culture or not any(self.patterns["cultural_insensitivity"][0].search(text) for _ in [1]),
            issue=None if respects_culture else "Text may not adequately respect cultural context",
            suggestion="Include language that acknowledges and respects cultural values and traditions"
        ))
        
        # Check 2: Avoids stigmatizing language
        no_stigma = not any(pattern.search(text) for pattern in self.patterns["stigmatizing"])
        checks.append(CulturalSensitivityCheck(
            check_type="stigma_free",
            passed=no_stigma,
            issue=None if no_stigma else "Text contains potentially stigmatizing language",
            suggestion="Use neutral, non-judgmental language that normalizes help-seeking"
        ))
        
        # Check 3: Avoids Western-centric assumptions
        no_western_assumptions = not any(pattern.search(text) for pattern in self.patterns["western_assumptions"])
        checks.append(CulturalSensitivityCheck(
            check_type="culturally_inclusive",
            passed=no_western_assumptions,
            issue=None if no_western_assumptions else "Text may contain Western-centric assumptions",
            suggestion="Acknowledge diverse approaches to mental health and support, including community and cultural resources"
        ))
        
        # Check 4: Appropriate advice
        appropriate_advice = not any(pattern.search(text) for pattern in self.patterns["inappropriate_advice"])
        checks.append(CulturalSensitivityCheck(
            check_type="appropriate_advice",
            passed=appropriate_advice,
            issue=None if appropriate_advice else "Text may contain inappropriate advice",
            suggestion="Provide advice that respects cultural values and doesn't require abandoning important relationships or beliefs"
        ))
        
        # Check 5: Inclusive language
        inclusive_language = not any(pattern.search(text) for pattern in self.patterns["alienating"])
        checks.append(CulturalSensitivityCheck(
            check_type="inclusive_language",
            passed=inclusive_language,
            issue=None if inclusive_language else "Text may use alienating language",
            suggestion="Use inclusive language that doesn't make assumptions or create distance"
        ))
        
        return checks
    
    def assess_overall_sensitivity(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assess overall cultural sensitivity.
        
        Args:
            text: Text to assess
            context: Additional context
            
        Returns:
            Overall sensitivity assessment
        """
        # Purpose: tests and callers may provide None/empty text; handle gracefully.
        # Inputs: text may be None/empty.
        # Outputs: stable assessment dict with low sensitivity and no crashes.
        # Behavior: returns default "low" assessment for empty input.
        if not text or not str(text).strip():
            return {
                "sensitivity_score": 0.0,
                "sensitivity_rating": "low",
                "bias_count": 0,
                "biases": [],
                "checks_passed": 0,
                "checks_failed": 0,
                "recommendations": ["Provide text to assess cultural sensitivity."]
            }

        text = str(text)
        biases = self.detect_biases(text)
        checks = self.validate_cultural_sensitivity(text, context)
        
        # Calculate scores
        bias_count = len(biases)
        failed_checks = [c for c in checks if not c.passed]
        passed_checks = [c for c in checks if c.passed]
        
        # Calculate sensitivity score (0-1, higher is better)
        sensitivity_score = 1.0 - (bias_count * 0.2) - (len(failed_checks) * 0.15)
        sensitivity_score = max(0.0, min(1.0, sensitivity_score))
        
        # Determine overall rating
        if sensitivity_score >= 0.8:
            rating = "high"
        elif sensitivity_score >= 0.6:
            rating = "medium"
        else:
            rating = "low"
        
        # Generate recommendations
        recommendations = []
        for check in failed_checks:
            if check.suggestion:
                recommendations.append(check.suggestion)
        
        for bias in biases:
            if bias.suggestion:
                recommendations.append(bias.suggestion)
        
        # Remove duplicates
        recommendations = list(dict.fromkeys(recommendations))
        
        return {
            "sensitivity_score": sensitivity_score,
            "sensitivity_rating": rating,
            "bias_count": bias_count,
            "biases": [
                {
                    "type": b.bias_type,
                    "severity": b.severity,
                    "description": b.description,
                    "suggestion": b.suggestion
                }
                for b in biases
            ],
            "checks_passed": len(passed_checks),
            "checks_failed": len(failed_checks),
            "sensitivity_checks": [
                {
                    "type": c.check_type,
                    "passed": c.passed,
                    "issue": c.issue,
                    "suggestion": c.suggestion
                }
                for c in checks
            ],
            "recommendations": recommendations,
            "is_culturally_sensitive": rating in ["high", "medium"]
        }
    
    def _determine_severity(self, bias_type: str, matches: List[str]) -> str:
        """Determine severity of bias"""
        high_severity_types = ["stigmatizing", "cultural_insensitivity", "inappropriate_advice"]
        
        if bias_type in high_severity_types:
            return "high"
        elif len(matches) > 1:
            return "medium"
        else:
            return "low"
    
    def _get_bias_info(self, bias_type: str) -> tuple:
        """Get description and suggestion for bias type"""
        info_map = {
            "western_assumptions": (
                "Text may assume Western approaches are the only or best option",
                "Acknowledge diverse approaches to mental health, including community support, cultural practices, and local resources"
            ),
            "stigmatizing": (
                "Text contains potentially stigmatizing language",
                "Use neutral, non-judgmental language. Normalize help-seeking and validate all emotions"
            ),
            "cultural_insensitivity": (
                "Text may be culturally insensitive",
                "Respect and acknowledge cultural values, traditions, and community structures. Avoid making assumptions about cultural practices"
            ),
            "inappropriate_advice": (
                "Text may contain inappropriate advice that conflicts with cultural values",
                "Provide advice that respects cultural values and doesn't require abandoning important relationships, beliefs, or community connections"
            ),
            "alienating": (
                "Text may use language that alienates the user",
                "Use inclusive, empathetic language that doesn't make assumptions or create distance. Acknowledge the user's unique experience"
            ),
        }
        
        return info_map.get(bias_type, ("Potential bias detected", "Review text for cultural sensitivity"))


# Global instance
_detector: Optional[BiasDetector] = None


def get_bias_detector() -> BiasDetector:
    """Get or create bias detector instance"""
    global _detector
    if _detector is None:
        _detector = BiasDetector()
    return _detector

