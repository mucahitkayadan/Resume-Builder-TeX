from typing import Optional, Dict
from ..connections.mongo_connection import MongoConnection
from ..repositories.portfolio_repository import MongoPortfolioRepository
from ..repositories.user_repository import MongoUserRepository
from ..repositories.resume_repository import MongoResumeRepository
from ..repositories.preamble_repository import MongoPreambleRepository
from ..repositories.tex_header_repository import MongoTexHeaderRepository
from ..models.preamble import Preamble
from ..models.resume import Resume
import mongomock
from datetime import datetime

class MongoUnitOfWork:
    def __init__(self, connection: MongoConnection):
        self.connection = connection
        self.portfolio: Optional[MongoPortfolioRepository] = None
        self.users: Optional[MongoUserRepository] = None
        self.resumes: Optional[MongoResumeRepository] = None
        self.preambles: Optional[MongoPreambleRepository] = None
        self.tex_headers: Optional[MongoTexHeaderRepository] = None
        self._session = None
        self._is_mock = isinstance(self.connection.client, mongomock.MongoClient)

    def __enter__(self):
        self._session = self.connection.start_session()
        self.portfolio = MongoPortfolioRepository(self.connection)
        self.users = MongoUserRepository(self.connection)
        self.resumes = MongoResumeRepository(self.connection)
        self.preambles = MongoPreambleRepository(self.connection)
        self.tex_headers = MongoTexHeaderRepository(self.connection)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.connection.end_session()

    def commit(self):
        self.connection.commit_transaction()

    def rollback(self):
        self.connection.abort_transaction()

    def get_resume_preamble(self) -> Optional[Preamble]:
        """Get the resume preamble"""
        if not self.preambles:
            raise ValueError("Preamble repository not initialized")
        return self.preambles.get_by_type("resume_preamble")

    def get_cover_letter_preamble(self) -> Optional[Preamble]:
        """Get the cover letter preamble"""
        if not self.preambles:
            raise ValueError("Preamble repository not initialized")
        return self.preambles.get_by_type("cover_letter_preamble")

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
        """Update the cover letter content and PDF for a resume"""
        if not self.resumes:
            raise ValueError("Resume repository not initialized")
        
        try:
            resume = self.resumes.get_by_id(resume_id)
            if resume:
                resume.cover_letter_content = cover_letter_content
                resume.cover_letter_pdf = cover_letter_pdf
                resume.updated_at = datetime.utcnow()
                return self.resumes.update(resume)
            return False
        except Exception as e:
            print(f"Error updating cover letter: {str(e)}")
            return False