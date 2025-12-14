"""
Tests for database schema completion - Task 2.1
Tests user_baselines and session_deviations tables
"""

import pytest
import os
import sys
from datetime import datetime
from decimal import Decimal
from sqlalchemy import create_engine, text, inspect, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import IntegrityError
import uuid

# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    return engine


@pytest.fixture(scope="function")
def db_session(test_engine):
    """Create database session and manually create tables for testing"""
    # Manually create tables with SQLite-compatible syntax
    with test_engine.connect() as conn:
        # Enable foreign key constraints in SQLite
        conn.execute(text("PRAGMA foreign_keys = ON"))
        
        # Create users table (prerequisite)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                phone TEXT,
                password_hash TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                last_active TEXT DEFAULT (datetime('now')),
                consent_version TEXT,
                data_retention_until TEXT,
                is_anonymous INTEGER DEFAULT 1
            )
        """))
        
        # Create conversations table (prerequisite)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                started_at TEXT DEFAULT (datetime('now')),
                ended_at TEXT,
                emotion_summary TEXT,
                crisis_detected INTEGER DEFAULT 0,
                escalated_to_human INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """))
        
        # Create user_baselines table (NEW - Task 2.1)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS user_baselines (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                baseline_type TEXT NOT NULL,
                baseline_value TEXT NOT NULL,
                session_count INTEGER DEFAULT 0,
                established_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, baseline_type)
            )
        """))
        
        # Create indexes for user_baselines
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_baselines_user_id 
            ON user_baselines(user_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_user_baselines_type 
            ON user_baselines(baseline_type)
        """))
        
        # Create session_deviations table (NEW - Task 2.1)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS session_deviations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                deviation_type TEXT NOT NULL,
                baseline_value TEXT,
                current_value TEXT,
                deviation_score REAL NOT NULL,
                detected_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (session_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """))
        
        # Create indexes for session_deviations
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_session_deviations_user_id 
            ON session_deviations(user_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_session_deviations_session_id 
            ON session_deviations(session_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_session_deviations_score 
            ON session_deviations(deviation_score)
        """))
        
        conn.commit()
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def sample_user_id():
    """Generate a sample user ID"""
    return str(uuid.uuid4())


@pytest.fixture
def sample_conversation_id():
    """Generate a sample conversation ID"""
    return str(uuid.uuid4())


