"""Unit tests for the authentication router.

This module contains tests for the authentication endpoints.
"""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from fastapi import FastAPI, status
from httpx import AsyncClient

from src.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def async_client(app: FastAPI) -> AsyncClient:
    """Create an async test client.

    Args:
        app: The FastAPI application instance

    Returns:
        AsyncClient: The async test client
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


async def test_register_user_success(
    app: FastAPI, async_client: AsyncClient, mock_auth_service: Mock
):
    """Test successful user registration.

    Args:
        app: The FastAPI test application
        async_client: The async HTTP client
        mock_auth_service: Mock auth service
    """
    # Arrange
    register_data = {
        "email": "test@example.com",
        "password": "StrongPass123!",
        "full_name": "Test User",
    }
    mock_auth_service.register_user.return_value = UserResponse(
        user_id="user123",
        email="test@example.com",
        full_name="Test User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Act
    response = await async_client.post("/auth/register", json=register_data)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == register_data["email"]
    assert response.json()["full_name"] == register_data["full_name"]
    mock_auth_service.register_user.assert_called_once_with(
        email=register_data["email"],
        password=register_data["password"],
        full_name=register_data["full_name"],
    )


async def test_login_user_success(
    app: FastAPI, async_client: AsyncClient, mock_auth_service: Mock
):
    """Test successful user login.

    Args:
        app: The FastAPI test application
        async_client: The async HTTP client
        mock_auth_service: Mock auth service
    """
    # Arrange
    login_data = {"email": "test@example.com", "password": "StrongPass123!"}
    mock_auth_service.login_user.return_value = TokenResponse(
        access_token="test.jwt.token", token_type="bearer"
    )

    # Act
    response = await async_client.post("/auth/login", json=login_data)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    mock_auth_service.login_user.assert_called_once_with(
        email=login_data["email"], password=login_data["password"]
    )


async def test_get_current_user_success(
    app: FastAPI,
    async_client: AsyncClient,
    mock_auth_service: Mock,
    test_user_token: str,
):
    """Test getting current user information.

    Args:
        app: The FastAPI test application
        async_client: The async HTTP client
        mock_auth_service: Mock auth service
        test_user_token: Test JWT token
    """
    # Arrange
    mock_auth_service.get_current_user.return_value = UserResponse(
        user_id="user123",
        email="test@example.com",
        full_name="Test User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    headers = {"Authorization": f"Bearer {test_user_token}"}

    # Act
    response = await async_client.get("/auth/me", headers=headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@example.com"
    assert response.json()["full_name"] == "Test User"
    mock_auth_service.get_current_user.assert_called_once()


async def test_register_user_invalid_data(
    app: FastAPI, async_client: AsyncClient, mock_auth_service: Mock
):
    """Test user registration with invalid data.

    Args:
        app: The FastAPI test application
        async_client: The async HTTP client
        mock_auth_service: Mock auth service
    """
    # Arrange
    invalid_data = {
        "email": "invalid-email",
        "password": "weak",
    }

    # Act
    response = await async_client.post("/auth/register", json=invalid_data)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "validation error" in response.json()["detail"].lower()
    mock_auth_service.register_user.assert_not_called()


async def test_login_user_invalid_credentials(
    app: FastAPI, async_client: AsyncClient, mock_auth_service: Mock
):
    """Test user login with invalid credentials.

    Args:
        app: The FastAPI test application
        async_client: The async HTTP client
        mock_auth_service: Mock auth service
    """
    # Arrange
    login_data = {"email": "test@example.com", "password": "WrongPass123!"}
    mock_auth_service.login_user.side_effect = ValueError("Invalid credentials")

    # Act
    response = await async_client.post("/auth/login", json=login_data)

    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "invalid credentials" in response.json()["detail"].lower()
    mock_auth_service.login_user.assert_called_once_with(
        email=login_data["email"], password=login_data["password"]
    )
