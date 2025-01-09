"""
This module defines the User model and related preference models for MongoDB.

Note:
    The Field(default_factory=dict) pattern is used throughout this module to properly handle
    mutable defaults in Pydantic v2 models. This is the recommended approach for dictionary fields
    to avoid the shared mutable state issues that can occur with direct dict defaults.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class LLMPreferences(BaseModel):
    """LLM preferences model"""
    model_type: str = "Claude"
    model_name: str = "claude-3-5-sonnet-20240620"
    temperature: float = 0.1

    model_config = ConfigDict(frozen=True)

class SkillsDetails(BaseModel):
    """Skills details preferences"""
    max_categories: int = 4
    min_skills_per_category: int = 3
    max_skills_per_category: int = 10

    model_config = ConfigDict(frozen=True)

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
    notifications: Dict[str, Any] = Field(default_factory=dict)
    privacy: Dict[str, Any] = Field(default_factory=dict)
    llm_preferences: LLMPreferences = Field(default_factory=LLMPreferences)
    section_preferences: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(
        validate_assignment=True,
        frozen=False,
        extra='allow'
    )

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

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        },
        extra='forbid'
    )

    def model_dump(self, exclude_none: bool = True, **kwargs) -> Dict[str, Any]:
        """Convert to dictionary for API response with sensitive data excluded"""
        excluded_fields = {
            'hashed_password',
            'reset_password_token',
            'reset_password_expires',
            'verification_token',
            'account_locked_until',
            'login_attempts'
        }
        return super().model_dump(
            exclude=excluded_fields,
            exclude_none=exclude_none,
            **kwargs
        )