import mongomock
import pytest

from src.core.database.connections.mongo_connection import MongoConnection
from src.core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork


@pytest.fixture
def mongo_connection():
    """Create a mock MongoDB connection"""
    connection = MongoConnection("mongodb://localhost", "test_db")
    connection._client = mongomock.MongoClient()
    connection._db = connection._client["test_db"]
    connection._is_mock = True
    return connection


@pytest.fixture
def mongo_uow(mongo_connection):
    """Create MongoDB Unit of Work"""
    return MongoUnitOfWork(mongo_connection)
