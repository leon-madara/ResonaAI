#!/usr/bin/env python3
"""
Basic test for Cultural Context Service functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "apps", "backend", "services", "cultural-context"))

from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from main import app

def test_basic_functionality():
    """Test basic service functionality"""
    client = TestClient(app)
    
    # Test health endpoint
    print("Testing health endpoint...")
    with patch('main.get_db', return_value=Mock()):
        with patch('main.CulturalRepository'):
            # Mock the entire services module to avoid numpy import
            with patch.dict('sys.modules', {
                'services.rag_service': MagicMock(),
                'services.embeddings': MagicMock(),
                'services.code_switch_analyzer': MagicMock(),
                'services.deflection_detector': MagicMock(),
                'services.bias_detector': MagicMock()
            }):
                # Mock the get_rag_service function
                mock_rag_service = MagicMock()
                mock_rag_service.check_connection.return_value = {
                    "vector_db_type": "memory",
                    "connected": True
                }
                
                # Mock the services.rag_service.get_rag_service function
                with patch('services.rag_service.get_rag_service', return_value=mock_rag_service):
                    response = client.get("/health")
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "healthy"
                    print("✅ Health endpoint works")
    
    # Test cultural context endpoint with mocked dependencies
    print("Testing cultural context endpoint...")
    with patch('main.get_db', return_value=Mock()):
        with patch('main._get_cache', return_value=None):
            with patch('main._load_kb', return_value={"entries": []}):
                with patch('main._load_cultural_norms', return_value={}):
                    with patch('main._retrieve_entries', return_value=[]):
                        with patch('main._detect_code_switching', return_value={"code_switching_detected": False}):
                            with patch('main._detect_deflection', return_value={"deflection_detected": False, "patterns": []}):
                                with patch('main._set_cache'):
                                    response = client.get(
                                        "/context?query=test&language=en",
                                        headers={"Authorization": "Bearer test-token"}
                                    )
                                    
                                    assert response.status_code == 200
                                    data = response.json()
                                    assert "cultural_context" in data
                                    assert "deflection_analysis" in data
                                    assert "code_switching_analysis" in data
                                    print("✅ Cultural context endpoint works")
    
    # Test cultural analysis endpoint
    print("Testing cultural analysis endpoint...")
    with patch('main.get_db', return_value=Mock()):
        with patch('main.get_cultural_context') as mock_context:
            mock_context.return_value = {
                "deflection_analysis": {"deflection_detected": False, "patterns": []},
                "code_switching_analysis": {"code_switching_detected": False}
            }
            
            with patch('main._load_cultural_norms', return_value={}):
                response = client.post(
                    "/cultural-analysis",
                    json={
                        "text": "I am fine",
                        "language": "en",
                        "emotion": "neutral"
                    },
                    headers={"Authorization": "Bearer test-token"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert "risk_factors" in data
                assert "conversation_guidance" in data
                assert "response_adaptations" in data
                assert "overall_risk_level" in data
                print("✅ Cultural analysis endpoint works")
    
    print("\n🎉 All basic tests passed! Cultural Context Service is working.")

if __name__ == "__main__":
    test_basic_functionality()