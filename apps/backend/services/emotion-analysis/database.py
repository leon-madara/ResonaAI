"""
Database connection and session management for Emotion Analysis Service
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import logging
from sqlalchemy.pool import StaticPool

from config import settings

logger = logging.getLogger(__name__)

_engine = None
_SessionLocal = None


def get_engine():
    """Get (or create) SQLAlchemy engine with test-friendly defaults."""
    global _engine
    if _engine is not None:
        return _engine

    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        _engine = create_engine(
            url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        _engine = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_sessionmaker():
    """Get (or create) sessionmaker bound to the engine."""
    global _SessionLocal
    if _SessionLocal is not None:
        return _SessionLocal
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """
    Get database session dependency for FastAPI
    
    Usage:
        @app.get("/endpoint")
        async def endpoint(db: Session = Depends(get_db)):
            ...
    """
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database sessions (for use outside FastAPI dependencies)
    
    Usage:
        with get_db_context() as db:
            # use db session
    """
    SessionLocal = get_sessionmaker()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables (if needed)"""
    from models.database_models import Base
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables initialized")

