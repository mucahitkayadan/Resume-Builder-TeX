# Testing is done - Successful
from typing import Dict, List, Any, Optional, Union
import logging
from src.core.database.factory import get_unit_of_work
from src.core.dto.portfolio.portfolio import PortfolioDTO

logger = logging.getLogger(__name__)


class PortfolioLoader:
    """
    A class to load user information from MongoDB.
    """

    def __init__(self, user_id: str):
        """Initialize MongoDB connection and load data for a specific user."""
        self.uow = get_unit_of_work()
        with self.uow:
            raw_portfolio = self.uow.portfolio.get_by_user_id(user_id)
            if not raw_portfolio:
                raise ValueError(f"Portfolio not found for user {user_id}")
            self.portfolio = PortfolioDTO.from_db_model(raw_portfolio)

    def get_section_data(self, section: str) -> Any:
        """Get data for a specific section from the portfolio."""
        logger.debug(f"Getting data for section: {section}")
        
        if hasattr(self.portfolio, section):
            data = getattr(self.portfolio, section)
            logger.debug(f"Found data for section {section}: {data}")
            return data
        else:
            logger.warning(f"Section {section} not found in portfolio")
            return None

if __name__ == '__main__':
    portfolio_loader = PortfolioLoader("mujakayadan")
    print(portfolio_loader.get_section_data('projects'))