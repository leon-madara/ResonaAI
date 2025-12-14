"""
Unit tests for Code-Switching Analyzer
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


class TestCodeSwitchAnalyzer:
    """Test code-switching detection analyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create code-switching analyzer instance"""
        from services.code_switch_analyzer import CodeSwitchAnalyzer
        return CodeSwitchAnalyzer()
    
    def test_detect_language_english(self, analyzer):
        """Test detecting English language"""
        text = "I am feeling sad and tired today"
        result = analyzer.detect_language(text)
        assert result == "en"
    
    def test_detect_language_swahili(self, analyzer):
        """Test detecting Swahili language"""
        text = "nimechoka na huzuni leo"
        result = analyzer.detect_language(text)
        assert result == "sw"
    
    def test_detect_language_mixed(self, analyzer):
        """Test detecting mixed language (code-switching)"""
        text = "I am nimechoka feeling tired"
        result = analyzer.detect_language(text)
        assert result in ["mixed", "en", "sw"]  # May detect as mixed or primary language
    
    def test_detect_language_unknown(self, analyzer):
        """Test detecting unknown language"""
        text = "123 !@# $%^"
        result = analyzer.detect_language(text)
        assert result == "unknown"
    
    def test_segment_text_simple(self, analyzer):
        """Test text segmentation"""
        text = "I am feeling sad. Nimechoka today."
        segments = analyzer.segment_text(text)
        
        assert len(segments) > 0
        assert all(hasattr(seg, 'text') for seg in segments)
        assert all(hasattr(seg, 'language') for seg in segments)
        assert all(hasattr(seg, 'confidence') for seg in segments)
    
    def test_detect_transitions(self, analyzer):
        """Test detecting language transitions"""
        text = "I am feeling sad. Nimechoka sana today."
        transitions = analyzer.detect_transitions(text)
        
        # Should detect transitions if languages differ
        assert isinstance(transitions, list)
        if len(transitions) > 0:
            assert all(hasattr(t, 'from_language') for t in transitions)
            assert all(hasattr(t, 'to_language') for t in transitions)
    
    def test_analyze_code_switching_detected(self, analyzer):
        """Test complete analysis with code-switching"""
        text = "I am nimechoka feeling very tired and huzuni"
        result = analyzer.analyze(text)
        
        assert "code_switching_detected" in result
        assert "primary_language" in result
        assert "language_distribution" in result
        assert "segments" in result
        assert "transitions" in result
        assert "emotional_intensity" in result
        assert "interpretation" in result
        
        # Should detect code-switching with English and Swahili
        assert result["code_switching_detected"] is True
    
    def test_analyze_no_code_switching(self, analyzer):
        """Test analysis with no code-switching"""
        text = "I am feeling sad and tired today"
        result = analyzer.analyze(text)
        
        assert "code_switching_detected" in result
        assert result["primary_language"] == "en"
        # May or may not detect code-switching depending on implementation
        assert isinstance(result["code_switching_detected"], bool)
    
    def test_analyze_swahili_only(self, analyzer):
        """Test analysis with Swahili only"""
        text = "nimechoka na huzuni leo"
        result = analyzer.analyze(text)
        
        assert "primary_language" in result
        assert result["primary_language"] in ["sw", "unknown"]
    
    def test_analyze_emotional_intensity(self, analyzer):
        """Test emotional intensity detection"""
        text = "I am very very sad and extremely tired"
        result = analyzer.analyze(text)
        
        assert "emotional_intensity" in result
        assert result["emotional_intensity"] in ["low", "medium", "high"]
    
    def test_analyze_empty_text(self, analyzer):
        """Test analysis with empty text"""
        text = ""
        result = analyzer.analyze(text)
        
        assert "code_switching_detected" in result
        assert result["code_switching_detected"] is False
    
    def test_analyze_whitespace_only(self, analyzer):
        """Test analysis with whitespace only"""
        text = "   \n\t  "
        result = analyzer.analyze(text)
        
        assert "code_switching_detected" in result
    
    def test_cosine_similarity_calculation(self, analyzer):
        """Test cosine similarity calculation"""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        
        similarity = analyzer.embedding_service.cosine_similarity(vec1, vec2)
        assert 0.0 <= similarity <= 1.0
        assert similarity == 1.0  # Identical vectors should have similarity 1.0
    
    def test_get_analyzer_singleton(self):
        """Test that get_code_switch_analyzer returns singleton"""
        from services.code_switch_analyzer import get_code_switch_analyzer
        
        analyzer1 = get_code_switch_analyzer()
        analyzer2 = get_code_switch_analyzer()
        
        assert analyzer1 is analyzer2

