from typing import Optional, Dict, Any
from datetime import datetime
from src.core.database.factory import get_unit_of_work
from ..schemas.portfolio import PortfolioResponse
from fastapi import UploadFile

class PortfolioService:
    def __init__(self):
        self.uow = get_unit_of_work()

    async def get_portfolio(self, user_id: str) -> Optional[PortfolioResponse]:
        with self.uow:
            portfolio = self.uow.portfolios.get_by_user_id(user_id)
            if not portfolio:
                return None
            return PortfolioResponse.model_validate(portfolio)

    async def update_portfolio(self, user_id: str, portfolio_data: dict):
        with self.uow:
            portfolio = self.uow.portfolios.get_by_user_id(user_id)
            if not portfolio:
                raise Exception("Portfolio not found")

            portfolio_data["updated_at"] = datetime.utcnow()
            updated = self.uow.portfolios.update(portfolio.id, portfolio_data)
            self.uow.commit()
            return updated

    async def upload_transcript(self, user_id: str, file: UploadFile):
        # TODO: Implement file upload logic
        pass 