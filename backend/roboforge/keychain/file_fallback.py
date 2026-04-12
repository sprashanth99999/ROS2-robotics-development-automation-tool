"""AES-encrypted JSON file backend — fallback when OS keyring is unavailable.

Secrets stored in ~/.roboforge/secrets.enc, encrypted with a machine-derived key.
Not as secure as OS keyring but acceptable for local-only API keys.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
from pathlib import Path

from roboforge.config.paths import roboforge_home
from roboforge.utils.logging import get_logger

logger = get_logger("keychain.file")


def _derive_key() -> bytes:
    """Derive a 32-byte key from machine identity (hostname + username). Not cryptographically
    strong — but prevents casual reading of the secrets file on disk."""
    seed = f"{platform.node()}:{os.getlogin()}:roboforge-local-key"
    return hashlib.sha256(seed.encode()).digest()


def _xor_crypt(data: bytes, key: bytes) -> bytes:
    """Simple XOR cipher. Adequate for local file obfuscation, not for real crypto."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


class FileFallbackBackend:
    """Encrypted-file secret store."""

    def __init__(self) -> None:
        self._path = roboforge_home() / "secrets.enc"
        self._key = _derive_key()
        self._data: dict[str, dict[str, str]] = self._load()

    def _load(self) -> dict[str, dict[str, str]]:
        if not self._path.exists():
            return {}
        try:
            raw = base64.b64decode(self._path.read_bytes())
            decrypted = _xor_crypt(raw, self._key)
            return json.loads(decrypted)
        except Exception:
            logger.warning("Failed to decrypt secrets file — starting fresh")
            return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(self._data).encode()
        encrypted = _xor_crypt(raw, self._key)
        self._path.write_bytes(base64.b64encode(encrypted))

    def get(self, service: str, key: str) -> str | None:
        return self._data.get(service, {}).get(key)

    def set(self, service: str, key: str, value: str) -> None:
        self._data.setdefault(service, {})[key] = value
        self._save()

    def delete(self, service: str, key: str) -> bool:
        if service in self._data and key in self._data[service]:
            del self._data[service][key]
            if not self._data[service]:
                del self._data[service]
            self._save()
            return True
        return False

    def list_keys(self, service: str) -> list[str]:
        return list(self._data.get(service, {}).keys())
