import os
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "src" / "llms" / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "created_resumes"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    # JWT settings
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY", "your-default-secret-key"
    )  # Never use default in production
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 30

    # MongoDB settings
    mongodb_uri: Optional[str] = None
    mongodb_database: Optional[str] = None

    # API settings
    api_v1_prefix: str = "/api/v1"

    # LLM settings
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # LinkedIn settings
    linkedin_email: Optional[str] = None
    linkedin_password: Optional[str] = None

    # Path settings
    project_root: Path = PROJECT_ROOT
    prompts_dir: Path = PROMPTS_DIR
    output_dir: Path = OUTPUT_DIR

    # CORS Settings
    cors_origins: List[str] = [
        "http://localhost:3000",  # React development server
        "http://localhost:8001",  # FastAPI server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8001",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    @property
    def feature_flags(self) -> Dict[str, bool]:
        return {"check_clearance": True}

    @property
    def app_constants(self) -> Dict[str, List[str]]:
        return {
            "clearance_keywords": [
                "security clearance",
                "clearance required",
                "US citizen only",
                "US Citizen",
                "Permanent Resident",
                "U.S. Citizenship",
                "Government Security Clearance",
            ]
        }

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "use_enum_values": True,
        "extra": "ignore",  # Allow extra fields
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load environment variables after initialization
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", self.jwt_secret_key)
        self.mongodb_uri = os.getenv("MONGODB_URI")
        self.mongodb_database = os.getenv("MONGODB_DATABASE")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.linkedin_email = os.getenv("LINKEDIN_EMAIL")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# For backward compatibility
FEATURE_FLAGS = settings.feature_flags
APP_CONSTANTS = settings.app_constants