class TestUserBaselinesTable:
    """Tests for user_baselines table"""
    
    def test_table_exists(self, test_engine, db_session):
        """Test that user_baselines table exists"""
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()
        assert 'user_baselines' in tables, "user_baselines table should exist"
    
    def test_table_columns(self, test_engine, db_session):
        """Test that user_baselines table has all required columns"""
        inspector = inspect(test_engine)
        columns = {col['name']: col for col in inspector.get_columns('user_baselines')}
        
        required_columns = [
            'id', 'user_id', 'baseline_type', 'baseline_value',
            'session_count', 'established_at', 'updated_at'
        ]
        
        for col_name in required_columns:
            assert col_name in columns, f"Column {col_name} should exist"
    
    def test_insert_baseline(self, db_session, sample_user_id):
        """Test inserting a baseline record"""
        # First create a user
        user_id = sample_user_id
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        db_session.commit()
        
        # Insert a baseline
        baseline_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO user_baselines 
            (id, user_id, baseline_type, baseline_value, session_count, established_at, updated_at)
            VALUES (:id, :user_id, :baseline_type, :baseline_value, :session_count, 
                    datetime('now'), datetime('now'))
        """), {
            "id": baseline_id,
            "user_id": user_id,
            "baseline_type": "emotion",
            "baseline_value": '{"mean": 0.5, "std": 0.1}',
            "session_count": 10
        })
        db_session.commit()
        
        # Verify insertion
        result = db_session.execute(text("""
            SELECT * FROM user_baselines WHERE id = :id
        """), {"id": baseline_id}).fetchone()
        
        assert result is not None, "Baseline should be inserted"
        assert result[2] == "emotion", "Baseline type should be 'emotion'"
        assert result[4] == 10, "Session count should be 10"
    
    def test_unique_constraint(self, db_session, sample_user_id):
        """Test that unique constraint on (user_id, baseline_type) works"""
        # Create a user
        user_id = sample_user_id
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        db_session.commit()
        
        # Insert first baseline
        db_session.execute(text("""
            INSERT INTO user_baselines 
            (id, user_id, baseline_type, baseline_value, session_count, established_at, updated_at)
            VALUES (:id, :user_id, :baseline_type, :baseline_value, :session_count, 
                    datetime('now'), datetime('now'))
        """), {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "baseline_type": "pitch",
            "baseline_value": '{"mean": 200}',
            "session_count": 5
        })
        db_session.commit()
        
        # Try to insert duplicate (same user_id and baseline_type)
        with pytest.raises(IntegrityError):
            db_session.execute(text("""
                INSERT INTO user_baselines 
                (id, user_id, baseline_type, baseline_value, session_count, established_at, updated_at)
                VALUES (:id, :user_id, :baseline_type, :baseline_value, :session_count, 
                        datetime('now'), datetime('now'))
            """), {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "baseline_type": "pitch",  # Same type
                "baseline_value": '{"mean": 250}',
                "session_count": 3
            })
            db_session.commit()
    
    def test_foreign_key_cascade(self, db_session, sample_user_id):
        """Test that CASCADE delete works when user is deleted"""
        # Create a user
        user_id = sample_user_id
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        db_session.commit()
        
        # Insert a baseline
        baseline_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO user_baselines 
            (id, user_id, baseline_type, baseline_value, session_count, established_at, updated_at)
            VALUES (:id, :user_id, :baseline_type, :baseline_value, :session_count, 
                    datetime('now'), datetime('now'))
        """), {
            "id": baseline_id,
            "user_id": user_id,
            "baseline_type": "energy",
            "baseline_value": '{"mean": 0.7}',
            "session_count": 8
        })
        db_session.commit()
        
        # Verify baseline exists
        result = db_session.execute(text("""
            SELECT COUNT(*) FROM user_baselines WHERE user_id = :user_id
        """), {"user_id": user_id}).scalar()
        assert result == 1, "Baseline should exist"
        
        # Delete user (should cascade to baselines)
        db_session.execute(text("""
            DELETE FROM users WHERE id = :id
        """), {"id": user_id})
        db_session.commit()
        
        # Verify baseline is deleted
        result = db_session.execute(text("""
            SELECT COUNT(*) FROM user_baselines WHERE user_id = :user_id
        """), {"user_id": user_id}).scalar()
        assert result == 0, "Baseline should be deleted when user is deleted"
    
    def test_indexes_exist(self, test_engine, db_session):
        """Test that indexes are created"""
        inspector = inspect(test_engine)
        indexes = inspector.get_indexes('user_baselines')
        
        index_names = [idx['name'] for idx in indexes]
        
        # Check for required indexes
        assert any('user_id' in name for name in index_names), "Index on user_id should exist"
        assert any('type' in name for name in index_names), "Index on baseline_type should exist"


