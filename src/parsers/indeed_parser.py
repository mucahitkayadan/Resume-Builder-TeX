"""Indeed job parser module."""

from typing import Dict, Optional

from bs4 import BeautifulSoup


def parse_indeed_job(html_content: str) -> Dict[str, Optional[str]]:
    """Parse Indeed job posting HTML.

    Args:
        html_content: HTML content of the job posting

    Returns:
        Dict[str, Optional[str]]: Parsed job data
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Initialize result dictionary
    job_data = {
        "title": None,
        "company": None,
        "location": None,
        "description": None,
        "salary": None,
        "job_type": None,
        "posted_date": None,
    }

    try:
        # Job title
        title_elem = soup.find("h1", {"class": "jobsearch-JobInfoHeader-title"})
        if title_elem:
            job_data["title"] = title_elem.get_text().strip()

        # Company name
        company_elem = soup.find("div", {"class": "jobsearch-InlineCompanyRating"})
        if company_elem:
            job_data["company"] = company_elem.find("a").get_text().strip()

        # Location
        location_elem = soup.find("div", {"class": "jobsearch-JobInfoHeader-subtitle"})
        if location_elem:
            job_data["location"] = location_elem.get_text().strip()

        # Job description
        description_elem = soup.find("div", {"id": "jobDescriptionText"})
        if description_elem:
            job_data["description"] = description_elem.get_text().strip()

        # Salary
        salary_elem = soup.find("span", {"class": "jobsearch-JobMetadataHeader-item"})
        if salary_elem:
            job_data["salary"] = salary_elem.get_text().strip()

        # Job type
        job_type_elem = soup.find("div", {"class": "jobsearch-JobMetadataHeader-item"})
        if job_type_elem:
            job_data["job_type"] = job_type_elem.get_text().strip()

        # Posted date
        date_elem = soup.find("span", {"class": "jobsearch-JobMetadataFooter-item"})
        if date_elem:
            job_data["posted_date"] = date_elem.get_text().strip()

    except Exception as e:
        print(f"Error parsing Indeed job: {str(e)}")

    return job_data
