from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class UserPreferences(BaseModel):
    """User Preferences Model"""
    location_details: Dict[str, str] = {
        'default_location': "San Francisco, CA"
    }
    project_details: Dict[str, int] = {
        'max_projects': 2,
        'bullet_points_per_project': 2
    }
    work_experience_details: Dict[str, int] = {
        'max_jobs': 4,
        'bullet_points_per_job': 2
    }
    skills_details: Dict[str, Any] = {
        'max_categories': 5,
        'min_skills_per_category': 6,
        'max_skills_per_category': 10
    }
    career_summary_details: Dict[str, int] = {
        'min_words': 15,
        'max_words': 25
    }
    education_details: Dict[str, int] = {
        'max_entries': 3,
        'max_courses': 5
    }
    cover_letter_details: Dict[str, Any] = {
        'paragraphs': 4,
        'target_grade_level': 12
    }
    awards_details: Dict[str, int] = {
        'max_awards': 4
    }
    publications_details: Dict[str, int] = {
        'max_publications': 3
    }

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
    preferences: UserPreferences = UserPreferences()
    life_story: Optional[str] = None
    signature_image: Optional[bytes] = None
    signature_filename: Optional[str] = None
    signature_content_type: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True