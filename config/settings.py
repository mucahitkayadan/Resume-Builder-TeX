from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List, Dict
from functools import lru_cache
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "created_resumes"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_default_algorithms() -> List[str]:
    return ["RS256"]

def get_default_cors_origins() -> List[str]:
    return [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

def get_default_feature_flags() -> Dict[str, bool]:
    return {
        'check_clearance': True
    }

def get_default_app_constants() -> Dict[str, List[str]]:
    return {
        'clearance_keywords': [
            "security clearance",
            "clearance required",
            "US citizen only",
            "US Citizen",
            "Permanent Resident",
            "U.S. Citizenship",
            "Government Security Clearance"
        ]
    }

class Settings(BaseSettings):
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
    
    # CORS settings
    CORS_ORIGINS: List[str] = Field(default_factory=get_default_cors_origins)
    
    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE")
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"

    # LLM settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    # LinkedIn settings
    LINKEDIN_EMAIL: str = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD: str = os.getenv("LINKEDIN_PASSWORD")

    # Application settings
    FEATURE_FLAGS: Dict[str, bool] = Field(default_factory=get_default_feature_flags)
    APP_CONSTANTS: Dict[str, List[str]] = Field(default_factory=get_default_app_constants)
    
    # Path settings
    PROJECT_ROOT: Path = PROJECT_ROOT
    PROMPTS_DIR: Path = PROMPTS_DIR
    OUTPUT_DIR: Path = OUTPUT_DIR
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

# For backward compatibility
FEATURE_FLAGS = settings.FEATURE_FLAGS
APP_CONSTANTS = settings.APP_CONSTANTS
