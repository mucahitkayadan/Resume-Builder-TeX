from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class Resume(BaseModel):
    """MongoDB Resume Model"""
    id: Optional[str]
    user_id: str
    company_name: str
    job_title: str
    job_description: str
    personal_information: Optional[str] = ""
    career_summary: Optional[str] = ""
    skills: Optional[str] = ""
    work_experience: Optional[str] = ""
    education: Optional[str] = ""
    projects: Optional[str] = ""
    awards: Optional[str] = ""
    publications: Optional[str] = ""
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = 0.1
    resume_pdf: Optional[bytes] = None
    cover_letter_content: Optional[str] = None
    cover_letter_pdf: Optional[bytes] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        protected_namespaces = ()