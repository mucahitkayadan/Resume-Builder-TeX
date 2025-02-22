"""MongoDB unit of work module."""

from typing import Optional

from ..connections.mongo_connection import AsyncMongoConnection, MongoConnection
from ..repositories import (
    PortfolioRepository,
    PreambleRepository,
    ProfileRepository,
    ResumeRepository,
    TexHeaderRepository,
    UserRepository,
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

    def get_last_resume_id(self, user_id: str) -> Optional[str]:
        """Get the ID of the user's most recent resume.

        Args:
            user_id: The ID of the user

        Returns:
            str: The ID of the most recent resume, or None if no resumes found
        """
        resume = self.resumes.get_latest_by_user_id(user_id)
        return resume.id if resume else None

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

    def get_resume_for_cover_letter(self, resume_id: str) -> dict:
        """Get resume data formatted for cover letter generation.

        Args:
            resume_id: The ID of the resume to retrieve

        Returns:
            dict: Resume data formatted for cover letter generation

        Raises:
            ValueError: If resume not found
        """
        resume = self.resumes.get_by_id(resume_id)
        if not resume:
            raise ValueError(f"Resume with ID {resume_id} not found")

        # Collect all non-empty sections
        resume_data = {}
        sections = [
            "personal_information",
            "career_summary",
            "skills",
            "work_experience",
            "education",
            "projects",
            "awards",
            "publications",
        ]

        for section in sections:
            content = getattr(resume, section, "")
            if content and isinstance(content, str):
                resume_data[section] = content

        return resume_data

    def __enter__(self) -> "MongoUnitOfWork":
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

    async def get_resume_for_cover_letter(self, resume_id: str) -> dict:
        """Get resume data formatted for cover letter generation asynchronously.

        Args:
            resume_id: The ID of the resume to retrieve

        Returns:
            dict: Resume data formatted for cover letter generation

        Raises:
            ValueError: If resume not found
        """
        resume = await self.resumes.get_by_id(resume_id)
        if not resume:
            raise ValueError(f"Resume with ID {resume_id} not found")

        # Collect all non-empty sections
        resume_data = {}
        sections = [
            "personal_information",
            "career_summary",
            "skills",
            "work_experience",
            "education",
            "projects",
            "awards",
            "publications",
        ]

        for section in sections:
            content = getattr(resume, section, "")
            if content and isinstance(content, str):
                resume_data[section] = content

        return resume_data

    async def __aenter__(self) -> "AsyncMongoUnitOfWork":
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
