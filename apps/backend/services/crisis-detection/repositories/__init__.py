"""
Crisis Detection Service repositories package.

Purpose:
- Provide a stable, service-local `repositories.*` import target in tests and service code.
- Avoid cross-service module collisions (gateway also defines a top-level `repositories` package).
"""

