from openai import OpenAI
import os
from .base import LLMStrategy
from config.llm_config import LLMConfig
from config.logger_config import setup_logger
from ..utils.errors import APIError, ConfigurationError
from ..utils.response import process_api_response
from typing import Tuple
from src.generator.utils.string_utils import sanitize_filename

logger = setup_logger(__name__)

class OpenAIStrategy(LLMStrategy):
    def __init__(self, system_instruction: str):
        super().__init__(system_instruction)
        self._model = LLMConfig.OPENAI_MODEL.name
        self._temperature = LLMConfig.OPENAI_MODEL.default_temperature
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ConfigurationError(LLMConfig.MISSING_API_KEY_ERROR.format("OpenAI"))
        self.client = OpenAI(api_key=api_key)

    def generate_content(self, prompt: str, data: str, job_description: str) -> str:
        try:
            logger.info(f"Sending request to OpenAI API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": self._format_prompt(prompt, data, job_description)}
                ],
                temperature=self.temperature,
                max_tokens=LLMConfig.OPENAI_MODEL.max_tokens,
                **LLMConfig.OPENAI_MODEL.default_options
            )
            return process_api_response(response, "OpenAI")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise APIError(f"OpenAI API error: {e}")

    def create_folder_name(self, prompt: str, job_description: str)  -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": self._format_prompt(prompt, job_description=job_description)}
                ],
                temperature=self.temperature,
                max_tokens=LLMConfig.OPENAI_MODEL.max_tokens,
                **LLMConfig.OPENAI_MODEL.default_options
            )
            result = process_api_response(response, "OpenAI")
            return result

        except Exception as e:
            logger.error(f"Error in create_folder_name: {e}")
            return "error_company_name|error_job_title"