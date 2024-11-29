from src.core.database.unit_of_work import MongoUnitOfWork
from src.core.dto.portfolio.portfolio import PortfolioDTO
from src.latex.utils.latex_escaper import LatexEscaper
from typing import Dict, Generator, Tuple

class ResumeGenerator:
    def __init__(self, unit_of_work: MongoUnitOfWork, ai_runner):
        self.uow = unit_of_work
        self.ai_runner = ai_runner
        self.latex_escaper = LatexEscaper()

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
        # Get portfolio from database
        with self.uow:
            portfolio = self.uow.portfolio.get_by_user_id('default_user')  # Make configurable
            if not portfolio:
                raise ValueError("No portfolio found for user")
            
            # Convert to DTO
            portfolio_dto = PortfolioDTO.from_db_model(portfolio, self.latex_escaper)

        # Generate resume using AI runner
        for update, progress in self.ai_runner.generate_resume(
            portfolio_dto,
            job_description,
            company_name,
            job_title,
            model_type,
            model_name,
            temperature,
            selected_sections
        ):
            yield update, progress

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
