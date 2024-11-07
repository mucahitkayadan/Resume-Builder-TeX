import sys
import os
import logging
import psutil
import asyncio

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from dotenv import load_dotenv
from easy_applier.resume_generator import ResumeGenerator
from easy_applier.job_applier import JobApplier
from easy_applier.linkedin_scraper import LinkedInScraper
from utils.database_manager import DatabaseManager
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.runners import AIRunner
from engine.ai_strategies import OpenAIStrategy
from easy_applier.linkedin_job_manager import LinkedInJobManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def kill_chrome_processes():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in ['chrome.exe', 'chromedriver.exe']:
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass

async def generate_resume_async(resume_generator, job_description, company_name, job_title, ai_strategy):
    try:
        return await asyncio.to_thread(
            resume_generator.process_resume_generation,
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            model_type=ai_strategy.__class__.__name__,
            model_name=ai_strategy.model,
            temperature=ai_strategy.temperature
        )
    except Exception as e:
        logger.error(f"Error generating resume: {str(e)}")
        return None

async def main():
    # Load environment variables
    load_dotenv()

    # Initialize components
    db_manager = DatabaseManager()
    json_loader = JsonLoader("../files/information.json")
    prompt_loader = PromptLoader("../prompts/")

    # Choose AI strategy
    ai_strategy = OpenAIStrategy(system_prompt=prompt_loader.get_system_prompt())
    ai_runner = AIRunner(ai_strategy)

    resume_generator = ResumeGenerator(db_manager, json_loader, prompt_loader, ai_runner)
    
    # Get LinkedIn credentials
    linkedin_email = os.getenv("LINKEDIN_EMAIL")
    linkedin_password = os.getenv("LINKEDIN_PASSWORD")

    if not linkedin_email or not linkedin_password:
        raise ValueError("LinkedIn credentials not found in .env file")

    # Initialize LinkedIn scraper
    scraper = LinkedInScraper(linkedin_email, linkedin_password)
    scraper.login()

    # Initialize JobApplier and LinkedInJobManager
    job_applier = JobApplier(scraper.driver)
    job_manager = LinkedInJobManager(scraper, job_applier, resume_generator)

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
            job_title,
            ai_strategy
        )
        tasks.append(task)

    # Wait for all resume generation tasks to complete
    try:
        resumes = await asyncio.gather(*tasks)
        
        # Process the generated resumes
        for i, resume_content in enumerate(resumes):
            if resume_content:
                logger.info(f"Resume generated for job {i+1}/{len(job_descriptions)}")
                # Here you can save or further process the resume_content
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
