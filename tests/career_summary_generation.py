import sys
from pathlib import Path
import logging

# Add project root to Python path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)

from __legacy__.engine import ResumeCreator
from __legacy__.engine import AIRunner
from __legacy__.engine import ClaudeStrategy
from src.loaders.prompt_loader import PromptLoader
from src.core.database.factory import get_unit_of_work

# Reference to config.py for logging setup

def career_summary_generation():
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    # Initialize components
    uow = get_unit_of_work()
    prompt_loader = PromptLoader("../prompts")
    ai_runner = AIRunner(ClaudeStrategy(prompt_loader.get_system_prompt()))

    # Initialize ResumeCreator
    resume_creator = ResumeCreator(ai_runner, prompt_loader, uow)

    with uow:
        # Get the latest resume
        latest_resume = uow.resumes.get_latest_resume()
        if not latest_resume:
            logger.error("No resume found in database")
            return

        # Get user's portfolio
        portfolio = uow.portfolios.get_by_user_id(latest_resume.user_id)
        if not portfolio:
            logger.error("No portfolio found for user")
            return

        # Process career summary
        try:
            career_summary = resume_creator.process_section(
                section="career_summary",
                process_type="process",
                job_description=latest_resume.job_description,
                user_id=latest_resume.user_id
            )
            
            print("\n=== Generated Career Summary ===")
            print(f"Job Description: {latest_resume.job_description[:200]}...")
            print("\nGenerated Summary:")
            print(career_summary)
            print("\nOriginal Portfolio Career Summary Data:")
            print(f"Job Titles: {portfolio.career_summary.job_titles}")
            print(f"Years of Experience: {portfolio.career_summary.years_of_experience}")
            print(f"Default Summary: {portfolio.career_summary.default_summary}")
            
        except Exception as e:
            logger.error(f"Error generating career summary: {str(e)}")

if __name__ == "__main__":
    career_summary_generation()
