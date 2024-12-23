from typing import Generator
from src.api.services.resume_service import ResumeService
from src.api.services.cover_letter_service import CoverLetterService
from src.api.services.portfolio_service import PortfolioService
from src.api.services.preferences_service import PreferencesService
from src.api.services.application_service import ApplicationService
from src.api.services.auth_service import AuthService

def get_auth_service() -> Generator[AuthService, None, None]:
    service = AuthService()
    try:
        yield service
    finally:
        pass

def get_resume_service() -> Generator[ResumeService, None, None]:
    service = ResumeService()
    try:
        yield service
    finally:
        pass

def get_cover_letter_service() -> Generator[CoverLetterService, None, None]:
    service = CoverLetterService()
    try:
        yield service
    finally:
        pass

def get_portfolio_service() -> Generator[PortfolioService, None, None]:
    service = PortfolioService()
    try:
        yield service
    finally:
        pass

def get_preferences_service() -> Generator[PreferencesService, None, None]:
    service = PreferencesService()
    try:
        yield service
    finally:
        pass

def get_application_service() -> Generator[ApplicationService, None, None]:
    service = ApplicationService()
    try:
        yield service
    finally:
        pass 