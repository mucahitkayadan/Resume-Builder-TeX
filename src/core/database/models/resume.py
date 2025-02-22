from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class Resume(BaseModel):
    """Resume content model"""

    id: Optional[str] = Field(None, alias="_id")
    user_id: str
    version: int = 1  # Default version
    title: str = "My Resume"
    template_id: str = "default"  # Default template

    # Content can be either structured data or LaTeX string
    personal_information: Union[Dict[str, str], str] = Field(default_factory=dict)
    career_summary: str = ""
    skills: Union[Dict[str, List[str]], str] = Field(default_factory=dict)
    work_experience: Union[List[Dict[str, Any]], str] = Field(default_factory=list)
    education: Union[List[Dict[str, Any]], str] = Field(default_factory=list)
    projects: Union[List[Dict[str, Any]], str] = Field(default_factory=list)
    awards: Union[List[Dict[str, Any]], str] = Field(default_factory=list)
    publications: Union[List[Dict[str, Any]], str] = Field(default_factory=list)

    # Generated PDFs
    resume_pdf: Optional[bytes] = None
    cover_letter_content: Optional[str] = None
    cover_letter_pdf: Optional[bytes] = None

    # Additional metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Optional fields for AI generation
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            bytes: lambda v: v.hex() if v else None,
        },
    )

    def is_latex_format(self) -> bool:
        """Check if the resume content is in LaTeX format"""
        return (
            isinstance(self.personal_information, str)
            and isinstance(self.skills, str)
            and isinstance(self.work_experience, str)
        )

    def is_structured_format(self) -> bool:
        """Check if the resume content is in structured format"""
        return (
            isinstance(self.personal_information, dict)
            and isinstance(self.skills, dict)
            and isinstance(self.work_experience, list)
        )

    def get_combined_latex(self) -> str:
        """Combine all LaTeX sections into a single document"""
        if not self.is_latex_format():
            raise ValueError("Resume content is not in LaTeX format")

        sections = [
            self.personal_information,
            self.career_summary,
            self.skills,
            self.work_experience,
            self.education,
            self.projects,
            self.awards,
            self.publications,
        ]

        return "\n\n".join(section for section in sections if section)
