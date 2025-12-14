"""Encryption client for conversation-engine.

Purpose:
- Ensure message content is encrypted at rest by delegating to the encryption-service.

Design notes:
- Uses encryption-service `/encrypt` and `/decrypt` endpoints (service-managed key).
- Stores raw ciphertext bytes (decoded from the service's base64) in the DB.
- Decryption re-encodes bytes back to base64 to match the encryption-service contract.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Optional

import httpx


@dataclass(frozen=True)
class EncryptionResult:
    """Result of an encryption operation."""

    ciphertext: bytes
    key_id: str


class EncryptionClient:
    """HTTP client for encryption-service."""

    def __init__(self, base_url: str, http_client: httpx.AsyncClient):
        self._base_url = base_url.rstrip("/")
        self._http = http_client

    async def encrypt_text(self, *, plaintext: str, key_id: Optional[str] = None) -> EncryptionResult:
        """Encrypt text and return ciphertext bytes."""
        payload = {"data": plaintext, "key_id": key_id}
        resp = await self._http.post(f"{self._base_url}/encrypt", json=payload)
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success"):
            raise RuntimeError("Encryption service returned success=false")
        result = body.get("result") or {}
        encrypted_b64 = result.get("encrypted_data")
        if not encrypted_b64:
            raise RuntimeError("Encryption service returned empty encrypted_data")

        ciphertext = base64.b64decode(encrypted_b64.encode("utf-8"))
        return EncryptionResult(ciphertext=ciphertext, key_id=result.get("key_id") or (key_id or "default"))

    async def decrypt_text(self, *, ciphertext: bytes, key_id: Optional[str] = None) -> str:
        """Decrypt ciphertext bytes and return plaintext."""
        encrypted_b64 = base64.b64encode(ciphertext).decode("utf-8")
        payload = {"encrypted_data": encrypted_b64, "key_id": key_id}
        resp = await self._http.post(f"{self._base_url}/decrypt", json=payload)
        resp.raise_for_status()
        body = resp.json()
        if not body.get("success"):
            raise RuntimeError("Decryption service returned success=false")
        data = body.get("data")
        if data is None:
            raise RuntimeError("Decryption service returned empty data")
        return str(data)
