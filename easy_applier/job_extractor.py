from linkedin_api import Linkedin
import logging
from typing import Optional, List, Dict
import time

logger = logging.getLogger(__name__)

class JobExtractor:
    def __init__(self, username: str, password: str):
        """
        Initialize JobExtractor with LinkedIn API
        
        Args:
            username: LinkedIn account email/username
            password: LinkedIn account password
        """
        try:
            self.api = Linkedin(username, password)
            logger.info("Successfully initialized LinkedIn API")
        except Exception as e:
            logger.error(f"Failed to initialize LinkedIn API: {str(e)}")
            raise

    def search_jobs(self, keywords: str, location: str, num_jobs: int = 25) -> List[Dict]:
        """
        Search for jobs using LinkedIn's API
        
        Args:
            keywords: Job search keywords
            location: Location for job search
            num_jobs: Number of jobs to fetch
        """
        try:
            jobs = []
            search_results = self.api.search_jobs(
                keywords=keywords,
                location_name=location,
                limit=num_jobs,
                experience=["2", "3", "4"],  # Entry to Senior level
                job_type=["F", "C"],  # Full-time and Contract
                remote=["1", "2", "3"]  # On-site, Remote, Hybrid
            )

            for job_result in search_results:
                try:
                    # Get detailed job information
                    job_id = job_result.get('job_id') or job_result.get('trackingUrn').split(':')[-1]
                    job_details = self.extract_job_details(job_id)
                    
                    if job_details:
                        jobs.append(job_details)
                        logger.info(f"Extracted job {len(jobs)}/{num_jobs}")
                    
                    # Add a small delay between requests
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error extracting job details: {str(e)}")
                    continue

            return jobs

        except Exception as e:
            logger.error(f"Error during job search: {str(e)}")
            return []

    def extract_job_details(self, job_id_or_url: str) -> Optional[Dict]:
        """
        Extract detailed job information using LinkedIn's API
        
        Args:
            job_id_or_url: LinkedIn job ID or full URL
        """
        try:
            # Extract job ID from URL if a URL is provided
            job_id = self._extract_job_id(job_id_or_url)
            if not job_id:
                logger.error(f"Could not extract job ID from: {job_id_or_url}")
                return None

            # Get job details
            job_data = self.api.get_job(job_id)
            
            # Get job skills (optional)
            try:
                job_skills = self.api.get_job_skills(job_id)
            except:
                job_skills = None

            if not job_data:
                return None

            # Extract relevant information
            return {
                'job_id': job_id,
                'title': job_data.get('title', ''),
                'company': job_data.get('companyDetails', {}).get('company', ''),
                'location': job_data.get('formattedLocation', ''),
                'description': job_data.get('description', {}).get('text', ''),
                'skills': job_skills.get('skills', []) if job_skills else [],
                'url': f"https://www.linkedin.com/jobs/view/{job_id}/",
                'source': 'LinkedIn',
                'employment_type': job_data.get('employmentType', ''),
                'seniority_level': job_data.get('seniorityLevel', ''),
                'posted_at': job_data.get('listedAt', ''),
            }

        except Exception as e:
            logger.error(f"Error extracting job details for {job_id_or_url}: {str(e)}")
            return None

    def _extract_job_id(self, job_id_or_url: str) -> Optional[str]:
        """
        Extract job ID from various LinkedIn URL formats or return the ID if already provided
        
        Args:
            job_id_or_url: Job ID or URL containing the job ID
        """
        try:
            # If it's already a job ID (just numbers)
            if job_id_or_url.isdigit():
                return job_id_or_url

            # Handle different URL formats
            if 'linkedin.com' in job_id_or_url.lower():
                # Format 1: /jobs/collections/recommended/?currentJobId=4098825071
                if 'currentJobId=' in job_id_or_url:
                    job_id = job_id_or_url.split('currentJobId=')[1].split('&')[0]
                    return job_id

                # Format 2: /jobs/view/4100040436/
                if '/jobs/view/' in job_id_or_url:
                    job_id = job_id_or_url.split('/jobs/view/')[1].split('/')[0].split('?')[0]
                    return job_id

                # Add more URL patterns as needed

            logger.warning(f"Could not extract job ID from: {job_id_or_url}")
            return None

        except Exception as e:
            logger.error(f"Error extracting job ID from {job_id_or_url}: {str(e)}")
            return None


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    from config.config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
    
    extractor = JobExtractor(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)

    job = extractor.extract_job_details("https://www.linkedin.com/jobs/collections/hiring-in-network/?currentJobId=4098985472&discover=top-applicant%2Chiring-in-network&discoveryOrigin=JOBS_HOME_COMPETITIVE_ADVANTAGE_JOB_COLLECTIONS")
    print(job)
    # jobs = extractor.search_jobs(
    #     keywords="Python Developer",
    #     location="Remote",
    #     num_jobs=5
    # )
    #
    # # Print results
    # for job in jobs:
    #     print(f"\nJob: {job['title']}")
    #     print(f"Company: {job['company']}")
    #     print(f"Location: {job['location']}")
    #     print(f"Skills: {', '.join(job['skills'])}")
    #     print(f"URL: {job['url']}")
    #     print("-" * 50)
