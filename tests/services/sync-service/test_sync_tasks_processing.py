"""Unit tests for sync-service background processing.

These tests focus on the worker logic (persistence, idempotency, partial failures,
conflict resolution, and retry bookkeeping) without requiring a running Celery worker.
"""

import os
import sys
import uuid
import importlib.util

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def db_engine():
    """SQLite engine with the minimal schema needed for worker processing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT
            )
        """))
        conn.execute(text("""
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                emotion_summary TEXT,
                crisis_detected BOOLEAN DEFAULT 0,
                escalated_to_human BOOLEAN DEFAULT 0
            )
        """))
        conn.execute(text("""
            CREATE TABLE messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                message_type TEXT NOT NULL,
                encrypted_content BLOB NOT NULL,
                emotion_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE sync_queue (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                encrypted_data BLOB,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed_at TIMESTAMP,
                retry_count INTEGER DEFAULT 0
            )
        """))
        conn.execute(text("""
            CREATE TABLE emotion_history (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                conversation_id TEXT,
                message_id TEXT,
                emotion_type TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                voice_emotion TEXT,
                text_sentiment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE user_baselines (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                baseline_type TEXT NOT NULL,
                baseline_value TEXT NOT NULL,
                session_count INTEGER DEFAULT 0,
                established_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.execute(text("""
            CREATE TABLE user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        conn.commit()

    return engine


@pytest.fixture()
def db_session(db_engine):
    """DB session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def sync_tasks_module(db_engine, monkeypatch):
    """Import sync_tasks with DB engine patched to our SQLite engine."""
    # Ensure the service directory is importable
    service_dir = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..",
            "apps", "backend", "services", "sync-service",
        )
    )
    if service_dir not in sys.path:
        sys.path.insert(0, service_dir)

    # Force the module to bind to our in-memory engine
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    # Provide a lightweight Celery shim so `workers.celery_app` can import.
    class _FakeConf:
        def update(self, *args, **kwargs):
            return None

    class _FakeCeleryApp:
        def __init__(self, *args, **kwargs):
            self.conf = _FakeConf()

        def task(self, *dargs, **dkwargs):
            def _decorator(fn):
                return fn
            return _decorator

    class _FakeCeleryModule:
        Celery = _FakeCeleryApp

    monkeypatch.setitem(sys.modules, "celery", _FakeCeleryModule())

    import sqlalchemy
    monkeypatch.setattr(sqlalchemy, "create_engine", lambda *args, **kwargs: db_engine)

    spec = importlib.util.spec_from_file_location(
        "sync_tasks",
        os.path.join(service_dir, "workers", "sync_tasks.py"),
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_conversation_sync_persists_messages_idempotent_and_partial_failures(db_session, sync_tasks_module):
    user_id = str(uuid.uuid4())
    sync_id = str(uuid.uuid4())

    db_session.execute(text("INSERT INTO users (id, email) VALUES (:id, :email)"), {"id": user_id, "email": "t@example.com"})
    db_session.execute(
        text("INSERT INTO sync_queue (id, user_id, operation_type, encrypted_data, status, retry_count) VALUES (:id, :user_id, :op, :data, 'pending', 0)"),
        {"id": sync_id, "user_id": user_id, "op": "conversation_sync", "data": b"{}"},
    )
    db_session.commit()

    payload = {
        "conversation_id": "conv-local-1",
        "messages": [
            {"id": "msg-local-1", "content": "Hello", "timestamp": "2025-12-12T10:00:00Z"},
            {"id": "msg-local-2", "timestamp": "2025-12-12T10:01:00Z"},  # missing content (partial failure)
        ],
    }

    result, should_retry = sync_tasks_module._handle_sync_operation(db_session, sync_id, user_id, "conversation_sync", payload)
    db_session.commit()

    assert should_retry is False
    assert result["success"] is True
    assert result["messages_inserted"] == 1
    assert result["messages_failed"] == 1

    # DB consistency: one message inserted.
    count = db_session.execute(text("SELECT COUNT(*) FROM messages")).scalar()
    assert int(count) == 1

    # Idempotency: reprocessing should not duplicate messages.
    sync_id_2 = str(uuid.uuid4())
    db_session.execute(
        text("INSERT INTO sync_queue (id, user_id, operation_type, encrypted_data, status, retry_count) VALUES (:id, :user_id, :op, :data, 'pending', 0)"),
        {"id": sync_id_2, "user_id": user_id, "op": "conversation_sync", "data": b"{}"},
    )
    db_session.commit()

    result2, should_retry2 = sync_tasks_module._handle_sync_operation(db_session, sync_id_2, user_id, "conversation_sync", payload)
    db_session.commit()

    assert should_retry2 is False
    assert result2["success"] is True
    count2 = db_session.execute(text("SELECT COUNT(*) FROM messages")).scalar()
    assert int(count2) == 1


def test_retry_bookkeeping_sets_pending_and_increments_retry_count(db_session, sync_tasks_module):
    user_id = str(uuid.uuid4())
    sync_id = str(uuid.uuid4())

    db_session.execute(text("INSERT INTO users (id, email) VALUES (:id, :email)"), {"id": user_id, "email": "t@example.com"})
    db_session.execute(
        text("INSERT INTO sync_queue (id, user_id, operation_type, encrypted_data, status, retry_count) VALUES (:id, :user_id, :op, :data, 'pending', 0)"),
        {"id": sync_id, "user_id": user_id, "op": "unknown", "data": b"{}"},
    )
    db_session.commit()

    result, should_retry = sync_tasks_module._handle_sync_operation(db_session, sync_id, user_id, "unknown", {})
    db_session.commit()

    assert result["success"] is False
    assert should_retry is True

    row = db_session.execute(text("SELECT status, retry_count FROM sync_queue WHERE id = :id"), {"id": sync_id}).fetchone()
    assert row.status == "pending"
    assert int(row.retry_count) == 1


def test_baseline_update_last_write_wins(db_session, sync_tasks_module):
    user_id = str(uuid.uuid4())
    sync_id = str(uuid.uuid4())

    db_session.execute(text("INSERT INTO users (id, email) VALUES (:id, :email)"), {"id": user_id, "email": "t@example.com"})

    # Seed an existing baseline updated later.
    db_session.execute(
        text(
            "INSERT INTO user_baselines (id, user_id, baseline_type, baseline_value, session_count, established_at, updated_at) "
            "VALUES (:id, :user_id, :t, :v, :c, CURRENT_TIMESTAMP, :updated_at)"
        ),
        {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "t": "voice",
            "v": "{\"pitch_mean\": 150.0, \"updated_at\": \"2025-12-12T12:00:00+00:00\"}",
            "c": 10,
            "updated_at": "2025-12-12T12:00:00+00:00",
        },
    )
    db_session.execute(
        text("INSERT INTO sync_queue (id, user_id, operation_type, encrypted_data, status, retry_count) VALUES (:id, :user_id, :op, :data, 'pending', 0)"),
        {"id": sync_id, "user_id": user_id, "op": "baseline_update", "data": b"{}"},
    )
    db_session.commit()

    payload = {
        "baseline_data": {"baseline_type": "voice", "pitch_mean": 999.0, "updated_at": "2025-12-12T11:00:00Z"},
        "strategy": "last_write_wins",
    }

    result, should_retry = sync_tasks_module._handle_sync_operation(db_session, sync_id, user_id, "baseline_update", payload)
    db_session.commit()

    assert should_retry is False
    assert result["success"] is True

    row = db_session.execute(
        text("SELECT baseline_value FROM user_baselines WHERE user_id = :user_id AND baseline_type = :t"),
        {"user_id": user_id, "t": "voice"},
    ).fetchone()

    # The newer remote baseline should remain (pitch_mean stays 150.0).
    assert "150.0" in str(row.baseline_value)


def test_preferences_sync_last_write_wins(db_session, sync_tasks_module):
    user_id = str(uuid.uuid4())
    sync_id = str(uuid.uuid4())

    db_session.execute(text("INSERT INTO users (id, email) VALUES (:id, :email)"), {"id": user_id, "email": "t@example.com"})

    # Seed existing preferences updated later.
    db_session.execute(
        text("INSERT INTO user_preferences (user_id, preferences, created_at, updated_at) VALUES (:user_id, :prefs, CURRENT_TIMESTAMP, :updated_at)"),
        {
            "user_id": user_id,
            "prefs": "{\"theme\": \"light\", \"updated_at\": \"2025-12-12T12:00:00+00:00\"}",
            "updated_at": "2025-12-12T12:00:00+00:00",
        },
    )
    db_session.execute(
        text("INSERT INTO sync_queue (id, user_id, operation_type, encrypted_data, status, retry_count) VALUES (:id, :user_id, :op, :data, 'pending', 0)"),
        {"id": sync_id, "user_id": user_id, "op": "user_preference_sync", "data": b"{}"},
    )
    db_session.commit()

    payload = {
        "preferences": {"theme": "dark"},
        "updated_at": "2025-12-12T11:00:00Z",
        "strategy": "last_write_wins",
    }

    result, should_retry = sync_tasks_module._handle_sync_operation(db_session, sync_id, user_id, "user_preference_sync", payload)
    db_session.commit()

    assert should_retry is False
    assert result["success"] is True

    row = db_session.execute(text("SELECT preferences FROM user_preferences WHERE user_id = :user_id"), {"user_id": user_id}).fetchone()
    assert "light" in str(row.preferences)
