"""
Unit tests for Breach Notification Service
"""

import pytest
import sys
import os
import uuid
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import jwt


class TestBreachNotification:
    """Test Breach Notification service endpoints"""
    
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
    def client(self, mock_db):
        """Create test client with mocked database"""
        service_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', '..', 
            'apps', 'backend', 'services', 'breach-notification'
        ))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main'] or mod_name.startswith('main.'):
                    if mod_name in sys.modules:
                        del sys.modules[mod_name]
            
            # Mock environment variables
            with patch.dict(os.environ, {
                'DATABASE_URL': 'sqlite:///:memory:',
                'JWT_SECRET_KEY': 'test-secret-key',
                'JWT_ALGORITHM': 'HS256'
            }):
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
                "email": "security@example.com",
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
        assert data["service"] == "breach-notification"
        assert "timestamp" in data
    
    def test_report_breach(self, client, auth_token, mock_db):
        """Test reporting a data breach"""
        # Mock breach creation
        mock_breach = Mock()
        mock_breach.id = uuid.uuid4()
        mock_breach.incident_id = "BR-20260112-ABC123"
        mock_breach.status = "detected"
        mock_breach.notification_deadline = datetime.utcnow() + timedelta(hours=72)
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', mock_breach.id))
        
        request_data = {
            "title": "Unauthorized database access",
            "description": "Suspicious activity detected in user database",
            "breach_type": "unauthorized_access",
            "severity": "high",
            "data_categories": ["email", "phone"],
            "affected_users_count": 100,
            "affected_user_ids": None
        }
        
        response = client.post(
            "/breach/report",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "breach_id" in data
        assert "incident_id" in data
        assert data["status"] == "detected"
        assert "notification_deadline" in data
        assert data["hours_remaining"] == 72
    
    def test_report_critical_breach(self, client, auth_token, mock_db):
        """Test reporting a critical severity breach"""
        mock_breach = Mock()
        mock_breach.id = uuid.uuid4()
        mock_breach.incident_id = "BR-20260112-CRITICAL"
        mock_breach.status = "detected"
        mock_breach.notification_deadline = datetime.utcnow() + timedelta(hours=72)
        mock_db.refresh = Mock(side_effect=lambda x: setattr(x, 'id', mock_breach.id))
        
        request_data = {
            "title": "Database breach with data exfiltration",
            "description": "Critical breach - sensitive data accessed and exported",
            "breach_type": "data_leak",
            "severity": "critical",
            "data_categories": ["email", "phone", "medical_records"],
            "affected_users_count": 1000,
            "affected_user_ids": None
        }
        
        response = client.post(
            "/breach/report",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "breach_id" in data
        assert "incident_id" in data
    
    def test_get_breach(self, client, auth_token, mock_db):
        """Test retrieving breach details"""
        breach_id = str(uuid.uuid4())
        
        # Mock breach retrieval
        mock_breach = Mock()
        mock_breach.id = uuid.UUID(breach_id)
        mock_breach.incident_id = "BR-20260112-ABC123"
        mock_breach.severity = "high"
        mock_breach.status = "detected"
        mock_breach.title = "Test breach"
        mock_breach.description = "Test description"
        mock_breach.breach_type = "unauthorized_access"
        mock_breach.data_categories = ["email"]
        mock_breach.affected_users_count = 100
        mock_breach.detected_at = datetime.utcnow()
        mock_breach.contained_at = None
        mock_breach.authority_notified_at = None
        mock_breach.users_notified_at = None
        mock_breach.notification_deadline = datetime.utcnow() + timedelta(hours=72)
        mock_breach.root_cause = None
        mock_breach.impact_assessment = None
        mock_breach.remediation_steps = None
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_breach)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            f"/breach/{breach_id}",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == breach_id
        assert data["incident_id"] == "BR-20260112-ABC123"
        assert data["severity"] == "high"
        assert data["status"] == "detected"
    
    def test_get_nonexistent_breach(self, client, auth_token, mock_db):
        """Test retrieving a non-existent breach"""
        breach_id = str(uuid.uuid4())
        
        # Mock breach not found
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            f"/breach/{breach_id}",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 404
    
    def test_update_breach_status(self, client, auth_token, mock_db):
        """Test updating breach status"""
        breach_id = str(uuid.uuid4())
        
        # Mock breach retrieval
        mock_breach = Mock()
        mock_breach.id = uuid.UUID(breach_id)
        mock_breach.status = "detected"
        mock_breach.contained_at = None
        mock_breach.resolved_at = None
        mock_breach.handled_by = None
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_breach)
        mock_db.query = Mock(return_value=mock_query)
        
        request_data = {
            "status": "contained",
            "root_cause": "SQL injection vulnerability",
            "impact_assessment": "100 user records accessed",
            "remediation_steps": ["Patch vulnerability", "Reset passwords"],
            "lessons_learned": "Need better input validation"
        }
        
        response = client.put(
            f"/breach/{breach_id}",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_notify_authority(self, client, auth_token, mock_db):
        """Test notifying the data protection authority"""
        breach_id = str(uuid.uuid4())
        
        # Mock breach retrieval
        mock_breach = Mock()
        mock_breach.id = uuid.UUID(breach_id)
        mock_breach.incident_id = "BR-20260112-ABC123"
        mock_breach.breach_type = "unauthorized_access"
        mock_breach.severity = "high"
        mock_breach.title = "Test breach"
        mock_breach.description = "Test description"
        mock_breach.data_categories = ["email"]
        mock_breach.affected_users_count = 100
        mock_breach.detected_at = datetime.utcnow()
        mock_breach.contained_at = datetime.utcnow()
        mock_breach.authority_notified_at = None
        mock_breach.status = "contained"
        mock_breach.root_cause = "SQL injection"
        mock_breach.remediation_steps = ["Patch applied"]
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_breach)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.post(
            f"/breach/{breach_id}/notify-authority",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notification_id" in data
        assert "notified_at" in data
        assert "recipient" in data
    
    def test_notify_authority_already_notified(self, client, auth_token, mock_db):
        """Test notifying authority when already notified"""
        breach_id = str(uuid.uuid4())
        
        # Mock breach already notified
        mock_breach = Mock()
        mock_breach.id = uuid.UUID(breach_id)
        mock_breach.authority_notified_at = datetime.utcnow()
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_breach)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.post(
            f"/breach/{breach_id}/notify-authority",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["already_notified"] is True
        assert "notified_at" in data
    
    def test_notify_users(self, client, auth_token, mock_db):
        """Test notifying affected users"""
        breach_id = str(uuid.uuid4())
        
        # Mock breach retrieval
        mock_breach = Mock()
        mock_breach.id = uuid.UUID(breach_id)
        mock_breach.incident_id = "BR-20260112-ABC123"
        mock_breach.affected_users_count = 100
        mock_breach.users_notified_at = None
        mock_breach.status = "notified_authority"
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_breach)
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.post(
            f"/breach/{breach_id}/notify-users",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "notified_at" in data
        assert data["affected_users_count"] == 100
    
    def test_list_breaches(self, client, auth_token, mock_db):
        """Test listing all breaches"""
        # Mock query results
        mock_breach1 = Mock()
        mock_breach1.id = uuid.uuid4()
        mock_breach1.incident_id = "BR-001"
        mock_breach1.severity = "high"
        mock_breach1.status = "detected"
        mock_breach1.title = "Breach 1"
        mock_breach1.affected_users_count = 100
        mock_breach1.detected_at = datetime.utcnow()
        mock_breach1.notification_deadline = datetime.utcnow() + timedelta(hours=72)
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[mock_breach1])
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            "/breaches",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "breaches" in data
        assert "count" in data
        assert data["count"] >= 0
    
    def test_list_breaches_with_filters(self, client, auth_token, mock_db):
        """Test listing breaches with status and severity filters"""
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            "/breaches?status=detected&severity=critical",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "breaches" in data
        assert "count" in data
    
    def test_get_pending_notifications(self, client, auth_token, mock_db):
        """Test getting breaches with pending notifications"""
        # Mock breach approaching deadline
        mock_breach = Mock()
        mock_breach.id = uuid.uuid4()
        mock_breach.incident_id = "BR-URGENT"
        mock_breach.title = "Urgent breach"
        mock_breach.severity = "critical"
        mock_breach.notification_deadline = datetime.utcnow() + timedelta(hours=6)
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[mock_breach])
        mock_db.query = Mock(return_value=mock_query)
        
        response = client.get(
            "/breaches/pending-notifications",
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "pending" in data
        assert "count" in data
        assert "urgent_count" in data
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        request_data = {
            "title": "Test breach",
            "description": "Test description",
            "breach_type": "unauthorized_access",
            "severity": "high",
            "data_categories": ["email"],
            "affected_users_count": 10
        }
        
        response = client.post(
            "/breach/report",
            json=request_data
        )
        
        assert response.status_code == 403
    
    def test_missing_required_fields(self, client, auth_token):
        """Test validation of required fields"""
        request_data = {
            "title": "Test",
            # Missing required fields
        }
        
        response = client.post(
            "/breach/report",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 422  # Validation error
