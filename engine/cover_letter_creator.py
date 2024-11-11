import os
import logging
from src.core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork
from utils.latex_compiler import generate_cover_letter_pdf
from src.loaders.prompt_loader import PromptLoader
from engine.runners import AIRunner

logger = logging.getLogger(__name__)

class CoverLetterCreator:
    """A class for creating cover letters based on job descriptions and resume data."""

    def __init__(self, ai_runner: AIRunner, prompt_loader: PromptLoader, uow: MongoUnitOfWork):
        """Initialize the CoverLetterCreator with necessary components."""
        self.ai_runner = ai_runner
        self.prompt_loader = prompt_loader
        self.uow = uow

    def generate_cover_letter(self, job_description: str, resume_id: str, company_name: str, job_title: str) -> str:
        """Generate a cover letter based on the given job description and resume data."""
        logger.info(f"Starting cover letter generation for resume ID: {resume_id}")
        
        if not job_description:
            return "Please enter a job description."

        with self.uow:
            # Get resume data for cover letter
            resume_data = self.uow.get_resume_for_cover_letter(resume_id)
            if not resume_data:
                return f"Resume with ID {resume_id} not found or has no content suitable for cover letter generation."

            # Get the resume to access user_id
            resume = self.uow.resumes.get_by_id(resume_id)
            if not resume:
                return f"Resume with ID {resume_id} not found."

        logger.info("Generating cover letter with AIRunner model")
        resume_data = self._ensure_string(resume_data)
        cover_letter_prompt = self.prompt_loader.get_cover_letter_prompt()

        try:
            cover_letter_content = self.ai_runner.process_section(cover_letter_prompt, resume_data, job_description)
        except Exception as e:
            logger.error(f"Failed to process cover letter: {str(e)}")
            return f"Failed to process cover letter: {str(e)}"

        output_dir = os.path.join("created_resumes", f"{company_name}_{job_title}")
        os.makedirs(output_dir, exist_ok=True)

        try:
            pdf_content, latex_content = generate_cover_letter_pdf(
                self.uow,
                cover_letter_content,
                output_dir,
                resume.user_id,
                resume_id
            )
            with self.uow:
                self.uow.update_cover_letter(resume_id, latex_content, pdf_content)
            return "Cover letter generated and saved successfully."
        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}")
            with self.uow:
                self.uow.update_cover_letter(resume_id, cover_letter_content, None)
            return "Cover letter content saved, but PDF generation failed."

    def _ensure_string(self, data):
        if isinstance(data, dict):
            return {k: self._ensure_string(v) for k, v in data.items()}
        elif isinstance(data, bytes):
            return data.decode('utf-8')
        elif isinstance(data, str):
            return data
        else:
            return str(data)
