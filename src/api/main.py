"""
Main application module for the Resume Builder API.
This module initializes the FastAPI application and configures routes, middleware and settings.
"""

import os
import sys
from pathlib import Path
from typing import Dict

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from config.settings import settings
from src.api.middleware.auth import verify_token
from src.api.routers import (
    auth_router,
    cover_letters_router,
    portfolio_router,
    preferences_router,
    resumes_router,
)


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Resume Builder API",
        description="API for building and managing resumes",
        version="1.0.0",
    )

    # Configure CORS middleware with more explicit settings
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
        ],
        expose_headers=["*"],
        max_age=600,
    )

    # Include all routers with prefix
    app.include_router(
        auth_router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"]
    )
    app.include_router(
        resumes_router,
        prefix=f"{settings.api_v1_prefix}/resumes",
        tags=["resumes"],
        dependencies=[Depends(verify_token)],
    )
    app.include_router(
        cover_letters_router,
        prefix=f"{settings.api_v1_prefix}/cover-letters",
        tags=["cover-letters"],
        dependencies=[Depends(verify_token)],
    )
    app.include_router(
        preferences_router,
        prefix=f"{settings.api_v1_prefix}/preferences",
        tags=["preferences"],
        dependencies=[Depends(verify_token)],
    )
    app.include_router(
        portfolio_router,
        prefix=f"{settings.api_v1_prefix}/portfolio",
        tags=["portfolio"],
        dependencies=[Depends(verify_token)],
    )

    @app.get("/")
    async def root():
        return {"message": "Resume Builder API"}

    return app
