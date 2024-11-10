from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Portfolio(BaseModel):
    """MongoDB Portfolio Model"""
    id: Optional[str]
    user_id: str
    personal_information: Dict[str, Any]
    career_summary: str
    skills: List[Dict[str, List[str]]]
    work_experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    awards: List[Dict[str, Any]]
    publications: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    languages: List[Dict[str, str]]
    created_at: datetime
    updated_at: datetime

    class Config:
        arbitrary_types_allowed = True 