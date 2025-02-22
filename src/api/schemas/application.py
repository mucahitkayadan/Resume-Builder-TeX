from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class InterviewStage(BaseModel):
    stage_name: str
    date: datetime
    notes: Optional[str]
    feedback: Optional[str]
    status: str


class JobApplicationBase(BaseModel):
    company_name: str
    job_title: str
    job_description: str
    job_url: Optional[HttpUrl]
    resume_id: Optional[str]
    cover_letter_id: Optional[str]
    status: ApplicationStatus = ApplicationStatus.DRAFT
    application_date: Optional[datetime]
    notes: Optional[str]
    salary_range: Optional[Dict[str, float]]
    interview_stages: List[InterviewStage] = []


class JobApplicationCreate(JobApplicationBase):
    pass


class JobApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus]
    notes: Optional[str]
    interview_stages: Optional[List[InterviewStage]]
    salary_range: Optional[Dict[str, float]]


class JobApplicationResponse(JobApplicationBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
