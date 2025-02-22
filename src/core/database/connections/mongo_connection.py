"""MongoDB connection handler module."""

import logging
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorClientSession
from pymongo import MongoClient
from pymongo.client_session import ClientSession

logger = logging.getLogger(__name__)


class MongoConnection:
    """MongoDB connection handler for synchronous operations."""

    def __init__(self, uri: str, database: str):
        """
        Initialize MongoDB connection.

        Args:
            uri: MongoDB connection URI
            database: Database name
        """
        self.client = MongoClient(uri)
        self.db = self.client[database]
        self._session: Optional[ClientSession] = None
        logger.info("Connected to MongoDB successfully")

    def __enter__(self) -> "MongoConnection":
        """Start a new session."""
        self._session = self.client.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the session."""
        if self._session:
            self._session.end_session()
            self._session = None

    @property
    def session(self) -> Optional[ClientSession]:
        """Get current session."""
        return self._session


class AsyncMongoConnection:
    """Async MongoDB connection handler."""

    def __init__(self, uri: str, database: str):
        """Initialize MongoDB connection."""
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database]
        self._session: Optional[AsyncIOMotorClientSession] = None
        logger.info("Connected to MongoDB successfully")

    async def __aenter__(self) -> "AsyncMongoConnection":
        """Start a new session."""
        self._session = await self.client.start_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End the session."""
        if self._session:
            await self._session.end_session()
            self._session = None

    @property
    def session(self) -> Optional[AsyncIOMotorClientSession]:
        """Get current session."""
        return self._session
