import logging

from src.llms.runner import LLMRunner
from src.latex.cover_letter.cover_letter_compiler import CoverLetterLatexCompiler
from src.loaders.prompt_loader import PromptLoader
from .utils.string_utils import ensure_string
from src.core.database.factory import get_unit_of_work
from src.resume.utils.output_manager import OutputManager

logger = logging.getLogger(__name__)

class CoverLetterGenerator:
    """A class for generating cover letters based on job descriptions and resume data."""

    def __init__(self, llm_runner: LLMRunner, user_id: str):
        """Initialize the CoverLetterGenerator with necessary parts."""
        self.llm_runner = llm_runner
        self.user_id = user_id
        self.prompt_loader = PromptLoader()
        self.uow = get_unit_of_work()
        self.latex_compiler = CoverLetterLatexCompiler()

    def generate_cover_letter(self, job_description: str, resume_id: str, output_manager: OutputManager) -> str:
        """Generate a cover letter based on the given job description and resume data."""
        logger.info(f"Starting cover letter generation for resume ID: {resume_id}")
        
        try:
            # Validate inputs and get resume data
            logger.debug("Validating inputs and getting resume data")
            validation_result = self._validate_and_get_data(job_description, resume_id)
            if isinstance(validation_result, str):
                logger.warning(f"Validation failed: {validation_result}")
                return validation_result
            resume_data, resume = validation_result
            logger.debug("Validation successful")

            # Generate content
            logger.debug("Generating cover letter content")
            cover_letter_content = self._generate_content(resume_data, job_description)
            logger.debug("Content generation complete")

            # Generate PDF
            logger.debug("Starting PDF generation")
            pdf_content, latex_content = self.latex_compiler.generate_pdf(
                content=cover_letter_content,
                output_manager=output_manager,
                user_id=self.user_id,
                resume_id=resume_id
            )
            logger.debug("PDF generation complete")
            
            if not pdf_content:
                logger.error("PDF generation failed")
                with self.uow:
                    self.uow.update_cover_letter(resume_id, latex_content, None)
                return "Cover letter content saved, but PDF generation failed."

            # Save to database
            with self.uow:
                self.uow.update_cover_letter(resume_id, latex_content, pdf_content)
            
            return "Cover letter generated and saved successfully."
            
        except Exception as e:
            logger.error(f"Failed to generate cover letter: {e}")
            raise

    def _validate_and_get_data(self, job_description: str, resume_id: str):
        """Validate inputs and retrieve necessary data."""
        if not job_description:
            return "Please enter a job description."

        # If no resume_id, create minimal resume data
        if not resume_id:
            with self.uow:
                portfolio = self.uow.portfolio.get_by_user_id(self.user_id)
                if not portfolio:
                    return "No portfolio found for user"
                
                minimal_resume = {
                    'personal_information': portfolio.personal_information,
                    'career_summary': "",
                    'skills': "",
                    'work_experience': "",
                    'education': "",
                    'projects': "",
                    'awards': "",
                    'publications': ""
                }
                return minimal_resume, None

        # If resume_id exists, get resume data
        with self.uow:
            resume_data = self.uow.get_resume_for_cover_letter(resume_id)
            if not resume_data:
                return f"Resume with ID {resume_id} not found or has no content suitable for cover letter generation."

            resume = self.uow.resumes.get_by_id(resume_id)
            if not resume:
                return f"Resume with ID {resume_id} not found."

        return resume_data, resume

    def _generate_content(self, resume_data: dict, job_description: str) -> str:
        """Generate cover letter content using AI."""
        resume_data = ensure_string(resume_data)
        cover_letter_prompt = self.prompt_loader.get_cover_letter_prompt()
        return self.llm_runner.generate_content(
            cover_letter_prompt, resume_data, job_description
        )
  