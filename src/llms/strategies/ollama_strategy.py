import os
import requests
from .base import LLMStrategy
from config.llm_config import LLMConfig
from ..utils.logger import setup_logger
from ..utils.errors import APIError, ConfigurationError
from ..utils.response import process_api_response

logger = setup_logger(__name__)

class OllamaStrategy(LLMStrategy):
    def __init__(self, system_instruction: str):
        super().__init__(system_instruction)
        self._model = LLMConfig.OLLAMA_MODEL.name
        self._temperature = LLMConfig.OLLAMA_MODEL.default_temperature
        self.base_url = os.getenv("OLLAMA_URI", LLMConfig.OLLAMA_DEFAULT_URI)

    def generate_content(self, prompt: str, data: str, job_description: str) -> str:
        try:
            logger.info(f"Sending request to Ollama API with model: {self.model}")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "system": self.system_instruction,
                    "prompt": self._format_prompt(prompt, data, job_description),
                    "temperature": self.temperature,
                    **LLMConfig.OLLAMA_MODEL.default_options
                }
            )
            response.raise_for_status()
            return process_api_response(response.json(), "Ollama")
        except requests.RequestException as e:
            logger.error(f"Ollama API request error: {e}")
            raise APIError(f"Ollama API request error: {e}")
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise APIError(f"Ollama API error: {e}")

    def create_folder_name(self, prompt: str, job_description: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "system": self.system_instruction,
                    "prompt": self._format_prompt(prompt, job_description=job_description),
                    "temperature": self.temperature,
                    **LLMConfig.OLLAMA_MODEL.default_options
                }
            )
            response.raise_for_status()
            result = process_api_response(response.json(), "Ollama")
            return result if result else LLMConfig.UNKNOWN_FOLDER_NAME
        except Exception as e:
            logger.error(f"Error in create_folder_name: {e}")
            return LLMConfig.ERROR_FOLDER_NAME