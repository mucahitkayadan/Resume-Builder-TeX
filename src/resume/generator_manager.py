from enum import Enum
from typing import Dict, Generator, Tuple, Optional
import logging

from src.resume.resume_generator import ResumeGenerator
from src.resume.cover_letter_generator import CoverLetterGenerator
from src.resume.utils.output_manager import OutputManager
from src.llms.runner import LLMRunner
from src.loaders.prompt_loader import PromptLoader

logger = logging.getLogger(__name__)

class GenerationType(Enum):
    RESUME = "resume"
    COVER_LETTER = "cover_letter"
    BOTH = "both"

class GeneratorManager:
    """Manages the generation of resumes and cover letters."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._llm_runner = None
        self._resume_generator = None
        self._cover_letter_generator = None
        self._prompt_loader = PromptLoader()

    @property
    def llm_runner(self) -> LLMRunner:
        if not self._llm_runner:
            raise ValueError("LLM Runner not configured")
        return self._llm_runner

    def configure_llm(self, model_type: str, model_name: str, temperature: float):
        """Configure LLM settings based on user input."""
        if not self._llm_runner:
            self._llm_runner = LLMRunner.create_with_config(
                model_type=model_type,
                model_name=model_name,
                temperature=temperature,
                prompt_loader=self._prompt_loader
            )
        else:
            self._llm_runner.update_config(
                model_type=model_type,
                model_name=model_name,
                temperature=temperature
            )
        logger.info(f"Configured LLM with {model_type}, {model_name}, temp={temperature}")

    @property
    def resume_generator(self) -> ResumeGenerator:
        if not self._resume_generator:
            self._resume_generator = ResumeGenerator(self.llm_runner, self.user_id)
        return self._resume_generator

    @property
    def cover_letter_generator(self) -> CoverLetterGenerator:
        if not self._cover_letter_generator:
            self._cover_letter_generator = CoverLetterGenerator(self.llm_runner, self.user_id)
        return self._cover_letter_generator

    def generate(self, 
                generation_type: GenerationType,
                job_description: str,
                selected_sections: Dict[str, str],
                output_manager: OutputManager) -> Generator[Tuple[str, float], None, None]:
        """Generate content based on the specified type."""
        try:
            if generation_type == GenerationType.RESUME:
                yield from self._generate_resume(job_description, selected_sections, output_manager)
            
            elif generation_type == GenerationType.COVER_LETTER:
                yield from self._generate_cover_letter(job_description, output_manager)
            
            elif generation_type == GenerationType.BOTH:
                resume = None
                # Generate resume first
                for result in self._generate_resume(job_description, selected_sections, output_manager):
                    if isinstance(result, tuple):
                        yield result
                    else:
                        resume = result

                if not resume:
                    raise ValueError("Resume generation failed")

                # Then generate cover letter
                yield from self._generate_cover_letter(
                    job_description, 
                    output_manager,
                    resume_id=resume.id
                )

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}", exc_info=True)
            raise

    def _generate_resume(self, job_description: str, selected_sections: Dict[str, str], 
                        output_manager: OutputManager):
        """Handle resume generation."""
        logger.info("Starting resume generation")
        for result in self.resume_generator.generate_resume(
            job_description=job_description,
            selected_sections=selected_sections,
            output_manager=output_manager
        ):
            if isinstance(result, tuple):
                yield result
            else:
                logger.info(f"Resume generated with ID: {result.id}")
                yield result

    def _generate_cover_letter(self, job_description: str, output_manager: OutputManager, 
                             resume_id: Optional[str] = None):
        """Handle cover letter generation."""
        logger.info("Starting cover letter generation")
        result = self.cover_letter_generator.generate_cover_letter(
            job_description=job_description,
            resume_id=resume_id,
            output_manager=output_manager
        )
        yield f"Cover letter generation: {result}", 1.0 