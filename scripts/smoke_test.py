"""
docker-compose smoke test runner (API Gateway).

Purpose:
- Provide a quick, repeatable set of HTTP calls to validate the stack.

Usage:
  python ResonaAI/scripts/smoke_test.py

Notes:
- Requires the stack running locally (default http://localhost:8000).
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, Optional

import httpx


def _print(title: str, payload: Any) -> None:
    print(f"\n== {title} ==")
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, indent=2))
    else:
        print(payload)


def _fail(msg: str) -> None:
    raise SystemExit(msg)


def main() -> int:
    base_url = os.getenv("SMOKE_BASE_URL", "http://localhost:8000").rstrip("/")
    email = os.getenv("SMOKE_EMAIL", "smoke_test@example.com")
    password = os.getenv("SMOKE_PASSWORD", "password123")

    with httpx.Client(timeout=15.0) as client:
        # 1) Health
        r = client.get(f"{base_url}/health")
        _print("GET /health", {"status_code": r.status_code, "body": r.json()})
        if r.status_code != 200:
            _fail("Health check failed")

        # 2) Register (may fail if already registered)
        register_payload = {
            "email": email,
            "password": password,
            "consent_version": "1.0",
            "is_anonymous": True,
        }
        r = client.post(f"{base_url}/auth/register", json=register_payload)
        try:
            body = r.json()
        except Exception:
            body = r.text
        _print("POST /auth/register", {"status_code": r.status_code, "body": body})

        # 3) Login
        r = client.post(f"{base_url}/auth/login", json={"email": email, "password": password})
        login_body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text}
        _print("POST /auth/login", {"status_code": r.status_code, "body": login_body})
        if r.status_code != 200:
            _fail("Login failed")

        token = login_body.get("access_token")
        if not token:
            _fail("No access_token returned from login")

        headers = {"Authorization": f"Bearer {token}"}

        # 4) Cultural context
        r = client.get(f"{base_url}/cultural/context", params={"query": "I feel tired", "language": "en"}, headers=headers)
        _print("GET /cultural/context", {"status_code": r.status_code, "body": r.json()})
        if r.status_code != 200:
            _fail("Cultural context request failed")

        # 5) Sync upload (uses dummy UUID; validates routing + response shape)
        sync_payload = {"user_id": "00000000-0000-0000-0000-000000000000", "operation_type": "smoke_test", "data": {"hello": "world"}}
        r = client.post(f"{base_url}/sync/upload", json=sync_payload, headers=headers)
        _print("POST /sync/upload", {"status_code": r.status_code, "body": r.json()})
        if r.status_code != 200:
            _fail("Sync upload failed")

    print("\nSmoke test: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


