import os
import logging
from typing import Dict, Generator, Tuple
from utils.document_utils import (
    process_sections,
    create_output_directory,
    save_job_description,
    get_or_create_folder_name
)
from utils.database_manager import DatabaseManager
from utils.latex_compiler import generate_resume_pdf
from engine.hardcode_sections import HardcodeSections
from loaders.tex_loader import TexLoader
from engine.runners import AIRunner
from engine.ai_strategies import OpenAIStrategy, ClaudeStrategy
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

class ResumeCreator:
    """
    A class for creating resumes based on job descriptions using AI models.

    This class handles the entire process of resume generation, including
    content creation, PDF generation, and database storage.

    Attributes:
        runner: An instance of the AI model runner.
        json_loader: An instance of JsonLoader for loading personal information.
        prompt_loader: An instance of PromptLoader for loading prompts.
        db_manager: An instance of DatabaseManager for database operations.
        logger: A logger instance for logging operations.
    """

    def __init__(self, ai_runner: AIRunner, json_loader: JsonLoader, prompt_loader: PromptLoader, db_manager: DatabaseManager):
        """
        Initialize the ResumeCreator with necessary components.

        Args:
            runner: An instance of the AI model runner.
            json_loader: An instance of JsonLoader.
            prompt_loader: An instance of PromptLoader.
            db_manager: An instance of DatabaseManager.
        """
        self.ai_runner = ai_runner
        self.json_loader = json_loader
        self.prompt_loader = prompt_loader
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)
        self.tex_loader = TexLoader(db_manager)
        self.hardcoder = HardcodeSections(json_loader, self.tex_loader)

    def generate_resume(self, job_description: str, company_name: str, job_title: str, 
                        model_type: str, model_name: str, temperature: float,
                        selected_sections: Dict[str, str]) -> Generator[Tuple[str, float], None, None]:
        """
        Generate a resume based on the given job description.

        This method handles the entire process of resume generation, including
        content creation, PDF generation, and database storage.

        Args:
            job_description: The job description to base the resume on.
            company_name: The name of the company.
            job_title: The title of the job.
            model_type: The type of AI model used.
            model_name: The name of the AI model used.
            temperature: The temperature setting for the AI model.
            selected_sections: A dictionary of sections to process.

        Yields:
            A tuple containing a status message and a progress value (0 to 1).

        Raises:
            Exception: If there's an error in PDF generation or database insertion.
        """
        self.logger.info("Starting resume generation process")
        self.logger.info(f"Generating resume with {self.ai_runner.__class__.__name__} model: {self.ai_runner.model}")
        
        if not job_description:
            self.logger.warning("Job description not provided")
            yield "Please enter a job description.", 0
            return

        # Set the appropriate strategy based on model_type
        if model_type == "OpenAI":
            self.ai_runner.set_strategy(OpenAIStrategy(model_name, temperature, self.prompt_loader.get_system_prompt()))
        elif model_type == "Claude":
            self.ai_runner.set_strategy(ClaudeStrategy(model_name, temperature, self.prompt_loader.get_system_prompt()))
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

        # Process sections
        content_dict: Dict[str, str] = {}
        for i, (section, process_type) in enumerate(selected_sections.items()):
            if process_type == "skip":
                continue
            elif process_type == "hardcode":
                content = self.hardcoder.hardcode_section(section)
            else:  # "process"
                prompt = getattr(self.prompt_loader, f"get_{section}_prompt")()
                data = getattr(self.json_loader, f"get_{section}")()
                content = self.ai_runner.process_section(prompt, data, job_description)
            
            content_dict[section] = content
            self.logger.info(f"Processed {section} section")
            yield f"Processed {section} section", (i + 1) / len(selected_sections)

        self.logger.info("Content generation completed")

        # Create output directory
        output_dir = create_output_directory(f"{company_name}_{job_title}")
        save_job_description(job_description, output_dir)

        # Generate PDF
        try:
            pdf_content = generate_resume_pdf(self.db_manager, content_dict, output_dir)
            self.logger.info("PDF generation successful")
        except Exception as e:
            self.logger.error(f"PDF generation failed: {str(e)}")
            yield f"Resume generation failed: {str(e)}", 1
            return

        # Insert into database
        try:
            resume_id = self.db_manager.insert_resume(
                company_name, 
                job_title, 
                job_description, 
                content_dict,
                pdf_content,
                model_type,
                model_name,
                temperature
            )
            self.logger.info(f"Resume {company_name}_{job_title} generated successfully with ID: {resume_id}")
            yield f"Resume {company_name}_{job_title} generated successfully with ID: {resume_id}", 1
        except Exception as e:
            self.logger.error(f"Database insertion failed: {str(e)}")
            yield f"Resume generation completed but database insertion failed: {str(e)}", 1

    def create_output_directory(self, company_name: str, job_title: str) -> str:
        """
        Create an output directory for the resume.

        Args:
            company_name: The name of the company.
            job_title: The title of the job.

        Returns:
            The path to the created output directory.
        """
        folder_name = f"{company_name}_{job_title}".replace(" ", "_")
        output_dir = os.path.join("created_resumes", folder_name)
        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(f"Created output directory: {output_dir}")
        return output_dir
