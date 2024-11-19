from __legacy__.engine import ResumeCreator
from __legacy__.database_manager import DatabaseManager
from __legacy__.json_loader import JsonLoader
from src.loaders.prompt_loader import PromptLoader
from __legacy__.engine import AIRunner
from typing import Dict, Generator, Tuple

class ResumeGenerator:
    def __init__(self, db_manager: DatabaseManager, json_loader: JsonLoader, prompt_loader: PromptLoader, ai_runner: AIRunner):
        self.resume_creator = ResumeCreator(ai_runner, json_loader, prompt_loader, db_manager)

    def generate_resume(
        self, 
        job_description: str, 
        company_name: str, 
        job_title: str,
        model_type: str,
        model_name: str,
        temperature: float,
        selected_sections: Dict[str, str]
    ) -> Generator[Tuple[str, float], None, None]:
        return self.resume_creator.generate_resume(
            job_description,
            company_name,
            job_title,
            model_type,
            model_name,
            temperature,
            selected_sections
        )

    def process_resume_generation(
        self, 
        job_description: str, 
        company_name: str, 
        job_title: str,
        model_type: str,
        model_name: str,
        temperature: float,
        selected_sections: Dict[str, str] = None
    ) -> Dict[str, str]:
        if selected_sections is None:
            selected_sections = {
                "personal_information": "process",
                "career_summary": "process",
                "skills": "process",
                "work_experience": "process",
                "education": "process",
                "projects": "process",
                "awards": "hardcode",
                "publications": "hardcode"
            }

        resume_content = {}
        for update, progress in self.generate_resume(
            job_description, 
            company_name, 
            job_title,
            model_type,
            model_name,
            temperature,
            selected_sections
        ):
            print(f"Progress: {progress * 100:.2f}% - {update}")
            
            if ':' in update:
                section, content = update.split(':', 1)
                resume_content[section.strip()] = content.strip()

        return resume_content
