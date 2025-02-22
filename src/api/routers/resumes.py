from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies.services import get_resume_service
from ..middleware.auth import verify_token
from ..schemas.resume import ResumeGenerationOptions, ResumeRequest, ResumeResponse
from ..services.resume_service import ResumeService

router = APIRouter()


@router.post("/generate", response_model=ResumeResponse)
async def generate_resume(
    request: ResumeRequest,
    options: Optional[ResumeGenerationOptions] = None,
    resume_service: ResumeService = Depends(get_resume_service),
    user_payload: Dict = Depends(verify_token),
):
    try:
        user_id = user_payload["sub"]
        resume = await resume_service.generate_resume(
            user_id=user_id,
            job_description=request.job_description,
            options=options.model_dump() if options else None,
        )
        return resume
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=List[ResumeResponse])
async def list_resumes(
    resume_service: ResumeService = Depends(get_resume_service),
    user_payload: Dict = Depends(verify_token),
):
    try:
        user_id = user_payload["sub"]
        resumes = await resume_service.list_resumes(user_id)
        return resumes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    resume_service: ResumeService = Depends(get_resume_service),
    user_payload: Dict = Depends(verify_token),
):
    try:
        user_id = user_payload["sub"]
        resume = await resume_service.get_resume(user_id, resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
            )
        return resume
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
