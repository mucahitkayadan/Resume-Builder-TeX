from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class UserPreferences(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    project_details: Dict[str, int] = Field(default_factory=dict)
    work_experience_details: Dict[str, int] = Field(default_factory=dict)
    skills_details: Dict[str, Any] = Field(default_factory=dict)
    career_summary_details: Dict[str, int] = Field(default_factory=dict)
    education_details: Dict[str, int] = Field(default_factory=dict)
    cover_letter_details: Dict[str, Any] = Field(default_factory=dict)
    awards_details: Dict[str, int] = Field(default_factory=dict)
    publications_details: Dict[str, int] = Field(default_factory=dict)
    
    llm_preferences: Optional[Dict] = Field(default_factory=dict)
    section_preferences: Optional[Dict] = Field(default_factory=dict)
    feature_preferences: Optional[Dict] = Field(default_factory=dict)

class UserBase(BaseModel):
    user_id: str = Field(..., min_length=3, description="Unique identifier for the user")
    email: EmailStr
    full_name: Optional[str] = Field(None, min_length=2)

class UserCreate(UserBase):
    password: str = Field(
        ..., 
        min_length=8,
        description="Password must be at least 8 characters long"
    )

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    created_at: datetime
    updated_at: datetime
    preferences: UserPreferences

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )

class UserPreferencesUpdate(BaseModel):
    project_details: Optional[Dict[str, int]] = None
    work_experience_details: Optional[Dict[str, int]] = None
    skills_details: Optional[Dict[str, Any]] = None
    career_summary_details: Optional[Dict[str, int]] = None
    education_details: Optional[Dict[str, int]] = None
    cover_letter_details: Optional[Dict[str, Any]] = None
    awards_details: Optional[Dict[str, int]] = None
    publications_details: Optional[Dict[str, int]] = None
    llm_preferences: Optional[Dict] = None
    section_preferences: Optional[Dict] = None
    feature_preferences: Optional[Dict] = None

    model_config = ConfigDict(protected_namespaces=()) 