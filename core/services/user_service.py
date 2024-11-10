from fastapi import Depends
from core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork
from ..models.user import User

class UserService:
    def __init__(self, uow: MongoUnitOfWork):
        self.uow = uow

    async def create_user(self, user: User) -> User:
        with self.uow:
            created_user = self.uow.users.add(user)
            return created_user 