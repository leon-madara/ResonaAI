"""
Celery application for Sync Service background jobs.

Purpose:
- Provides a Celery entrypoint for docker-compose workers/beat:
  `celery -A app.celery worker --loglevel=info`
"""

import os
from celery import Celery


def _get_env(name: str, default: str) -> str:
    """Get environment variable with default."""
    return os.getenv(name, default)


# Celery broker/backend default to Redis (as defined in docker-compose.yml)
celery = Celery(
    "sync_service",
    broker=_get_env("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=_get_env("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

# Minimal config — can be extended later for retries, queues, etc.
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery.task(name="sync_service.noop")
def noop() -> str:
    """No-op task used for smoke testing Celery wiring."""
    return "ok"


