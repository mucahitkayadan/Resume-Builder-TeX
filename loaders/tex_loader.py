from typing import List, Dict, Union

class TexLoader:
    """
    A class for loading LaTeX template files.
    """

    def __init__(self, base_path: str) -> None:
        """
        Initialize the TexLoader with a base path for template files.

        Args:
            base_path (str): The base directory path where LaTeX template files are stored.
        """
        self.base_path = base_path

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
