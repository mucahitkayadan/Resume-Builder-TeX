import logging
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Feature flags
CHECK_CLEARANCE = True

# Clearance keywords
CLEARANCE_KEYWORDS = [
    "security clearance",
    "clearance required",
    "US citizen only",
    "US Citizen",
    "Permanent Resident"
]

# Default location
DEFAULT_LOCATION = "San Francisco, CA"

# Maximum number of projects to include
MAX_PROJECTS = 4

# Number of skill categories to list
MIN_SKILL_CATEGORIES = 5

# Number of skills per category
MIN_SKILLS_PER_CATEGORY = 6
MAX_SKILLS_PER_CATEGORY = 10

# Logging configuration
LOGGING_ENABLED = True
LOG_LEVEL = logging.DEBUG  # Can be DEBUG, INFO, WARNING, ERROR, CRITICAL

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Database path
DATABASE_PATH = "__legacy__/db/resumes.db"

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "user_information")
MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "portfolio")


# Ollama Configuration
OLLAMA_URI = "http://localhost:11434"

