from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime

class LLMPreferences(BaseModel):
    """LLM preferences model"""
    model_type: str = "Claude"
    model_name: str = "claude-3-5-sonnet-20240620"
    temperature: float = 0.1

class SkillsDetails(BaseModel):
    """Skills details preferences"""
    max_categories: int = 4
    min_skills_per_category: int = 3
    max_skills_per_category: int = 10

class UserPreferences(BaseModel):
    """User preferences model"""
    project_details: Dict[str, Any] = Field(default_factory=dict)
    work_experience_details: Dict[str, Any] = Field(default_factory=dict)
    skills_details: SkillsDetails = Field(default_factory=SkillsDetails)
    career_summary_details: Dict[str, Any] = Field(default_factory=dict)
    education_details: Dict[str, Any] = Field(default_factory=dict)
    cover_letter_details: Dict[str, Any] = Field(default_factory=dict)
    awards_details: Dict[str, Any] = Field(default_factory=dict)
    publications_details: Dict[str, Any] = Field(default_factory=dict)
    feature_preferences: Dict[str, Any] = Field(default_factory=dict)
    llm_preferences: LLMPreferences = Field(default_factory=LLMPreferences)
    section_preferences: Dict[str, Any] = Field(default_factory=dict)
    notifications: Dict[str, Any] = Field(default_factory=dict)
    privacy: Dict[str, Any] = Field(default_factory=dict)

class User(BaseModel):
    """MongoDB User Model"""
    id: Optional[str] = None
    email: EmailStr
    user_id: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    email_verified: bool = False
    last_active: Optional[datetime] = None
    login_attempts: int = 0
    reset_password_token: Optional[str] = None
    reset_password_expires: Optional[datetime] = None
    verification_token: Optional[str] = None
    account_locked_until: Optional[datetime] = None
    subscription_status: str = "free"
    subscription_expires: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True