from dataclasses import dataclass
from typing import List, Dict, Any
from src.latex.utils.latex_escaper import LatexEscaper
from .sections import (
    CareerSummaryDTO, EducationItemDTO, ProjectDTO, 
    WorkExperienceDTO, AwardDTO, PublicationDTO, PersonalInformationDTO
)
from .base_dto import BaseDTO

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
    def from_db_model(cls, data: Dict[str, Any]) -> 'PortfolioDTO':
        return cls(
            personal_information=PersonalInformationDTO(
                name=LatexEscaper.escape_text(data.personal_information.get('name', '')),
                email=LatexEscaper.escape_text(data.personal_information.get('email', '')),
                phone=LatexEscaper.escape_text(data.personal_information.get('phone', '')),
                address=LatexEscaper.escape_text(data.personal_information.get('address', '')),
                linkedin=LatexEscaper.escape_text(data.personal_information.get('linkedin', '')),
                github=LatexEscaper.escape_text(data.personal_information.get('github', ''))
            ),
            career_summary=CareerSummaryDTO(
                job_titles=[LatexEscaper.escape_text(title) for title in data.career_summary.job_titles],
                years_of_experience=str(data.career_summary.years_of_experience),
                default_summary=LatexEscaper.escape_text(data.career_summary.default_summary)
            ),
            education=[
                EducationItemDTO(
                    university_name=LatexEscaper.escape_text(edu.get('university_name', '')),
                    location=LatexEscaper.escape_text(edu.get('location', '')),
                    degree_type=LatexEscaper.escape_text(edu.get('degree_type', '')),
                    degree=LatexEscaper.escape_text(edu.get('degree', '')),
                    time=LatexEscaper.escape_text(edu.get('time', '')),
                    transcript=[LatexEscaper.escape_text(course) for course in edu.get('transcript', [])]
                )
                for edu in data.education
            ],
            skills=[
                {
                    LatexEscaper.escape_text(category): [
                        LatexEscaper.escape_text(skill) for skill in skills
                    ]
                    for category, skills in skill_group.items()
                }
                for skill_group in data.skills
            ],
            work_experience=[
                WorkExperienceDTO(
                    job_title=LatexEscaper.escape_text(exp.get('job_title', '')),
                    company=LatexEscaper.escape_text(exp.get('company', '')),
                    location=LatexEscaper.escape_text(exp.get('location', '')),
                    time=LatexEscaper.escape_text(exp.get('time', '')),
                    responsibilities=[
                        LatexEscaper.escape_text(resp) for resp in exp.get('responsibilities', [])
                    ]
                )
                for exp in data.work_experience
            ],
            projects=[
                ProjectDTO(
                    name=LatexEscaper.escape_text(proj.get('name', '')),
                    technologies=LatexEscaper.escape_text(proj.get('technologies', '')),
                    date=LatexEscaper.escape_text(proj.get('date', '')),
                    bullet_points=[
                        LatexEscaper.escape_text(point) for point in proj.get('bullet_points', [])
                    ]
                )
                for proj in data.projects
            ],
            awards=[
                AwardDTO(
                    name=LatexEscaper.escape_text(award.get('name', '')),
                    explanation=LatexEscaper.escape_text(award.get('explanation', ''))
                )
                for award in data.awards
            ],
            publications=[
                PublicationDTO(
                    name=LatexEscaper.escape_text(pub.get('name', '')),
                    publisher=LatexEscaper.escape_text(pub.get('publisher', '')),
                    time=LatexEscaper.escape_text(pub.get('time', '')),
                    link=LatexEscaper.escape_text(pub.get('link', ''))
                )
                for pub in data.publications
            ]
        )