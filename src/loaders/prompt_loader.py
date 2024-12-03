# Testing is done - Successful
from string import Template
from typing import Dict, Any, Optional
from config.settings import PROMPTS_DIR
from src.core.database.factory import get_unit_of_work


class PromptLoader:
    """
    A class to load prompts from a specified directory.
    """

    def __init__(self):
        """
        Initialize the PromptLoader with a base directory path and unit of work.
        """
        self.prompt_dir = PROMPTS_DIR
        self.uow = get_unit_of_work()

    def _load_prompt(self, filename: str, user_id: Optional[str] = None) -> str:
        """
        Load and format a prompt file with user preferences if available.
        
        Args:
            filename: The name of the file to load
            user_id: Optional user ID to load preferences
            
        Returns:
            Formatted prompt string
        """
        prompt_path = self.prompt_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
            
        with open(prompt_path, 'r', encoding='utf-8') as f:
            template = Template(f.read().strip())
            
        # Get user preferences if user_id is provided
        variables = {}
        if user_id:
            with self.uow as uow:
                preferences = uow.users.get_preferences(user_id)
                if preferences:
                    # Flatten nested dictionary
                    for category, values in preferences.items():
                        if isinstance(values, dict):
                            for key, value in values.items():
                                variables[f"{category}_{key}"] = value
                        else:
                            variables[category] = values
                            
        return template.safe_substitute(variables)

    def get_section_prompt(self, section: str, user_id: Optional[str] = None) -> str:
        """
        Get the prompt for a specific section with user preferences.
        
        Args:
            section (str): The section name (e.g. 'career_summary', 'skills')
            user_id: Optional user ID to load preferences
            
        Returns:
            str: The prompt text for the specified section
        """
        filename = f"{section.lower()}_prompt.txt"
        return self._load_prompt(filename, user_id)

    def get_system_prompt(self):
        return self._load_prompt('system_prompt.txt')

    def get_folder_name_prompt(self):
        return self._load_prompt('folder_name_prompt.txt')

    def get_cover_letter_prompt(self, user_id: str) -> str:
        """
        Get the cover letter prompt with user's life story.
        
        Args:
            user_id: The user ID to load preferences
            
        Returns:
            str: The cover letter prompt with user's life story
        """
        prompt = self._load_prompt('cover_letter_prompt.txt', user_id)
        
        # Add life story if available
        with self.uow as uow:
            life_story = uow.users.get_life_story(user_id)
            if life_story:
                # Replace the hardcoded life story with the user's story
                prompt = prompt.replace(
                    "SOME INFORMATION ABOUT ME:",
                    f"SOME INFORMATION ABOUT ME:\n{life_story}"
                )
        
        return prompt

if __name__ == '__main__':
    prompt_loader = PromptLoader()
    print(f"Resolved PROMPTS_FOLDER: {PROMPTS_DIR}")
    print(prompt_loader.get_section_prompt('skills'))
