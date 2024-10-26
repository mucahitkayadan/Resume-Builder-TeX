import os
from typing import List, Dict, Union
import re
import logging
from utils.latex_utils import escape_latex  # Import the escape_latex function
from utils.database_manager import DatabaseManager

class TexLoader:
    """
    A class for loading LaTeX template files.
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the TexLoader with a database manager.

        Args:
            db_manager (DatabaseManager): The database manager to use for loading templates.
        """
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

    def load_file(self, filename: str) -> str:
        """
        Load the content of a file from the base path.

        Args:
            filename (str): The name of the file to load.

        Returns:
            str: The content of the loaded file.
        """
        with open(f"{self.base_path}/{filename}", "r") as file:
            return file.read()

    def get_section_content(self, section_name: str) -> str:
        """
        Get the content of a specific section LaTeX template file.

        Args:
            section_name (str): The name of the section file to load.

        Returns:
            str: The content of the section file.
        """
        return self.load_file(f"{section_name}.tex")

    # Existing methods for specific sections can be removed or kept as needed

    def load_template(self, template_name):
        with open(f"{self.template_dir}/{template_name}.tex", "r") as file:
            return file.read()

    def format_template(self, template_name, **kwargs):
        template = self.load_template(template_name)
        return template.format(**kwargs)

    def get_template(self, name: str) -> str:
        content = self.db_manager.get_tex_header(name)
        if content is None:
            raise ValueError(f"Template '{name}' not found in the database")
        return content

    def safe_format_template(self, template_name: str, **kwargs) -> str:
        template = self.get_template(template_name)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"KeyError in template '{template_name}': {e}")
            raise ValueError(f"Missing key in template '{template_name}': {e}")
        except ValueError as e:
            self.logger.error(f"ValueError in template '{template_name}': {e}")
            raise ValueError(f"Error formatting template '{template_name}': {e}")
