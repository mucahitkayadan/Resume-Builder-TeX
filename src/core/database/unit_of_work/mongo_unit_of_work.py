from typing import Optional, Dict
from ..connections.mongo_connection import MongoConnection
from ..repositories.portfolio_repository import MongoPortfolioRepository
from ..repositories.user_repository import MongoUserRepository
from ..repositories.resume_repository import MongoResumeRepository
from ..repositories.preamble_repository import MongoPreambleRepository
from ..repositories.tex_header_repository import MongoTexHeaderRepository
from ..repositories.profile_repository import MongoProfileRepository
from ..models.preamble import Preamble
from datetime import datetime, timezone
import os
import logging

logger = logging.getLogger(__name__)

class MongoUnitOfWork:
    def __init__(self, connection: MongoConnection):
        self.connection = connection
        self.portfolio = None
        self.users = None
        self.resumes = None
        self.profiles = None
        self.preambles = None
        self.tex_headers = None
        self._in_transaction = False

    def _ensure_connection(self):
        """Ensure database connection is established"""
        if not self.connection.is_connected:
            self.connection.connect()

    async def _ensure_async_connection(self):
        """Ensure async database connection is established"""
        if not self.connection.is_connected:
            await self.connection.connect_async()

    def __enter__(self):
        self._ensure_connection()
        self._init_repositories()
        self._in_transaction = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self._in_transaction = False

    async def __aenter__(self):
        await self._ensure_async_connection()
        self._init_repositories()
        self._in_transaction = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback_async()
        else:
            await self.commit_async()
        self._in_transaction = False

    def _init_repositories(self):
        """Initialize all repositories"""
        self.portfolio = MongoPortfolioRepository(self.connection)
        self.users = MongoUserRepository(self.connection)
        self.resumes = MongoResumeRepository(self.connection)
        self.profiles = MongoProfileRepository(self.connection)
        self.preambles = MongoPreambleRepository(self.connection)
        self.tex_headers = MongoTexHeaderRepository(self.connection)

    def commit(self):
        if self._in_transaction:
            self.connection.commit_transaction()

    def rollback(self):
        if self._in_transaction:
            self.connection.abort_transaction()

    async def commit_async(self):
        if self._in_transaction:
            await self.connection.commit_transaction_async()

    async def rollback_async(self):
        if self._in_transaction:
            await self.connection.abort_transaction_async()

    def get_resume_preamble(self) -> Optional[Preamble]:
        """Get the résumé preamble"""
        if not self.preambles:
            raise ValueError("Preamble repository not initialized")
        return self.preambles.get_by_type("resume_preamble")

    def get_cover_letter_preamble(self) -> Optional[Preamble]:
        """Get the cover letter preamble"""
        if not self.preambles:
            raise ValueError("Preamble repository not initialized")
        return self.preambles.get_by_type("cover_letter_preamble")

    def get_last_resume_id(self, user_id: str) -> Optional[str]:
        """Get the id of the last resume"""
        if not self.resumes:
            raise ValueError("Resume repository not initialized")
        
        logger.debug(f"Getting last resume ID for user_id: {user_id}")
        
        try:
            # Query directly for the _id field
            result = self.resumes.collection.find_one(
                {'user_id': user_id},
                sort=[('created_at', -1)],
                projection={'_id': 1}  # Only get the _id field
            )
            
            if result and '_id' in result:
                resume_id = str(result['_id'])
                logger.debug(f"Found latest resume ID: {resume_id}")
                return resume_id
                
            logger.debug("No resume found for user")
            return None
            
        except Exception as e:
            logger.error(f"Error getting last resume ID: {str(e)}")
            return None

    def get_resume_for_cover_letter(self, resume_id: str) -> Optional[Dict[str, str]]:
        """Get only the necessary resume sections for cover letter generation"""
        if not self.resumes:
            raise ValueError("Resume repository not initialized")
        
        try:
            resume = self.resumes.get_by_id(resume_id)
            if resume:
                return {
                    'personal_information': resume.personal_information,
                    'career_summary': resume.career_summary,
                    'skills': resume.skills,
                    'work_experience': resume.work_experience,
                    'education': resume.education,
                    'projects': resume.projects,
                    'awards': resume.awards,
                    'publications': resume.publications
                }
            return None
        except Exception as e:
            print(f"Error retrieving resume for cover letter: {str(e)}")
            return None

    def update_cover_letter(self, resume_id: str, cover_letter_content: str, cover_letter_pdf: Optional[bytes] = None) -> bool:
        """Update the cover letter content and PDF for a résumé"""
        if not self.resumes:
            raise ValueError("Resume repository not initialized")
        
        try:
            resume = self.resumes.get_by_id(resume_id)
            if resume:
                resume.cover_letter_content = cover_letter_content
                resume.cover_letter_pdf = cover_letter_pdf
                resume.updated_at = datetime.now(timezone.utc)
                return self.resumes.update(resume)
            return False
        except Exception as e:
            print(f"Error updating cover letter: {str(e)}")
            return False

    def update_user_signature(self, user_id: str, signature_path: str) -> bool:
        """Update user's signature with an image file"""
        if not self.users:
            raise ValueError("User repository not initialized")
        
        try:
            user = self.users.get_by_id(user_id)
            if user:
                with open(signature_path, 'rb') as f:
                    signature_image = f.read()
                
                user.signature_image = signature_image
                user.signature_filename = os.path.basename(signature_path)
                user.signature_content_type = 'image/jpeg'  # Assuming it's always jpg
                user.updated_at = datetime.now(timezone.utc)
                
                return self.users.update(user)
            return False
        except Exception as e:
            print(f"Error updating user signature: {str(e)}")
            return False

    def get_user_signature(self, user_id: str) -> Optional[bytes]:
        """Get user's signature image"""
        if not self.users:
            raise ValueError("User repository not initialized")
        
        try:
            user = self.users.get_by_user_id(user_id)
            if user and hasattr(user, 'signature_image'):
                return user.signature_image
            return None
        except Exception as e:
            print(f"Error retrieving user signature: {str(e)}")
            return None
