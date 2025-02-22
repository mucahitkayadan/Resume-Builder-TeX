import shutil
from pathlib import Path

from config.settings import OUTPUT_DIR

from .job_info import JobInfo
from .string_utils import sanitize_filename


class OutputManager:
    def __init__(self, job_info: JobInfo):
        self.job_info = job_info
        self.output_dir = self._create_output_directory()

    def _create_output_directory(self) -> Path:
        """Create and return the output directory path."""
        safe_company = sanitize_filename(self.job_info.company_name)
        safe_job = sanitize_filename(self.job_info.job_title)
        folder_name = f"{safe_company}_{safe_job}"

        output_dir = OUTPUT_DIR / folder_name
        counter = 1
        while output_dir.exists():
            output_dir = OUTPUT_DIR / f"{folder_name}_{counter}"
            counter += 1

        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_job_info(self) -> JobInfo:
        return self.job_info

    def get_resume_path(self) -> Path:
        """Get path for resume file."""
        return self.output_dir / "resume.tex"

    def get_cover_letter_path(self) -> Path:
        """Get path for cover letter file."""
        return self.output_dir / "cover_letter.tex"

    def save_job_description(self, content: str) -> None:
        """Save job description to output directory."""
        job_desc_path = self.output_dir / "job_description.txt"
        job_desc_path.write_text(content, encoding="utf-8")

    def cleanup(self) -> None:
        """Clean up the output directory if something goes wrong."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
