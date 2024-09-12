import json
from typing import Dict, List, Any

class JsonLoader:
    """
    A class for loading and accessing JSON data from a file.
    """

    def __init__(self, json_file_path: str) -> None:
        """
        Initialize the JsonLoader with the given JSON file path.

        Args:
            json_file_path (str): The path to the JSON file to be loaded.
        """
        with open(json_file_path, "r") as file:
            self.data: Dict[str, Any] = json.load(file)

    def get_personal_information(self) -> Dict[str, Any]:
        """
        Retrieve personal information from the loaded JSON data.

        Returns:
            Dict[str, Any]: A dictionary containing personal information.
        """
        return self.data.get("personal_information", {})

    def get_job_titles(self) -> List[str]:
        """
        Retrieve job titles from the loaded JSON data.

        Returns:
            List[str]: A list of job titles.
        """
        return self.data.get("job_titles", [])

    def get_career_summary(self) -> Dict[str, Any]:
        """
        Retrieve career summary from the loaded JSON data.

        Returns:
            Dict[str, Any]: A dictionary containing career summary information.
        """
        return self.data.get("career_summary", {})

    def get_skills(self) -> Dict[str, Any]:
        """
        Retrieve skills from the loaded JSON data.

        Returns:
            Dict[str, Any]: A dictionary containing skills information.
        """
        return self.data.get("skills", {})

    def get_work_experience(self) -> Dict[str, Any]:
        """
        Retrieve work experience from the loaded JSON data.

        Returns:
            Dict[str, Any]: A dictionary containing work experience information.
        """
        return self.data.get("work_experience", {})

    def get_education(self) -> List[Dict[str, Any]]:
        """
        Retrieve education information from the loaded JSON data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing education information.
        """
        return self.data.get("education", [])

    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Retrieve projects from the loaded JSON data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing project information.
        """
        return self.data.get("projects", [])

    def get_awards(self) -> List[Dict[str, Any]]:
        """
        Retrieve awards from the loaded JSON data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing award information.
        """
        return self.data.get("awards", [])

    def get_publications(self) -> List[Dict[str, Any]]:
        """
        Retrieve publications from the loaded JSON data.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing publication information.
        """
        return self.data.get("publications", [])
