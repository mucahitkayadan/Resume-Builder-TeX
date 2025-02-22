# Testing is done - Successful
import logging
from string import Template
from typing import Any, Dict, Optional

from config.config import test_user_id
from config.settings import PROMPTS_DIR
from src.core.database.factory import get_unit_of_work

logger = logging.getLogger(__name__)


class PromptLoader:
    """
    A class to load prompts from a specified directory.
    """

    def __init__(self, user_id: Optional[str] = None):
        """
        Initialize the PromptLoader with a base directory path and user_id.

        Args:
            user_id: Optional user ID (can be either user_id or _id)
        """
        self.prompt_dir = PROMPTS_DIR
        self.user_id = user_id
        self.uow = get_unit_of_work()
        self._preferences = None

    @property
    def preferences(self) -> Optional[Dict[str, Any]]:
        """Lazy load user preferences"""
        if self._preferences is None and self.user_id:
            try:
                with self.uow as uow:
                    user = uow.users.get_by_user_id(self.user_id)
                    if not user:
                        user = uow.users.get_by_id(self.user_id)
                    if user and user.preferences:
                        self._preferences = user.preferences.model_dump()
                        logger.debug(f"Loaded preferences: {self._preferences}")
            except Exception as e:
                logger.error(f"Error loading preferences for user {self.user_id}: {e}")
                self._preferences = None
        return self._preferences

    def _read_template_file(self, filename: str) -> Template:
        """Read and create a template from a file.

        Args:
            filename: Name of the file to read

        Returns:
            Template object created from file contents

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        prompt_path = self.prompt_dir / filename
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found at {prompt_path}")

        with open(prompt_path, "r", encoding="utf-8") as f:
            return Template(f.read().strip())

    def _get_preference_variables(self) -> Dict[str, Any]:
        """Get variables from user preferences.

        Returns:
            Dictionary of variables for template substitution
        """
        variables = {}
        if self.preferences:
            for category, values in self.preferences.items():
                if isinstance(values, dict):
                    for key, value in values.items():
                        variables[f"{category}_{key}"] = value
                else:
                    variables[category] = values
        return variables

    def _add_life_story(self, variables: Dict[str, Any]) -> None:
        """Add life story to variables if available.

        Args:
            variables: Dictionary to add life story to
        """
        try:
            with self.uow as uow:
                user = uow.users.get_by_user_id(self.user_id)
                if not user:
                    user = uow.users.get_by_id(self.user_id)
                if user and user.life_story:
                    variables["life_story"] = user.life_story
                else:
                    variables["life_story"] = "No personal story available."
        except Exception as e:
            logger.error(f"Error loading life story: {e}")
            variables["life_story"] = "No personal story available."

    def _load_prompt(self, filename: str) -> str:
        """
        Load and format a prompt file with user preferences if available.

        Args:
            filename: The name of the file to load

        Returns:
            Formatted prompt string
        """
        try:
            template = self._read_template_file(filename)
            variables = self._get_preference_variables()

            # Add life story if loading cover letter prompt
            if filename == "cover_letter_prompt.txt" and self.user_id:
                self._add_life_story(variables)

            return template.safe_substitute(variables)
        except Exception as e:
            logger.error(f"Error loading prompt {filename}: {e}")
            raise

    def get_section_prompt(self, section: str) -> str:
        """
        Get the prompt for a specific section with user preferences.

        Args:
            section: The section name (e.g. 'career_summary', 'skills')

        Returns:
            str: The formatted prompt text

        Raises:
            FileNotFoundError: If prompt file doesn't exist
            TemplateError: If template substitution fails
        """
        filename = f"{section.lower()}_prompt.txt"
        return self._load_prompt(filename)

    def get_system_prompt(self):
        return self._load_prompt("system_prompt.txt")

    def get_folder_name_prompt(self):
        return self._load_prompt("folder_name_prompt.txt")

    def get_cover_letter_prompt(self) -> str:
        """
        Get the cover letter prompt with user's life story.

        Returns:
            str: The cover letter prompt with user's life story
        """
        return self._load_prompt("cover_letter_prompt.txt")

    def refresh_preferences(self) -> None:
        """Force reload of user preferences"""
        self._preferences = None
        _ = self.preferences  # Trigger reload


if __name__ == "__main__":
    # Example usage
    prompt_loader = PromptLoader(user_id=test_user_id)
    print(f"Resolved PROMPTS_FOLDER: {PROMPTS_DIR}")
    prompt = prompt_loader.get_section_prompt("projects")
    print(prompt)
