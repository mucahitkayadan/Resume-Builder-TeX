from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
OUTPUT_DIR = PROJECT_ROOT / "created_resumes"

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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
        "Permanent Resident",
        "U.S. Citizenship",
        "Government Security Clearance"
    ]
}
