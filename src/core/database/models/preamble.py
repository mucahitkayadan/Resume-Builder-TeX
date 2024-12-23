from pydantic import BaseModel
from typing import Optional

class Preamble(BaseModel):
    """MongoDB Preamble Model"""
    id: Optional[str]
    name: str
    content: str
    type: str

    class Config:
        arbitrary_types_allowed = True