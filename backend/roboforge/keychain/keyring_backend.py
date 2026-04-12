"""OS keychain backend using the `keyring` library (macOS Keychain, Windows Credential Locker, etc.)."""

from __future__ import annotations

from roboforge.utils.logging import get_logger

logger = get_logger("keychain.keyring")

SERVICE_PREFIX = "roboforge"


def _svc(service: str) -> str:
    return f"{SERVICE_PREFIX}.{service}"


class KeyringBackend:
    """Wraps python-keyring. Falls back gracefully if keyring unavailable."""

    def __init__(self) -> None:
        try:
            import keyring as _kr  # noqa: F811
            self._kr = _kr
            logger.info("OS keyring available: %s", _kr.get_keyring().name)
        except ImportError:
            self._kr = None
            logger.warning("python-keyring not installed — keyring backend disabled")

    @property
    def available(self) -> bool:
        return self._kr is not None

    def get(self, service: str, key: str) -> str | None:
        if not self._kr:
            return None
        return self._kr.get_password(_svc(service), key)

    def set(self, service: str, key: str, value: str) -> None:
        if not self._kr:
            raise RuntimeError("keyring not available")
        self._kr.set_password(_svc(service), key, value)

    def delete(self, service: str, key: str) -> bool:
        if not self._kr:
            return False
        try:
            self._kr.delete_password(_svc(service), key)
            return True
        except Exception:
            return False

    def list_keys(self, service: str) -> list[str]:
        # keyring doesn't support listing — tracked in file_fallback instead
        return []
