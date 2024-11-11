from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TexHeader(BaseModel):
    """MongoDB TeX Header Model"""
    id: Optional[str]
    name: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True 