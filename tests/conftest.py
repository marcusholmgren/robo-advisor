"""Test configuration and fixtures."""

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from tortoise import Tortoise

from app.main import app
from app.database import TORTOISE_ORM


@pytest.fixture(scope="function", autouse=True)
async def initialize_db():
    """
    Initialize the test database before each test.
    This fixture ensures that the application uses an in-memory SQLite
    database for all tests, providing isolation and speed.
    """
    # Create a copy of the production ORM config
    test_config = TORTOISE_ORM.copy()
    # Point the 'default' connection to an in-memory SQLite database
    test_config["connections"]["default"] = "sqlite://:memory:"

    await Tortoise.init(
        config=test_config,
    )
    # Generate the database schema in the in-memory database
    await Tortoise.generate_schemas()
    yield
    # Clean up the connection after the test
    await Tortoise.close_connections()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Async client for making requests to the app during tests."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
