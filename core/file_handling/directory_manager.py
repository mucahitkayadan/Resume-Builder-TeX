import os
import shutil
from typing import Optional, List
from datetime import datetime

class DirectoryManager:
    """Handles directory creation and management"""
    
    def __init__(self, base_dir: str = "created_resumes"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)
    
    def create_output_directory(self, company_name: str, job_title: str) -> str:
        """Create and return path to output directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{company_name}_{job_title}_{timestamp}".replace(" ", "_")
        output_dir = os.path.join(self.base_dir, folder_name)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def save_job_description(self, job_description: str, output_dir: str) -> str:
        """Save job description to file"""
        file_path = os.path.join(output_dir, "job_description.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(job_description)
        return file_path
    
    def get_latest_resume_path(self, output_dir: str) -> Optional[str]:
        """Get path to the latest resume in directory"""
        pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
        if not pdf_files:
            return None
        return os.path.join(output_dir, max(pdf_files))
    
    def cleanup_old_files(self, days: int = 30) -> None:
        """Remove directories older than specified days"""
        current_time = datetime.now()
        for dir_name in os.listdir(self.base_dir):
            dir_path = os.path.join(self.base_dir, dir_name)
            if not os.path.isdir(dir_path):
                continue
                
            dir_time = datetime.fromtimestamp(os.path.getctime(dir_path))
            if (current_time - dir_time).days > days:
                shutil.rmtree(dir_path)