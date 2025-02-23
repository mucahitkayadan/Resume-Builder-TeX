"""Test fixtures and configuration for pytest.

This module contains shared fixtures and configuration for all tests.
"""

import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

from config.settings import Settings, get_settings
from src.api.main import create_app
from src.api.services.auth_service import AuthService
from src.core.database.connections import AsyncMongoConnection, MongoConnection
from src.core.database.repositories.portfolio_repository import (
    MongoPortfolioRepository as PortfolioRepository,
)
from src.core.database.repositories.resume_repository import (
    MongoResumeRepository as ResumeRepository,
)
from src.core.database.repositories.user_repository import (
    MongoUserRepository as UserRepository,
)
from src.core.database.unit_of_work import AsyncMongoUnitOfWork, MongoUnitOfWork


@pytest.fixture
def settings() -> Settings:
    """Create test settings.

    Returns:
        Settings: Test settings
    """
    test_settings = Settings(
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="test_db",
        jwt_secret_key="test_secret",
        jwt_algorithm="HS256",
        jwt_expires_minutes=30,
    )
    return test_settings


@pytest.fixture
def app(settings: Settings) -> FastAPI:
    """Create a FastAPI test application.

    Args:
        settings: Test settings

    Returns:
        FastAPI: The test application instance
    """
    app = create_app()
    return app


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing.

    Args:
        app: The FastAPI application instance

    Yields:
        AsyncClient: An async HTTP client for making test requests
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_mongo_connection() -> MongoConnection:
    """Create a mock MongoDB connection.

    Returns:
        MongoConnection: Mock MongoDB connection
    """
    connection = MongoConnection(uri="mongodb://test", database="test_db")
    connection._client = AsyncMongoMockClient()
    connection._db = connection._client["test_db"]
    connection._is_mock = True
    return connection


@pytest.fixture
async def mock_uow(mock_mongo_connection) -> AsyncGenerator[MongoUnitOfWork, None]:
    """Create a mock MongoDB unit of work.

    Args:
        mock_mongo_connection: Mock MongoDB connection

    Yields:
        MongoUnitOfWork: Mock MongoDB unit of work
    """
    async with AsyncMongoUnitOfWork(mock_mongo_connection) as uow:
        yield uow


@pytest.fixture
def mock_auth_service() -> MagicMock:
    """Create a mock authentication service.

    Returns:
        MagicMock: A mock auth service instance
    """
    return MagicMock()


@pytest.fixture
def mock_resume_service() -> MagicMock:
    """Create a mock resume service.

    Returns:
        MagicMock: A mock resume service instance
    """
    return MagicMock()


@pytest.fixture
def mock_cover_letter_service() -> MagicMock:
    """Create a mock cover letter service.

    Returns:
        MagicMock: A mock cover letter service instance
    """
    return MagicMock()


@pytest.fixture
def mock_portfolio_service() -> MagicMock:
    """Create a mock portfolio service.

    Returns:
        MagicMock: A mock portfolio service instance
    """
    return MagicMock()


@pytest.fixture
def mock_preferences_service() -> MagicMock:
    """Create a mock preferences service.

    Returns:
        MagicMock: A mock preferences service instance
    """
    return MagicMock()


@pytest.fixture
def test_user_token() -> str:
    """Create a test JWT token.

    Returns:
        str: A test JWT token
    """
    return "test.jwt.token"


@pytest.fixture
def mongo_connection(settings: Settings) -> MongoConnection:
    """Create test MongoDB connection.

    Args:
        settings: Test settings

    Returns:
        MongoConnection: Test MongoDB connection
    """
    return MongoConnection(uri=settings.mongodb_uri, database=settings.mongodb_database)


@pytest.fixture
def portfolio_repository(mongo_connection: MongoConnection) -> PortfolioRepository:
    """Create test portfolio repository.

    Args:
        mongo_connection: Test MongoDB connection

    Returns:
        PortfolioRepository: Test portfolio repository
    """
    return PortfolioRepository(mongo_connection)


@pytest.fixture
def resume_repository(mongo_connection: MongoConnection) -> ResumeRepository:
    """Create test resume repository.

    Args:
        mongo_connection: Test MongoDB connection

    Returns:
        ResumeRepository: Test resume repository
    """
    return ResumeRepository(mongo_connection)


@pytest.fixture
def user_repository(mongo_connection: MongoConnection) -> UserRepository:
    """Create test user repository.

    Args:
        mongo_connection: Test MongoDB connection

    Returns:
        UserRepository: Test user repository
    """
    return UserRepository(mongo_connection)


@pytest.fixture
def test_data() -> dict:
    """Create test data.

    Returns:
        dict: Test data
    """
    return {
        "prompt": "Write a test prompt",
        "data": '{"name": "John Doe", "skills": ["Python", "Testing"]}',
        "job_description": "Looking for a Python developer with testing experience",
    }


@pytest.fixture
def system_instruction() -> str:
    """Create test system instruction.

    Returns:
        str: Test system instruction
    """
    return "You are a helpful assistant."
