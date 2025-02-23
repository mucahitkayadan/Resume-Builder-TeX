"""Authentication exceptions module."""

from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Base authentication error."""

    def __init__(self, detail: str):
        """Initialize the error.

        Args:
            detail: Error detail message
        """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid credentials error."""

    def __init__(self):
        """Initialize the error."""
        super().__init__("Could not validate credentials")


class InvalidTokenError(AuthenticationError):
    """Invalid token error."""

    def __init__(self):
        """Initialize the error."""
        super().__init__("Invalid authentication token")


class TokenExpiredError(AuthenticationError):
    """Token expired error."""

    def __init__(self):
        """Initialize the error."""
        super().__init__("Token has expired")


class UserNotFoundError(HTTPException):
    """User not found error."""

    def __init__(self):
        """Initialize the error."""
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


class EmailAlreadyRegisteredError(HTTPException):
    """Email already registered error."""

    def __init__(self):
        """Initialize the error."""
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
