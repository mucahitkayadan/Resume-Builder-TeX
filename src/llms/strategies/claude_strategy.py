import os
from anthropic import Anthropic
from .base import LLMStrategy
from config.llm_config import LLMConfig
from config.logger_config import setup_logger
from ..utils.errors import APIError, ConfigurationError
from ..utils.response import process_api_response

logger = setup_logger(__name__)

class ClaudeStrategy(LLMStrategy):
    def __init__(self, system_instruction: str):
        super().__init__(system_instruction)
        self._model = LLMConfig.CLAUDE_MODEL.name
        self._temperature = LLMConfig.CLAUDE_MODEL.default_temperature
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ConfigurationError(LLMConfig.MISSING_API_KEY_ERROR.format("Anthropic"))
        self.client = Anthropic(api_key=api_key)

    def generate_content(self, prompt: str, data: str, job_description: str) -> str:
        try:
            logger.info(f"Sending request to Claude API with model: {self.model}")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=LLMConfig.CLAUDE_MODEL.max_tokens,
                system=self.system_instruction,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": self._format_prompt(prompt, data, job_description)}
                ]
            )
            return process_api_response(response, "Claude")
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise APIError(f"Claude API error: {e}")

    def create_folder_name(self, prompt: str, job_description: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=LLMConfig.CLAUDE_MODEL.max_tokens,
                system=self.system_instruction,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": self._format_prompt(prompt, job_description=job_description)}
                ]
            )
            result = process_api_response(response, "Claude")
            return result if result else LLMConfig.UNKNOWN_FOLDER_NAME
        except Exception as e:
            logger.error(f"Error in create_folder_name: {e}")
            return LLMConfig.ERROR_FOLDER_NAME