import logging
from enum import Enum
from typing import Dict, Generator, Optional, Tuple

from config.settings import APP_CONSTANTS, FEATURE_FLAGS
from src.core.database.factory import get_unit_of_work
from src.generator.cover_letter_generator import CoverLetterGenerator
from src.generator.resume_generator import ResumeGenerator
from src.generator.utils.job_analysis import check_clearance_requirement
from src.generator.utils.output_manager import OutputManager
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
        logger.debug(f"Initializing GeneratorManager with user_id: {user_id}")
        self._prompt_loader = PromptLoader(user_id=user_id)

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
                prompt_loader=self._prompt_loader,
            )
        else:
            self._llm_runner.update_config(
                model_type=model_type, model_name=model_name, temperature=temperature
            )
        logger.info(
            f"Configured LLM with {model_type}, {model_name}, temp={temperature}"
        )

    @property
    def resume_generator(self) -> ResumeGenerator:
        if not self._resume_generator:
            self._resume_generator = ResumeGenerator(self.llm_runner, self.user_id)
        return self._resume_generator

    @property
    def cover_letter_generator(self) -> CoverLetterGenerator:
        if not self._cover_letter_generator:
            self._cover_letter_generator = CoverLetterGenerator(
                self.llm_runner, self.user_id
            )
        return self._cover_letter_generator

    def generate(
        self,
        generation_type: GenerationType,
        job_description: str,
        selected_sections: Dict[str, str],
        output_manager: OutputManager,
    ) -> Generator[Tuple[str, float], None, None]:
        """Generate content based on the specified type."""
        try:
            # Get user preferences for features
            with get_unit_of_work() as uow:
                preferences = uow.users.get_preferences(self.user_id)
                feature_flags = (
                    preferences.get("feature_preferences", {}) if preferences else {}
                )

            # Check clearance if the feature is enabled
            if feature_flags.get("check_clearance", FEATURE_FLAGS["check_clearance"]):
                if check_clearance_requirement(
                    job_description, APP_CONSTANTS["clearance_keywords"]
                ):
                    raise ValueError(
                        "Cannot generate content for positions requiring security clearance"
                    )

            # Generate based on type
            if generation_type == GenerationType.RESUME:
                yield from self._generate_resume(
                    job_description, selected_sections, output_manager
                )

            elif generation_type == GenerationType.COVER_LETTER:
                yield from self._generate_cover_letter(job_description, output_manager)

            elif generation_type == GenerationType.BOTH:
                resume = None
                # Generate resume first
                for result in self._generate_resume(
                    job_description, selected_sections, output_manager
                ):
                    if isinstance(result, tuple):
                        yield result
                    else:
                        resume = result

                if not resume:
                    raise ValueError("Resume generation failed")

                # Then generate cover letter
                yield from self._generate_cover_letter(
                    job_description, output_manager, resume_id=resume.id
                )

            # Auto-save if enabled
            if feature_flags.get("auto_save", True):
                output_manager.save_job_description(job_description)

        except Exception as e:
            logger.error(f"Generation failed: {str(e)}", exc_info=True)
            raise

    def _generate_resume(
        self,
        job_description: str,
        selected_sections: Dict[str, str],
        output_manager: OutputManager,
    ):
        """Handle resume generation."""
        logger.info("Starting resume generation")
        for result in self.resume_generator.generate_resume(
            job_description=job_description,
            selected_sections=selected_sections,
            output_manager=output_manager,
        ):
            if isinstance(result, tuple):
                yield result
            else:
                logger.info(f"Resume generated with ID: {result.id}")
                yield result

    def _generate_cover_letter(
        self,
        job_description: str,
        output_manager: OutputManager,
        resume_id: Optional[str] = None,
    ):
        """Handle cover letter generation."""
        logger.info("Starting cover letter generation")
        logger.debug(f"Current user_id: {self.user_id}")

        try:
            # If no resume_id provided, get the latest resume
            if not resume_id:
                with get_unit_of_work() as uow:
                    logger.debug(f"Getting last resume ID for user_id: {self.user_id}")
                    latest_resume_id = uow.get_last_resume_id(self.user_id)
                    logger.debug(f"Retrieved latest_resume_id: {latest_resume_id}")
                    if latest_resume_id:
                        resume_id = latest_resume_id
                        logger.info(f"Using latest resume with ID: {resume_id}")
                    else:
                        logger.warning("No existing resume found for user")
                        raise ValueError(
                            "No resume found. Please generate a resume first or select an existing one."
                        )

            if not resume_id:
                raise ValueError("Resume ID is required for cover letter generation")

            result = self.cover_letter_generator.generate_cover_letter(
                job_description=job_description,
                resume_id=resume_id,
                output_manager=output_manager,
            )

            if isinstance(result, str) and "Failed to save" in result:
                logger.error(f"Cover letter generation failed: {result}")
                raise ValueError(result)

            yield f"Cover letter generation: {result}", 1.0

        except Exception as e:
            logger.error(f"Cover letter generation failed: {str(e)}")
            raise
