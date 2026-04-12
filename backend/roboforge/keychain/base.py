"""Abstract keychain backend protocol."""

from __future__ import annotations

from typing import Protocol


class KeychainBackend(Protocol):
    """Store and retrieve secrets. Implementations: OS keyring or encrypted file."""

    def get(self, service: str, key: str) -> str | None: ...
    def set(self, service: str, key: str, value: str) -> None: ...
    def delete(self, service: str, key: str) -> bool: ...
    def list_keys(self, service: str) -> list[str]: ...
