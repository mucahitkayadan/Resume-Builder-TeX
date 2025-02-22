import logging
from abc import ABC, abstractmethod
from typing import Tuple

logger = logging.getLogger(__name__)


class LLMStrategy(ABC):
    def __init__(self, system_instruction: str):
        self._model: str = ""
        self._temperature: float = 0.1
        self.system_instruction = system_instruction

    @property
    def model(self) -> str:
        return self._model

    @model.setter
    def model(self, value: str):
        if not value:
            raise ValueError("Model name cannot be empty")
        self._model = value

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float):
        if 0.0 <= value <= 1.0:
            self._temperature = value
        else:
            raise ValueError("Temperature must be between 0.0 and 1.0")

    def _format_prompt(
        self, prompt: str, data: str = None, job_description: str = None
    ) -> str:
        formatted_prompt = f"{prompt}\n\n"
        if data:
            formatted_prompt += (
                f"Here is the personal information in JSON format:\n"
                f"<data> \n{data}\n </data>\n\n"
            )
        if job_description:
            formatted_prompt += (
                f"Job Description:\n"
                f"<job_description> \n{job_description}\n </job_description>\n\n"
            )
        return formatted_prompt

    @abstractmethod
    def generate_content(self, prompt: str, data: str, job_description: str) -> str:
        pass

    @abstractmethod
    def create_folder_name(self, prompt: str, job_description: str) -> str:
        pass
