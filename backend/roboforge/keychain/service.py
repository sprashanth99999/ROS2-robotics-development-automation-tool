"""SecretStore facade — auto-selects OS keyring or file fallback.

Usage:
    from roboforge.keychain.service import secrets
    secrets.set_provider_key("claude", "sk-ant-...")
    key = secrets.get_provider_key("claude")
"""

from __future__ import annotations

from roboforge.keychain.file_fallback import FileFallbackBackend
from roboforge.keychain.keyring_backend import KeyringBackend
from roboforge.utils.logging import get_logger

logger = get_logger("keychain")

PROVIDER_SERVICE = "ai_providers"


class SecretStore:
    """Unified secret storage — prefers OS keyring, falls back to encrypted file."""

    def __init__(self) -> None:
        self._keyring = KeyringBackend()
        self._file = FileFallbackBackend()
        self._backend = self._keyring if self._keyring.available else self._file
        logger.info("Secret store using: %s", type(self._backend).__name__)

    def get_provider_key(self, provider: str) -> str | None:
        return self._backend.get(PROVIDER_SERVICE, provider)

    def set_provider_key(self, provider: str, api_key: str) -> None:
        self._backend.set(PROVIDER_SERVICE, provider, api_key)

    def delete_provider_key(self, provider: str) -> bool:
        return self._backend.delete(PROVIDER_SERVICE, provider)

    def list_providers_with_keys(self) -> list[str]:
        return self._backend.list_keys(PROVIDER_SERVICE)

    def get(self, service: str, key: str) -> str | None:
        return self._backend.get(service, key)

    def set(self, service: str, key: str, value: str) -> None:
        self._backend.set(service, key, value)


# Module-level singleton
secrets = SecretStore()
