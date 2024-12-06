import logging
from typing import List

logger = logging.getLogger(__name__)

def check_clearance_requirement(job_description: str, clearance_keywords: List[str]) -> bool:
    """
    Check if the job description contains keywords related to security clearance requirements.

    Args:
        job_description (str): The job description text
        clearance_keywords (List[str]): List of clearance-related keywords to check

    Returns:
        bool: True if clearance-related keywords are found, False otherwise
    """
    return any(keyword.lower() in job_description.lower() for keyword in clearance_keywords) 