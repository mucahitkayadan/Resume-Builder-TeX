from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Optional, List
from ..schemas.application import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
    ApplicationStatus
)
from ..services.application_service import ApplicationService
from ..middleware.auth import auth0_middleware

router = APIRouter()

@router.post("/", response_model=JobApplicationResponse)
async def create_application(
    application: JobApplicationCreate,
    application_service: ApplicationService = Depends(get_application_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        created = await application_service.create_application(user_id, application)
        return created
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[JobApplicationResponse])
async def list_applications(
    status: Optional[ApplicationStatus] = None,
    application_service: ApplicationService = Depends(get_application_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        applications = await application_service.list_applications(user_id, status)
        return applications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{application_id}", response_model=JobApplicationResponse)
async def get_application(
    application_id: str,
    application_service: ApplicationService = Depends(get_application_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        application = await application_service.get_application(user_id, application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        return application
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.patch("/{application_id}", response_model=JobApplicationResponse)
async def update_application(
    application_id: str,
    update: JobApplicationUpdate,
    application_service: ApplicationService = Depends(get_application_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        updated = await application_service.update_application(
            user_id, application_id, update
        )
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    application_service: ApplicationService = Depends(get_application_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        await application_service.delete_application(user_id, application_id)
        return {"message": "Application deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 