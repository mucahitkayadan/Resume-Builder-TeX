"""Portfolio schemas module."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class PortfolioBase(BaseModel):
    """Base portfolio schema."""

    title: str = Field(..., description="Portfolio title")
    description: str = Field(..., description="Portfolio description")
    skills: List[str] = Field(default_factory=list, description="List of skills")
    projects: List[str] = Field(default_factory=list, description="List of projects")
    experience: List[str] = Field(
        default_factory=list, description="List of experience"
    )
    education: List[str] = Field(default_factory=list, description="List of education")
    certifications: List[str] = Field(
        default_factory=list, description="List of certifications"
    )
    awards: List[str] = Field(default_factory=list, description="List of awards")
    publications: List[str] = Field(
        default_factory=list, description="List of publications"
    )
    languages: List[str] = Field(default_factory=list, description="List of languages")
    interests: List[str] = Field(default_factory=list, description="List of interests")
    website: Optional[str] = Field(None, description="Portfolio website")
    github: Optional[str] = Field(None, description="GitHub profile")
    linkedin: Optional[str] = Field(None, description="LinkedIn profile")
    twitter: Optional[str] = Field(None, description="Twitter profile")
    blog: Optional[str] = Field(None, description="Blog URL")


class PortfolioCreate(PortfolioBase):
    """Portfolio creation schema."""

    pass


class PortfolioUpdate(BaseModel):
    """Portfolio update schema."""

    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    experience: Optional[List[str]] = None
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    awards: Optional[List[str]] = None
    publications: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    website: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    blog: Optional[str] = None


class PortfolioResponse(PortfolioBase):
    """Portfolio response schema."""

    id: str = Field(..., description="Portfolio ID")
    user_id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
