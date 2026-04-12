"""Shared test fixtures for the roboforge backend test suite."""

import pytest
from httpx import ASGITransport, AsyncClient

from roboforge.main import create_app


@pytest.fixture
def app():
    """Create a fresh FastAPI app instance per test."""
    return create_app()


@pytest.fixture
async def client(app):
    """Async HTTP test client — no real server needed."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
