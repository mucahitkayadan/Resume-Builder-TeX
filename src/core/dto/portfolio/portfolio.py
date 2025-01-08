from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.core.database.models.portfolio import Portfolio
from src.core.database.models.profile import Profile
from src.latex.utils.latex_escaper import LatexEscaper

@dataclass
class PortfolioDTO:
    # Personal Information
    name: str
    phone: str
    email: str
    linkedin: str
    github: str
    address: str
    website: str
    
    # Portfolio Sections
    career_summary: Dict[str, Any]
    work_experience: List[Dict[str, Any]]
    skills: List[Dict[str, List[str]]]
    education: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    awards: List[Dict[str, Any]]
    publications: List[Dict[str, Any]]

    @classmethod
    def from_db_models(cls, portfolio: Portfolio, profile: Profile):
        """Create DTO from both Portfolio and Profile models"""
        return cls(
            name=LatexEscaper.escape_text(profile.personal_information.get('full_name', '')),
            phone=LatexEscaper.escape_text(profile.personal_information.get('phone', '')),
            email=LatexEscaper.escape_text(profile.personal_information.get('email', '')),
            linkedin=LatexEscaper.escape_text(profile.personal_information.get('linkedin', '')),
            github=LatexEscaper.escape_text(profile.personal_information.get('github', '')),
            address=LatexEscaper.escape_text(profile.personal_information.get('address', '')),
            website=LatexEscaper.escape_text(profile.personal_information.get('website', '')),
            career_summary=portfolio.career_summary,
            work_experience=portfolio.work_experience,
            skills=portfolio.skills,
            education=portfolio.education,
            projects=portfolio.projects,
            awards=portfolio.awards,
            publications=portfolio.publications
        )

    def get_personal_information(self) -> Dict[str, str]:
        """Get all personal information as a dictionary"""
        return {
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'linkedin': self.linkedin,
            'github': self.github,
            'address': self.address,
            'website': self.website
        }