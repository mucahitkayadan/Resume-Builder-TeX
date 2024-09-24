import os
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion
from anthropic import Anthropic, APIError

from loaders.tex_loader import TexLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class BaseRunner(ABC):
    """
    Abstract base class for AI model runners.
    """

    def __init__(self, model: str, system_prompt: str):
        """
        Initialize the BaseRunner.

        Args:
            model (str): The name of the AI model to use.
            system_prompt (str): The system prompt to use for the AI model.
        """
        self.model = model
        self.system_prompt = system_prompt

    @abstractmethod
    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        """
        Abstract method to process a section using the AI API.

        Args:
            :param prompt: (str): The prompt for the AI model.
            :param data: (str): The data to process.
            :param job_description: (str): The job description.
        Returns:
            str: The processed section content.
        """
        pass

    def process_personal_information(self, prompt: str, personal_info: Dict[str, str], job_description: str) -> str:
        """Process personal information section."""
        return self.process_section(prompt, str(personal_info), job_description)

    # def process_career_summary(self, prompt: str, data: dict, job_description: str) -> str:
    #     """Process career summary section."""
    #     return self.process_section(prompt, str(data), job_description)

    def process_work_experience(self, prompt: str, work_experience: List[Dict[str, Any]], job_description: str) -> str:
        """Process work experience section."""
        return self.process_section(prompt, str(work_experience), job_description)

    def process_skills(self, prompt: str, skills: Dict[str, List[str]], job_description: str) -> str:
        """Process skills section."""
        return self.process_section(prompt, str(skills), job_description)

    def process_education(self, prompt: str, education: List[Dict[str, Any]], job_description: str) -> str:
        """Process education section."""
        return self.process_section(prompt, str(education), job_description)

    def process_projects(self, prompt: str, projects: List[Dict[str, Any]], job_description: str) -> str:
        """Process projects section."""
        return self.process_section(prompt, str(projects), job_description)

    def create_folder_name(self, prompt: str, job_description: str) -> str:
        """Create a folder name based on the job description."""
        return self.process_section(prompt, "", job_description)

    def process_awards(self, prompt: str, awards: List[Dict[str, Any]], job_description: str) -> str:
        """Process awards section."""
        return self.process_section(prompt, str(awards), job_description)

    def process_publications(self, prompt: str, publications: List[Dict[str, Any]], job_description: str) -> str:
        """Process publications section."""
        return self.process_section(prompt, str(publications), job_description)

    def collect_resume_content(self, tex_loader: TexLoader) -> str:
        """
        Collect content from all sections of the résumé using TexLoader.

        Args:
            tex_loader (TexLoader): An instance of TexLoader to load section content.

        Returns:
            str: Collected content from all sections.
        """
        sections = [
            "personal_information",
            "work_experience",
            "skills",
            "education",
            "projects",
            "awards",
            "publications"
        ]
        content = {section: tex_loader.get_section_content(section) for section in sections}
        return "\n\n".join([f"{section.capitalize()}:\n{details}" for section, details in content.items()])

    def process_career_summary(self, prompt: str, data: dict, job_description: str, tex_loader: TexLoader) -> str:
        """Process career summary section."""
        resume_content = self.collect_resume_content(tex_loader)
        return self.process_section(prompt, f"{str(data)}\n{resume_content}", job_description)

    def process_cover_letter(self, prompt: str, tex_loader: TexLoader,  job_description: str) -> str:
        """Process cover letter section."""
        resume_content = self.collect_resume_content(tex_loader)
        return self.process_section(prompt, resume_content, job_description)

