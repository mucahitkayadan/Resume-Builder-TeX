import os
import logging
import subprocess
import json
from utils.database_manager import DatabaseManager
from loaders.tex_loader import TexLoader
from utils.latex_compiler import generate_cover_letter_pdf  # Add this import at the top of the file

class CoverLetterCreator:
    def __init__(self, runner, json_loader, prompt_loader, db_manager):
        self.runner = runner
        self.json_loader = json_loader
        self.prompt_loader = prompt_loader
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager

    def generate_cover_letter(self, job_description, resume_id, company_name, job_title):
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
        elif not isinstance(resume_data, str):
            self.logger.error(f"Unexpected resume_data type: {type(resume_data)}")
            resume_data = json.dumps({})  # Convert to empty JSON string as fallback
        self.logger.info(f"Resume data type after conversion: {type(resume_data)}")
        self.logger.debug(f"Resume data content (first 100 chars): {resume_data[:100]}...")

        self.logger.info("Fetching cover letter prompt")
        cover_letter_prompt = self.prompt_loader.get_cover_letter_prompt()
        self.logger.info("Processing cover letter with AI model")
        cover_letter_content = self.runner.process_cover_letter(cover_letter_prompt, resume_data, job_description)

        # Generate PDF
        output_dir = os.path.join("created_resumes", f"{company_name}_{job_title}")
        os.makedirs(output_dir, exist_ok=True)
        self.logger.info(f"Created output directory: {output_dir}")
        
        try:
            self.logger.info("Generating cover letter PDF")
            pdf_content = generate_cover_letter_pdf(
                self.db_manager, 
                cover_letter_content, 
                resume_id,
                output_dir,
                company_name,
                job_title,
                self.json_loader  # Pass the JsonLoader instance
            )
            self.logger.info("PDF generation successful")
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            return f"Error: Failed to generate PDF. Please check the logs for more details."

        # Update resume with cover letter
        try:
            self.db_manager.update_cover_letter(resume_id, cover_letter_content, pdf_content)
        except Exception as e:
            self.logger.error(f"Error updating cover letter in database: {str(e)}")
            return f"Error: Failed to update cover letter in database. Please check the logs for more details."

        return f"Cover letter generated successfully for resume ID: {resume_id}"