from fastapi import APIRouter, Depends
from ..dependencies import get_db
from src.core.services.user_service import UserService

router = APIRouter()

@router.post("/users/")
async def create_user(user: User, db: MongoUnitOfWork = Depends(get_db)):
    service = UserService(db)
    return await service.create_user(user) 