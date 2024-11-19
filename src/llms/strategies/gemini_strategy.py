import os
import google.generativeai as genai
from .base import LLMStrategy
from config.llm_config import LLMConfig
from config.logger_config import setup_logger
from ..utils.errors import APIError, ConfigurationError
from ..utils.response import process_api_response

logger = setup_logger(__name__)

class GeminiStrategy(LLMStrategy):
    def __init__(self, system_instruction: str):
        super().__init__(system_instruction)
        self._model = LLMConfig.GEMINI_MODEL.name
        self._temperature = LLMConfig.GEMINI_MODEL.default_temperature
        
        api_key = LLMConfig.get_provider_config("Gemini")
        if not api_key:
            raise ConfigurationError(LLMConfig.MISSING_API_KEY_ERROR.format("Gemini"))
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=self.model,
            generation_config={
                "temperature": self.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )

    def generate_content(self, prompt: str, data: str, job_description: str) -> str:
        try:
            logger.info(f"Sending request to Gemini API with model: {self.model}")
            response = self.model.generate_content(
                self._format_prompt(prompt, data, job_description)
            )
            return process_api_response(response, "Gemini")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise APIError(f"Gemini API error: {e}")

    def create_folder_name(self, prompt: str, job_description: str) -> str:
        try:
            response = self.model.generate_content(
                self._format_prompt(prompt, job_description=job_description)
            )
            result = process_api_response(response, "Gemini")
            return result.strip().replace('"', '').replace("'", "")
        except Exception as e:
            logger.error(f"Error in create_folder_name: {e}")
            return "error_company_name|error_job_title" 