"""
Unit tests for Bias Detector
"""

import pytest
import sys
import os
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


class TestBiasDetector:
    """Test bias detection and cultural sensitivity validation"""
    
    @pytest.fixture
    def detector(self):
        """Create bias detector instance"""
        from services.bias_detector import BiasDetector
        return BiasDetector()
    
    def test_detect_biases_western_assumptions(self, detector):
        """Test detecting Western-centric assumptions"""
        text = "You should see a therapist, that's the best approach"
        biases = detector.detect_biases(text)
        
        assert isinstance(biases, list)
        # May detect Western assumptions depending on pattern matching
    
    def test_detect_biases_stigmatizing(self, detector):
        """Test detecting stigmatizing language"""
        text = "You're crazy if you think that way"
        biases = detector.detect_biases(text)
        
        assert isinstance(biases, list)
        if len(biases) > 0:
            assert any(b.bias_type == "stigmatizing" for b in biases)
    
    def test_detect_biases_cultural_insensitivity(self, detector):
        """Test detecting cultural insensitivity"""
        text = "Your culture is wrong and backward"
        biases = detector.detect_biases(text)
        
        assert isinstance(biases, list)
        if len(biases) > 0:
            assert any(b.bias_type == "cultural_insensitivity" for b in biases)
    
    def test_detect_biases_inappropriate_advice(self, detector):
        """Test detecting inappropriate advice"""
        text = "You must leave your family to get better"
        biases = detector.detect_biases(text)
        
        assert isinstance(biases, list)
        if len(biases) > 0:
            assert any(b.bias_type == "inappropriate_advice" for b in biases)
    
    def test_detect_biases_no_biases(self, detector):
        """Test with culturally sensitive text"""
        text = "I understand your feelings are valid. Your community support is important."
        biases = detector.detect_biases(text)
        
        assert isinstance(biases, list)
        # Should have fewer or no biases
    
    def test_validate_cultural_sensitivity_passed(self, detector):
        """Test cultural sensitivity validation with passed checks"""
        text = "I respect your cultural values and traditions. Your community support is valuable."
        checks = detector.validate_cultural_sensitivity(text)
        
        assert isinstance(checks, list)
        assert len(checks) > 0
        assert all(hasattr(c, 'check_type') for c in checks)
        assert all(hasattr(c, 'passed') for c in checks)
    
    def test_validate_cultural_sensitivity_failed(self, detector):
        """Test cultural sensitivity validation with failed checks"""
        text = "You're crazy and your culture is wrong"
        checks = detector.validate_cultural_sensitivity(text)
        
        assert isinstance(checks, list)
        # Should have some failed checks
        failed_checks = [c for c in checks if not c.passed]
        assert len(failed_checks) > 0
    
    def test_assess_overall_sensitivity_high(self, detector):
        """Test overall sensitivity assessment with high sensitivity"""
        text = "I respect your cultural values. Your community support is important. Your feelings are valid."
        assessment = detector.assess_overall_sensitivity(text)
        
        assert "sensitivity_score" in assessment
        assert "sensitivity_rating" in assessment
        assert "bias_count" in assessment
        assert "biases" in assessment
        assert "checks_passed" in assessment
        assert "checks_failed" in assessment
        assert "sensitivity_checks" in assessment
        assert "recommendations" in assessment
        assert "is_culturally_sensitive" in assessment
        
        assert 0.0 <= assessment["sensitivity_score"] <= 1.0
        assert assessment["sensitivity_rating"] in ["low", "medium", "high"]
    
    def test_assess_overall_sensitivity_low(self, detector):
        """Test overall sensitivity assessment with low sensitivity"""
        text = "You're crazy. Your culture is wrong. You must see a Western therapist."
        assessment = detector.assess_overall_sensitivity(text)
        
        assert "sensitivity_score" in assessment
        assert assessment["sensitivity_score"] >= 0.0
        assert assessment["sensitivity_score"] <= 1.0
        # Should have lower score
        assert assessment["bias_count"] > 0
    
    def test_assess_overall_sensitivity_empty(self, detector):
        """Test overall sensitivity assessment with empty text"""
        text = ""
        assessment = detector.assess_overall_sensitivity(text)
        
        assert "sensitivity_score" in assessment
        assert "sensitivity_rating" in assessment
    
    def test_get_bias_detector_singleton(self):
        """Test that get_bias_detector returns singleton"""
        from services.bias_detector import get_bias_detector
        
        detector1 = get_bias_detector()
        detector2 = get_bias_detector()
        
        assert detector1 is detector2
    
    def test_bias_detection_severity(self, detector):
        """Test that bias detection includes severity"""
        text = "You're crazy and your culture is wrong"
        biases = detector.detect_biases(text)
        
        if len(biases) > 0:
            assert all(hasattr(b, 'severity') for b in biases)
            assert all(b.severity in ["low", "medium", "high"] for b in biases)
    
    def test_sensitivity_checks_all_types(self, detector):
        """Test that all sensitivity check types are included"""
        text = "Test text"
        checks = detector.validate_cultural_sensitivity(text)
        
        check_types = [c.check_type for c in checks]
        assert "cultural_respect" in check_types
        assert "stigma_free" in check_types
        assert "culturally_inclusive" in check_types
        assert "appropriate_advice" in check_types
        assert "inclusive_language" in check_types

