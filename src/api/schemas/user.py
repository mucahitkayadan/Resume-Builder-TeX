"""User schemas module."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)
    
class UserUpdate(BaseModel):
    """User update schema."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserResponse(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    created_at: datetime
    updated_at: datetime

# Alias for backward compatibility
User = UserResponse

class UserPreferencesBase(BaseModel):
    """Base user preferences schema."""
    theme: str = "light"
    language: str = "en"
    notifications_enabled: bool = True
    email_notifications: bool = True

class UserPreferencesUpdate(UserPreferencesBase):
    """User preferences update schema."""
    theme: Optional[str] = None
    language: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None

class UserPreferencesResponse(UserPreferencesBase):
    """User preferences response schema."""
    model_config = ConfigDict(from_attributes=True)
    
    user_id: str
    created_at: datetime
    updated_at: datetime