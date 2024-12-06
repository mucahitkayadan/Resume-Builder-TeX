from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ResumeRequest(BaseModel):
    job_description: str

class ResumeGenerationOptions(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    temperature: Optional[float] = 0.1
    model_type: Optional[str] = "openai"
    model_name: Optional[str] = "gpt-3.5-turbo"

class ResumeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=(),
        json_encoders={bytes: lambda v: v.decode('utf-8') if v else None}
    )

    id: str
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
    created_at: datetime
    updated_at: datetime