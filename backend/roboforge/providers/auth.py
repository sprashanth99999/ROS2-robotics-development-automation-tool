"""Auth helpers — resolve API key from keychain or env var."""

from __future__ import annotations

import os

from roboforge.keychain.service import secrets


def resolve_api_key(provider: str, env_var: str | None = None) -> str | None:
    """Try keychain first, then env var, then return None."""
    key = secrets.get_provider_key(provider)
    if key:
        return key
    if env_var:
        return os.environ.get(env_var)
    return os.environ.get(f"{provider.upper()}_API_KEY")
