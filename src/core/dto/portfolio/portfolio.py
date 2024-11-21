from dataclasses import dataclass
from typing import List, Dict, Any
from src.latex.utils.latex_escaper import LatexEscaper
from .sections import (
    CareerSummaryDTO, EducationItemDTO, ProjectDTO, 
    WorkExperienceDTO, AwardDTO, PublicationDTO, PersonalInformationDTO
)
from .base import BaseDTO

@dataclass
class PortfolioDTO(BaseDTO):
    personal_information: PersonalInformationDTO
    career_summary: CareerSummaryDTO
    education: List[EducationItemDTO]
    skills: List[Dict[str, List[str]]]
    work_experience: List[WorkExperienceDTO]
    projects: List[ProjectDTO]
    awards: List[AwardDTO]
    publications: List[PublicationDTO]

    @classmethod
    def from_db_model(cls, data: Dict[str, Any], escaper: LatexEscaper) -> 'PortfolioDTO':
        return cls(
            personal_information=PersonalInformationDTO(
                name=cls.escape_text(data.personal_information.get('name', ''), escaper),
                email=cls.escape_text(data.personal_information.get('email', ''), escaper),
                phone=cls.escape_text(data.personal_information.get('phone', ''), escaper),
                address=cls.escape_text(data.personal_information.get('address', ''), escaper),
                linkedin=cls.escape_text(data.personal_information.get('linkedin', ''), escaper),
                github=cls.escape_text(data.personal_information.get('github', ''), escaper)
            ),
            career_summary=CareerSummaryDTO(
                job_titles=[cls.escape_text(title, escaper) for title in data.career_summary.job_titles],
                years_of_experience=str(data.career_summary.years_of_experience),
                default_summary=cls.escape_text(data.career_summary.default_summary, escaper)
            ),
            education=[
                EducationItemDTO(
                    university_name=cls.escape_text(edu.get('university_name', ''), escaper),
                    location=cls.escape_text(edu.get('location', ''), escaper),
                    degree_type=cls.escape_text(edu.get('degree_type', ''), escaper),
                    degree=cls.escape_text(edu.get('degree', ''), escaper),
                    time=cls.escape_text(edu.get('time', ''), escaper),
                    transcript=[cls.escape_text(course, escaper) for course in edu.get('transcript', [])]
                )
                for edu in data.education
            ],
            skills=[
                {
                    cls.escape_text(category, escaper): [
                        cls.escape_text(skill, escaper) for skill in skills
                    ]
                    for category, skills in skill_group.items()
                }
                for skill_group in data.skills
            ],
            work_experience=[
                WorkExperienceDTO(
                    job_title=cls.escape_text(exp.get('job_title', ''), escaper),
                    company=cls.escape_text(exp.get('company', ''), escaper),
                    location=cls.escape_text(exp.get('location', ''), escaper),
                    time=cls.escape_text(exp.get('time', ''), escaper),
                    responsibilities=[
                        cls.escape_text(resp, escaper) for resp in exp.get('responsibilities', [])
                    ]
                )
                for exp in data.work_experience
            ],
            projects=[
                ProjectDTO(
                    name=cls.escape_text(proj.get('name', ''), escaper),
                    technologies=cls.escape_text(proj.get('technologies', ''), escaper),
                    date=cls.escape_text(proj.get('date', ''), escaper),
                    bullet_points=[
                        cls.escape_text(point, escaper) for point in proj.get('bullet_points', [])
                    ]
                )
                for proj in data.projects
            ],
            awards=[
                AwardDTO(
                    name=cls.escape_text(award.get('name', ''), escaper),
                    explanation=cls.escape_text(award.get('explanation', ''), escaper)
                )
                for award in data.awards
            ],
            publications=[
                PublicationDTO(
                    name=cls.escape_text(pub.get('name', ''), escaper),
                    publisher=cls.escape_text(pub.get('publisher', ''), escaper),
                    date=cls.escape_text(pub.get('date', ''), escaper),
                    description=cls.escape_text(pub.get('description', ''), escaper)
                )
                for pub in data.publications
            ]
        )