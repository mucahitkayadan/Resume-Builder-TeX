"""
This module defines the User model and related preference models for MongoDB.

Note:
    The Field(default_factory=dict) pattern is used throughout this module to properly handle
    mutable defaults in Pydantic v2 models. This is the recommended approach for dictionary fields
    to avoid the shared mutable state issues that can occur with direct dict defaults.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class UserPreferences(BaseModel):
    """User preferences model."""
    
    feature_preferences: Dict[str, bool] = Field(default_factory=dict)
    project_details: Dict[str, int] = Field(default_factory=dict)
    work_experience_details: Dict[str, int] = Field(default_factory=dict)
    skills_details: Dict[str, int] = Field(default_factory=dict)
    career_summary_details: Dict[str, int] = Field(default_factory=dict)
    education_details: Dict[str, int] = Field(default_factory=dict)
    section_preferences: Dict[str, str] = Field(default_factory=dict)

class User(BaseModel):
    """User model."""
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
        json_encoders={ObjectId: str}
    )
    
    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    email: str
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    account_locked_until: Optional[datetime] = None
    email_verified: bool = False
    last_active: Optional[datetime] = None
    login_attempts: int = 0
    reset_password_expires: Optional[datetime] = None
    reset_password_token: Optional[str] = None
    subscription_expires: Optional[datetime] = None
    subscription_status: str = "free"
    verification_token: Optional[str] = None