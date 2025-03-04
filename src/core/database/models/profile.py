from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Signature(BaseModel):
    """Signature Model"""
    content_type: str
    filename: str
    image: Any  # Using Any for BSON Binary data

class Profile(BaseModel):
    """MongoDB Profile Model"""
    id: Optional[str]
    user_id: str
    personal_information: Dict[str, str]
    signature: Optional[Signature] = None
    life_story: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True 