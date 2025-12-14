"""
Database integration tests for Cultural Context Service
"""

import pytest
import sys
import os
from datetime import datetime, timezone, timedelta
import importlib.util
import types

# Add service directory to path
service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'apps', 'backend', 'services', 'cultural-context'))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import after path setup (avoid cross-service module cache collisions)
models_spec = importlib.util.spec_from_file_location(
    "cultural_context_models",
    os.path.join(service_dir, "models", "database_models.py"),
)
models_module = importlib.util.module_from_spec(models_spec)
assert models_spec.loader is not None
models_spec.loader.exec_module(models_module)
Base = models_module.Base
CulturalContextCache = models_module.CulturalContextCache

models_pkg = types.ModuleType("models")
models_pkg.database_models = models_module
sys.modules["models"] = models_pkg
sys.modules["models.database_models"] = models_module

repo_spec = importlib.util.spec_from_file_location(
    "cultural_context_repo",
    os.path.join(service_dir, "repositories", "cultural_repository.py"),
)
repo_module = importlib.util.module_from_spec(repo_spec)
assert repo_spec.loader is not None
repo_spec.loader.exec_module(repo_module)
CulturalRepository = repo_module.CulturalRepository


@pytest.fixture
def test_db():
    """Create test database session"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


class TestCulturalRepository:
    """Test CulturalRepository database operations"""
    
    def test_cache_context(self, test_db):
        """Test caching cultural context"""
        repo = CulturalRepository(test_db)
        
        context_data = {
            "context": "test context",
            "language": "en",
            "query": "test query"
        }
        
        cache_entry = repo.cache_context(
            context_key="en:test",
            context_data=context_data,
            language="en",
            region="east_africa"
        )
        
        assert cache_entry.id is not None
        assert cache_entry.context_key == "en:test"
        assert cache_entry.context_data == context_data
        assert cache_entry.language == "en"
    
    def test_get_cached_context(self, test_db):
        """Test retrieving cached context"""
        repo = CulturalRepository(test_db)
        
        # Cache context
        context_data = {"context": "test"}
        repo.cache_context(
            context_key="en:test",
            context_data=context_data,
            language="en"
        )
        
        # Retrieve it
        cached = repo.get_cached_context("en:test")
        
        assert cached is not None
        assert cached.context_data == context_data
    
    def test_get_cached_context_expired(self, test_db):
        """Test that expired cache entries are not returned"""
        repo = CulturalRepository(test_db)
        
        # Cache with short expiration
        context_data = {"context": "test"}
        cache_entry = repo.cache_context(
            context_key="en:test",
            context_data=context_data,
            language="en",
            expires_in_hours=0  # Expires immediately (in past)
        )
        
        # Manually set expires_at to past
        cache_entry.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        test_db.commit()
        
        # Try to retrieve (should return None and delete expired entry)
        cached = repo.get_cached_context("en:test")
        
        assert cached is None
    
    def test_delete_context(self, test_db):
        """Test deleting cached context"""
        repo = CulturalRepository(test_db)
        
        # Cache context
        repo.cache_context(
            context_key="en:test",
            context_data={"context": "test"},
            language="en"
        )
        
        # Delete it
        result = repo.delete_context("en:test")
        
        assert result is True
        cached = repo.get_cached_context("en:test")
        assert cached is None
    
    def test_get_by_language(self, test_db):
        """Test retrieving cached contexts by language"""
        repo = CulturalRepository(test_db)
        
        # Cache contexts in different languages
        repo.cache_context(
            context_key="en:test1",
            context_data={"context": "english"},
            language="en"
        )
        repo.cache_context(
            context_key="sw:test2",
            context_data={"context": "swahili"},
            language="sw"
        )
        
        # Get English contexts
        english_contexts = repo.get_by_language("en")
        
        assert len(english_contexts) == 1
        assert english_contexts[0].language == "en"

