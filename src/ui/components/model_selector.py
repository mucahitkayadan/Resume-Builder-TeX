import streamlit as st

from config.logger_config import setup_logger
from src.core.database.factory import get_unit_of_work

logger = setup_logger(__name__)


class ModelSelector:
    def __init__(self):
        logger.debug("Initializing ModelSelector")
        self.model_types = ["OpenAI", "Claude", "Ollama", "Gemini"]
        self.model_options = {
            "OpenAI": [
                "gpt-4o",
                "gpt-4o-mini",
                "gpt-4o-2024-08-06",
                "o1-mini",
                "gpt-4o-2024-05-13",
            ],
            "Claude": [
                "claude-3-5-sonnet-latest",
                "claude-3-opus-latest",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
            ],
            "Ollama": [
                "llama3.1",
                "llama2",
                "llama2-uncensored",
                "mistral",
                "mixtral",
                "codellama",
                "neural-chat",
            ],
            "Gemini": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.5-pro-exp-0801"],
        }
        # Load saved preferences
        self._load_saved_preferences()

    def _load_saved_preferences(self):
        """Load saved preferences from database"""
        try:
            with get_unit_of_work() as uow:
                preferences = uow.users.get_preferences(st.session_state["user_id"])
                if preferences and preferences.get("llm_preferences"):
                    llm_prefs = preferences["llm_preferences"]
                    # Store preferences in session state
                    st.session_state["model_type"] = llm_prefs["model_type"]
                    st.session_state["model_name"] = llm_prefs["model_name"]
                    st.session_state["temperature"] = llm_prefs["temperature"]
        except Exception as e:
            logger.error(f"Error loading model preferences: {e}")

    def get_model_settings(self):
        """Get model settings, preferring saved preferences"""
        # Use saved preferences if available
        if "model_type" in st.session_state:
            model_type = st.session_state["model_type"]
            model_name = st.session_state["model_name"]
            temperature = st.session_state["temperature"]
        else:
            # Default values if no preferences saved
            model_type = "Claude"
            model_name = "claude-3-5-sonnet-20240620"
            temperature = 0.1

        return model_type, model_name, temperature
