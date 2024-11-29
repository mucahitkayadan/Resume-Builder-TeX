# Testing is done - Successful
from typing import Dict, List, Any, Optional, Union
import logging
from src.core.database.factory import get_unit_of_work

class PortfolioLoader:
    """
    A class to load user information from MongoDB.
    """

    def __init__(self, user_id: str):
        """Initialize MongoDB connection and load data for a specific user."""
        self.uow = get_unit_of_work()
        self.user_id = user_id
        self.data = self._load_data()

    def _load_data(self) -> Optional[Any]:
        """Load user data from MongoDB by user ID."""
        try:
            with self.uow:
                # Fetch portfolio using user_id
                return self.uow.portfolio.get_by_user_id(self.user_id)
        except Exception as e:
            logging.error(f"Error loading data from MongoDB: {e}")
            return None

    def get_section_data(self, section: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Get data for a specific section from MongoDB.

        Args:
            section: Name of the section to retrieve (e.g., 'personal_information', 'skills')

        Returns:
            Dictionary or list containing the section data
        """
        if not self.data:
            logging.error("No data loaded for the user.")
            return {}

        section_mapping = {
            'personal_information': self.data.personal_information,
            'career_summary': self.data.career_summary.dict(),
            'skills': self.data.skills,
            'work_experience': self.data.work_experience,
            'education': self.data.education,
            'projects': self.data.projects,
            'awards': self.data.awards,
            'publications': self.data.publications,
            'certifications': self.data.certifications,
            'languages': self.data.languages,
        }

        if section not in section_mapping:
            raise ValueError(f"Invalid section name: {section}")

        return section_mapping[section]

if __name__ == '__main__':
    portfolio_loader = PortfolioLoader("mujakayadan")
    print(portfolio_loader.get_section_data('personal_information'))