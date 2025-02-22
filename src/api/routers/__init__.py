from .auth import router as auth_router
from .cover_letters import router as cover_letters_router
from .portfolio import router as portfolio_router
from .preferences import router as preferences_router
from .resumes import router as resumes_router

__all__ = [
    "auth_router",
    "resumes_router",
    "cover_letters_router",
    "portfolio_router",
    "preferences_router",
]
