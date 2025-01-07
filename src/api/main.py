"""
Main application module for the Resume Builder API.
This module initializes the FastAPI application and configures routes, middleware and settings.
"""

import os
import sys
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.api.routers import (
    auth_router,
    resumes_router,
    cover_letters_router,
    portfolio_router,
    preferences_router
)
from src.api.middleware.auth import verify_token
from config.settings import settings


def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title="Resume Builder API",
        description="API for building and managing resumes",
        version="1.0.0"
    )

    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with their prefixes and dependencies
    app.include_router(auth_router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"])
    app.include_router(
        resumes_router,
        prefix=f"{settings.api_v1_prefix}/resumes",
        tags=["resumes"],
        dependencies=[Depends(verify_token)]
    )
    app.include_router(
        cover_letters_router,
        prefix=f"{settings.api_v1_prefix}/cover-letters",
        tags=["cover-letters"],
        dependencies=[Depends(verify_token)]
    )
    app.include_router(
        preferences_router,
        prefix=f"{settings.api_v1_prefix}/preferences",
        tags=["preferences"],
        dependencies=[Depends(verify_token)]
    )
    app.include_router(
        portfolio_router,
        prefix=f"{settings.api_v1_prefix}/portfolio",
        tags=["portfolio"],
        dependencies=[Depends(verify_token)]
    )

    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        """
        Health check endpoint to verify API status.
        
        Returns:
            Dict[str, str]: Status response indicating API health
        """
        return {"status": "healthy"}

    return app