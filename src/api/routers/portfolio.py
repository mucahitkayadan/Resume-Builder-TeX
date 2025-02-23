"""Portfolio router module."""

from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from ..dependencies.services import get_portfolio_service
from ..middleware.auth import verify_token
from ..schemas.portfolio import PortfolioCreate, PortfolioResponse, PortfolioUpdate
from ..services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("/", response_model=List[PortfolioResponse])
async def get_portfolios(
    user_payload: Dict = Depends(verify_token),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """Get all portfolios for the current user.

    Args:
        user_payload: User payload from token
        portfolio_service: Portfolio service instance

    Returns:
        List[PortfolioResponse]: List of portfolios

    Raises:
        HTTPException: If an error occurs
    """
    try:
        user_id = user_payload["sub"]
        portfolios = await portfolio_service.get_portfolios(user_id)
        return portfolios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: str,
    user_payload: Dict = Depends(verify_token),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """Get a portfolio by ID.

    Args:
        portfolio_id: Portfolio ID
        user_payload: User payload from token
        portfolio_service: Portfolio service instance

    Returns:
        PortfolioResponse: Portfolio data

    Raises:
        HTTPException: If portfolio not found or an error occurs
    """
    try:
        user_id = user_payload["sub"]
        portfolio = await portfolio_service.get_portfolio(portfolio_id, user_id)
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


@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio: PortfolioCreate,
    user_payload: Dict = Depends(verify_token),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """Create a new portfolio.

    Args:
        portfolio: Portfolio data
        user_payload: User payload from token
        portfolio_service: Portfolio service instance

    Returns:
        PortfolioResponse: Created portfolio

    Raises:
        HTTPException: If an error occurs
    """
    try:
        user_id = user_payload["sub"]
        return await portfolio_service.create_portfolio(portfolio, user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str,
    portfolio: PortfolioUpdate,
    user_payload: Dict = Depends(verify_token),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """Update a portfolio.

    Args:
        portfolio_id: Portfolio ID
        portfolio: Portfolio update data
        user_payload: User payload from token
        portfolio_service: Portfolio service instance

    Returns:
        PortfolioResponse: Updated portfolio

    Raises:
        HTTPException: If portfolio not found or an error occurs
    """
    try:
        user_id = user_payload["sub"]
        updated_portfolio = await portfolio_service.update_portfolio(
            portfolio_id, portfolio, user_id
        )
        if not updated_portfolio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
            )
        return updated_portfolio
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_portfolio(
    portfolio_id: str,
    user_payload: Dict = Depends(verify_token),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    """Delete a portfolio.

    Args:
        portfolio_id: Portfolio ID
        user_payload: User payload from token
        portfolio_service: Portfolio service instance

    Raises:
        HTTPException: If portfolio not found or an error occurs
    """
    try:
        user_id = user_payload["sub"]
        deleted = await portfolio_service.delete_portfolio(portfolio_id, user_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Portfolio not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
