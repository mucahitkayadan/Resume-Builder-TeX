from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..schemas.analytics import (
    ApplicationMetrics,
    UserActivityMetrics,
    DateRangeParams
)
from ..services.analytics_service import AnalyticsService
from ..middleware.auth import auth0_middleware

router = APIRouter()

@router.get("/applications/metrics", response_model=ApplicationMetrics)
async def get_application_metrics(
    date_range: DateRangeParams = Depends(),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        metrics = await analytics_service.get_application_metrics(
            user_id,
            date_range.start_date,
            date_range.end_date
        )
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/activity", response_model=UserActivityMetrics)
async def get_user_activity(
    date_range: DateRangeParams = Depends(),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
    user_payload: Dict = Depends(auth0_middleware)
):
    try:
        user_id = user_payload["sub"]
        activity = await analytics_service.get_user_activity(
            user_id,
            date_range.start_date,
            date_range.end_date
        )
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 