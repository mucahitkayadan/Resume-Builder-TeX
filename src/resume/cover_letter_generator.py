import logging

from src.llms.runner import LLMRunner
from src.latex.cover_letter.cover_letter_compiler import CoverLetterLatexCompiler
from src.loaders.prompt_loader import PromptLoader
from .utils.string_utils import ensure_string
from .utils.file_ops import create_output_directory
from src.core.database.factory import get_unit_of_work

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

    def generate_cover_letter(self,
                              job_description: str,
                              resume_id: str,
                              company_name: str,
                              job_title: str) -> str:
        """
        Generate a cover letter based on the given job description and resume data.
        
        Args:
            job_description: Job description text
            resume_id: ID of the associated resume
            company_name: Target company name
            job_title: Target job title
            
        Returns:
            Status message indicating success or failure
        """
        logger.info(f"Starting cover letter generation for resume ID: {resume_id}")
        
        # Validate inputs and get resume data
        validation_result = self._validate_and_get_data(job_description, resume_id)
        if isinstance(validation_result, str):
            return validation_result
        resume_data, resume = validation_result

        # Generate content
        try:
            cover_letter_content = self._generate_content(resume_data, job_description)
        except Exception as e:
            logger.error(f"Failed to generate cover letter content: {e}")
            return f"Failed to generate cover letter content: {str(e)}"

        # Generate PDF
        return self._generate_and_save_pdf(
            cover_letter_content, company_name, job_title, 
            resume.user_id, resume_id
        )

    def _validate_and_get_data(self, job_description: str, resume_id: str):
        """Validate inputs and retrieve necessary data."""
        if not job_description:
            return "Please enter a job description."

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

    def _generate_and_save_pdf(self, content: str, company_name: str, 
                              job_title: str, user_id: str, resume_id: str) -> str:
        """Generate PDF and save to database."""
        output_dir = create_output_directory(company_name, job_title)
        
        try:
            pdf_content, latex_content = self.latex_compiler.generate_pdf(
                content=content,
                output_dir=output_dir,
                user_id=user_id,
                resume_id=resume_id
            )
            
            with self.uow:
                self.uow.update_cover_letter(resume_id, latex_content, pdf_content)
            return "Cover letter generated and saved successfully."
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            with self.uow:
                self.uow.update_cover_letter(resume_id, content, None)
            return "Cover letter content saved, but PDF generation failed." 