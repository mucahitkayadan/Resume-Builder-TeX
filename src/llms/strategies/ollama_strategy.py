import json
import os

import requests

from config.llm_config import LLMConfig
from config.logger_config import setup_logger

from ..utils.errors import APIError, ConfigurationError
from ..utils.response import process_api_response
from .base import LLMStrategy

logger = setup_logger(__name__)


class OllamaStrategy(LLMStrategy):
    def __init__(self, system_instruction: str):
        super().__init__(system_instruction)
        self._model = LLMConfig.OLLAMA_MODEL.name
        self._temperature = LLMConfig.OLLAMA_MODEL.default_temperature
        self.base_url = LLMConfig.get_provider_config("Ollama")

    def _process_ollama_response(self, response: requests.Response) -> str:
        """Process streaming response from Ollama API."""
        if not response.ok:
            raise APIError(
                f"Ollama API request failed with status {response.status_code}"
            )

        try:
            # Get the last response from streaming output
            content = ""
            for line in response.iter_lines():
                if line:
                    content = json.loads(line.decode("utf-8"))["response"]
            return content.strip()
        except json.JSONDecodeError as e:
            raise APIError(f"Failed to parse Ollama API response: {e}")

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
                    "stream": True,
                    **LLMConfig.OLLAMA_MODEL.default_options,
                },
                stream=True,
            )
            return self._process_ollama_response(response)
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
                    "system": "Create a concise folder name using underscores for this job application.",
                    "prompt": self._format_prompt(
                        prompt, job_description=job_description
                    ),
                    "temperature": self.temperature,
                    "stream": True,
                    **LLMConfig.OLLAMA_MODEL.default_options,
                },
                stream=True,
            )
            result = self._process_ollama_response(response)
            # Clean up the folder name
            folder_name = result.strip().replace('"', "").replace("'", "")
            return folder_name

        except Exception as e:
            logger.error(f"Error in create_folder_name: {e}")
            return "error_company_name|error_job_title"
