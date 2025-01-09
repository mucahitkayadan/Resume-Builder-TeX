"""
Service dependencies for FastAPI endpoints.
"""

from typing import Generator, AsyncGenerator
from src.api.services.resume_service import ResumeService
from src.api.services.cover_letter_service import CoverLetterService
from src.api.services.portfolio_service import PortfolioService
from src.api.services.preferences_service import PreferencesService
from src.api.services.auth_service import AuthService
from src.core.database.factory import get_async_unit_of_work

async def get_auth_service() -> AsyncGenerator[AuthService, None]:
    """Get auth service instance."""
    service = AuthService()
    try:
        yield service
    finally:
        pass

async def get_resume_service() -> AsyncGenerator[ResumeService, None]:
    """Get resume service instance."""
    service = ResumeService()
    try:
        yield service
    finally:
        pass

async def get_cover_letter_service() -> AsyncGenerator[CoverLetterService, None]:
    """Get cover letter service instance."""
    service = CoverLetterService()
    try:
        yield service
    finally:
        pass

async def get_portfolio_service() -> AsyncGenerator[PortfolioService, None]:
    """Get portfolio service instance."""
    service = PortfolioService()
    try:
        yield service
    finally:
        pass

async def get_preferences_service() -> AsyncGenerator[PreferencesService, None]:
    """Get preferences service instance."""
    service = PreferencesService()
    try:
        yield service
    finally:
        pass

async def get_uow():
    """Get async unit of work instance."""
    async with get_async_unit_of_work() as uow:
        yield uow
