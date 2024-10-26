import os
import re
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion
from anthropic import Anthropic, APIError

from loaders.tex_loader import TexLoader
from engine.ai_strategies import AIStrategy, OpenAIStrategy, ClaudeStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class BaseRunner(ABC):
    """
    Abstract base class for AI model runners.
    """

    def __init__(self, model: str, temperature: float, system_prompt: str):
        """
        Initialize the BaseRunner.

        Args:
            model (str): The name of the AI model to use.
            temperature (float): The temperature setting for the model.
            system_prompt (str): The system prompt for the AI model.
        """
        self.model: str = model
        self.temperature: float = temperature
        self.runner_type: str = self.__class__.__name__
        self.system_prompt: str = system_prompt

    @abstractmethod
    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        """
        Abstract method to process a section using the AI API.

        Args:
            prompt (str): The prompt for the AI model.
            data (str): The data to process.
            job_description (str): The job description.

        Returns:
            str: The processed section content.
        """
        pass

    def process_personal_information(self, prompt: str, personal_info: Dict[str, str], job_description: str) -> str:
        """
        Process personal information section.

        Args:
            prompt (str): The prompt for the AI model.
            personal_info (Dict[str, str]): Personal information data.
            job_description (str): The job description.

        Returns:
            str: Processed personal information content.
        """
        return self.process_section(prompt, str(personal_info), job_description)

    def process_work_experience(self, prompt: str, work_experience: List[Dict[str, Any]], job_description: str) -> str:
        """
        Process work experience section.

        Args:
            prompt (str): The prompt for the AI model.
            work_experience (List[Dict[str, Any]]): Work experience data.
            job_description (str): The job description.

        Returns:
            str: Processed work experience content.
        """
        return self.process_section(prompt, str(work_experience), job_description)

    def process_skills(self, prompt: str, skills: Dict[str, List[str]], job_description: str) -> str:
        """
        Process skills section.

        Args:
            prompt (str): The prompt for the AI model.
            skills (Dict[str, List[str]]): Skills data.
            job_description (str): The job description.

        Returns:
            str: Processed skills content.
        """
        return self.process_section(prompt, str(skills), job_description)

    def process_education(self, prompt: str, education: List[Dict[str, Any]], job_description: str) -> str:
        """
        Process education section.

        Args:
            prompt (str): The prompt for the AI model.
            education (List[Dict[str, Any]]): Education data.
            job_description (str): The job description.

        Returns:
            str: Processed education content.
        """
        return self.process_section(prompt, str(education), job_description)

    def process_projects(self, prompt: str, projects: List[Dict[str, Any]], job_description: str) -> str:
        """
        Process projects section.

        Args:
            prompt (str): The prompt for the AI model.
            projects (List[Dict[str, Any]]): Projects data.
            job_description (str): The job description.

        Returns:
            str: Processed projects content.
        """
        return self.process_section(prompt, str(projects), job_description)

    def create_folder_name(self, prompt: str, job_description: str) -> str:
        """
        Create a folder name based on the job description.

        Args:
            prompt (str): The prompt for the AI model.
            job_description (str): The job description.

        Returns:
            str: Generated folder name.
        """
        try:
            result = self.process_section(prompt, "", job_description)
            parts = result.split('|')
            if len(parts) == 2:
                return result
            else:
                logger.warning(f"Unexpected format in create_folder_name result: {result}")
                match = re.search(r'(.*?)[,|](.*)$', result)
                if match:
                    return f"{match.group(1).strip()}|{match.group(2).strip()}"
                else:
                    return f"Unknown_Company|{result[:50]}"
        except Exception as e:
            logger.error(f"Error in create_folder_name: {str(e)}")
            return "Error_Company|Error_Position"

    def process_awards(self, prompt: str, awards: List[Dict[str, Any]], job_description: str) -> str:
        """
        Process awards section.

        Args:
            prompt (str): The prompt for the AI model.
            awards (List[Dict[str, Any]]): Awards data.
            job_description (str): The job description.

        Returns:
            str: Processed awards content.
        """
        return self.process_section(prompt, str(awards), job_description)

    def process_publications(self, prompt: str, publications: List[Dict[str, Any]], job_description: str) -> str:
        """
        Process publications section.

        Args:
            prompt (str): The prompt for the AI model.
            publications (List[Dict[str, Any]]): Publications data.
            job_description (str): The job description.

        Returns:
            str: Processed publications content.
        """
        return self.process_section(prompt, str(publications), job_description)

    def collect_resume_content(self, sections_content: Dict[str, str]) -> str:
        """
        Collect content from all sections of the résumé.

        Args:
            sections_content (Dict[str, str]): A dictionary containing the content of each section.

        Returns:
            str: Collected content from all sections.
        """
        return "\n\n".join([f"{section.capitalize()}:\n{details}" for section, details in sections_content.items()])

    def process_career_summary(self, prompt: str, data: Dict[str, Any], job_description: str) -> str:
        """
        Process career summary section.

        Args:
            prompt (str): The prompt for the AI model.
            data (Dict[str, Any]): Career summary data.
            job_description (str): The job description.

        Returns:
            str: Processed career summary content.
        """
        return self.process_section(prompt, str(data), job_description)

    def process_cover_letter(self, prompt: str, resume_content: str, job_description: str) -> str:
        """
        Process cover letter section.

        Args:
            prompt (str): The prompt for the AI model.
            resume_content (str): The content of the resume.
            job_description (str): The job description.

        Returns:
            str: Processed cover letter content.
        """
        return self.process_section(prompt, resume_content, job_description)

class AIRunner:
    def __init__(self, strategy: AIStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: AIStrategy):
        self.strategy = strategy

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        return self.strategy.process_section(prompt, data, job_description)

    def create_folder_name(self, folder_name_prompt: str, job_description: str) -> str:
        return self.strategy.create_folder_name(folder_name_prompt, job_description)

    @property
    def model(self):
        return self.strategy.model

    @property
    def temperature(self):
        return self.strategy.temperature
