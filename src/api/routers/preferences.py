from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies.services import get_preferences_service
from ..middleware.auth import verify_token
from ..schemas.user import UserPreferencesUpdate
from ..services.preferences_service import PreferencesService

router = APIRouter()


@router.get("/")
async def get_preferences(
    preferences_service: PreferencesService = Depends(get_preferences_service),
    user_payload: Dict = Depends(verify_token),
):
    try:
        user_id = user_payload["sub"]
        preferences = await preferences_service.get_preferences(user_id)
        return preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    preferences_service: PreferencesService = Depends(get_preferences_service),
    user_payload: Dict = Depends(verify_token),
):
    try:
        user_id = user_payload["sub"]
        preferences_dict = {
            k: v for k, v in preferences.model_dump().items() if v is not None
        }
        updated_preferences = await preferences_service.update_preferences(
            user_id, preferences_dict
        )
        return updated_preferences
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
