from fastapi import APIRouter, HTTPException, status, Depends
from ..schemas.user import UserCreate, UserResponse, UserLogin, UserUpdate
from ..services.auth_service import AuthService
from ..middleware.auth import verify_token
from ..dependencies.services import get_auth_service
from typing import Dict
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=UserResponse)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.create_user(user_data)
        return user
    except Exception as e:
        logger.error(f"Signup failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login")
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        token = await auth_service.login_user(credentials)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_payload: Dict = Depends(verify_token),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        user = await auth_service.get_user_by_id(user_payload["sub"])
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.put("/profile/{user_id}", response_model=UserResponse)
async def update_profile(
    user_id: str,
    profile_data: UserUpdate,
    user_payload: Dict = Depends(verify_token),
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        # Verify the user is updating their own profile
        if user_payload["sub"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this profile"
            )
        
        updated_user = await auth_service.update_user(user_id, profile_data)
        return updated_user
    except Exception as e:
        logger.error(f"Profile update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 