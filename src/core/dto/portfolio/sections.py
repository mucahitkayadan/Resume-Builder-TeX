from dataclasses import dataclass
from typing import List
from .base_dto import BaseDTO

@dataclass
class CareerSummaryDTO(BaseDTO):
    job_titles: List[str]
    years_of_experience: str
    default_summary: str

@dataclass
class EducationItemDTO(BaseDTO):
    university_name: str
    location: str
    degree_type: str
    degree: str
    time: str
    transcript: List[str]

@dataclass
class ProjectDTO(BaseDTO):
    name: str
    technologies: str
    date: str
    bullet_points: List[str]

@dataclass
class WorkExperienceDTO(BaseDTO):
    job_title: str
    company: str
    location: str
    time: str
    responsibilities: List[str]

@dataclass
class AwardDTO(BaseDTO):
    name: str
    explanation: str

@dataclass
class PublicationDTO(BaseDTO):
    name: str
    publisher: str
    time: str
    link: str

@dataclass
class PersonalInformationDTO(BaseDTO):
    name: str
    email: str
    phone: str
    address: str
    linkedin: str
    github: str
