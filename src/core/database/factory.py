"""Database factory module for creating database connections and unit of work."""

from typing import AsyncGenerator

from config.config import MONGODB_DATABASE, MONGODB_URI

from .connections import AsyncMongoConnection, MongoConnection
from .unit_of_work import AsyncMongoUnitOfWork, MongoUnitOfWork


def get_database_connection() -> MongoConnection:
    """
    Get a MongoDB connection instance.

    Returns:
        MongoConnection: MongoDB connection instance
    """
    connection = MongoConnection(uri=MONGODB_URI, database=MONGODB_DATABASE)
    return connection


def get_async_database_connection() -> AsyncMongoConnection:
    """
    Get an async MongoDB connection instance.

    Returns:
        AsyncMongoConnection: Async MongoDB connection instance
    """
    connection = AsyncMongoConnection(uri=MONGODB_URI, database=MONGODB_DATABASE)
    return connection


def get_unit_of_work() -> MongoUnitOfWork:
    """
    Get a MongoDB unit of work instance.

    Returns:
        MongoUnitOfWork: MongoDB unit of work instance
    """
    connection = get_database_connection()
    return MongoUnitOfWork(connection)


async def get_async_unit_of_work() -> AsyncGenerator[AsyncMongoUnitOfWork, None]:
    """
    Get an async MongoDB unit of work instance.

    Yields:
        AsyncMongoUnitOfWork: Async MongoDB unit of work instance
    """
    connection = get_async_database_connection()
    async with AsyncMongoUnitOfWork(connection) as uow:
        yield uow
