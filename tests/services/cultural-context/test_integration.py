"""
Integration tests for Cultural Context Service
Tests the integration between different components
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


class TestCulturalContextIntegration:
    """Integration tests for Cultural Context Service"""
    
    @pytest.fixture
    def mock_patterns(self):
        """Create mock patterns file"""
        return {
            "version": "1.0",
            "patterns": [
                {
                    "pattern": "sawa",
                    "type": "deflection",
                    "severity": "low",
                    "cultural_meaning": "Polite deflection",
                    "interpretation": "User may not be ready",
                    "probe_suggestions": ["How are you really feeling?"],
                    "context_indicators": [],
                    "risk_assessment": {"low": "Single use"}
                }
            ],
            "voice_contradiction_indicators": [],
            "cultural_context": {"region": "east_africa"}
        }
    
    @pytest.fixture
    def mock_kb(self):
        """Create mock knowledge base"""
        return {
            "version": "1.0",
            "entries": [
                {
                    "id": "entry-1",
                    "keywords": ["sad", "depressed"],
                    "language": "en",
                    "region": "east_africa",
                    "content": "Test content about sadness"
                }
            ]
        }
    
    def test_code_switching_with_deflection(self, mock_patterns):
        """Test integration of code-switching and deflection detection"""
        from services.code_switch_analyzer import get_code_switch_analyzer
        from services.deflection_detector import get_deflection_detector
        
        # Create temporary patterns file
        temp_dir = tempfile.mkdtemp()
        patterns_path = os.path.join(temp_dir, "swahili_patterns.json")
        
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(mock_patterns, f)
        
        try:
            code_switch_analyzer = get_code_switch_analyzer()
            deflection_detector = get_deflection_detector(patterns_path=patterns_path)
            
            text = "I am sawa feeling fine"
            
            # Analyze code-switching
            code_switch_result = code_switch_analyzer.analyze(text)
            
            # Analyze deflections
            deflection_result = deflection_detector.analyze(text)
            
            # Both should work together
            assert "code_switching_detected" in code_switch_result
            assert "deflection_detected" in deflection_result
            
        finally:
            os.remove(patterns_path)
            os.rmdir(temp_dir)
    
    def test_bias_detection_with_cultural_context(self):
        """Test integration of bias detection with cultural context"""
        from services.bias_detector import get_bias_detector
        
        detector = get_bias_detector()
        
        # Text that should be culturally sensitive
        sensitive_text = "I respect your cultural values and community support. Your feelings are valid."
        
        assessment = detector.assess_overall_sensitivity(sensitive_text)
        
        assert "sensitivity_score" in assessment
        assert "is_culturally_sensitive" in assessment
        # Should be culturally sensitive
        assert assessment["is_culturally_sensitive"] is True
    
    def test_rag_with_embeddings(self):
        """Test integration of RAG service with embeddings"""
        from services.rag_service import get_rag_service
        from services.embeddings import get_embedding_service
        
        embedding_service = get_embedding_service()
        rag_service = get_rag_service()
        
        if embedding_service.is_available() and rag_service.is_available():
            # Index an entry
            entry_id = "test-entry"
            text = "Mental health support in East Africa"
            metadata = {"keywords": ["mental", "health"], "language": "en"}
            
            indexed = rag_service.index_entry(entry_id, text, metadata)
            
            if indexed:
                # Search for it
                results = rag_service.search("mental health", top_k=3)
                
                assert isinstance(results, list)
        else:
            pytest.skip("RAG or embedding service not available")
    
    def test_full_context_analysis_flow(self, mock_patterns, mock_kb):
        """Test full context analysis flow"""
        from services.code_switch_analyzer import get_code_switch_analyzer
        from services.deflection_detector import get_deflection_detector
        from services.bias_detector import get_bias_detector
        
        # Create temporary patterns file
        temp_dir = tempfile.mkdtemp()
        patterns_path = os.path.join(temp_dir, "swahili_patterns.json")
        
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(mock_patterns, f)
        
        try:
            text = "I am sawa feeling fine, but nimechoka"
            
            # Run all analyses
            code_switch_result = get_code_switch_analyzer().analyze(text)
            deflection_result = get_deflection_detector(patterns_path=patterns_path).analyze(text)
            bias_result = get_bias_detector().assess_overall_sensitivity(text)
            
            # All should complete successfully
            assert "code_switching_detected" in code_switch_result
            assert "deflection_detected" in deflection_result
            assert "sensitivity_score" in bias_result
            
        finally:
            os.remove(patterns_path)
            os.rmdir(temp_dir)
    
    def test_error_handling_integration(self):
        """Test error handling across services"""
        from services.code_switch_analyzer import get_code_switch_analyzer
        from services.bias_detector import get_bias_detector
        
        # Test with None/empty inputs
        analyzer = get_code_switch_analyzer()
        detector = get_bias_detector()
        
        # Should handle gracefully
        result1 = analyzer.analyze(None)
        result2 = detector.assess_overall_sensitivity(None)
        
        # Should not raise exceptions
        assert isinstance(result1, dict)
        assert isinstance(result2, dict)
    
    def test_full_query_flow_integration(self, mock_patterns, mock_kb):
        """Test full flow: query → code-switching → deflection → bias check"""
        from services.code_switch_analyzer import get_code_switch_analyzer
        from services.deflection_detector import get_deflection_detector
        from services.bias_detector import get_bias_detector
        
        # Create temporary patterns file
        temp_dir = tempfile.mkdtemp()
        patterns_path = os.path.join(temp_dir, "swahili_patterns.json")
        
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(mock_patterns, f)
        
        try:
            # Simulate a user query with code-switching and deflection
            user_query = "I am feeling sawa but nimechoka sana"
            
            # Step 1: Analyze code-switching
            code_switch_analyzer = get_code_switch_analyzer()
            code_switch_result = code_switch_analyzer.analyze(user_query)
            
            assert "code_switching_detected" in code_switch_result
            assert code_switch_result["code_switching_detected"] is True
            
            # Step 2: Detect deflection
            deflection_detector = get_deflection_detector(patterns_path=patterns_path)
            deflection_result = deflection_detector.analyze(user_query, language="mixed")
            
            assert "deflection_detected" in deflection_result
            
            # Step 3: Generate AI response (simulate)
            ai_response = "I understand you're saying you're okay, but I sense you're very tired. It's okay to not be okay."
            
            # Step 4: Check AI response for bias
            bias_detector = get_bias_detector()
            bias_result = bias_detector.assess_overall_sensitivity(ai_response)
            
            assert "sensitivity_score" in bias_result
            assert "is_culturally_sensitive" in bias_result
            
            # Full flow completed successfully
            assert isinstance(code_switch_result, dict)
            assert isinstance(deflection_result, dict)
            assert isinstance(bias_result, dict)
            
        finally:
            os.remove(patterns_path)
            os.rmdir(temp_dir)
    
    def test_cultural_norms_with_context_retrieval(self):
        """Test cultural norms integration with context retrieval"""
        from services.bias_detector import get_bias_detector
        
        # Create a response that respects cultural norms
        culturally_sensitive_response = (
            "I respect your family values and understand the importance of community support. "
            "Your feelings are valid, and seeking help is a sign of strength."
        )
        
        # Check that it passes cultural sensitivity checks
        detector = get_bias_detector()
        result = detector.assess_overall_sensitivity(culturally_sensitive_response)
        
        assert "is_culturally_sensitive" in result
        assert result["is_culturally_sensitive"] is True
        assert result["sensitivity_score"] > 0.5  # Should have decent sensitivity score
    
    def test_rag_fallback_to_keyword_search(self):
        """Test RAG fallback to keyword search when vector DB unavailable"""
        from services.rag_service import get_rag_service
        
        rag_service = get_rag_service()
        
        # If RAG is unavailable, should fallback gracefully
        if not rag_service.is_available():
            # Test that service handles unavailability
            results = rag_service.search("test query", top_k=3)
            assert results == []
        else:
            # Test that service works when available
            results = rag_service.search("mental health", top_k=3)
            assert isinstance(results, list)
    
    def test_caching_integration_with_database(self):
        """Test caching integration with database"""
        # This is tested indirectly through the API endpoint tests
        # but we can verify the cache logic works
        # Note: Cache is mocked in fixtures, so this tests the mock behavior
        pass  # Placeholder for database-specific caching tests
    
    def test_error_propagation_across_services(self, mock_patterns):
        """Test error propagation across service boundaries"""
        from services.code_switch_analyzer import get_code_switch_analyzer
        from services.deflection_detector import get_deflection_detector
        
        # Create temporary patterns file
        temp_dir = tempfile.mkdtemp()
        patterns_path = os.path.join(temp_dir, "swahili_patterns.json")
        
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(mock_patterns, f)
        
        try:
            # Test that services handle errors gracefully
            analyzer = get_code_switch_analyzer()
            detector = get_deflection_detector(patterns_path=patterns_path)
            
            # Test with invalid input
            result1 = analyzer.analyze("")
            result2 = detector.analyze("", language="en")
            
            # Should not raise exceptions
            assert isinstance(result1, dict)
            assert isinstance(result2, dict)
            
            # Test with special characters
            result3 = analyzer.analyze("!@#$%^&*()")
            result4 = detector.analyze("!@#$%^&*()", language="en")
            
            assert isinstance(result3, dict)
            assert isinstance(result4, dict)
            
        finally:
            os.remove(patterns_path)
            os.rmdir(temp_dir)
    
    def test_multilingual_integration_flow(self, mock_patterns):
        """Test integration flow with multilingual content"""
        from services.code_switch_analyzer import get_code_switch_analyzer
        from services.deflection_detector import get_deflection_detector
        
        # Create temporary patterns file
        temp_dir = tempfile.mkdtemp()
        patterns_path = os.path.join(temp_dir, "swahili_patterns.json")
        
        with open(patterns_path, 'w', encoding='utf-8') as f:
            json.dump(mock_patterns, f)
        
        try:
            analyzer = get_code_switch_analyzer()
            detector = get_deflection_detector(patterns_path=patterns_path)
            
            # Test English
            en_result = analyzer.analyze("I am feeling sad and tired")
            assert "primary_language" in en_result
            
            # Test Swahili
            sw_text = "nimechoka na huzuni"
            sw_result = analyzer.analyze(sw_text)
            assert "primary_language" in sw_result
            
            # Test mixed (code-switching)
            mixed_text = "I am nimechoka and feeling huzuni"
            mixed_result = analyzer.analyze(mixed_text)
            assert "code_switching_detected" in mixed_result
            
            # Verify deflection detection works across languages
            deflection_en = detector.analyze("I'm fine", language="en")
            deflection_sw = detector.analyze("sawa tu", language="sw")
            
            assert "deflection_detected" in deflection_en
            assert "deflection_detected" in deflection_sw
            
        finally:
            os.remove(patterns_path)
            os.rmdir(temp_dir)

