"""
This module defines the User model and related preference models for MongoDB.

Note:
    The Field(default_factory=dict) pattern is used throughout this module to properly handle
    mutable defaults in Pydantic v2 models. This is the recommended approach for dictionary fields
    to avoid the shared mutable state issues that can occur with direct dict defaults.
"""
from typing import Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class ProjectDetails(BaseModel):
    max_projects: int = Field(default=4)
    bullet_points_per_project: int = Field(default=3)

class WorkExperienceDetails(BaseModel):
    max_jobs: int = Field(default=4)
    bullet_points_per_job: int = Field(default=3)

class SkillsDetails(BaseModel):
    max_categories: int = Field(default=5)
    min_skills_per_category: int = Field(default=7)
    max_skills_per_category: int = Field(default=15)

class CareerSummaryDetails(BaseModel):
    min_words: int = Field(default=15)
    max_words: int = Field(default=25)

class EducationDetails(BaseModel):
    max_entries: int = Field(default=3)
    max_courses: int = Field(default=4)

class CoverLetterDetails(BaseModel):
    paragraphs: int = Field(default=5)
    target_grade_level: int = Field(default=25)

class AwardsDetails(BaseModel):
    max_awards: int = Field(default=4)

class PublicationsDetails(BaseModel):
    max_publications: int = Field(default=3)

class FeaturePreferences(BaseModel):
    check_clearance: bool = Field(default=True)
    auto_save: bool = Field(default=True)
    dark_mode: bool = Field(default=False)

class LLMPreferences(BaseModel):
    model_type: str = Field(default="Claude")
    model_name: str = Field(default="claude-3-5-sonnet-20240620")
    temperature: float = Field(default=0.1)

class SectionPreferences(BaseModel):
    personal_information: Literal["Process", "Hardcode"] = Field(default="Process")
    career_summary: Literal["Process", "Hardcode"] = Field(default="Process")
    skills: Literal["Process", "Hardcode"] = Field(default="Process")
    work_experience: Literal["Process", "Hardcode"] = Field(default="Process")
    education: Literal["Process", "Hardcode"] = Field(default="Process")
    projects: Literal["Process", "Hardcode"] = Field(default="Process")
    awards: Literal["Process", "Hardcode"] = Field(default="Process")
    publications: Literal["Process", "Hardcode"] = Field(default="Process")

class NotificationPreferences(BaseModel):
    email_updates: bool = Field(default=True)
    job_alerts: bool = Field(default=True)
    newsletter: bool = Field(default=False)

class PrivacyPreferences(BaseModel):
    profile_visibility: Literal["public", "private"] = Field(default="public")
    show_email: bool = Field(default=False)
    show_phone: bool = Field(default=False)

class UserPreferences(BaseModel):
    """User preferences model."""
    project_details: ProjectDetails = Field(default_factory=ProjectDetails)
    work_experience_details: WorkExperienceDetails = Field(default_factory=WorkExperienceDetails)
    skills_details: SkillsDetails = Field(default_factory=SkillsDetails)
    career_summary_details: CareerSummaryDetails = Field(default_factory=CareerSummaryDetails)
    education_details: EducationDetails = Field(default_factory=EducationDetails)
    cover_letter_details: CoverLetterDetails = Field(default_factory=CoverLetterDetails)
    awards_details: AwardsDetails = Field(default_factory=AwardsDetails)
    publications_details: PublicationsDetails = Field(default_factory=PublicationsDetails)
    feature_preferences: FeaturePreferences = Field(default_factory=FeaturePreferences)
    llm_preferences: LLMPreferences = Field(default_factory=LLMPreferences)
    section_preferences: SectionPreferences = Field(default_factory=SectionPreferences)
    notifications: NotificationPreferences = Field(default_factory=NotificationPreferences)
    privacy: PrivacyPreferences = Field(default_factory=PrivacyPreferences)

class User(BaseModel):
    """User model for MongoDB."""
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )

    id: Optional[str] = Field(default=None, alias="_id")
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    user_id: str
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    account_locked_until: Optional[datetime] = None
    email_verified: bool = False
    last_active: Optional[datetime] = None
    login_attempts: int = 0
    reset_password_expires: Optional[datetime] = None
    reset_password_token: Optional[str] = None
    subscription_expires: Optional[datetime] = None
    subscription_status: str = "free"
    verification_token: Optional[str] = None