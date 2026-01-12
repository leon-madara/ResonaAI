"""
Fixed Property Test for Frontend Integration Consistency

**Property 4: Frontend Integration Consistency**
**Validates: Requirements 3.2, 3.3, 3.4, 3.5**
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from fastapi.testclient import TestClient
from unittest.mock import Mock

from ..api.mock_api_server import MockAPIServer


class TestFrontendIntegrationFixed:
    """Fixed property-based tests for frontend integration consistency"""
    
    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage interface with test data"""
        storage = Mock()
        
        # Mock data responses
        test_users = [
            {
                "id": "user_1",
                "profile": {
                    "age": 22,
                    "gender": "female",
                    "location": "Nairobi, Kenya",
                    "primary_language": "Swahili",
                    "secondary_language": "English"
                },
                "baseline_data": {
                    "voice_patterns": {
                        "average_pitch": 180.5,
                        "speech_rate": 145.2,
                        "emotional_baseline": "neutral"
                    },
                    "emotional_patterns": {
                        "dominant_emotions": ["neutral", "happy", "stressed"]
                    }
                }
            }
        ]
        
        test_conversations = [
            {
                "id": "conv_1",
                "user_id": "user_1",
                "scenario": "academic_pressure",
                "messages": [
                    {
                        "id": "msg_1",
                        "timestamp": "2024-01-12T10:00:00Z",
                        "speaker": "user",
                        "text": "Nimechoka na masomo",
                        "emotion": {
                            "detected": "sad",
                            "confidence": 0.78
                        }
                    }
                ]
            }
        ]
        
        storage.load_data.side_effect = lambda data_type: {
            "users": {"users": test_users},
            "conversations": {"conversations": test_conversations},
            "cultural_patterns": {"patterns": []},
            "emotions": {"emotion_data": []},
            "voice_analysis": {"voice_data": []}
        }.get(data_type, {})
        
        return storage
    
    @pytest.fixture
    def api_client(self, mock_storage):
        """Create a test client for the mock API server"""
        server = MockAPIServer(mock_storage)
        return TestClient(server.app)
    
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(user_id=st.sampled_from([
        "user123", "testuser", "demo_user", "user_abc", "sample123",
        "test_user_1", "demo123", "user_test", "abc123", "test123"
    ]))
    def test_user_data_integration_fixed(self, api_client, user_id):
        """
        Feature: demo-data-generator, Property 4: Frontend Integration Consistency
        
        Test user-related endpoints integration with frontend expectations.
        
        **Validates: Requirements 3.2, 3.3**
        """
        # Test user profile endpoint
        profile_response = api_client.get("/users/me", headers={
            "Authorization": "Bearer demo_token"
        })
        
        assert profile_response.status_code == 200
        profile_data = profile_response.json()
        
        # Validate user profile structure
        assert "id" in profile_data
        assert "username" in profile_data
        assert "email" in profile_data
        
        # Test baseline data endpoint
        baseline_response = api_client.get(f"/baseline-tracker/baseline/{user_id}", headers={
            "Authorization": "Bearer demo_token"
        })
        
        assert baseline_response.status_code == 200
        baseline_data = baseline_response.json()
        
        # Validate baseline response structure
        assert "success" in baseline_data
        assert "data" in baseline_data
        assert baseline_data["success"] is True
        
        baseline_info = baseline_data["data"]
        assert "voice_patterns" in baseline_info
        assert "emotional_patterns" in baseline_info
        
        voice_patterns = baseline_info["voice_patterns"]
        assert "average_pitch" in voice_patterns
        assert "speech_rate" in voice_patterns
        assert "emotional_baseline" in voice_patterns
        
        # Verify numeric values are reasonable
        assert isinstance(voice_patterns["average_pitch"], (int, float))
        assert isinstance(voice_patterns["speech_rate"], (int, float))
        assert voice_patterns["average_pitch"] > 0
        assert voice_patterns["speech_rate"] > 0