import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_output_directory(company_name: str, job_title: str) -> Path:
    """Create and return the output directory path for resume files."""
    output_dir = Path("created_resumes") / f"{company_name}_{job_title}"
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir

def save_job_description(job_description: str, output_dir: Path) -> None:
    """Save the job description to a text file."""
    job_desc_path = output_dir / "job_description.txt"
    try:
        job_desc_path.write_text(job_description)
        logger.info(f"Saved job description to: {job_desc_path}")
    except Exception as e:
        logger.error(f"Failed to save job description: {e}")
        raise 