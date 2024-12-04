from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

# Helper functions to create default dictionaries
def get_project_defaults() -> Dict[str, int]:
    return {
        'max_projects': 2,
        'bullet_points_per_project': 2
    }

def get_work_experience_defaults() -> Dict[str, int]:
    return {
        'max_jobs': 4,
        'bullet_points_per_job': 2
    }

def get_skills_defaults() -> Dict[str, Any]:
    return {
        'max_categories': 5,
        'min_skills_per_category': 6,
        'max_skills_per_category': 10
    }

def get_career_summary_defaults() -> Dict[str, int]:
    return {
        'min_words': 15,
        'max_words': 25
    }

def get_education_defaults() -> Dict[str, int]:
    return {
        'max_entries': 3,
        'max_courses': 5
    }

def get_cover_letter_defaults() -> Dict[str, Any]:
    return {
        'paragraphs': 4,
        'target_grade_level': 12
    }

def get_awards_defaults() -> Dict[str, int]:
    return {
        'max_awards': 4
    }

def get_publications_defaults() -> Dict[str, int]:
    return {
        'max_publications': 3
    }

class UserPreferences(BaseModel):
    """User Preferences Model"""
    project_details: Dict[str, int] = Field(default_factory=get_project_defaults)
    work_experience_details: Dict[str, int] = Field(default_factory=get_work_experience_defaults)
    skills_details: Dict[str, Any] = Field(default_factory=get_skills_defaults)
    career_summary_details: Dict[str, int] = Field(default_factory=get_career_summary_defaults)
    education_details: Dict[str, int] = Field(default_factory=get_education_defaults)
    cover_letter_details: Dict[str, Any] = Field(default_factory=get_cover_letter_defaults)
    awards_details: Dict[str, int] = Field(default_factory=get_awards_defaults)
    publications_details: Dict[str, int] = Field(default_factory=get_publications_defaults)

class User(BaseModel):
    """User Model"""
    id: Optional[str]
    email: EmailStr
    hashed_password: str
    full_name: Optional[str]
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    life_story: Optional[str] = None
    signature_image: Optional[bytes] = None
    signature_filename: Optional[str] = None
    signature_content_type: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True