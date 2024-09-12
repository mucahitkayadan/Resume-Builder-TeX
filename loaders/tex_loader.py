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

    def get_main(self) -> str:
        """
        Get the content of the main LaTeX template file.

        Returns:
            str: The content of the main.tex file.
        """
        return self.load_file("main.tex")

    def get_preamble(self) -> str:
        """
        Get the content of the preamble LaTeX template file.

        Returns:
            str: The content of the preamble.tex file.
        """
        return self.load_file("preamble.tex")

    def get_personal_information(self) -> str:
        """
        Get the content of the personal information LaTeX template file.

        Returns:
            str: The content of the personal_information.tex file.
        """
        return self.load_file("personal_information.tex")

    def get_career_summary(self) -> str:
        """
        Get the content of the career summary LaTeX template file.

        Returns:
            str: The content of the career_summary.tex file.
        """
        return self.load_file("career_summary.tex")

    def get_skills(self) -> str:
        """
        Get the content of the skills LaTeX template file.

        Returns:
            str: The content of the skills.tex file.
        """
        return self.load_file("skills.tex")

    def get_work_experience(self) -> str:
        """
        Get the content of the work experience LaTeX template file.

        Returns:
            str: The content of the work_experience.tex file.
        """
        return self.load_file("work_experience.tex")

    def get_education(self) -> str:
        """
        Get the content of the education LaTeX template file.

        Returns:
            str: The content of the education.tex file.
        """
        return self.load_file("education.tex")

    def get_projects(self) -> str:
        """
        Get the content of the projects LaTeX template file.

        Returns:
            str: The content of the projects.tex file.
        """
        return self.load_file("projects.tex")

    def get_awards(self) -> str:
        """
        Get the content of the awards LaTeX template file.

        Returns:
            str: The content of the awards.tex file.
        """
        return self.load_file("awards.tex")

    def get_publications(self) -> str:
        """
        Get the content of the publications LaTeX template file.

        Returns:
            str: The content of the publications.tex file.
        """
        return self.load_file("publications.tex")
