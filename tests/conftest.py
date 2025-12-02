"""Pytest configuration and fixtures."""

import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.database import init_database, get_database, close_database
from app.database import BookRepository, ChangeLogRepository
from app.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_database():
    """Create a test database connection."""
    # Use a test database
    test_db_name = f"{settings.mongodb_db_name}_test"
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[test_db_name]
    
    # Clean up test database
    await client.drop_database(test_db_name)
    
    yield database
    
    # Cleanup
    await client.drop_database(test_db_name)
    client.close()


@pytest.fixture
async def book_repo(test_database):
    """Create a book repository for testing."""
    return BookRepository(test_database)


@pytest.fixture
async def change_log_repo(test_database):
    """Create a change log repository for testing."""
    return ChangeLogRepository(test_database)







