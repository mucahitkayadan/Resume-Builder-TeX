"""Authentication router module."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.schemas.auth import Token
from src.api.schemas.user import User, UserCreate
from src.core.database.factory import get_unit_of_work
from src.core.exceptions.auth_exceptions import InvalidCredentialsError
from src.core.security.auth import get_current_active_user

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), uow=Depends(get_unit_of_work)
):
    """Login endpoint.

    Args:
        form_data: Form data containing email and password
        uow: Unit of work instance

    Returns:
        Token: Access token

    Raises:
        HTTPException: If authentication fails
    """
    try:
        with uow as unit_of_work:
            user = unit_of_work.users.get_by_email(
                form_data.username
            )  # OAuth2 form uses username field
            if not user:
                raise InvalidCredentialsError("Incorrect email or password")

            # Verify password and create token here
            # ... (implementation details)

            return Token(access_token="your_token_here", token_type="bearer")
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("/me", response_model=User)
def get_current_user(current_user: User = Depends(get_current_active_user)):
    """Get current user endpoint.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current user information
    """
    return current_user


@router.post("/register", response_model=User)
def register(user_data: UserCreate, uow=Depends(get_unit_of_work)):
    """Register new user endpoint.

    Args:
        user_data: User creation data
        uow: Unit of work instance

    Returns:
        User: Created user

    Raises:
        HTTPException: If registration fails
    """
    try:
        with uow as unit_of_work:
            if unit_of_work.users.get_by_email(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            return unit_of_work.users.add(user_data)
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
