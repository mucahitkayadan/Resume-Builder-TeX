from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Optional
from datetime import datetime

class CoverLetterRequest(BaseModel):
    job_description: str
    resume_id: Optional[str] = None  # Optional resume to base the cover letter on

class CoverLetterGenerationOptions(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    temperature: Optional[float] = 0.1
    model_type: Optional[str] = "openai"
    model_name: Optional[str] = "gpt-3.5-turbo"
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"
    focus_points: Optional[list[str]] = Field(default_factory=list)

class CoverLetterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    id: str
    company_name: str
    job_title: str
    content: str
    pdf_url: Optional[str]
    resume_id: Optional[str]
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    created_at: datetime
    updated_at: datetime 