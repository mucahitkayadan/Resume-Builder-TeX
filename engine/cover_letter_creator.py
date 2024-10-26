import os
import logging
import subprocess
import json
from typing import Optional, Any
from utils.database_manager import DatabaseManager
from loaders.tex_loader import TexLoader
from utils.latex_compiler import generate_cover_letter_pdf
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader

class CoverLetterCreator:
    """
    A class for creating cover letters based on job descriptions and resume data.

    This class handles the process of cover letter generation, including
    content creation, PDF generation, and database storage.

    Attributes:
        runner: An instance of the AI model runner.
        json_loader (JsonLoader): An instance of JsonLoader for loading personal information.
        prompt_loader (PromptLoader): An instance of PromptLoader for loading prompts.
        logger (logging.Logger): A logger instance for logging operations.
        db_manager (DatabaseManager): An instance of DatabaseManager for database operations.
    """

    def __init__(self, runner: Any, json_loader: JsonLoader, prompt_loader: PromptLoader, db_manager: DatabaseManager):
        """
        Initialize the CoverLetterCreator with necessary components.

        Args:
            runner: An instance of the AI model runner.
            json_loader (JsonLoader): An instance of JsonLoader.
            prompt_loader (PromptLoader): An instance of PromptLoader.
            db_manager (DatabaseManager): An instance of DatabaseManager.
        """
        self.runner = runner
        self.json_loader = json_loader
        self.prompt_loader = prompt_loader
        self.logger = logging.getLogger(__name__)
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
        self.logger.info(f"Starting cover letter generation for resume ID: {resume_id}")
        
        if not job_description:
            self.logger.warning("Job description not provided")
            return "Please enter a job description."

        self.logger.info(f"Generating cover letter with {self.runner.__class__.__name__} model: {self.runner.model}")

        # Get resume data
        self.logger.info(f"Fetching resume data for ID: {resume_id}")
        resume_data = self.db_manager.get_resume(resume_id)
        self.logger.info(f"Resume data type: {type(resume_data)}")
        self.logger.debug(f"Resume data content: {resume_data}")
        
        if not resume_data:
            self.logger.error(f"Resume with ID {resume_id} not found")
            return f"Error: Resume with ID {resume_id} not found"

        # Ensure resume_data is a string
        self.logger.info("Ensuring resume_data is a string")
        if isinstance(resume_data, dict):
            self.logger.info("Converting resume_data dict to JSON string")
            resume_data = json.dumps(resume_data)
        elif isinstance(resume_data, bytes):
            self.logger.info("Converting resume_data bytes to string")
            resume_data = resume_data.decode('utf-8')
            # Try to parse it as JSON, if it fails, use it as is
            try:
                json.loads(resume_data)
            except json.JSONDecodeError:
                self.logger.info("resume_data is not valid JSON, using as plain text")
        elif not isinstance(resume_data, str):
            self.logger.error(f"Unexpected resume_data type: {type(resume_data)}")
            resume_data = json.dumps({})  # Convert to empty JSON string as fallback

        self.logger.info("Fetching cover letter prompt")
        cover_letter_prompt = self.prompt_loader.get_cover_letter_prompt()
        self.logger.info("Processing cover letter with AI model")
        try:
            cover_letter_content = self.runner.process_cover_letter(cover_letter_prompt, resume_data, job_description)
        except Exception as e:
            self.logger.error(f"Error processing cover letter: {str(e)}")
            return f"Error: Failed to process cover letter. Please check the logs for more details."

        # Generate PDF
        output_dir = os.path.join("created_resumes", f"{company_name}_{job_title}")
        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(f"Created output directory: {output_dir}")
        
        pdf_content = None
        latex_content = None
        
        try:
            self.logger.info("Generating cover letter PDF")
            pdf_content, latex_content = generate_cover_letter_pdf(
                self.db_manager, 
                cover_letter_content,
                resume_id,
                output_dir,
                company_name,
                job_title,
                self.json_loader
            )
            self.logger.info("PDF generation successful")
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            # Even if PDF generation fails, we still have the LaTeX content
            latex_content = cover_letter_content

        # Update resume with cover letter
        try:
            self.db_manager.update_cover_letter(resume_id, latex_content, pdf_content)
            self.logger.info("Cover letter updated in database successfully")
            if pdf_content:
                return f"Cover letter generated and saved successfully for resume ID: {resume_id}"
            else:
                return f"Cover letter content saved, but PDF generation failed for resume ID: {resume_id}"
        except Exception as e:
            self.logger.error(f"Error updating cover letter in database: {str(e)}")
            return f"Error: Failed to update cover letter in database. Please check the logs for more details."
