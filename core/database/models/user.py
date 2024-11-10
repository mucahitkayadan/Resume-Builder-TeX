from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

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
    preferences: Dict[str, Any] = {}
    signature_image: Optional[bytes] = None
    signature_filename: Optional[str] = None
    signature_content_type: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True