from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class Resume(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: Optional[str] = None
    user_id: str
    company_name: str
    job_title: str
    job_description: str
    personal_information: Optional[str] = None
    career_summary: Optional[str] = None
    skills: Optional[str] = None
    work_experience: Optional[str] = None
    education: Optional[str] = None
    projects: Optional[str] = None
    awards: Optional[str] = None
    publications: Optional[str] = None
    resume_pdf: Optional[bytes] = None
    cover_letter_content: Optional[str] = None
    cover_letter_pdf: Optional[bytes] = None
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None