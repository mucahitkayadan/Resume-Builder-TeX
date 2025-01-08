from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class CareerSummary(BaseModel):
    """Career Summary Model"""
    job_titles: List[str] = Field(default_factory=list)
    years_of_experience: str
    default_summary: str

class PortfolioTemplatePreferences(BaseModel):
    style: str = "modern"
    font: str = "calibri"
    spacing: str = "compact"

class CustomSections(BaseModel):
    enabled: List[str] = Field(default_factory=lambda: ["certifications", "languages", "interests"])
    order: List[str] = Field(default_factory=lambda: [
        "career_summary",
        "work_experience",
        "skills",
        "education",
        "projects",
        "awards",
        "publications"
    ])

class Portfolio(BaseModel):
    """MongoDB Portfolio Model"""
    id: Optional[str]
    user_id: str
    profile_id: str  # Reference to profiles collection
    version: str = "1.0"
    is_active: bool = True
    template_preferences: PortfolioTemplatePreferences = Field(default_factory=PortfolioTemplatePreferences)
    custom_sections: CustomSections = Field(default_factory=CustomSections)
    career_summary: CareerSummary
    skills: List[Dict[str, List[str]]]
    work_experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    awards: List[Dict[str, Any]]
    publications: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    languages: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True