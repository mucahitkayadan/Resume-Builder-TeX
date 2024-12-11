from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Optional, List
from ..schemas.cover_letter import (
    CoverLetterRequest,
    CoverLetterResponse,
    CoverLetterGenerationOptions
)
from ..dependencies.services import get_cover_letter_service
from ..services.cover_letter_service import CoverLetterService
from ..middleware.auth import verify_token

router = APIRouter()

@router.post("/generate", response_model=CoverLetterResponse)
async def generate_cover_letter(
    request: CoverLetterRequest,
    options: Optional[CoverLetterGenerationOptions] = None,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    user_payload: Dict = Depends(verify_token)
):
    try:
        user_id = user_payload["sub"]
        cover_letter = await cover_letter_service.generate_cover_letter(
            user_id=user_id,
            job_description=request.job_description,
            company_name=request.company_name,
            job_title=request.job_title,
            resume_id=request.resume_id,
            options=options.dict() if options else None
        )
        return cover_letter
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{cover_letter_id}", response_model=CoverLetterResponse)
async def get_cover_letter(
    cover_letter_id: str,
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    user_payload: Dict = Depends(verify_token)
):
    try:
        user_id = user_payload["sub"]
        cover_letter = await cover_letter_service.get_cover_letter(user_id, cover_letter_id)
        if not cover_letter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cover letter not found"
            )
        return cover_letter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[CoverLetterResponse])
async def list_cover_letters(
    cover_letter_service: CoverLetterService = Depends(get_cover_letter_service),
    user_payload: Dict = Depends(verify_token)
):
    try:
        user_id = user_payload["sub"]
        cover_letters = await cover_letter_service.list_cover_letters(user_id)
        return cover_letters
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 