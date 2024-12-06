import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
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
    app = FastAPI(
        title="Resume Builder API",
        description="API for building and managing resumes",
        version="1.0.0"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
    app.include_router(
        resumes_router,
        prefix=f"{settings.API_V1_PREFIX}/resumes",
        tags=["resumes"],
        dependencies=[Depends(verify_token)]
    )
    app.include_router(
        cover_letters_router,
        prefix=f"{settings.API_V1_PREFIX}/cover-letters",
        tags=["cover-letters"],
        dependencies=[Depends(verify_token)]
    )
    app.include_router(
        preferences_router,
        prefix=f"{settings.API_V1_PREFIX}/preferences",
        tags=["preferences"],
        dependencies=[Depends(verify_token)]
    )
    app.include_router(
        portfolio_router,
        prefix=f"{settings.API_V1_PREFIX}/portfolio",
        tags=["portfolio"],
        dependencies=[Depends(verify_token)]
    )

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app 