import os

from dotenv import load_dotenv

from .logger_config import setup_logger

load_dotenv()

# LinkedIn credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "user_information")

# LLM API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Ollama Configuration
OLLAMA_URI = "http://localhost:11434"

# This configuration is used in the Streamlit app, since there is no sign-up and sign-in logics are implemented in the Streamlit UI
# Note that these logics are implemented in the back-end service.
test_user_id = "mujakayadan"

__all__ = [
    "LINKEDIN_EMAIL",
    "LINKEDIN_PASSWORD",
    "MONGODB_URI",
    "MONGODB_DATABASE",
    "ANTHROPIC_API_KEY",
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "OLLAMA_URI",
    "test_user_id",
    "setup_logger",
]
