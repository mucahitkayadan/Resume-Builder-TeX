from typing import Any, Dict, Optional

from config.logger_config import setup_logger

from .errors import ResponseError

logger = setup_logger(__name__)


def process_api_response(response: Any, provider: str) -> str:
    """Process API responses consistently across different providers."""
    try:
        if hasattr(response, "choices"):  # OpenAI
            return response.choices[0].message.content if response.choices else ""
        elif hasattr(response, "content"):  # Claude
            return response.content[0].text if response.content else ""
        elif isinstance(response, Dict):  # Ollama
            return response.get("response", "")
        elif provider == "Gemini":  # Add Gemini support
            return response.text if response else ""
        else:
            logger.warning(f"Unknown response format from {provider}")
            return ""
    except Exception as e:
        logger.error(f"Error processing {provider} response: {e}")
        raise ResponseError(f"Failed to process {provider} response: {e}")
