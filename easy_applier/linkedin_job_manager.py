import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from src.core.database.unit_of_work import MongoUnitOfWork
from src.core.database.models.resume import Resume
from src.generator.utils.output_manager import OutputManager
from src.generator.utils.job_info import JobInfo
from easy_applier.job_extractor import JobExtractor
import logging

logger = logging.getLogger(__name__)


class LinkedInJobManager:
    def __init__(self, scraper, job_applier, resume_generator, unit_of_work: MongoUnitOfWork):
        self.scraper = scraper
        self.driver = scraper.driver
        self.job_applier = job_applier
        self.resume_generator = resume_generator
        self.uow = unit_of_work

    def save_resume(self, resume_content: dict, company_name: str, job_title: str) -> str:
        # Create Resume model instance
        resume = Resume(
            user_id='default_user',  # You might want to make this configurable
            company_name=company_name,
            job_title=job_title,
            **resume_content
        )

        # Save to database using unit of work
        with self.uow:
            self.uow.resumes.add(resume)

        # Create job info
        job_info = JobInfo(
            company_name=company_name,
            job_title=job_title
        )

        # Use OutputManager to handle file saving
        output_manager = OutputManager(job_info)
        resume_path = output_manager.save_resume_text(resume_content)
        
        return str(resume_path)

    async def run_job_search_and_apply(self, keywords: str, location: str, num_jobs: int, resumes: list, ai_strategy):
        self.scraper.search_jobs(keywords, location)
        jobs = self.scraper.get_job_details()

        for job, resume_content in zip(jobs[:num_jobs], resumes):
            # Save resume
            resume_path = self.save_resume(
                resume_content, 
                job['company'], 
                job['title']
            )

            # Apply to job
            success = await self.job_applier.apply_to_job(job['link'], resume_path)
            if success:
                print(f"Successfully applied to {job['title']} at {job['company']}")
            else:
                print(f"Failed to apply to {job['title']} at {job['company']}")

    def get_job_description(self, job_url: str) -> dict:
        """Get detailed job information from a job URL."""
        try:
            job_extractor = JobExtractor(self.driver)
            job_details = job_extractor.extract_job_details(job_url)
            if job_details:
                return job_details
            else:
                logger.error(f"Failed to extract job details from {job_url}")
                return None
        except Exception as e:
            logger.error(f"Error getting job description: {str(e)}")
            return None

    def search_and_get_job_descriptions(self, keywords: str, location: str, num_jobs: int) -> list:
        self.scraper.search_jobs(keywords, location)
        time.sleep(5)

        job_details_list = []
        try:
            job_cards = WebDriverWait(self.scraper.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-card-container"))
            )

            for i, card in enumerate(job_cards[:num_jobs]):
                try:
                    link = card.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    job_details = self.get_job_description(link)
                    
                    if job_details:
                        job_details_list.append(job_details)
                        print(f"Extracted job details {i+1}/{num_jobs}")
                        print("-" * 50)
                except Exception as e:
                    print(f"Error extracting job {i+1}: {str(e)}")

            return job_details_list
        except Exception as e:
            print(f"Failed to get job listings: {str(e)}")
            return []

    def extract_company_and_title(self, job_description):
        # This is a simple implementation. You might want to use more sophisticated
        # methods like regex or NLP to extract company name and job title accurately.
        lines = job_description.split('\n')
        company_name = lines[1] if len(lines) > 1 else "Unknown Company"
        job_title = lines[0] if len(lines) > 0 else "Unknown Position"
        return company_name, job_title
