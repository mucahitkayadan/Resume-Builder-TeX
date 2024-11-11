import logging
from typing import Any, Dict
from .strategies.base import LLMStrategy

logger = logging.getLogger(__name__)

class LLMRunner:
    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: LLMStrategy):
        self.strategy = strategy

    def generate_content(self, prompt: str, data: str, job_description: str) -> str:
        return self.strategy.generate_content(prompt, data, job_description)

    def create_folder_name(self, naming_prompt: str, job_description: str) -> str:
        return self.strategy.create_folder_name(naming_prompt, job_description)

    def get_config(self) -> Dict[str, Any]:
        return {
            'type': self.strategy.__class__.__name__,
            'model': self.strategy.model,
            'temperature': self.strategy.temperature
        }