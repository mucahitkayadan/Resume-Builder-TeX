from pathlib import Path
from config.settings import OUTPUT_FOLDER
import shutil

class OutputManager:
    def __init__(self, company_name: str, job_title: str):
        self.company_name = company_name
        self.job_title = job_title
        self.output_dir = self._create_output_directory()

    def _create_output_directory(self) -> Path:
        """Create and return the output directory path."""
        # Create a safe directory name from company and job title
        safe_name = f"{self.company_name}_{self.job_title}".replace(' ', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '_-')
        
        # Create unique directory
        output_dir = OUTPUT_FOLDER / safe_name
        counter = 1
        while output_dir.exists():
            output_dir = OUTPUT_FOLDER / f"{safe_name}_{counter}"
            counter += 1
            
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def get_resume_path(self) -> Path:
        """Get path for resume file."""
        return self.output_dir / "resume.tex"

    def get_cover_letter_path(self) -> Path:
        """Get path for cover letter file."""
        return self.output_dir / "cover_letter.tex"

    def save_job_description(self, content: str) -> None:
        """Save job description to output directory."""
        job_desc_path = self.output_dir / "job_description.txt"
        job_desc_path.write_text(content, encoding='utf-8')

    def cleanup(self) -> None:
        """Clean up the output directory if something goes wrong."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
