from typing import AsyncGenerator
from src.core.database.connections.mongo_connection import MongoConnection
from src.core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork
import os

def get_database_connection():
    """Get synchronous database connection"""
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DATABASE", "user_information")
    connection = MongoConnection(uri=uri, db_name=db_name)
    connection.connect()
    return connection

async def get_async_database_connection():
    """Get asynchronous database connection"""
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DATABASE", "user_information")
    connection = MongoConnection(uri=uri, db_name=db_name)
    await connection.connect_async()
    return connection

def get_unit_of_work():
    """Get synchronous unit of work"""
    connection = get_database_connection()
    return MongoUnitOfWork(connection)

async def get_async_unit_of_work() -> AsyncGenerator[MongoUnitOfWork, None]:
    """Get asynchronous unit of work"""
    try:
        connection = await get_async_database_connection()
        uow = MongoUnitOfWork(connection)
        yield uow
    finally:
        await connection.close_async() 