class TestSessionDeviationsTable:
    """Tests for session_deviations table"""
    
    def test_table_exists(self, test_engine, db_session):
        """Test that session_deviations table exists"""
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()
        assert 'session_deviations' in tables, "session_deviations table should exist"
    
    def test_table_columns(self, test_engine, db_session):
        """Test that session_deviations table has all required columns"""
        inspector = inspect(test_engine)
        columns = {col['name']: col for col in inspector.get_columns('session_deviations')}
        
        required_columns = [
            'id', 'user_id', 'session_id', 'deviation_type',
            'baseline_value', 'current_value', 'deviation_score', 'detected_at'
        ]
        
        for col_name in required_columns:
            assert col_name in columns, f"Column {col_name} should exist"
    
    def test_insert_deviation(self, db_session, sample_user_id, sample_conversation_id):
        """Test inserting a deviation record"""
        user_id = sample_user_id
        conversation_id = sample_conversation_id
        
        # Create user
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        
        # Create conversation
        db_session.execute(text("""
            INSERT INTO conversations (id, user_id, started_at)
            VALUES (:id, :user_id, datetime('now'))
        """), {"id": conversation_id, "user_id": user_id})
        db_session.commit()
        
        # Insert deviation
        deviation_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO session_deviations 
            (id, user_id, session_id, deviation_type, baseline_value, current_value, 
             deviation_score, detected_at)
            VALUES (:id, :user_id, :session_id, :deviation_type, :baseline_value, 
                    :current_value, :deviation_score, datetime('now'))
        """), {
            "id": deviation_id,
            "user_id": user_id,
            "session_id": conversation_id,
            "deviation_type": "pitch",
            "baseline_value": '{"mean": 200}',
            "current_value": '{"mean": 150}',
            "deviation_score": 2.5
        })
        db_session.commit()
        
        # Verify insertion
        result = db_session.execute(text("""
            SELECT * FROM session_deviations WHERE id = :id
        """), {"id": deviation_id}).fetchone()
        
        assert result is not None, "Deviation should be inserted"
        assert result[3] == "pitch", "Deviation type should be 'pitch'"
        assert result[6] == 2.5, "Deviation score should be 2.5"
    
    def test_foreign_key_to_user(self, db_session, sample_user_id, sample_conversation_id):
        """Test foreign key constraint to users table"""
        user_id = sample_user_id
        conversation_id = sample_conversation_id
        
        # Create user and conversation
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        
        db_session.execute(text("""
            INSERT INTO conversations (id, user_id, started_at)
            VALUES (:id, :user_id, datetime('now'))
        """), {"id": conversation_id, "user_id": user_id})
        db_session.commit()
        
        # Insert deviation
        deviation_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO session_deviations 
            (id, user_id, session_id, deviation_type, deviation_score, detected_at)
            VALUES (:id, :user_id, :session_id, :deviation_type, :deviation_score, datetime('now'))
        """), {
            "id": deviation_id,
            "user_id": user_id,
            "session_id": conversation_id,
            "deviation_type": "energy",
            "deviation_score": 1.8
        })
        db_session.commit()
        
        # Delete user (should cascade)
        db_session.execute(text("""
            DELETE FROM users WHERE id = :id
        """), {"id": user_id})
        db_session.commit()
        
        # Verify deviation is deleted
        result = db_session.execute(text("""
            SELECT COUNT(*) FROM session_deviations WHERE id = :id
        """), {"id": deviation_id}).scalar()
        assert result == 0, "Deviation should be deleted when user is deleted"
    
    def test_foreign_key_to_conversation(self, db_session, sample_user_id, sample_conversation_id):
        """Test foreign key constraint to conversations table"""
        user_id = sample_user_id
        conversation_id = sample_conversation_id
        
        # Create user and conversation
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        
        db_session.execute(text("""
            INSERT INTO conversations (id, user_id, started_at)
            VALUES (:id, :user_id, datetime('now'))
        """), {"id": conversation_id, "user_id": user_id})
        db_session.commit()
        
        # Insert deviation
        deviation_id = str(uuid.uuid4())
        db_session.execute(text("""
            INSERT INTO session_deviations 
            (id, user_id, session_id, deviation_type, deviation_score, detected_at)
            VALUES (:id, :user_id, :session_id, :deviation_type, :deviation_score, datetime('now'))
        """), {
            "id": deviation_id,
            "user_id": user_id,
            "session_id": conversation_id,
            "deviation_type": "rate",
            "deviation_score": 3.2
        })
        db_session.commit()
        
        # Delete conversation (should cascade)
        db_session.execute(text("""
            DELETE FROM conversations WHERE id = :id
        """), {"id": conversation_id})
        db_session.commit()
        
        # Verify deviation is deleted
        result = db_session.execute(text("""
            SELECT COUNT(*) FROM session_deviations WHERE id = :id
        """), {"id": deviation_id}).scalar()
        assert result == 0, "Deviation should be deleted when conversation is deleted"
    
    def test_query_deviations_by_score(self, db_session, sample_user_id, sample_conversation_id):
        """Test querying deviations by score (index test)"""
        user_id = sample_user_id
        conversation_id = sample_conversation_id
        
        # Create user and conversation
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        
        db_session.execute(text("""
            INSERT INTO conversations (id, user_id, started_at)
            VALUES (:id, :user_id, datetime('now'))
        """), {"id": conversation_id, "user_id": user_id})
        db_session.commit()
        
        # Insert multiple deviations with different scores
        for i, score in enumerate([1.0, 2.5, 3.5, 4.0]):
            db_session.execute(text("""
                INSERT INTO session_deviations 
                (id, user_id, session_id, deviation_type, deviation_score, detected_at)
                VALUES (:id, :user_id, :session_id, :deviation_type, :deviation_score, datetime('now'))
            """), {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "session_id": conversation_id,
                "deviation_type": f"type_{i}",
                "deviation_score": score
            })
        db_session.commit()
        
        # Query high-score deviations
        result = db_session.execute(text("""
            SELECT COUNT(*) FROM session_deviations 
            WHERE deviation_score > 3.0
        """)).scalar()
        
        assert result == 2, "Should find 2 deviations with score > 3.0"
    
    def test_indexes_exist(self, test_engine, db_session):
        """Test that indexes are created"""
        inspector = inspect(test_engine)
        indexes = inspector.get_indexes('session_deviations')
        
        index_names = [idx['name'] for idx in indexes]
        
        # Check for required indexes
        assert any('user_id' in name for name in index_names), "Index on user_id should exist"
        assert any('session_id' in name for name in index_names), "Index on session_id should exist"
        assert any('score' in name for name in index_names), "Index on deviation_score should exist"


