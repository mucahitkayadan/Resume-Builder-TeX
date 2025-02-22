"""MongoDB unit of work module."""

from typing import Optional
from ..connections.mongo_connection import MongoConnection, AsyncMongoConnection
from ..repositories import (
    PortfolioRepository,
    ProfileRepository,
    ResumeRepository,
    PreambleRepository,
    TexHeaderRepository,
    UserRepository
)

class MongoUnitOfWork:
    """MongoDB unit of work for synchronous operations."""
    
    def __init__(self, connection: MongoConnection):
        """Initialize MongoUnitOfWork with a database connection."""
        self.connection = connection
        self.users = UserRepository(connection)
        self.portfolios = PortfolioRepository(connection)
        self.profiles = ProfileRepository(connection)
        self.resumes = ResumeRepository(connection)
        self.preambles = PreambleRepository(connection)
        self.tex_headers = TexHeaderRepository(connection)
    
    def get_cover_letter_preamble(self) -> Optional[str]:
        """Get cover letter preamble."""
        preamble = self.preambles.get_by_type("cover_letter_preamble")
        return preamble.content if preamble else None

    def get_resume_preamble(self) -> Optional[str]:
        """Get resume preamble."""
        preamble = self.preambles.get_by_type("resume_preamble")
        return preamble.content if preamble else None

    def get_user_signature(self, user_id: str) -> Optional[str]:
        """Get user signature."""
        profile = self.profiles.get_by_user_id(user_id)
        return profile.signature if profile else None

    def get_tex_header(self) -> Optional[str]:
        """Get TeX header."""
        header = self.tex_headers.get_latest()
        return header.content if header else None
        
    def __enter__(self) -> 'MongoUnitOfWork':
        """Enter the unit of work context."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the unit of work context."""
        if exc_type is not None:
            self.rollback()
        
    def commit(self):
        """Commit the current transaction."""
        if self.connection.session:
            self.connection.session.commit_transaction()
            
    def rollback(self):
        """Rollback the current transaction."""
        if self.connection.session:
            self.connection.session.abort_transaction()

class AsyncMongoUnitOfWork:
    """MongoDB unit of work for asynchronous operations."""
    
    def __init__(self, connection: AsyncMongoConnection):
        """Initialize AsyncMongoUnitOfWork with a database connection."""
        self.connection = connection
        self.users = UserRepository(connection)
        self.portfolios = PortfolioRepository(connection)
        self.profiles = ProfileRepository(connection)
        self.resumes = ResumeRepository(connection)
        self.preambles = PreambleRepository(connection)
        self.tex_headers = TexHeaderRepository(connection)
    
    async def get_cover_letter_preamble(self) -> Optional[str]:
        """Get cover letter preamble asynchronously."""
        preamble = await self.preambles.get_by_type("cover_letter_preamble")
        return preamble.content if preamble else None

    async def get_resume_preamble(self) -> Optional[str]:
        """Get resume preamble asynchronously."""
        preamble = await self.preambles.get_by_type("resume_preamble")
        return preamble.content if preamble else None

    async def get_user_signature(self, user_id: str) -> Optional[str]:
        """Get user signature asynchronously."""
        profile = await self.profiles.get_by_user_id(user_id)
        return profile.signature if profile else None

    async def get_tex_header(self) -> Optional[str]:
        """Get TeX header asynchronously."""
        header = await self.tex_headers.get_latest()
        return header.content if header else None
        
    async def __aenter__(self) -> 'AsyncMongoUnitOfWork':
        """Enter the async unit of work context."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the async unit of work context."""
        if exc_type is not None:
            await self.rollback()
        
    async def commit(self):
        """Commit the current transaction asynchronously."""
        if self.connection.session:
            await self.connection.session.commit_transaction()
            
    async def rollback(self):
        """Rollback the current transaction asynchronously."""
        if self.connection.session:
            await self.connection.session.abort_transaction()
