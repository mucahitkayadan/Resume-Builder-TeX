import os
import logging
from utils.database_manager import DatabaseManager
from loaders.tex_loader import TexLoader

class CoverLetterCreator:
    def __init__(self, runner, json_loader, prompt_loader):
        self.runner = runner
        self.json_loader = json_loader
        self.prompt_loader = prompt_loader
        self.logger = logging.getLogger(__name__)
        self.db_manager = DatabaseManager()

    def generate_cover_letter(self, job_description):
        if not job_description:
            self.logger.warning("Job description not provided")
            return "Please enter a job description."

        self.logger.info(f"Generating cover letter with {self.runner.runner_type} model: {self.runner.model}")

        cover_letter_prompt = self.prompt_loader.get_cover_letter_prompt()
        resume_content = self.json_loader.get_all_data()  # Get all resume data
        cover_letter_content = self.runner.process_cover_letter(cover_letter_prompt, str(resume_content), job_description)

        # Get company name and job title
        folder_name_prompt = self.prompt_loader.get_folder_name_prompt()
        company_name, job_title = self.runner.create_folder_name(folder_name_prompt, job_description)

        # Insert into database
        resume_id = self.db_manager.insert_resume(company_name, job_title, {}, cover_letter_content)

        return f"Cover letter generated successfully with ID: {resume_id}"