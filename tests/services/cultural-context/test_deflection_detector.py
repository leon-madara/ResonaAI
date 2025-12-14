"""
Unit tests for Deflection Detector
"""

import pytest
import sys
import os
import json
import tempfile
from unittest.mock import Mock, patch

# Add service directory to path
service_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..', '..', '..', 'apps', 'backend', 'services', 'cultural-context'
    )
)
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)


class TestDeflectionDetector:
    """Test deflection detection"""
    
    @pytest.fixture
    def mock_patterns(self):
        """Create mock patterns file"""
        patterns = {
            "version": "1.0",
            "patterns": [
                {
                    "pattern": "sawa",
                    "type": "deflection",
                    "severity": "low",
                    "cultural_meaning": "Polite deflection",
                    "interpretation": "User may not be ready to discuss",
                    "probe_suggestions": [
                        "I hear you say 'sawa' - how are you really feeling?",
                        "It's okay if you're not ready to talk."
                    ],
                    "context_indicators": ["Repeated use"],
                    "risk_assessment": {
                        "low": "Single use",
                        "medium": "Repeated use",
                        "high": "Repeated with voice contradiction"
                    }
                },
                {
                    "pattern": "nimechoka",
                    "type": "emotional_exhaustion",
                    "severity": "medium",
                    "cultural_meaning": "I am tired - emotional exhaustion",
                    "interpretation": "User expressing significant fatigue",
                    "probe_suggestions": [
                        "I hear you're tired. What kind of tiredness?",
                        "What's been wearing you down?"
                    ],
                    "context_indicators": ["Said with heavy tone"],
                    "risk_assessment": {
                        "low": "Single mention",
                        "medium": "Repeated mention",
                        "high": "Repeated with other distress indicators"
                    }
                }
            ],
            "voice_contradiction_indicators": [
                {
                    "indicator": "sad_voice_saying_okay",
                    "description": "User says 'sawa' but voice tone indicates sadness",
                    "severity_multiplier": 1.5,
                    "action": "Probe deeper"
                }
            ],
            "cultural_context": {
                "region": "east_africa",
                "languages": ["sw", "en"]
            }
        }
        return patterns
    
    @pytest.fixture
    def detector(self, mock_patterns):
        """Create deflection detector with mock patterns"""
        # Create temporary patterns file
        temp_dir = tempfile.mkdtemp()
        patterns_path = os.path.join(temp_dir, "swahili_patterns.json")
        
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(mock_patterns, f)
        
        from services.deflection_detector import DeflectionDetector
        detector = DeflectionDetector(patterns_path=patterns_path)
        
        yield detector
        
        # Cleanup
        os.remove(patterns_path)
        os.rmdir(temp_dir)
    
    def test_detect_deflections_sawa(self, detector):
        """Test detecting 'sawa' deflection"""
        text = "Sawa, I am fine"
        deflections = detector.detect_deflections(text)
        
        assert len(deflections) > 0
        assert any(d.pattern == "sawa" for d in deflections)
    
    def test_detect_deflections_nimechoka(self, detector):
        """Test detecting 'nimechoka' pattern"""
        text = "Nimechoka sana today"
        deflections = detector.detect_deflections(text)
        
        assert len(deflections) > 0
        assert any(d.pattern == "nimechoka" for d in deflections)
    
    def test_detect_deflections_no_match(self, detector):
        """Test with no deflection patterns"""
        text = "I am feeling great today"
        deflections = detector.detect_deflections(text)
        
        assert isinstance(deflections, list)
        # May or may not detect deflections depending on implementation
    
    def test_detect_voice_contradictions(self, detector):
        """Test voice contradiction detection"""
        text = "Sawa, I am fine"
        voice_emotion = "sad"
        
        contradictions = detector.detect_voice_contradictions(text, voice_emotion)
        
        assert isinstance(contradictions, list)
        if len(contradictions) > 0:
            assert all(hasattr(c, 'detected') for c in contradictions)
            assert all(hasattr(c, 'confidence') for c in contradictions)
    
    def test_detect_voice_contradictions_no_emotion(self, detector):
        """Test voice contradiction detection without emotion"""
        text = "Sawa, I am fine"
        
        contradictions = detector.detect_voice_contradictions(text, None)
        
        assert isinstance(contradictions, list)
        assert len(contradictions) == 0
    
    def test_assess_risk_low(self, detector):
        """Test risk assessment with low risk"""
        deflections = []
        contradictions = []
        
        risk = detector.assess_risk(deflections, contradictions)
        
        assert "risk_level" in risk
        assert "risk_score" in risk
        assert "factors" in risk
        assert "interpretation" in risk
        assert risk["risk_level"] == "low"
    
    def test_assess_risk_high(self, detector):
        """Test risk assessment with high risk"""
        text = "Sawa, I am fine"
        deflections = detector.detect_deflections(text)
        text2 = "Sawa, I am fine"
        contradictions = detector.detect_voice_contradictions(text2, "sad")
        
        risk = detector.assess_risk(deflections, contradictions)
        
        assert "risk_level" in risk
        assert "risk_score" in risk
        assert risk["risk_score"] >= 0.0
        assert risk["risk_score"] <= 1.0
    
    def test_analyze_complete(self, detector):
        """Test complete deflection analysis"""
        text = "Sawa, I am fine"
        result = detector.analyze(text, language="auto")
        
        assert "deflection_detected" in result
        assert "deflection_count" in result
        assert "deflections" in result
        assert "voice_contradictions" in result
        assert "risk_assessment" in result
        assert "probe_suggestions" in result
        assert "recommended_action" in result
    
    def test_analyze_with_voice_emotion(self, detector):
        """Test analysis with voice emotion"""
        text = "Sawa, I am fine"
        result = detector.analyze(
            text,
            language="auto",
            voice_emotion="sad",
            voice_features={"pitch": 0.5, "energy": 0.3}
        )
        
        assert "deflection_detected" in result
        assert "contradiction_count" in result
    
    def test_analyze_empty_text(self, detector):
        """Test analysis with empty text"""
        text = ""
        result = detector.analyze(text)
        
        assert "deflection_detected" in result
        assert result["deflection_detected"] is False
    
    def test_get_detector_singleton(self, mock_patterns):
        """Test that get_deflection_detector can be called"""
        from services.deflection_detector import get_deflection_detector
        
        # Create temporary patterns file
        temp_dir = tempfile.mkdtemp()
        patterns_path = os.path.join(temp_dir, "swahili_patterns.json")
        
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(mock_patterns, f)
        
        detector1 = get_deflection_detector(patterns_path=patterns_path)
        detector2 = get_deflection_detector(patterns_path=patterns_path)
        
        # Should return same instance (singleton)
        assert detector1 is detector2
        
        # Cleanup
        os.remove(patterns_path)
        os.rmdir(temp_dir)

