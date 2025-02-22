"""Resume schemas module."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ResumeBase(BaseModel):
    """Base resume schema."""

    title: str = "My Resume"
    template_id: str = "default"
    version: int = 1
    personal_information: str
    career_summary: str
    skills: str
    work_experience: str
    education: str
    projects: str
    awards: str
    publications: str
    resume_pdf: Optional[bytes] = None
    cover_letter_content: Optional[str] = None
    cover_letter_pdf: Optional[bytes] = None
    model_type: str = "ClaudeStrategy"
    model_name: str = "ClaudeStrategy"
    temperature: float = 0.1

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True


class ResumeCreate(ResumeBase):
    """Resume create schema."""

    pass


class ResumeUpdate(BaseModel):
    """Resume update schema."""

    title: Optional[str] = None
    template_id: Optional[str] = None
    version: Optional[int] = None
    personal_information: Optional[str] = None
    career_summary: Optional[str] = None
    skills: Optional[str] = None
    work_experience: Optional[str] = None
    education: Optional[str] = None
    projects: Optional[str] = None
    awards: Optional[str] = None
    publications: Optional[str] = None
    resume_pdf: Optional[bytes] = None
    cover_letter_content: Optional[str] = None
    cover_letter_pdf: Optional[bytes] = None
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None

    class Config:
        """Pydantic config."""

        arbitrary_types_allowed = True


class Resume(ResumeBase):
    """Resume schema with database fields."""

    _id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
