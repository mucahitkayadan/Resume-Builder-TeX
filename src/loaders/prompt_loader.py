# Testing is done - Successful
from config.settings import PROMPTS_FOLDER


class PromptLoader:
    """
    A class to load prompts from a specified directory.
    """

    def __init__(self):
        """
        Initialize the PromptLoader with a base directory path.
        """
        self.prompt_dir = PROMPTS_FOLDER

    def _load_prompt(self, filename: str) -> str:
        """Load the content of a prompt file.
        Args:
            filename (str): The name of the file to load.
        Returns:
            str: The content of the prompt file.
        """
        prompt_path = self.prompt_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
        return prompt

    def get_section_prompt(self, section: str) -> str:
        """
        Get the prompt for a specific section.
        
        Args:
            section (str): The section name (e.g. 'career_summary', 'skills')
            
        Returns:
            str: The prompt text for the specified section
        """
        filename = f"{section.lower()}_prompt.txt"
        return self._load_prompt(filename)

    def get_system_prompt(self):
        return self._load_prompt('system_prompt.txt')

    def get_folder_name_prompt(self):
        return self._load_prompt('folder_name_prompt.txt')

    def get_cover_letter_prompt(self):
        return self._load_prompt('cover_letter_prompt.txt')

if __name__ == '__main__':
    prompt_loader = PromptLoader()
    print(f"Resolved PROMPTS_FOLDER: {PROMPTS_FOLDER}")
    print(prompt_loader.get_section_prompt('skills'))