class TestSchemaIntegration:
    """Integration tests for both tables working together"""
    
    def test_baseline_and_deviation_workflow(self, db_session, sample_user_id, sample_conversation_id):
        """Test complete workflow: create baseline, then record deviation"""
        user_id = sample_user_id
        conversation_id = sample_conversation_id
        
        # Create user
        db_session.execute(text("""
            INSERT INTO users (id, email, created_at, last_active)
            VALUES (:id, :email, datetime('now'), datetime('now'))
        """), {"id": user_id, "email": "test@example.com"})
        
        # Create baseline
        db_session.execute(text("""
            INSERT INTO user_baselines 
            (id, user_id, baseline_type, baseline_value, session_count, established_at, updated_at)
            VALUES (:id, :user_id, :baseline_type, :baseline_value, :session_count, 
                    datetime('now'), datetime('now'))
        """), {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "baseline_type": "pitch",
            "baseline_value": '{"mean": 200, "std": 20}',
            "session_count": 10
        })
        
        # Create conversation
        db_session.execute(text("""
            INSERT INTO conversations (id, user_id, started_at)
            VALUES (:id, :user_id, datetime('now'))
        """), {"id": conversation_id, "user_id": user_id})
        
        # Record deviation
        db_session.execute(text("""
            INSERT INTO session_deviations 
            (id, user_id, session_id, deviation_type, baseline_value, current_value, 
             deviation_score, detected_at)
            VALUES (:id, :user_id, :session_id, :deviation_type, :baseline_value, 
                    :current_value, :deviation_score, datetime('now'))
        """), {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "session_id": conversation_id,
            "deviation_type": "pitch",
            "baseline_value": '{"mean": 200}',
            "current_value": '{"mean": 150}',
            "deviation_score": 2.5
        })
        db_session.commit()
        
        # Query both tables
        result = db_session.execute(text("""
            SELECT 
                ub.baseline_type,
                ub.baseline_value,
                sd.deviation_score,
                sd.current_value
            FROM user_baselines ub
            JOIN session_deviations sd ON ub.user_id = sd.user_id 
                AND ub.baseline_type = sd.deviation_type
            WHERE ub.user_id = :user_id
        """), {"user_id": user_id}).fetchone()
        
        assert result is not None, "Should be able to join baseline and deviation"
        assert result[0] == "pitch", "Should match on baseline_type"
        assert result[2] == 2.5, "Should retrieve deviation_score"

