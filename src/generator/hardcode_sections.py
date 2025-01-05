from src.latex.utils import LatexEscaper
from src.loaders.tex_loader import TexLoader
from src.core.database.factory import get_unit_of_work
from src.core.dto.portfolio.portfolio import PortfolioDTO
import logging

logger = logging.getLogger(__name__)

class HardcodeSections:
    def __init__(self, user_id: str):
        logger.debug(f"Initializing HardcodeSections for user {user_id}")
        self.uow = get_unit_of_work()
        self.tex_loader = TexLoader()
        with self.uow:
            raw_portfolio = self.uow.portfolio.get_by_user_id(user_id)
            if not raw_portfolio:
                logger.error(f"Portfolio not found for user {user_id}")
                raise ValueError(f"Portfolio not found for user {user_id}")
            self.portfolio = PortfolioDTO.from_db_model(raw_portfolio)
            logger.debug("Successfully loaded portfolio")

    def hardcode_section(self, section: str) -> str:
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
            personal_info = {
                'name': self.portfolio.personal_information.name,
                'email': self.portfolio.personal_information.email,
                'phone': self.portfolio.personal_information.phone,
                'address': self.portfolio.personal_information.address,
                'LinkedIn': self.portfolio.personal_information.linkedin,
                'GitHub': self.portfolio.personal_information.github,
                'website': self.portfolio.personal_information.website
            }
            logger.debug(f"Personal info data: {personal_info}")
            content = self.tex_loader.safe_format_template('personal_information', 
                escape_latex=False, 
                **personal_info
            )
            logger.debug(f"Generated personal info content length: {len(content)}")
            return content
        except Exception as e:
            logger.error(f"Error in hardcode_personal_information: {str(e)}", exc_info=True)
            raise

    def hardcode_career_summary(self) -> str:
        logger.debug("Hardcoding career summary")
        try:
            job_title = self.portfolio.career_summary.job_titles[0] if self.portfolio.career_summary.job_titles else 'Professional'
            logger.debug(f"Using job title: {job_title}")
            
            content = self.tex_loader.safe_format_template(
                'career_summary',
                escape_latex=False,
                job_title=LatexEscaper.escape_text(job_title),
                years_of_experience=str(self.portfolio.career_summary.years_of_experience),
                summary=LatexEscaper.escape_text(self.portfolio.career_summary.default_summary)
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
            responsibilities = exp.responsibilities
            responsibilities_content = "\n".join([
                f"        \\resumeItem{{{r}}}"
                for r in responsibilities
            ])
            exp_data = {
                'job_title': exp.job_title,
                'time': exp.time,
                'company': exp.company,
                'location': exp.location,
                'responsibilities': responsibilities_content
            }
            exp_content = self.tex_loader.safe_format_template('work_experience_item', **exp_data)
            experience_content += exp_content
        return self.tex_loader.safe_format_template('work_experience', experience_content=experience_content)

    def hardcode_education(self) -> str:
        education_content = "\\resumeSubHeadingListStart\n"
        for edu in self.portfolio.education:
            edu_data = {
                'university': edu.university_name,
                'location': edu.location,
                'degree': f"{edu.degree_type} in {edu.degree}".strip(),
                'time': edu.time,
                'key_courses': f"Key Courses: {', '.join(edu.transcript)}"
            }
            education_content += self.tex_loader.safe_format_template('education_item', **edu_data)
        education_content += "\\resumeSubHeadingListEnd"
        return self.tex_loader.safe_format_template('education', education_content=education_content)

    def hardcode_projects(self) -> str:
        projects_content = "\\resumeSubHeadingListStart\n"
        for project in self.portfolio.projects:
            bullet_points_content = "\n".join([
                f"    \\resumeItem{{{point}}}"
                for point in project.bullet_points
            ])
            
            name_and_tech = f"{project.name}" + (f" \\textbullet{{}} {project.technologies}" if project.technologies else "")
            
            project_data = {
                'name_and_tech': name_and_tech,
                'date': project.date,
                'bullet_points': bullet_points_content
            }
            project_content = self.tex_loader.safe_format_template('project_item', **project_data)
            projects_content += project_content
        projects_content += "\\resumeSubHeadingListEnd"
        return projects_content

    def hardcode_awards(self) -> str:
        awards_content = ""
        for award in self.portfolio.awards:
            award_data = {
                'name': award.name,
                'explanation': award.explanation
            }
            awards_content += self.tex_loader.safe_format_template('award_item', **award_data)
        return self.tex_loader.safe_format_template('awards', awards_content=awards_content)

    def hardcode_publications(self) -> str:
        publications_content = ""
        for pub in self.portfolio.publications:
            pub_data = {
                'name': pub.name,
                'publisher': pub.publisher,
                'time': pub.time,
                'link': pub.link
            }
            publications_content += self.tex_loader.safe_format_template('publication_item', **pub_data)
        return self.tex_loader.safe_format_template('publications', publications_content=publications_content)
