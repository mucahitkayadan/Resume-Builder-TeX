import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from easy_applier.linkedin_scraper import LinkedInScraper
from easy_applier.job_applier import JobApplier
from easy_applier.resume_generator import ResumeGenerator
from utils.file_operations import create_output_directory
from utils.database_manager import DatabaseManager
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.runners import AIRunner

class LinkedInJobManager:
    def __init__(self, scraper, job_applier, resume_generator):
        self.scraper = scraper
        self.driver = scraper.driver
        self.job_applier = job_applier
        self.resume_generator = resume_generator

    def save_resume(self, resume_content, output_dir, company_name, job_title):
        # This is a simple text-based save function. 
        # You might want to replace this with a function that generates a PDF using LaTeX.
        resume_filename = f"resume_{company_name}_{job_title}.txt".replace(" ", "_")
        resume_path = os.path.join(output_dir, resume_filename)
        
        with open(resume_path, "w") as f:
            for section, content in resume_content.items():
                f.write(f"{section}:\n{content}\n\n")
        
        return resume_path

    async def run_job_search_and_apply(self, keywords, location, num_jobs, resumes, ai_strategy):
        self.scraper.search_jobs(keywords, location)
        jobs = self.scraper.get_job_details()

        for job, resume_content in zip(jobs[:num_jobs], resumes):
            # Save the tailored resume
            output_dir = create_output_directory(job['company'], job['title'])
            resume_path = self.save_resume(resume_content, output_dir, job['company'], job['title'])

            # Apply to the job
            success = await self.job_applier.apply_to_job(job['link'], resume_path)
            if success:
                print(f"Successfully applied to {job['title']} at {job['company']}")
            else:
                print(f"Failed to apply to {job['title']} at {job['company']}")

    def search_and_get_job_descriptions(self, keywords, location, num_jobs):
        self.scraper.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={keywords}&location={location}")
        time.sleep(5)  # Wait for page to load

        job_descriptions = []
        for i in range(num_jobs):
            try:
                # Click on job listing
                job_listings = WebDriverWait(self.scraper.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".job-card-container"))
                )
                if i < len(job_listings):
                    job_listings[i].click()
                    time.sleep(2)  # Wait for job details to load

                    # Extract job description
                    job_description = WebDriverWait(self.scraper.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".job-view-layout"))
                    ).text

                    job_descriptions.append(job_description)
                    print(f"Extracted job description for {i+1}:")
                    print(job_description[:500] + "..." if len(job_description) > 500 else job_description)
                    print("-" * 50)
                else:
                    break  # No more job listings found
            except Exception as e:
                print(f"Error extracting job description: {str(e)}")

        return job_descriptions

    def extract_company_and_title(self, job_description):
        # This is a simple implementation. You might want to use more sophisticated
        # methods like regex or NLP to extract company name and job title accurately.
        lines = job_description.split('\n')
        company_name = lines[1] if len(lines) > 1 else "Unknown Company"
        job_title = lines[0] if len(lines) > 0 else "Unknown Position"
        return company_name, job_title
