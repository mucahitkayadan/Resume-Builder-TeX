from abc import ABC, abstractmethod
from openai import OpenAI
from openai.types.chat import ChatCompletion
from openai import OpenAIError
from anthropic import Anthropic
import os
import logging

logger = logging.getLogger(__name__)

class AIStrategy(ABC):
    @abstractmethod
    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        pass

    @abstractmethod
    def create_folder_name(self, prompt: str, job_description: str) -> str:
        pass

class OpenAIStrategy(AIStrategy):
    def __init__(self, model: str, temperature: float, system_prompt: str):
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        try:
            logger.info(f"Sending request to OpenAI API with model: {self.model}")
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"{prompt}\n\n"
                                                f"Here is the personal information in JSON format:\n"
                                                f"<data> \n{data}\n </data>\n\n"
                                                f"And here is the job description:\n"
                                                f"<job_description> \n{job_description}\n </job_description>\n\n"
                    }
                ],
                temperature=self.temperature,
                presence_penalty=0,
                frequency_penalty=0.3,
                max_tokens=1000
            )
            logger.info("Received response from OpenAI API")
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                logger.warning("Received empty content from OpenAI API")
                return ""
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error processing section: {e}")
            return f"Unexpected error: {str(e)}"

    def create_folder_name(self, prompt: str, job_description: str) -> str:
        try:
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"{prompt}\n\n"
                                                f"Job Description:\n"
                                                f"<job_description> \n{job_description}\n </job_description>\n\n"
                    }
                ],
                temperature=self.temperature,
                max_tokens=100
            )
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                logger.warning("Received empty content from OpenAI API for folder name")
                return "Unknown_Company|Unknown_Position"
        except Exception as e:
            logger.error(f"Error in create_folder_name: {str(e)}")
            return "Error_Company|Error_Position"

class ClaudeStrategy(AIStrategy):
    def __init__(self, model: str, temperature: float, system_prompt: str):
        self.model = model
        self.temperature = temperature
        self.system_prompt = system_prompt
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        try:
            logger.info(f"Sending request to Claude API with model: {self.model}")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n"
                                                f"Here is the personal information in JSON format:\n"
                                                f"<data> \n{data}\n </data>\n\n"
                                                f"And here is the job description:\n"
                                                f"<job_description> \n{job_description}\n </job_description>\n\n"
                    }
                ]
            )
            logger.info("Received response from Claude API")
            if response.content:
                return response.content[0].text
            else:
                logger.warning("Received empty content from Claude API")
                return ""
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Error: {str(e)}"

    def create_folder_name(self, prompt: str, job_description: str) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=100,
                system=self.system_prompt,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\n"
                                                f"Job Description:\n"
                                                f"<job_description> \n{job_description}\n </job_description>\n\n"
                    }
                ]
            )
            if response.content:
                return response.content[0].text
            else:
                logger.warning("Received empty content from Claude API for folder name")
                return "Unknown_Company|Unknown_Position"
        except Exception as e:
            logger.error(f"Error in create_folder_name: {str(e)}")
            return "Error_Company|Error_Position"
