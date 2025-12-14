"""
Unit tests for Crisis Detection Service
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from datetime import datetime
from uuid import uuid4

# Store original working directory
original_cwd = os.getcwd()


class TestCrisisDetection:
    """Test Crisis Detection service endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        # Change to service directory for imports
        service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'crisis-detection'))
        old_cwd = os.getcwd()
        os.chdir(service_dir)
        
        try:
            # Add service directory to Python path
            if service_dir not in sys.path:
                sys.path.insert(0, service_dir)
            
            # Clear cached modules
            modules_to_remove = []
            for mod_name in list(sys.modules.keys()):
                if mod_name in ['main', 'config', 'database', 'models', 'models.database_models', 'repositories', 'repositories.crisis_repository']:
                    modules_to_remove.append(mod_name)
            for mod in modules_to_remove:
                if mod in sys.modules:
                    del sys.modules[mod]

            with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
                # Import app after env is set so the service uses SQLite
                from database import init_db
                init_db()
            
                with patch('main.risk_calculator') as mock_calculator:
                    mock_calculator.calculate_risk = Mock(return_value={
                        "risk_level": "medium",
                        "risk_score": 0.65,
                        "crisis_detected": False,
                        "detection_methods": ["emotion", "keyword"],
                        "escalation_required": False,
                        "recommended_action": "monitor"
                    })

                    from main import app
                    yield TestClient(app)
        finally:
            os.chdir(old_cwd)
            if service_dir in sys.path:
                sys.path.remove(service_dir)
    
    @pytest.fixture
    def auth_token(self):
        """Generate a test JWT token"""
        return "Bearer test-token"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "crisis-detection"
    
    def test_detect_crisis_low_risk(self, client, auth_token):
        """Test crisis detection with low risk"""
        user_id = str(uuid4())
        request_data = {
            "user_id": user_id,
            "transcript": "I'm feeling okay today",
            "emotion_data": {
                "emotion": "neutral",
                "confidence": 0.70
            },
            "dissonance_data": None,
            "baseline_data": None
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "medium"
        assert data["crisis_detected"] is False
        assert "detection_methods" in data
        assert "recommended_action" in data
        assert "timestamp" in data
        assert "details" in data
    
    def test_detect_crisis_high_risk(self, client, auth_token):
        """Test crisis detection with high risk"""
        user_id = str(uuid4())
        with patch('main.risk_calculator') as mock_calculator:
            mock_calculator.calculate_risk = Mock(return_value={
                "risk_level": "critical",
                "risk_score": 0.95,
                "crisis_detected": True,
                "detection_methods": ["keyword", "emotion", "dissonance"],
                "escalation_required": True,
                "recommended_action": "emergency"
            })
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "user_id": user_id,
                "transcript": "I want to end it all",
                "emotion_data": {
                    "emotion": "sad",
                    "confidence": 0.95
                },
                "dissonance_data": {
                    "dissonance_level": "high",
                    "risk_level": "high"
                },
                "baseline_data": {
                    "deviation_detected": True,
                    "deviation_score": 0.85
                }
            }
            
            response = test_client.post(
                "/detect",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["risk_level"] == "critical"
            assert data["crisis_detected"] is True
            assert data["escalation_required"] is True
            assert data["recommended_action"] == "emergency"
    
    def test_detect_crisis_with_all_data(self, client, auth_token):
        """Test crisis detection with all data sources"""
        user_id = str(uuid4())
        request_data = {
            "user_id": user_id,
            "session_id": "session-123",
            "conversation_id": "conv-456",
            "transcript": "I'm struggling",
            "emotion_data": {
                "emotion": "sad",
                "confidence": 0.85
            },
            "dissonance_data": {
                "dissonance_level": "medium",
                "risk_level": "medium"
            },
            "baseline_data": {
                "deviation_detected": True,
                "deviation_score": 0.60
            }
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "details" in data
        assert data["details"]["user_id"] == user_id
        assert data["details"]["session_id"] == "session-123"
        assert data["details"]["conversation_id"] == "conv-456"
    
    def test_detect_crisis_missing_transcript(self, client, auth_token):
        """Test crisis detection with missing transcript"""
        user_id = str(uuid4())
        request_data = {
            "user_id": user_id,
            "emotion_data": {"emotion": "sad"}
        }
        
        response = client.post(
            "/detect",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        # transcript is optional in the current API contract
        assert response.status_code == 200
    
    def test_detect_crisis_no_auth(self, client):
        """Test crisis detection without authentication"""
        request_data = {
            "user_id": str(uuid4()),
            "transcript": "I'm feeling down"
        }
        
        response = client.post("/detect", json=request_data)
        assert response.status_code == 403
    
    def test_escalate_crisis(self, client, auth_token):
        """Test crisis escalation"""
        # Create a crisis event first so we can reference it
        from database import SessionLocal
        from repositories.crisis_repository import CrisisRepository

        user_uuid = uuid4()
        with SessionLocal() as db:
            repo = CrisisRepository(db)
            event = repo.create_crisis_event(
                user_id=user_uuid,
                risk_level="critical",
                detection_method="test",
                escalation_required=True,
            )

        request_data = {
            "user_id": str(user_uuid),
            "risk_level": "critical",
            "crisis_id": str(event.id),
            "escalation_type": "emergency",
            "reason": "High risk detected"
        }
        
        response = client.post(
            "/escalate",
            json=request_data,
            headers={"Authorization": auth_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "escalation_id" in data
        assert data["status"] in ["routed", "created", "initiated"]
        assert "action_taken" in data
        assert "timestamp" in data
    
    def test_escalate_crisis_different_types(self, client, auth_token):
        """Test different escalation types"""
        from database import SessionLocal
        from repositories.crisis_repository import CrisisRepository

        user_uuid = uuid4()
        with SessionLocal() as db:
            repo = CrisisRepository(db)
            event = repo.create_crisis_event(
                user_id=user_uuid,
                risk_level="high",
                detection_method="test",
                escalation_required=True,
            )

        escalation_types = ["emergency", "human_review", "monitoring"]
        
        for esc_type in escalation_types:
            request_data = {
                "user_id": str(user_uuid),
                "risk_level": "high",
                "crisis_id": str(event.id),
                "escalation_type": esc_type,
                "reason": f"Escalating via {esc_type}"
            }
            
            response = client.post(
                "/escalate",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert esc_type in data["action_taken"].lower()

    def test_escalate_crisis_idempotent(self, client, auth_token):
        """Repeated escalation calls should be idempotent."""
        from database import SessionLocal
        from repositories.crisis_repository import CrisisRepository

        user_uuid = uuid4()
        with SessionLocal() as db:
            repo = CrisisRepository(db)
            event = repo.create_crisis_event(
                user_id=user_uuid,
                risk_level="high",
                detection_method="test",
                escalation_required=True,
            )

        idempotency_key = f"{event.id}:human_review"
        request_data = {
            "user_id": str(user_uuid),
            "risk_level": "high",
            "crisis_id": str(event.id),
            "escalation_type": "human_review",
            "idempotency_key": idempotency_key,
        }

        r1 = client.post("/escalate", json=request_data, headers={"Authorization": auth_token})
        assert r1.status_code == 200
        e1 = r1.json()["escalation_id"]

        r2 = client.post("/escalate", json=request_data, headers={"Authorization": auth_token})
        assert r2.status_code == 200
        e2 = r2.json()["escalation_id"]

        assert e1 == e2

    def test_escalate_crisis_persists_record(self, client, auth_token):
        """Escalation should create a persisted escalation record."""
        from database import SessionLocal
        from repositories.crisis_repository import CrisisRepository
        from models.database_models import CrisisEscalation
        import uuid as uuid_module

        user_uuid = uuid4()
        with SessionLocal() as db:
            repo = CrisisRepository(db)
            event = repo.create_crisis_event(
                user_id=user_uuid,
                risk_level="critical",
                detection_method="test",
                escalation_required=True,
            )

        resp = client.post(
            "/escalate",
            json={
                "user_id": str(user_uuid),
                "risk_level": "critical",
                "crisis_id": str(event.id),
                "escalation_type": "human_review",
            },
            headers={"Authorization": auth_token},
        )
        assert resp.status_code == 200
        escalation_id = resp.json()["escalation_id"]

        with SessionLocal() as db:
            row = db.query(CrisisEscalation).filter(CrisisEscalation.id == uuid_module.UUID(escalation_id)).first()
            assert row is not None
            assert row.status in ("routed", "created", "failed")

    def test_escalate_crisis_failure_handling(self, client, auth_token):
        """If routing fails, escalation should be marked failed and request should error."""
        from database import SessionLocal
        from models.database_models import CrisisEscalation
        import repositories.crisis_repository as crisis_repo_module

        user_uuid = uuid4()
        with SessionLocal() as db:
            repo = crisis_repo_module.CrisisRepository(db)
            event = repo.create_crisis_event(
                user_id=user_uuid,
                risk_level="critical",
                detection_method="test",
                escalation_required=True,
            )

        # Fail only the "routed" transition; allow the failure transition to persist.
        original_update = crisis_repo_module.CrisisRepository.update_escalation_state

        def fail_routed(self, *, escalation_id, new_status, action_taken=None, error_message=None):
            if new_status == "routed":
                raise RuntimeError("routing provider down")
            return original_update(
                self,
                escalation_id=escalation_id,
                new_status=new_status,
                action_taken=action_taken,
                error_message=error_message,
            )

        with patch.object(crisis_repo_module.CrisisRepository, "update_escalation_state", new=fail_routed):
            resp = client.post(
                "/escalate",
                json={
                    "user_id": str(user_uuid),
                    "risk_level": "critical",
                    "crisis_id": str(event.id),
                    "escalation_type": "emergency",
                    "idempotency_key": f"{event.id}:emergency:fail",
                },
                headers={"Authorization": auth_token},
            )
            assert resp.status_code in (500, 502)

        # Confirm a failed record exists for the idempotency key.
        with SessionLocal() as db:
            row = (
                db.query(CrisisEscalation)
                .filter(CrisisEscalation.idempotency_key == f"{event.id}:emergency:fail")
                .first()
            )
            assert row is not None
            assert row.status == "failed"
    
    def test_escalate_crisis_no_auth(self, client):
        """Test escalation without authentication"""
        request_data = {
            "user_id": str(uuid4()),
            "risk_level": "high",
            "crisis_id": str(uuid4()),
            "escalation_type": "emergency"
        }
        
        response = client.post("/escalate", json=request_data)
        assert response.status_code == 403
    
    def test_detect_crisis_error_handling(self, client, auth_token):
        """Test error handling in crisis detection"""
        with patch('main.risk_calculator') as mock_calculator:
            mock_calculator.calculate_risk = Mock(side_effect=Exception("Calculation failed"))
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "user_id": "test-user",
                "transcript": "I'm feeling down"
            }
            
            response = test_client.post(
                "/detect",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 500
            assert "failed" in response.json()["detail"].lower()
    
    def test_detect_crisis_medium_risk(self, client, auth_token):
        """Test crisis detection with medium risk"""
        with patch('main.risk_calculator') as mock_calculator:
            mock_calculator.calculate_risk = Mock(return_value={
                "risk_level": "medium",
                "risk_score": 0.70,
                "crisis_detected": True,
                "detection_methods": ["emotion", "dissonance"],
                "escalation_required": True,
                "recommended_action": "review"
            })
            
            from main import app
            test_client = TestClient(app)
            
            request_data = {
                "user_id": "test-user",
                "transcript": "I'm having a hard time",
                "emotion_data": {"emotion": "sad", "confidence": 0.80},
                "dissonance_data": {"dissonance_level": "medium"}
            }
            
            response = test_client.post(
                "/detect",
                json=request_data,
                headers={"Authorization": auth_token}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["risk_level"] == "medium"
            assert data["crisis_detected"] is True
            assert data["escalation_required"] is True

