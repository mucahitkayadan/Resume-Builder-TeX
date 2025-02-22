from typing import Dict, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from ..dependencies.services import get_portfolio_service
from ..middleware.auth import verify_token
from ..schemas.portfolio import (
    Award,
    CareerSummary,
    Education,
    PersonalInformation,
    PortfolioResponse,
    Project,
    Publication,
    WorkExperience,
)
from ..services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("/", response_model=PortfolioResponse)
async def get_portfolio(
    user_payload: Dict = Depends(verify_token),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    try:
        user_id = user_payload["sub"]
        portfolio = await portfolio_service.get_portfolio(user_id)
        if not portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
            )
        return portfolio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
