import os
from src.core.database.connections.mongo_connection import MongoConnection


def get_database_connection():
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("MONGODB_DATABASE", "user_information")
    return MongoConnection(uri=uri, db_name=db_name)

def get_unit_of_work():
    connection = get_database_connection()
    # Import here to avoid circular import
    from src.core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork
    return MongoUnitOfWork(connection) 