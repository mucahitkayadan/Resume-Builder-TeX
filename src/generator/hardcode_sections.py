from typing import Optional, Dict, Any
from src.latex.utils import LatexEscaper
from src.loaders.tex_loader import TexLoader
from src.core.database.factory import get_unit_of_work
from src.core.dto.portfolio.portfolio import PortfolioDTO
from src.core.exceptions.database_exceptions import DatabaseError
import logging

logger = logging.getLogger(__name__)

class HardcodeSections:
    """Class to handle hardcoded sections from portfolio"""
    
    def __init__(self, user_id: str):
        """Initialize with user_id and load portfolio data"""
        self.user_id = user_id
        self.portfolio = None
        self.tex_loader = TexLoader()
        
        # Load portfolio data
        with get_unit_of_work() as uow:
            raw_portfolio = uow.portfolios.get_by_user_id(user_id)
            raw_profile = uow.profiles.get_by_user_id(user_id)
            
            if not raw_portfolio:
                logger.error(f"Portfolio not found for user {user_id}")
                raise DatabaseError(f"Portfolio not found for user {user_id}")
                
            if not raw_profile:
                logger.error(f"Profile not found for user {user_id}")
                raise DatabaseError(f"Profile not found for user {user_id}")
            
            self.portfolio = PortfolioDTO.from_db_models(raw_portfolio, raw_profile)
            logger.debug(f"Loaded portfolio data for user {user_id}")

    def hardcode_section(self, section: str) -> str:
        """Get hardcoded LaTeX content for a specific section"""
        logger.debug(f"Starting hardcode for section: {section}")
        method = getattr(self, f"hardcode_{section}", None)
        if not method:
            logger.error(f"No hardcode method found for section: {section}")
            raise ValueError(f"No hardcode method for section: {section}")
        
        try:
            content = method()
            if content:
                logger.debug(f"Successfully hardcoded section {section}, content length: {len(content)}")
                return content
            else:
                logger.warning(f"Hardcode method returned empty content for section {section}")
                return ""
        except Exception as e:
            logger.error(f"Error in hardcode method for section {section}: {str(e)}", exc_info=True)
            raise

    def hardcode_personal_information(self) -> str:
        logger.debug("Hardcoding personal information")
        try:
            personal_info = self.portfolio.get_personal_information()
            logger.debug(f"Raw personal info: {personal_info}")
            
            # Convert keys to match template expectations with safe access
            template_info = {
                'name': personal_info.get('name', ''),
                'phone': personal_info.get('phone', ''),
                'email': personal_info.get('email', ''),
                'LinkedIn': personal_info.get('linkedin', ''),
                'GitHub': personal_info.get('github', ''),
                'website': personal_info.get('website', ''),
                'address': personal_info.get('address', '')
            }
            
            # Verify all required fields are present
            missing_fields = [k for k, v in template_info.items() if not v]
            if missing_fields:
                logger.warning(f"Missing personal information fields: {missing_fields}")
            
            logger.debug(f"Template info data: {template_info}")
            content = self.tex_loader.safe_format_template('personal_information', 
                escape_latex=False, 
                **template_info
            )
            logger.debug(f"Generated personal info content length: {len(content)}")
            return content
        except Exception as e:
            logger.error(f"Error in hardcode_personal_information: {str(e)}", exc_info=True)
            raise

    def hardcode_career_summary(self) -> str:
        logger.debug("Hardcoding career summary")
        try:
            job_title = self.portfolio.career_summary.get('job_titles', ['Professional'])[0]
            logger.debug(f"Using job title: {job_title}")
            
            content = self.tex_loader.safe_format_template(
                'career_summary',
                escape_latex=False,
                job_title=LatexEscaper.escape_text(job_title),
                years_of_experience=str(self.portfolio.career_summary.get('years_of_experience', '')),
                summary=LatexEscaper.escape_text(self.portfolio.career_summary.get('default_summary', ''))
            )
            logger.debug(f"Generated career summary content length: {len(content)}")
            return content
        except Exception as e:
            logger.error(f"Error in hardcode_career_summary: {str(e)}", exc_info=True)
            raise

    def hardcode_skills(self) -> str:
        logger.debug("Hardcoding skills")
        try:
            skills_content = ""
            for skill_category in self.portfolio.skills:
                for category, skill_list in skill_category.items():
                    escaped_category = LatexEscaper.escape_text(category)
                    escaped_skills = ', '.join(map(LatexEscaper.escape_text, skill_list))
                    skills_content += f"    \\resumeSkillHeading{{{escaped_category}}}{{{escaped_skills}}}\n"
                    logger.debug(f"Added skill category: {category} with {len(skill_list)} skills")
            
            content = self.tex_loader.safe_format_template('skills', skills_content=skills_content)
            logger.debug(f"Generated skills content length: {len(content)}")
            return content
        except Exception as e:
            logger.error(f"Error in hardcode_skills: {str(e)}", exc_info=True)
            raise

    def hardcode_work_experience(self) -> str:
        experience_content = ""
        for exp in self.portfolio.work_experience:
            responsibilities = exp.get('responsibilities', [])
            responsibilities_content = "\n".join([
                f"        \\resumeItem{{{LatexEscaper.escape_text(r)}}}"
                for r in responsibilities
            ])
            exp_data = {
                'job_title': LatexEscaper.escape_text(exp.get('job_title', '')),
                'time': LatexEscaper.escape_text(exp.get('time', '')),
                'company': LatexEscaper.escape_text(exp.get('company', '')),
                'location': LatexEscaper.escape_text(exp.get('location', '')),
                'responsibilities': responsibilities_content
            }
            exp_content = self.tex_loader.safe_format_template('work_experience_item', **exp_data)
            experience_content += exp_content
        return self.tex_loader.safe_format_template('work_experience', experience_content=experience_content)

    def hardcode_education(self) -> str:
        education_content = "\\resumeSubHeadingListStart\n"
        for edu in self.portfolio.education:
            edu_data = {
                'university': LatexEscaper.escape_text(edu.get('university_name', '')),
                'location': LatexEscaper.escape_text(edu.get('location', '')),
                'degree': LatexEscaper.escape_text(f"{edu.get('degree_type', '')} in {edu.get('degree', '')}".strip()),
                'time': LatexEscaper.escape_text(edu.get('time', '')),
                'key_courses': LatexEscaper.escape_text(f"Key Courses: {', '.join(edu.get('transcript', []))}")
            }
            education_content += self.tex_loader.safe_format_template('education_item', **edu_data)
        education_content += "\\resumeSubHeadingListEnd"
        return self.tex_loader.safe_format_template('education', education_content=education_content)

    def hardcode_projects(self) -> str:
        projects_content = "\\resumeSubHeadingListStart\n"
        for project in self.portfolio.projects:
            bullet_points_content = "\n".join([
                f"    \\resumeItem{{{LatexEscaper.escape_text(point)}}}"
                for point in project.get('bullet_points', [])
            ])
            
            name_and_tech = LatexEscaper.escape_text(project.get('name', ''))
            if project.get('technologies'):
                name_and_tech += f" \\textbullet{{}} {LatexEscaper.escape_text(project['technologies'])}"
            
            project_data = {
                'name_and_tech': name_and_tech,
                'date': LatexEscaper.escape_text(project.get('date', '')),
                'bullet_points': bullet_points_content
            }
            projects_content += self.tex_loader.safe_format_template('project_item', **project_data)
        projects_content += "\\resumeSubHeadingListEnd"
        return projects_content

    def hardcode_awards(self) -> str:
        awards_content = ""
        for award in self.portfolio.awards:
            award_data = {
                'name': LatexEscaper.escape_text(award.get('name', '')),
                'explanation': LatexEscaper.escape_text(award.get('explanation', ''))
            }
            awards_content += self.tex_loader.safe_format_template('award_item', **award_data)
        return self.tex_loader.safe_format_template('awards', awards_content=awards_content)

    def hardcode_publications(self) -> str:
        publications_content = ""
        for pub in self.portfolio.publications:
            pub_data = {
                'name': LatexEscaper.escape_text(pub.get('name', '')),
                'publisher': LatexEscaper.escape_text(pub.get('publisher', '')),
                'time': LatexEscaper.escape_text(pub.get('time', '')),
                'link': LatexEscaper.escape_text(pub.get('link', ''))
            }
            publications_content += self.tex_loader.safe_format_template('publication_item', **pub_data)
        return self.tex_loader.safe_format_template('publications', publications_content=publications_content)
