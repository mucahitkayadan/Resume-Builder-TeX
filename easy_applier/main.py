from easy_applier.linkedin_scraper import LinkedInScraper
from easy_applier.resume_generator import ResumeGenerator
from easy_applier.job_applier import JobApplier
from easy_applier.utils import create_output_directory, get_latest_resume_path
from utils.database_manager import DatabaseManager
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.runners import OpenAIRunner

def main():
    # Initialize components
    db_manager = DatabaseManager()
    json_loader = JsonLoader("files/information.json")
    prompt_loader = PromptLoader("prompts/")
    runner = OpenAIRunner("gpt-4", 0.7, prompt_loader.get_system_prompt())

    resume_generator = ResumeGenerator(db_manager, json_loader, prompt_loader, runner)
    
    # LinkedIn credentials (consider using environment variables for security)
    linkedin_email = "your_email@example.com"
    linkedin_password = "your_password"

    # Initialize LinkedIn scraper
    scraper = LinkedInScraper(linkedin_email, linkedin_password)
    scraper.login()

    # Search for jobs
    scraper.search_jobs("Software Engineer", "San Francisco, CA")
    jobs = scraper.get_job_details()

    # Process each job
    for job in jobs:
        # Generate resume
        output_dir = create_output_directory(job['company'], job['title'])
        resume_generator.generate_resume(job['description'], job['company'], job['title'])

        # Get the path of the generated resume
        resume_path = get_latest_resume_path(output_dir)

        if resume_path:
            # Apply to the job
            applier = JobApplier(scraper.driver)
            success = applier.apply_to_job(job['link'], resume_path)
            if success:
                print(f"Successfully applied to {job['title']} at {job['company']}")
            else:
                print(f"Failed to apply to {job['title']} at {job['company']}")
        else:
            print(f"Failed to generate resume for {job['title']} at {job['company']}")

    # Clean up
    scraper.close()

if __name__ == "__main__":
    main()

