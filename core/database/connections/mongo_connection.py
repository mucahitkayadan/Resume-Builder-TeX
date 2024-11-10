from typing import Optional, ContextManager
import mongomock
from pymongo import MongoClient, database
from config import MONGODB_URI, MONGODB_DATABASE

class MongoConnection(ContextManager[database.Database]):
    def __init__(self, uri: str = MONGODB_URI, db_name: str = MONGODB_DATABASE):
        self._client: Optional[MongoClient] = None
        self._db = None
        self._is_mock = False
        self._uri = uri
        self._db_name = db_name
        self._session = None
        self._collections_backup = {}
        # Initialize connection immediately
        self._client = MongoClient(self._uri)
        self._db = self._client[self._db_name]

    @property
    def client(self):
        return self._client

    @property
    def db(self):
        return self._db

    def start_session(self):
        if not self._is_mock:
            self._session = self.client.start_session()
            self._session.start_transaction()
        else:
            # Backup collections for mock rollback
            self._collections_backup = {}
            for collection_name in self.db.list_collection_names():
                self._collections_backup[collection_name] = [
                    {k: v for k, v in doc.items() if k != '_id'} 
                    for doc in self.db[collection_name].find()
                ]
        return self._session

    def commit_transaction(self):
        if self._session and not self._is_mock:
            self._session.commit_transaction()
        self._collections_backup = {}

    def abort_transaction(self):
        if self._session and not self._is_mock:
            self._session.abort_transaction()
        elif self._is_mock:
            # Restore collections from backup
            for collection_name in self.db.list_collection_names():
                self.db[collection_name].delete_many({})
                if collection_name in self._collections_backup and self._collections_backup[collection_name]:
                    self.db[collection_name].insert_many(self._collections_backup[collection_name])

    def end_session(self):
        if self._session and not self._is_mock:
            self._session.end_session()
        self._collections_backup = {}

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.abort_transaction()
        else:
            self.commit_transaction()

    def get_database(self, db_name: str):
        return self.client[db_name]

    def close(self):
        if self._client:
            self._client.close()

    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        return self.db[collection_name]
