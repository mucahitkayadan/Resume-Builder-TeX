from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class PersonalInformation(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None

class CareerSummary(BaseModel):
    job_titles: List[str]
    years_of_experience: int
    default_summary: str

class WorkExperience(BaseModel):
    company: str
    job_title: str
    time: str
    location: str
    responsibilities: List[str]

class Education(BaseModel):
    university_name: str
    degree_type: str
    degree: str
    time: str
    location: str
    transcript: List[str] = []

class Project(BaseModel):
    name: str
    date: str
    technologies: Optional[str] = None
    bullet_points: List[str]

class Award(BaseModel):
    name: str
    explanation: str

class Publication(BaseModel):
    name: str
    publisher: str
    time: str
    link: Optional[str] = None

class PortfolioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    personal_information: PersonalInformation
    career_summary: CareerSummary
    work_experience: List[WorkExperience]
    education: List[Education]
    projects: List[Project]
    skills: List[Dict[str, List[str]]]
    awards: List[Award]
    publications: List[Publication] 