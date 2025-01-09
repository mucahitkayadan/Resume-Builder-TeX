from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

class MongoConnection:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client: Optional[MongoClient] = None
        self.async_client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._transaction = None

    def connect(self):
        """Connect synchronously to MongoDB"""
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise

    async def connect_async(self):
        """Connect asynchronously to MongoDB"""
        try:
            self.async_client = AsyncIOMotorClient(self.uri)
            self.db = self.async_client[self.db_name]
            logger.info("Connected to MongoDB successfully (async)")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB async: {str(e)}")
            raise

    def close(self):
        """Close synchronous connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")

    async def close_async(self):
        """Close asynchronous connection"""
        if self.async_client:
            self.async_client.close()
            logger.info("Closed MongoDB async connection")

    def start_transaction(self):
        """Start a synchronous transaction"""
        if not self._transaction:
            self._transaction = self.client.start_session()
            self._transaction.start_transaction()

    async def start_transaction_async(self):
        """Start an asynchronous transaction"""
        if not self._transaction:
            self._transaction = await self.async_client.start_session()
            await self._transaction.start_transaction()

    def commit_transaction(self):
        """Commit a synchronous transaction"""
        if self._transaction:
            self._transaction.commit_transaction()
            self._transaction.end_session()
            self._transaction = None

    async def commit_transaction_async(self):
        """Commit an asynchronous transaction"""
        if self._transaction:
            await self._transaction.commit_transaction()
            await self._transaction.end_session()
            self._transaction = None

    def abort_transaction(self):
        """Abort a synchronous transaction"""
        if self._transaction:
            self._transaction.abort_transaction()
            self._transaction.end_session()
            self._transaction = None

    async def abort_transaction_async(self):
        """Abort an asynchronous transaction"""
        if self._transaction:
            await self._transaction.abort_transaction()
            await self._transaction.end_session()
            self._transaction = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return bool(self.client or self.async_client)

    @property
    def is_transaction_active(self) -> bool:
        """Check if a transaction is active"""
        return bool(self._transaction)
