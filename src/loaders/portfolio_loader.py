from typing import Dict, Any
import logging
from src.core.database.factory import get_unit_of_work
from src.core.dto.portfolio.portfolio import PortfolioDTO
from config.config import test_user_id

logger = logging.getLogger(__name__)


class PortfolioLoader:
    """
    A class to load user information from MongoDB.
    
    This class handles the loading and processing of portfolio data from the database,
    combining information from both portfolio and profile collections.
    
    Attributes:
        uow: Unit of Work instance for database operations
        portfolio: PortfolioDTO instance containing combined portfolio and profile data
    """

    def __init__(self, user_id: str):
        """
        Initialize MongoDB connection and load data for a specific user.
        
        Args:
            user_id (str): The user ID to load portfolio data for
            
        Raises:
            ValueError: If portfolio or profile is not found for the user
        """
        self.uow = get_unit_of_work()
        with self.uow:
            # Get portfolio data
            raw_portfolio = self.uow.portfolios.get_by_user_id(user_id)
            if not raw_portfolio:
                raise ValueError(f"Portfolio not found for user {user_id}")
            
            # Get profile data
            raw_profile = self.uow.profiles.get_by_user_id(user_id)
            if not raw_profile:
                raise ValueError(f"Profile not found for user {user_id}")
            
            # Combine the data for DTO
            self.portfolio = PortfolioDTO.from_db_models(raw_portfolio, raw_profile)

    def get_section_data(self, section: str) -> Any:
        """
        Get data for a specific section from the portfolio.
        
        Args:
            section (str): The name of the section to retrieve
            
        Returns:
            Any: The data for the requested section, or None if not found
            
        Note:
            Special handling is provided for the 'personal_information' section
        """
        logger.debug(f"Getting data for section: {section}")
        
        if section == "personal_information":
            data = self.portfolio.get_personal_information()
            logger.debug(f"Found personal information: {data}")
            return data
        elif hasattr(self.portfolio, section):
            data = getattr(self.portfolio, section)
            logger.debug(f"Found data for section {section}: {data}")
            return data
        else:
            logger.warning(f"Section {section} not found in portfolio")
            return None

    def get_all_sections(self) -> Dict[str, Any]:
        """
        Get all sections from the portfolio.
        
        Returns:
            Dict[str, Any]: A dictionary containing all portfolio sections
            
        Note:
            This includes personal information and all portfolio sections
        """
        sections = {
            'personal_information': self.get_section_data('personal_information'),
            'career_summary': self.get_section_data('career_summary'),
            'work_experience': self.get_section_data('work_experience'),
            'skills': self.get_section_data('skills'),
            'education': self.get_section_data('education'),
            'projects': self.get_section_data('projects'),
            'awards': self.get_section_data('awards'),
            'publications': self.get_section_data('publications')
        }
        return sections


if __name__ == '__main__':
    portfolio_loader = PortfolioLoader(test_user_id)
    all_sections = portfolio_loader.get_all_sections()
    
    # Print each section with a header
    for section_name, section_data in all_sections.items():
        print(f"\n{'='*20} {section_name.upper()} {'='*20}")
        print(section_data)