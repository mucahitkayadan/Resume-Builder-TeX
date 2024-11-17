import os
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Logging Configuration
LOGGING_CONFIG = {
    'enabled': True,
    'level': logging.DEBUG,
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# Feature Configuration
FEATURE_FLAGS = {
    'check_clearance': True
}

# Application Constants
APP_CONSTANTS = {
    'clearance_keywords': [
        "security clearance",
        "clearance required",
        "US citizen only",
        "US Citizen",
        "Permanent Resident"
    ],
    'default_location': "San Francisco, CA",
    'max_projects': 4,
    'min_skill_categories': 5,
    'min_skills_per_category': 6,
    'max_skills_per_category': 10
}

# API Credentials
CREDENTIALS = {
    'linkedin_email': os.getenv("LINKEDIN_EMAIL"),
    'linkedin_password': os.getenv("LINKEDIN_PASSWORD"),
    'ollama_uri': "http://localhost:11434"
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_FOLDER = PROJECT_ROOT / "prompts"
OUTPUT_FOLDER = PROJECT_ROOT / "created_resumes"
# Create output directory if it doesn't exist
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
