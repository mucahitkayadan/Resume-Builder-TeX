from engine.resume_creator import ResumeCreator
from utils.database_manager import DatabaseManager
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader

class ResumeGenerator:
    def __init__(self, db_manager, json_loader, prompt_loader, runner):
        self.resume_creator = ResumeCreator(runner, json_loader, prompt_loader, db_manager)

    def generate_resume(self, job_description, company_name, job_title):
        # You'll need to adapt this method to match your existing ResumeCreator implementation
        return self.resume_creator.generate_resume(
            job_description,
            company_name,
            job_title,
            "OpenAI",  # Assuming OpenAI model, adjust as needed
            "gpt-4",   # Adjust model name as needed
            0.7,       # Adjust temperature as needed
            {
                "personal_information": "process",
                "career_summary": "process",
                "skills": "process",
                "work_experience": "process",
                "education": "process",
                "projects": "process",
            }
        )