class OpenAIRunner(BaseRunner):
    """Runner for OpenAI models."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.1, system_prompt: str = "You are a professional resume writer. Do not add external text to your answers, answer only with asked latex content, no introduction or explanation."):
        """
        Initialize the OpenAIRunner.

        Args:
            model (str): The OpenAI model to use.
            temperature (float): The temperature setting for the model.
            system_prompt (str): The system prompt for the OpenAI model.
        """
        super().__init__(model, system_prompt)
        self.temperature = temperature
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        """
        Process a section using the OpenAI API.

        Args:
            :param prompt: (str): The prompt for the AI model.
            :param data: (str): The data to process.
            :param job_description: (str): The job description.
        Returns:
            str: The processed section content.
        """
        try:
            logger.info(f"Sending request to OpenAI API with model: {self.model}")
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"PROMPT: {prompt}\n\n"
                                                f"USER PROFILE: **YOU WILL USE ONLY THIS DATA WHEN CRAFTING THE PART OF "
                                                f"THE RESUME. DO NOT ADD OR ASSUME ANY SKILL OR TECHNOLOGY IF IT IS NOT "
                                                f"EXPLICITLY GIVEN AND EVEN IT IS A MUST IN THE JOB DESCRIPTION!!**{data}\n\n"
                                                f"JOB DESCRIPTION: {job_description}"
                    }
                ],
                temperature=self.temperature,  # Pass the temperature here
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


class ClaudeRunner(BaseRunner):
    """Runner for Claude (Anthropic) models."""

    def __init__(self, model: str = "claude-3-5-sonnet-20240620", temperature: float = 0.1, system_prompt: str = "You are a professional resume writer. Do not add external text to your answers, answer only with asked latex content, no introduction or explanation."):
        """
        Initialize the ClaudeRunner.

        Args:
            model (str): The Claude model to use.
            temperature (float): The temperature setting for the model.
            system_prompt (str): The system prompt for the Claude model.
        """
        super().__init__(model, system_prompt)
        self.temperature = temperature  # Store the temperature
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=api_key)

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        """
        Process a section using the Claude API.

        Args:
            :param prompt: (str): The prompt for the AI model.
            :param data: (str): The data to process.
            :param job_description: (str): The job description.
        Returns:
            str: The processed section content.
        """
        try:
            logger.info(f"Sending request to Claude API with model: {self.model}")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=self.system_prompt,
                temperature=self.temperature,  # Pass the temperature here
                messages=[
                    {"role": "user", "content": f"PROMPT: {prompt}\n\n"
                                                f"User Profile: **YOU WILL USE ONLY THIS DATA WHEN CRAFTING THE PART OF "
                                                f"THE RESUME. DO NOT ADD OR ASSUME ANY SKILL OR TECHNOLOGY IF IT IS NOT "
                                                f"EXPLICITLY GIVEN AND EVEN IT IS A MUST IN THE JOB DESCRIPTION!!**{data}\n\n"
                                                f"JOB DESCRIPTION: {job_description}"
                    }
                ]
            )
            logger.info("Received response from Claude API")
            if response.content:
                return response.content[0].text
            else:
                logger.warning("Received empty content from Claude API")
                return ""
        except APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error processing section: {e}")
            return f"Unexpected error: {str(e)}"


class Runner(BaseRunner):
    """Main runner class that delegates to specific AI model runners."""

    def __init__(self, runner_type: str, model: Optional[str] = None, system_prompt: Optional[str] = None, temperature: Optional[float] = 0.1):
        """
        Initialize the Runner.

        Args:
            runner_type (str): The type of runner to use ("openai" or "claude").
            model (Optional[str]): The specific model to use, if any.
            system_prompt (Optional[str]): The system prompt to use, if any.
            temperature (Optional[float]): The temperature setting for the model.
        """
        super().__init__(model or "", system_prompt or "")
        self.runner_type = runner_type  # Add this line
        if runner_type == "openai":
            if model and not (model.startswith("gpt-") or model.startswith("o1-")):
                raise ValueError(f"Invalid model for OpenAI: {model}")
            self.runner = OpenAIRunner(model=model, system_prompt=system_prompt, temperature=temperature)
        elif runner_type == "claude":
            if model and not model.startswith("claude-"):
                raise ValueError(f"Invalid model for Claude: {model}")
            self.runner = ClaudeRunner(model=model, system_prompt=system_prompt, temperature=temperature)
        else:
            raise ValueError(f"Unsupported runner type: {runner_type}")

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        return self.runner.process_section(prompt, data, job_description)

    def __getattr__(self, name):
        if name == "runner_type":
            return self.runner_type
        return getattr(self.runner, name)
