import os
from typing import Optional

class PromptLoader:
    """
    A class for loading prompt files from a specified base path.
    """

    def __init__(self, prompt_dir):
        """
        Initialize the PromptLoader with a base path.

        Args:
            prompt_dir (str): The base directory path where prompt files are stored.
        """
        self.prompt_dir = prompt_dir

    def _load_prompt(self, filename):
        with open(os.path.join(self.prompt_dir, filename), 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
        return prompt

    def get_header_prompt(self) -> str:
        """Get the prompt for the header section."""
        return self._load_prompt("header_prompt.txt")

    def get_career_summary_prompt(self) -> str:
        """Get the prompt for the career summary section."""
        return self._load_prompt("career_summary_prompt.txt")

    def get_skills_prompt(self) -> str:
        """Get the prompt for the skills section."""
        return self._load_prompt("skills_prompt.txt")

    def get_work_experience_prompt(self) -> str:
        """Get the prompt for the work experience section."""
        return self._load_prompt("work_experience_prompt.txt")

    def get_education_prompt(self) -> str:
        """Get the prompt for the education section."""
        return self._load_prompt("education_prompt.txt")

    def get_projects_prompt(self) -> str:
        """Get the prompt for the projects section."""
        return self._load_prompt("projects_prompt.txt")

    def get_awards_prompt(self) -> str:
        """Get the prompt for the awards section."""
        return self._load_prompt("awards_prompt.txt")

    def get_publications_prompt(self) -> str:
        """Get the prompt for the publications section."""
        return self._load_prompt("publications_prompt.txt")

    def get_personal_information_prompt(self):
        return self._load_prompt('personal_information_prompt.txt')

    def get_job_titles_prompt(self):
        return self._load_prompt('job_titles_prompt.txt')
