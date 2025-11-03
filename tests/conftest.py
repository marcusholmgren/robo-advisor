"""Test configuration and fixtures."""

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise

from app.main import app


@pytest.fixture(scope="function", autouse=True)
async def initialize_db():
    """Initialize test database before each test."""
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["app.models"]})
    await Tortoise.generate_schemas()
    yield
    await Tortoise.close_connections()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async client for testing."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
