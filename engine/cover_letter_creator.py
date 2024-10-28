import os
import logging
from utils.database_manager import DatabaseManager
from utils.latex_compiler import generate_cover_letter_pdf
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.runners import AIRunner

logger = logging.getLogger(__name__)

class CoverLetterCreator:
    """
    A class for creating cover letters based on job descriptions and resume data.

    This class handles the process of cover letter generation, including
    content creation, PDF generation, and database storage.

    Attributes:
        json_loader (JsonLoader): An instance of JsonLoader for loading personal information.
        prompt_loader (PromptLoader): An instance of PromptLoader for loading promp
        db_manager (DatabaseManager): An instance of DatabaseManager for database operations.
    """

    def __init__(self, ai_runner: AIRunner, json_loader: JsonLoader, prompt_loader: PromptLoader, db_manager: DatabaseManager):
        """
        Initialize the CoverLetterCreator with necessary components.

        Args:
            json_loader (JsonLoader): An instance of JsonLoader.
            prompt_loader (PromptLoader): An instance of PromptLoader.
            db_manager (DatabaseManager): An instance of DatabaseManager.
        """
        self.ai_runner = ai_runner
        self.json_loader = json_loader
        self.prompt_loader = prompt_loader
        self.db_manager = db_manager

    def generate_cover_letter(self, job_description: str, resume_id: int, company_name: str, job_title: str) -> str:
        """
        Generate a cover letter based on the given job description and resume data.

        This method handles the entire process of cover letter generation, including
        content creation, PDF generation, and database storage.

        Args:
            job_description (str): The job description to base the cover letter on.
            resume_id (int): The ID of the resume in the database.
            company_name (str): The name of the company.
            job_title (str): The title of the job.

        Returns:
            str: A message indicating the result of the cover letter generation process.

        Raises:
            Exception: If there's an error in PDF generation or database insertion.
        """
        logger.info(f"Starting cover letter generation for resume ID: {resume_id}")
        
        if not job_description:
            return "Please enter a job description."

        # Use the new method to get resume data for cover letter
        resume_data = self.db_manager.get_resume_for_cover_letter(resume_id)
        if not resume_data:
            return f"Resume with ID {resume_id} not found or has no content suitable for cover letter generation."

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
                self.db_manager,
                cover_letter_content,
                resume_id,
                output_dir,
                company_name,
                job_title,
                self.json_loader
            )
            self.db_manager.update_cover_letter(resume_id, latex_content, pdf_content)
            return "Cover letter generated and saved successfully."
        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}")
            self.db_manager.update_cover_letter(resume_id, cover_letter_content, None)
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
