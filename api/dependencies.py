from fastapi import Depends
from core.database.factory import get_unit_of_work
from core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork

async def get_db() -> MongoUnitOfWork:
    uow = get_unit_of_work()
    try:
        yield uow
    finally:
        uow.connection.close() 