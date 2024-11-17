import os
from pathlib import Path
import logging
from config.settings import OUTPUT_FOLDER
from .string_utils import sanitize_filename

logger = logging.getLogger(__name__)


def create_output_directory(company_name: str, job_title: str) -> Path:
    """
    Create an output directory for storing generated files.

    Args:
        company_name (str): Name of the company
        job_title (str): Title of the job position

    Returns:
        Path: Path to the created output directory
    """
    # Sanitize both company name and job title
    safe_company = sanitize_filename(company_name.lower())
    safe_job = sanitize_filename(job_title.lower())
    
    # Create folder name
    folder_name = f"{safe_company}_{safe_job}"
    
    # Use OUTPUT_FOLDER from settings
    output_dir = OUTPUT_FOLDER / folder_name
    
    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Created output directory: {output_dir}")
    
    return output_dir

def save_job_description(job_description: str, output_dir: Path) -> None:
    """Save job description to a text file in the output directory."""
    file_path = output_dir / 'job_description.txt'
    file_path.write_text(job_description, encoding='utf-8')
    logger.debug(f"Saved job description to: {file_path}")