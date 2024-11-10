import os
import sys
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from easy_applier.resume_generator import ResumeGenerator
from easy_applier.linkedin_scraper import LinkedInScraper
from easy_applier.linkedin_job_manager import LinkedInJobManager
from __legacy__.database_manager import DatabaseManager
from __legacy__.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.runners import AIRunner
from engine.ai_strategies import ClaudeStrategy

def test_linkedin_scraper():
    print("\n=== Testing LinkedIn Scraper ===")
    try:
        scraper = LinkedInScraper()
        test_url = "https://www.linkedin.com/jobs/view/123456789"
        job_info = scraper.scrape_job_posting(test_url)
        
        print(f"Job URL: {test_url}")
        print(f"Job Title: {job_info.get('title', 'N/A')}")
        print(f"Company: {job_info.get('company', 'N/A')}")
        print(f"Description Length: {len(job_info.get('description', ''))}")
        print("LinkedIn Scraper Test: PASSED")
    except Exception as e:
        print(f"LinkedIn Scraper Test: FAILED - {str(e)}")

def test_resume_generator():
    print("\n=== Testing Resume Generator ===")
    try:
        db_manager = DatabaseManager("../__legacy__/db/resumes.db")
        json_loader = JsonLoader("../__legacy__/files/information.json")
        prompt_loader = PromptLoader("../prompts")
        ai_strategy = ClaudeStrategy()
        ai_runner = AIRunner(ai_strategy)
        
        generator = ResumeGenerator(ai_runner, json_loader, prompt_loader, db_manager)
        
        test_job = {
            "description": "Looking for a Python developer with ML experience",
            "company": "Test Corp",
            "title": "Senior Developer"
        }
        
        result = generator.generate_resume(
            test_job["description"],
            test_job["company"],
            test_job["title"],
            "claude",
            "claude-3-sonnet",
            0.7,
            {"all": True}
        )
        
        print(f"Resume Generation Test:")
        print(f"Company: {test_job['company']}")
        print(f"Job Title: {test_job['title']}")
        print(f"Generated Resume Path: {result if result else 'None'}")
        print("Resume Generator Test: PASSED")
    except Exception as e:
        print(f"Resume Generator Test: FAILED - {str(e)}")

def test_job_manager():
    print("\n=== Testing LinkedIn Job Manager ===")
    try:
        manager = LinkedInJobManager()
        test_search = {
            "keywords": "python developer",
            "location": "United States",
            "remote": True
        }
        
        jobs = manager.search_jobs(**test_search)
        
        print(f"Search Parameters: {test_search}")
        print(f"Number of Jobs Found: {len(jobs)}")
        if jobs:
            print("\nFirst Job Details:")
            print(f"Title: {jobs[0].get('title', 'N/A')}")
            print(f"Company: {jobs[0].get('company', 'N/A')}")
            print(f"Location: {jobs[0].get('location', 'N/A')}")
        print("Job Manager Test: PASSED")
    except Exception as e:
        print(f"Job Manager Test: FAILED - {str(e)}")

def run_all_tests():
    print(f"Starting Easy Applier Tests at {datetime.now()}")
    print("=" * 50)
    
    test_linkedin_scraper()
    test_resume_generator()
    test_job_manager()
    
    print("\n" + "=" * 50)
    print(f"Tests completed at {datetime.now()}")

if __name__ == "__main__":
    run_all_tests()
