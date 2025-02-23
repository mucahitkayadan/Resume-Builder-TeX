"""Unit tests for the authentication service.

This module contains tests for the authentication service functionality.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from src.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.api.services.auth_service import AuthService
from src.core.database.repositories.user_repository import (
    MongoUserRepository as UserRepository,
)
from src.core.database.unit_of_work import MongoUnitOfWork
from src.core.security import create_access_token, get_password_hash, verify_password

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_user_repository() -> Mock:
    """Create mock user repository.

    Returns:
        Mock: Mock user repository
    """
    return Mock(spec=UserRepository)


@pytest.fixture
def auth_service(mock_user_repository: Mock) -> AuthService:
    """Create auth service with mock repository.

    Args:
        mock_user_repository: Mock user repository

    Returns:
        AuthService: Auth service instance
    """
    return AuthService(user_repository=mock_user_repository)


async def test_register_user_success(
    auth_service: AuthService, mock_user_repository: Mock
):
    """Test successful user registration.

    Args:
        auth_service: Auth service instance
        mock_user_repository: Mock user repository
    """
    # Arrange
    email = "test@example.com"
    password = "StrongPass123!"
    full_name = "Test User"
    hashed_password = get_password_hash(password)

    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.create.return_value = UserResponse(
        user_id="user123",
        email=email,
        full_name=full_name,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Act
    result = await auth_service.register_user(
        email=email, password=password, full_name=full_name
    )

    # Assert
    assert result.email == email
    assert result.full_name == full_name
    mock_user_repository.get_by_email.assert_called_once_with(email)
    mock_user_repository.create.assert_called_once()


async def test_register_user_existing_email(
    auth_service: AuthService, mock_user_repository: Mock
):
    """Test user registration with existing email.

    Args:
        auth_service: Auth service instance
        mock_user_repository: Mock user repository
    """
    # Arrange
    email = "existing@example.com"
    password = "StrongPass123!"
    full_name = "Test User"

    mock_user_repository.get_by_email.return_value = UserResponse(
        user_id="existing_user",
        email=email,
        full_name="Existing User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Email already registered"):
        await auth_service.register_user(
            email=email, password=password, full_name=full_name
        )
    mock_user_repository.get_by_email.assert_called_once_with(email)
    mock_user_repository.create.assert_not_called()


async def test_login_user_success(
    auth_service: AuthService, mock_user_repository: Mock
):
    """Test successful user login.

    Args:
        auth_service: Auth service instance
        mock_user_repository: Mock user repository
    """
    # Arrange
    email = "test@example.com"
    password = "StrongPass123!"
    hashed_password = get_password_hash(password)

    mock_user_repository.get_by_email.return_value = UserResponse(
        user_id="user123",
        email=email,
        full_name="Test User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        hashed_password=hashed_password,
    )

    # Act
    result = await auth_service.login_user(email=email, password=password)

    # Assert
    assert result.access_token
    assert result.token_type == "bearer"
    mock_user_repository.get_by_email.assert_called_once_with(email)


async def test_login_user_invalid_credentials(
    auth_service: AuthService, mock_user_repository: Mock
):
    """Test user login with invalid credentials.

    Args:
        auth_service: Auth service instance
        mock_user_repository: Mock user repository
    """
    # Arrange
    email = "test@example.com"
    password = "WrongPass123!"

    mock_user_repository.get_by_email.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid credentials"):
        await auth_service.login_user(email=email, password=password)
    mock_user_repository.get_by_email.assert_called_once_with(email)


async def test_get_current_user_success(
    auth_service: AuthService, mock_user_repository: Mock
):
    """Test getting current user information.

    Args:
        auth_service: Auth service instance
        mock_user_repository: Mock user repository
    """
    # Arrange
    user_id = "user123"
    mock_user_repository.get_by_id.return_value = UserResponse(
        user_id=user_id,
        email="test@example.com",
        full_name="Test User",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    # Act
    result = await auth_service.get_current_user(user_id)

    # Assert
    assert result.user_id == user_id
    assert result.email == "test@example.com"
    mock_user_repository.get_by_id.assert_called_once_with(user_id)


async def test_get_current_user_not_found(
    auth_service: AuthService, mock_user_repository: Mock
):
    """Test getting non-existent user information.

    Args:
        auth_service: Auth service instance
        mock_user_repository: Mock user repository
    """
    # Arrange
    user_id = "nonexistent_id"
    mock_user_repository.get_by_id.return_value = None

    # Act & Assert
    with pytest.raises(ValueError, match="User not found"):
        await auth_service.get_current_user(user_id)
    mock_user_repository.get_by_id.assert_called_once_with(user_id)
