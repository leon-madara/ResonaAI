"""
WebSocket Integration Test for Mock API Server

This module tests the WebSocket functionality of the MockAPIServer.
"""

import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock

from ..api.mock_api_server import MockAPIServer


class TestWebSocketIntegration:
    """Test WebSocket functionality"""
    
    @pytest.fixture
    def mock_storage(self):
        """Create a mock storage interface"""
        storage = Mock()
        storage.load_data.return_value = {"users": [], "conversations": []}
        return storage
    
    @pytest.fixture
    def api_server(self, mock_storage):
        """Create MockAPIServer instance"""
        return MockAPIServer(mock_storage)
    
    @pytest.fixture
    def client(self, api_server):
        """Create test client"""
        return TestClient(api_server.app)
    
    def test_websocket_connection(self, client):
        """Test WebSocket connection and message handling"""
        with client.websocket_connect("/ws/test_user") as websocket:
            # Send a test message
            test_message = {"type": "chat", "message": "Hello"}
            websocket.send_text(json.dumps(test_message))
            
            # Receive response
            data = websocket.receive_text()
            response = json.loads(data)
            
            assert response["type"] == "response"
            assert response["user_id"] == "test_user"
            assert "timestamp" in response
            assert response["data"] == test_message
    
    def test_websocket_manager(self, api_server):
        """Test WebSocket manager functionality"""
        manager = api_server.websocket_manager
        
        # Test initial state
        assert len(manager.active_connections) == 0
        
        # Test connection management (mock WebSocket)
        mock_websocket = Mock()
        manager.active_connections.append(mock_websocket)
        
        assert len(manager.active_connections) == 1
        
        # Test disconnect
        manager.disconnect(mock_websocket)
        assert len(manager.active_connections) == 0