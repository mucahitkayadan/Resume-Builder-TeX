import sys
import os
import logging
import psutil
import asyncio

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from easy_applier.job_applier import JobApplier
from easy_applier.linkedin_scraper import LinkedInScraper
from easy_applier.linkedin_job_manager import LinkedInJobManager
from src.resume.resume_generator import ResumeGenerator
from src.core.database.factory import get_unit_of_work
from src.llms.strategies import OpenAIStrategy, ClaudeStrategy, OllamaStrategy, GeminiStrategy
from config.config import (
    LINKEDIN_EMAIL,
    LINKEDIN_PASSWORD,
)
from config.settings import APP_CONSTANTS
from config.llm_config import LLMConfig

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def kill_chrome_processes():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['chrome.exe', 'chromedriver.exe']:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

async def generate_resume_async(resume_generator, job_description, company_name, job_title):
    try:
        return await resume_generator.generate_resume(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title
        )
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return None

async def main():
    # Load environment variables
    load_dotenv()

    # Initialize database connection
    unit_of_work = get_unit_of_work()

    # Initialize LLM configuration
    llm_config = LLMConfig()
    
    # Initialize LLM strategy
    system_instruction = "You are an AI assistant helping to generate resumes and cover letters."
    
    # Use OpenAI by default
    llm_strategy = OpenAIStrategy(system_instruction)
    llm_strategy.model = llm_config.OPENAI_MODEL.name
    llm_strategy.temperature = llm_config.OPENAI_MODEL.default_temperature

    # Initialize resume generator
    resume_generator = ResumeGenerator(unit_of_work, llm_strategy)
    
    # Get LinkedIn credentials
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        raise ValueError("LinkedIn credentials not found in configuration")

    # Initialize LinkedIn scraper
    scraper = LinkedInScraper(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
    scraper.login()

    # Initialize JobApplier and LinkedInJobManager
    job_applier = JobApplier(scraper.driver, unit_of_work)
    job_manager = LinkedInJobManager(scraper, job_applier, resume_generator, unit_of_work)

    # Set job search parameters
    keywords = "Software Engineer"
    location = "San Francisco, CA"
    num_jobs = 10

    # Search for jobs and get job descriptions
    job_descriptions = job_manager.search_and_get_job_descriptions(keywords, location, num_jobs)

    if not job_descriptions:
        logger.error("No job descriptions found. Exiting.")
        return

    # Create tasks for resume generation
    tasks = []
    for i, job_description in enumerate(job_descriptions):
        logger.info(f"Preparing resume generation for job {i+1}/{len(job_descriptions)}")
        company_name, job_title = job_manager.extract_company_and_title(job_description)
        
        task = generate_resume_async(
            resume_generator,
            job_description,
            company_name,
            job_title
        )
        tasks.append(task)

    # Wait for all resume generation tasks to complete
    try:
        resumes = await asyncio.gather(*tasks)
        
        # Process the generated resumes
        for i, resume_content in enumerate(resumes):
            if resume_content:
                logger.info(f"Resume generated for job {i+1}/{len(job_descriptions)}")
            else:
                logger.warning(f"Failed to generate resume for job {i+1}")
                
    except Exception as e:
        logger.error(f"Error during resume generation: {str(e)}")

    logger.info("Job search and resume generation completed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
