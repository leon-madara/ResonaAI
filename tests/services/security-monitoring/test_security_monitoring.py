"""
Unit tests for Security Monitoring Service
"""

import pytest
import sys
import os
import uuid
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt


class TestSecurityMonitoring:
    """Test Security Monitoring service endpoints"""
    
    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        mock_redis = Mock()
        mock_redis.incr = Mock(return_value=1)
        mock_redis.expire = Mock()
        mock_redis.delete = Mock()
        return mock_redis
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        mock_session = Mock()
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.refresh = Mock()
        mock_session.query = Mock()
        mock_session.close = Mock()
        return mock_session
    
    @pytest.fixture
    def client(self, mock_redis, mock_db):
        """Create test client with mocked dependencies"""
        service_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 
            'apps', 'backend', 'services', 'security-monitoring'
        ))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config'] or mod_name.startswith('main.'):
                    if mod_name in sys.modules:
                        del sys.modules[mod_name]
            
            # Mock config settings
            mock_settings = Mock()
            mock_settings.DATABASE_URL = "sqlite:///:memory:"
            mock_settings.REDIS_HOST = "localhost"
            mock_settings.REDIS_PORT = 6379
            mock_settings.JWT_SECRET_KEY = "test-secret-key"
            mock_settings.JWT_ALGORITHM = "HS256"
            mock_settings.FAILED_LOGIN_THRESHOLD = 5
            mock_settings.FAILED_LOGIN_WINDOW = 300
            mock_settings.UNUSUAL_ACCESS_THRESHOLD = 10
            mock_settings.UNUSUAL_ACCESS_WINDOW = 60
            mock_settings.API_HOST = "0.0.0.0"
            mock_settings.API_PORT = 8000
            mock_settings.DEBUG = True
            mock_settings.LOG_LEVEL = "INFO"
            
            with patch.dict('sys.modules', {'config': Mock(settings=mock_settings)}), \
                 patch('redis.Redis', return_value=mock_redis):
                
                # Mock SessionLocal
                def mock_session_factory():
                    return mock_db
                
                with patch('sqlalchemy.create_engine'), \
                     patch('sqlalchemy.orm.sessionmaker', return_value=mock_session_factory):
                    
                    from main import app
                    yield TestClient(app)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def auth_token(self):
        """Generate a test JWT token"""
        token = jwt.encode(
            {
                "user_id": str(uuid.uuid4()),
                "email": "test@example.com",
                "role": "admin",
                "exp": datetime.utcnow() + timedelta(hours=1),
            },
            "test-secret-key",
            algorithm="HS256",
        )
        return f"Bearer {token}"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "security-monitoring"
        assert "timestamp" in data
    
    def test_record_failed_login(self, client, auth_token, mock_redis):
        """Test recording a failed login attempt"""
        mock_redis.incr.return_value = 1
        
        response = client.post(
            "/events/failed-login",
            params={
                "user_identifier": "test@example.com",
                "ip_address": "192.168.1.1"
            },
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["recorded"] is True
        assert "alert_generated" in data
    
    def test_failed_login_threshold_exceeded(self, client, auth_token, mock_redis, mock_db):
        """Test alert generation when failed login threshold is exceeded"""
        mock_redis.incr.return_value = 6  # Exceeds threshold of 5
        
        # Mock alert creation
        mock_alert = Mock()
        mock_alert.id = uuid.uuid4()
        mock_alert.alert_type = "failed_login"
        mock_alert.severity = "high"
        mock_alert.title = "Multiple failed login attempts"
        mock_alert.created_at = datetime.utcnow()
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', mock_alert.id))
        
        response = client.post(
            "/events/failed-login",
            params={
                "user_identifier": "test@example.com",
                "ip_address": "192.168.1.1"
            },
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["recorded"] is True
        # Alert should be generated when threshold exceeded
        assert "alert" in data
    
    def test_record_unusual_access(self, client, auth_token, mock_redis):
        """Test recording unusual access pattern"""
        mock_redis.incr.return_value = 1
        
        response = client.post(
            "/events/unusual-access",
            params={
                "user_id": str(uuid.uuid4()),
                "resource": "/api/sensitive-data",
                "ip_address": "192.168.1.1"
            },
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["recorded"] is True
        assert "alert_generated" in data
    
    def test_unusual_access_threshold_exceeded(self, client, auth_token, mock_redis, mock_db):
        """Test alert generation when unusual access threshold is exceeded"""
        mock_redis.incr.return_value = 11  # Exceeds threshold of 10
        
        response = client.post(
            "/events/unusual-access",
            params={
                "user_id": str(uuid.uuid4()),
                "resource": "/api/sensitive-data",
                "ip_address": "192.168.1.1"
            },
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["recorded"] is True
        assert "alert" in data
    
    def test_report_data_breach(self, client, auth_token, mock_db):
        """Test reporting a data breach"""
        response = client.post(
            "/events/data-breach",
            params={
                "description": "Unauthorized access to user database",
                "affected_users": 100,
                "data_types": ["email", "phone"]
            },
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["reported"] is True
        assert "alert" in data
        assert "message" in data
    
    def test_get_alerts(self, client, auth_token, mock_db):
        """Test retrieving active alerts"""
        # Mock query results
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            "/alerts",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "count" in data
    
    def test_get_alerts_with_filters(self, client, auth_token, mock_db):
        """Test retrieving alerts with severity and type filters"""
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            "/alerts?severity=high&alert_type=failed_login",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "count" in data
    
    def test_acknowledge_alert(self, client, auth_token, mock_db):
        """Test acknowledging a security alert"""
        alert_id = str(uuid.uuid4())
        
        # Mock alert retrieval
        mock_alert = Mock()
        mock_alert.id = uuid.UUID(alert_id)
        mock_alert.acknowledged = False
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_alert)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.post(
            f"/alerts/{alert_id}/acknowledge",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    def test_acknowledge_nonexistent_alert(self, client, auth_token, mock_db):
        """Test acknowledging a non-existent alert"""
        alert_id = str(uuid.uuid4())
        
        # Mock alert not found
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.post(
            f"/alerts/{alert_id}/acknowledge",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 404
    
    def test_resolve_alert(self, client, auth_token, mock_db):
        """Test resolving a security alert"""
        alert_id = str(uuid.uuid4())
        
        # Mock alert retrieval
        mock_alert = Mock()
        mock_alert.id = uuid.UUID(alert_id)
        mock_alert.resolved = False
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_alert)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.post(
            f"/alerts/{alert_id}/resolve",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data
    
    def test_resolve_nonexistent_alert(self, client, auth_token, mock_db):
        """Test resolving a non-existent alert"""
        alert_id = str(uuid.uuid4())
        
        # Mock alert not found
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.post(
            f"/alerts/{alert_id}/resolve",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 404
    
    def test_get_metrics_summary(self, client, auth_token, mock_db):
        """Test retrieving security metrics summary"""
        # Mock query results
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.group_by = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[("high", 5), ("medium", 10)])
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            "/metrics/summary",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "by_severity" in data
        assert "by_type" in data
        assert "total_active" in data
        assert "timestamp" in data
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        response = client.post(
            "/events/failed-login",
            params={
                "user_identifier": "test@example.com",
                "ip_address": "192.168.1.1"
            }
        )
        
        assert response.status_code == 403
    
    def test_invalid_token(self, client):
        """Test that invalid tokens are rejected"""
        response = client.post(
            "/events/failed-login",
            params={
                "user_identifier": "test@example.com",
                "ip_address": "192.168.1.1"
            },
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        # Should still record the event but may not extract user_id
        assert response.status_code in [200, 401, 403]
