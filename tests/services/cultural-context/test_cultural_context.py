"""
Tests for Cultural Context Service
Comprehensive test coverage for all cultural context functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Import the main app
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "apps", "backend", "services", "cultural-context"))

from main import app
from database import get_db


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock(spec=Session)


@pytest.fixture
def mock_auth_token():
    """Mock authentication token"""
    return "Bearer test-token"


@pytest.fixture
def sample_swahili_text():
    """Sample Swahili text for testing"""
    return "Nimechoka sana, lakini sawa tu. Sijambo."


@pytest.fixture
def sample_cultural_context():
    """Sample cultural context response"""
    return {
        "cultural_context": [
            {
                "id": "swahili_deflection_nimechoka",
                "content": "The phrase 'nimechoka' often indicates emotional exhaustion",
                "keywords": ["nimechoka", "tired", "exhaustion"],
                "cultural_significance": "high"
            }
        ],
        "deflection_analysis": {
            "deflection_detected": True,
            "patterns": [
                {
                    "pattern": "nimechoka",
                    "type": "emotional_exhaustion",
                    "severity": "medium",
                    "cultural_meaning": "I am tired - can indicate emotional exhaustion"
                }
            ]
        },
        "code_switching_analysis": {
            "code_switching_detected": False,
            "intensity": "low"
        }
    }


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self, client, mock_db):
        """Test successful health check"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main.CulturalRepository'):
                with patch('services.rag_service.get_rag_service') as mock_rag:
                    mock_rag.return_value.check_connection.return_value = {
                        "vector_db_type": "memory",
                        "connected": True
                    }
                    
                    response = client.get("/health")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["status"] == "healthy"
                    assert data["service"] == "cultural-context"
                    assert data["db_connected"] is True
                    assert "vector_db" in data
    
    def test_health_check_db_failure(self, client):
        """Test health check with database failure"""
        with patch('main.get_db', side_effect=Exception("DB connection failed")):
            with patch('services.rag_service.get_rag_service') as mock_rag:
                mock_rag.return_value.check_connection.return_value = {
                    "vector_db_type": "memory",
                    "connected": True
                }
                
                response = client.get("/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["db_connected"] is False


class TestCulturalContextEndpoint:
    """Test cultural context retrieval endpoint"""
    
    def test_get_cultural_context_success(self, client, mock_db, mock_auth_token, sample_cultural_context):
        """Test successful cultural context retrieval"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main._get_cache', return_value=None):
                with patch('main._load_kb') as mock_load_kb:
                    with patch('main._load_cultural_norms') as mock_load_norms:
                        with patch('main._retrieve_entries') as mock_retrieve:
                            with patch('main._detect_code_switching') as mock_code_switch:
                                with patch('main._detect_deflection') as mock_deflection:
                                    with patch('main._set_cache'):
                                        # Setup mocks
                                        mock_load_kb.return_value = {"entries": []}
                                        mock_load_norms.return_value = {"cultural_values": {}}
                                        mock_retrieve.return_value = []
                                        mock_code_switch.return_value = {"code_switching_detected": False}
                                        mock_deflection.return_value = {"deflection_detected": False, "patterns": []}
                                        
                                        response = client.get(
                                            "/context?query=nimechoka&language=sw",
                                            headers={"Authorization": mock_auth_token}
                                        )
                                        
                                        assert response.status_code == 200
                                        data = response.json()
                                        assert "cultural_context" in data
                                        assert "deflection_analysis" in data
                                        assert "code_switching_analysis" in data
    
    def test_get_cultural_context_missing_query(self, client, mock_auth_token):
        """Test cultural context with missing query parameter"""
        response = client.get(
            "/context",
            headers={"Authorization": mock_auth_token}
        )
        
        assert response.status_code == 400
        assert "query is required" in response.json()["detail"]
    
    def test_get_cultural_context_cached(self, client, mock_db, mock_auth_token, sample_cultural_context):
        """Test cultural context retrieval from cache"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main._get_cache', return_value=sample_cultural_context):
                response = client.get(
                    "/context?query=nimechoka&language=sw",
                    headers={"Authorization": mock_auth_token}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["source"] == "db_cache"
                assert "cultural_context" in data


class TestBiasCheckEndpoint:
    """Test bias detection endpoint"""
    
    def test_bias_check_success(self, client, mock_auth_token):
        """Test successful bias check"""
        with patch('services.bias_detector.get_bias_detector') as mock_detector:
            mock_detector.return_value.assess_overall_sensitivity.return_value = {
                "overall_sensitivity": "appropriate",
                "issues": [],
                "suggestions": []
            }
            
            response = client.post(
                "/bias-check?text=This is appropriate text",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "overall_sensitivity" in data
    
    def test_bias_check_missing_text(self, client, mock_auth_token):
        """Test bias check with missing text"""
        response = client.post(
            "/bias-check",
            headers={"Authorization": mock_auth_token}
        )
        
        assert response.status_code == 400
        assert "text is required" in response.json()["detail"]
    
    def test_bias_check_detector_failure(self, client, mock_auth_token):
        """Test bias check with detector failure"""
        with patch('services.bias_detector.get_bias_detector', side_effect=Exception("Detector failed")):
            response = client.post(
                "/bias-check?text=test text",
                headers={"Authorization": mock_auth_token}
            )
            
            assert response.status_code == 500
            assert "Bias detection failed" in response.json()["detail"]


class TestCulturalAnalysisEndpoint:
    """Test comprehensive cultural analysis endpoint"""
    
    def test_cultural_analysis_success(self, client, mock_db, mock_auth_token):
        """Test successful cultural analysis"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main.get_cultural_context') as mock_context:
                mock_context.return_value = {
                    "deflection_analysis": {
                        "deflection_detected": True,
                        "patterns": [
                            {
                                "pattern": "nimechoka",
                                "severity": "medium",
                                "probe_suggestions": ["Can you tell me more?"]
                            }
                        ]
                    },
                    "code_switching_analysis": {
                        "code_switching_detected": True,
                        "intensity": "high"
                    }
                }
                
                with patch('main._load_cultural_norms') as mock_norms:
                    mock_norms.return_value = {
                        "cultural_values": {
                            "privacy_and_family_reputation": {},
                            "spiritual_and_religious_beliefs": {}
                        }
                    }
                    
                    response = client.post(
                        "/cultural-analysis",
                        json={
                            "text": "Nimechoka sana",
                            "language": "sw",
                            "emotion": "sad"
                        },
                        headers={"Authorization": mock_auth_token}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert "risk_factors" in data
                    assert "conversation_guidance" in data
                    assert "response_adaptations" in data
                    assert "overall_risk_level" in data
    
    def test_cultural_analysis_voice_contradiction(self, client, mock_db, mock_auth_token):
        """Test cultural analysis with voice-text contradiction"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main.get_cultural_context') as mock_context:
                mock_context.return_value = {
                    "deflection_analysis": {"deflection_detected": False, "patterns": []},
                    "code_switching_analysis": {"code_switching_detected": False}
                }
                
                with patch('main._load_cultural_norms', return_value={}):
                    response = client.post(
                        "/cultural-analysis",
                        json={
                            "text": "I'm fine, everything is okay",
                            "language": "en",
                            "emotion": "sad",
                            "voice_features": {"tone": "sad", "energy": "low"}
                        },
                        headers={"Authorization": mock_auth_token}
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    
                    # Should detect voice-text contradiction
                    risk_factors = data["risk_factors"]
                    contradiction_risks = [rf for rf in risk_factors if rf["type"] == "voice_text_contradiction"]
                    assert len(contradiction_risks) > 0


class TestIndexKnowledgeBaseEndpoint:
    """Test knowledge base indexing endpoint"""
    
    def test_index_kb_success(self, client, mock_auth_token):
        """Test successful knowledge base indexing"""
        with patch('services.rag_service.get_rag_service') as mock_rag:
            with patch('main._load_kb') as mock_load_kb:
                mock_rag_instance = Mock()
                mock_rag_instance.vector_db_type = "memory"
                mock_rag_instance.clear_index.return_value = True
                mock_rag_instance.index_knowledge_base.return_value = 5
                mock_rag_instance.get_index_stats.return_value = {"total_vector_count": 5}
                mock_rag.return_value = mock_rag_instance
                
                mock_load_kb.return_value = {
                    "entries": [
                        {"id": "1", "content": "test1"},
                        {"id": "2", "content": "test2"},
                        {"id": "3", "content": "test3"},
                        {"id": "4", "content": "test4"},
                        {"id": "5", "content": "test5"}
                    ]
                }
                
                response = client.post(
                    "/index-kb?clear_existing=true",
                    headers={"Authorization": mock_auth_token}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["indexed_count"] == 5
                assert data["total_entries"] == 5
    
    def test_index_kb_no_entries(self, client, mock_auth_token):
        """Test indexing with no knowledge base entries"""
        with patch('services.rag_service.get_rag_service') as mock_rag:
            with patch('main._load_kb') as mock_load_kb:
                mock_rag_instance = Mock()
                mock_rag_instance.vector_db_type = "memory"
                mock_rag.return_value = mock_rag_instance
                
                mock_load_kb.return_value = {"entries": []}
                
                response = client.post(
                    "/index-kb",
                    headers={"Authorization": mock_auth_token}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["indexed_count"] == 0
                assert data["total_entries"] == 0
    
    def test_index_kb_file_not_found(self, client, mock_auth_token):
        """Test indexing with missing knowledge base file"""
        with patch('services.rag_service.get_rag_service') as mock_rag:
            with patch('main._load_kb', side_effect=FileNotFoundError("KB file not found")):
                mock_rag_instance = Mock()
                mock_rag_instance.vector_db_type = "memory"
                mock_rag.return_value = mock_rag_instance
                
                response = client.post(
                    "/index-kb",
                    headers={"Authorization": mock_auth_token}
                )
                
                assert response.status_code == 404
                assert "Knowledge base file not found" in response.json()["detail"]


class TestCulturalPatternDetection:
    """Test cultural pattern detection functionality"""
    
    def test_swahili_deflection_detection(self, client, mock_db, mock_auth_token):
        """Test detection of Swahili deflection patterns"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main._get_cache', return_value=None):
                with patch('main._load_kb', return_value={"entries": []}):
                    with patch('main._load_cultural_norms', return_value={}):
                        with patch('main._retrieve_entries', return_value=[]):
                            with patch('main._detect_code_switching') as mock_code_switch:
                                with patch('main._detect_deflection') as mock_deflection:
                                    with patch('main._set_cache'):
                                        # Mock deflection detection
                                        mock_deflection.return_value = {
                                            "deflection_detected": True,
                                            "patterns": [
                                                {
                                                    "pattern": "sawa",
                                                    "type": "deflection",
                                                    "severity": "low",
                                                    "cultural_meaning": "Polite deflection"
                                                }
                                            ]
                                        }
                                        mock_code_switch.return_value = {"code_switching_detected": False}
                                        
                                        response = client.get(
                                            "/context?query=sawa tu&language=sw",
                                            headers={"Authorization": mock_auth_token}
                                        )
                                        
                                        assert response.status_code == 200
                                        data = response.json()
                                        assert data["deflection_analysis"]["deflection_detected"] is True
                                        assert len(data["deflection_analysis"]["patterns"]) == 1
    
    def test_code_switching_detection(self, client, mock_db, mock_auth_token):
        """Test detection of code-switching patterns"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main._get_cache', return_value=None):
                with patch('main._load_kb', return_value={"entries": []}):
                    with patch('main._load_cultural_norms', return_value={}):
                        with patch('main._retrieve_entries', return_value=[]):
                            with patch('main._detect_deflection') as mock_deflection:
                                with patch('main._detect_code_switching') as mock_code_switch:
                                    with patch('main._set_cache'):
                                        # Mock code-switching detection
                                        mock_code_switch.return_value = {
                                            "code_switching_detected": True,
                                            "swahili_words": ["nimechoka"],
                                            "english_words": ["tired"],
                                            "intensity": "high"
                                        }
                                        mock_deflection.return_value = {"deflection_detected": False, "patterns": []}
                                        
                                        response = client.get(
                                            "/context?query=I am nimechoka very tired&language=en",
                                            headers={"Authorization": mock_auth_token}
                                        )
                                        
                                        assert response.status_code == 200
                                        data = response.json()
                                        assert data["code_switching_analysis"]["code_switching_detected"] is True
                                        assert data["code_switching_analysis"]["intensity"] == "high"


class TestRAGIntegration:
    """Test RAG service integration"""
    
    def test_rag_retrieval_success(self, client, mock_db, mock_auth_token):
        """Test successful RAG-based context retrieval"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main._get_cache', return_value=None):
                with patch('main._load_kb') as mock_load_kb:
                    with patch('main._load_cultural_norms', return_value={}):
                        with patch('services.rag_service.get_rag_service') as mock_rag:
                            with patch('main._detect_code_switching', return_value={"code_switching_detected": False}):
                                with patch('main._detect_deflection', return_value={"deflection_detected": False, "patterns": []}):
                                    with patch('main._set_cache'):
                                        # Setup RAG mock
                                        mock_rag_instance = Mock()
                                        mock_rag_instance.is_available.return_value = True
                                        mock_rag_instance.search.return_value = [
                                            {
                                                "id": "swahili_deflection_sawa",
                                                "score": 0.95,
                                                "metadata": {
                                                    "text": "Sawa deflection pattern",
                                                    "keywords": ["sawa", "deflection"]
                                                }
                                            }
                                        ]
                                        mock_rag.return_value = mock_rag_instance
                                        
                                        # Setup KB with matching entry
                                        mock_load_kb.return_value = {
                                            "entries": [
                                                {
                                                    "id": "swahili_deflection_sawa",
                                                    "content": "Sawa deflection pattern",
                                                    "keywords": ["sawa", "deflection"]
                                                }
                                            ]
                                        }
                                        
                                        response = client.get(
                                            "/context?query=sawa&language=sw",
                                            headers={"Authorization": mock_auth_token}
                                        )
                                        
                                        assert response.status_code == 200
                                        data = response.json()
                                        assert len(data["cultural_context"]) > 0
    
    def test_rag_fallback_to_keyword_search(self, client, mock_db, mock_auth_token):
        """Test fallback to keyword search when RAG fails"""
        with patch('main.get_db', return_value=mock_db):
            with patch('main._get_cache', return_value=None):
                with patch('main._load_kb') as mock_load_kb:
                    with patch('main._load_cultural_norms', return_value={}):
                        with patch('services.rag_service.get_rag_service') as mock_rag:
                            with patch('main._detect_code_switching', return_value={"code_switching_detected": False}):
                                with patch('main._detect_deflection', return_value={"deflection_detected": False, "patterns": []}):
                                    with patch('main._set_cache'):
                                        # Setup RAG to fail
                                        mock_rag_instance = Mock()
                                        mock_rag_instance.is_available.return_value = False
                                        mock_rag.return_value = mock_rag_instance
                                        
                                        # Setup KB for keyword search
                                        mock_load_kb.return_value = {
                                            "entries": [
                                                {
                                                    "id": "test_entry",
                                                    "content": "Test content",
                                                    "keywords": ["sawa", "deflection"],
                                                    "language": "sw"
                                                }
                                            ]
                                        }
                                        
                                        response = client.get(
                                            "/context?query=sawa&language=sw",
                                            headers={"Authorization": mock_auth_token}
                                        )
                                        
                                        assert response.status_code == 200
                                        data = response.json()
                                        # Should still get results from keyword search
                                        assert "cultural_context" in data


if __name__ == "__main__":
    pytest.main([__file__])