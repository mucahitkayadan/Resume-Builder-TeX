import logging
import sys
from typing import Dict, Generator, Tuple
from pathlib import Path

from src.core.database.unit_of_work import MongoUnitOfWork
from src.core.database.models.resume import Resume
from src.llms.runner import AIRunner
from src.llms.strategies import OpenAIStrategy, ClaudeStrategy, OllamaStrategy
from src.latex.resume.resume_compiler import ResumeLatexCompiler
from src.loaders.prompt_loader import PromptLoader
from src.loaders.tex_loader import TexLoader
from .hardcode_sections import HardcodeSections
from .utils.file_ops import create_output_directory, save_job_description

logger = logging.getLogger(__name__)

class ResumeGenerator:
    """
    A class for generating resumes based on job descriptions using AI models.
    
    This class handles the entire process of resume generation, including
    content creation, PDF generation, and database storage.
    """

    def __init__(self, ai_runner: AIRunner, prompt_loader: PromptLoader, uow: MongoUnitOfWork):
        """Initialize the ResumeGenerator with necessary components."""
        self.ai_runner = ai_runner
        self.prompt_loader = prompt_loader
        self.uow = uow
        self.tex_loader = TexLoader(uow)
        self.hardcoder = HardcodeSections(uow, self.tex_loader)
        self.latex_compiler = ResumeLatexCompiler(uow)

    def generate_resume(self, job_description: str, company_name: str, job_title: str, 
                       model_type: str, model_name: str, temperature: float,
                       selected_sections: Dict[str, str], user_id: str) -> Generator[Tuple[str, float], None, None]:
        """
        Generate a resume based on the provided job description and settings.
        
        Args:
            job_description: Job description text
            company_name: Target company name
            job_title: Target job title
            model_type: AI model type (OpenAI, Claude, Ollama)
            model_name: Specific model name
            temperature: Model temperature setting
            selected_sections: Dictionary of sections to process
            user_id: User identifier
            
        Yields:
            Tuple of (status message, progress percentage)
        """
        logger.info("Starting resume generation process")
        
        # Set AI strategy
        strategy = self._get_ai_strategy(model_type)
        strategy.model = model_name
        strategy.temperature = temperature
        self.ai_runner.set_strategy(strategy)
        
        # Process sections
        content_dict = self._process_sections(selected_sections, job_description, user_id)
        
        # Generate and save resume
        try:
            resume = self._generate_and_save_resume(
                content_dict, job_description, company_name, 
                job_title, user_id, model_type, model_name, temperature
            )
            yield f"Resume generated and saved successfully (ID: {resume.id})", 1
        except Exception as e:
            logger.error(f"Resume generation failed: {str(e)}", exc_info=True)
            yield f"Resume generation failed: {str(e)}", 1

    def _get_ai_strategy(self, model_type: str):
        """Get appropriate AI strategy based on model type."""
        strategy_map = {
            "OpenAI": OpenAIStrategy,
            "Claude": ClaudeStrategy,
            "Ollama": OllamaStrategy
        }
        strategy_class = strategy_map.get(model_type)
        if not strategy_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        return strategy_class(self.prompt_loader.get_system_prompt())

    def _process_sections(self, selected_sections: Dict[str, str], 
                         job_description: str, user_id: str) -> Dict[str, str]:
        """Process each selected section."""
        content_dict = {}
        for section, process_type in selected_sections.items():
            try:
                content = self.process_section(section, process_type, job_description, user_id)
                if content:
                    content_dict[section] = content
                    logger.info(f"Processed {section} section")
            except Exception as e:
                logger.error(f"Failed to process section {section}: {e}")
        return content_dict

    def _generate_and_save_resume(self, content_dict: Dict[str, str], 
                                job_description: str, company_name: str, 
                                job_title: str, user_id: str, model_type: str,
                                model_name: str, temperature: float) -> Resume:
        """Generate PDF and save resume to database."""
        output_dir = create_output_directory(company_name, job_title)
        save_job_description(job_description, output_dir)

        generated_pdf = self.latex_compiler.generate_pdf(content_dict, output_dir)
        if not generated_pdf:
            raise Exception("PDF generation failed")

        resume = Resume(
            id=None,
            user_id=user_id,
            company_name=company_name,
            job_title=job_title,
            job_description=job_description,
            **content_dict,
            model_type=model_type,
            model_name=model_name,
            temperature=temperature,
            resume_pdf=generated_pdf
        )

        with self.uow:
            return self.uow.resumes.add(resume)

    def process_section(self, section: str, process_type: str, 
                       job_description: str, user_id: str) -> str:
        """Process a single section based on the process type."""
        if process_type == "hardcode":
            return self.hardcoder.hardcode_section(section, user_id)
        elif process_type == "ai":
            prompt = self.prompt_loader.get_section_prompt(section)
            return self.ai_runner.process_section(prompt, job_description)
        else:
            raise ValueError(f"Invalid process type: {process_type}") 