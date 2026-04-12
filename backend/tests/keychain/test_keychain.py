"""Tests for the keychain module — file fallback backend + SecretStore facade."""

import os
import pytest
from pathlib import Path


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    """Point .roboforge to a temp dir so tests don't touch real secrets."""
    monkeypatch.setenv("ROBOFORGE_HOME", str(tmp_path / ".roboforge"))


class TestFileFallbackBackend:
    def test_set_get_roundtrip(self):
        from roboforge.keychain.file_fallback import FileFallbackBackend
        fb = FileFallbackBackend()
        fb.set("svc", "key1", "secret123")
        assert fb.get("svc", "key1") == "secret123"

    def test_get_missing_returns_none(self):
        from roboforge.keychain.file_fallback import FileFallbackBackend
        fb = FileFallbackBackend()
        assert fb.get("svc", "nope") is None

    def test_delete(self):
        from roboforge.keychain.file_fallback import FileFallbackBackend
        fb = FileFallbackBackend()
        fb.set("svc", "k", "v")
        assert fb.delete("svc", "k") is True
        assert fb.get("svc", "k") is None
        assert fb.delete("svc", "k") is False

    def test_list_keys(self):
        from roboforge.keychain.file_fallback import FileFallbackBackend
        fb = FileFallbackBackend()
        fb.set("ai", "claude", "key1")
        fb.set("ai", "gemini", "key2")
        assert sorted(fb.list_keys("ai")) == ["claude", "gemini"]

    def test_persistence_across_instances(self):
        from roboforge.keychain.file_fallback import FileFallbackBackend
        fb1 = FileFallbackBackend()
        fb1.set("svc", "persist", "yes")
        fb2 = FileFallbackBackend()
        assert fb2.get("svc", "persist") == "yes"


class TestSecretStore:
    def test_provider_key_roundtrip(self):
        from roboforge.keychain.service import SecretStore
        store = SecretStore()
        store.set_provider_key("claude", "sk-ant-test")
        assert store.get_provider_key("claude") == "sk-ant-test"

    def test_delete_provider_key(self):
        from roboforge.keychain.service import SecretStore
        store = SecretStore()
        store.set_provider_key("openai", "sk-test")
        assert store.delete_provider_key("openai") is True
        assert store.get_provider_key("openai") is None
