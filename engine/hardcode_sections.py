from typing import Dict, Any, List
from core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork
from loaders.tex_loader import TexLoader
import logging
from utils.latex_utils import escape_latex

logger = logging.getLogger(__name__)

class HardcodeSections:
    def __init__(self, uow: MongoUnitOfWork, tex_loader: TexLoader):
        self.uow = uow
        self.tex_loader = tex_loader

    def hardcode_section(self, section: str, user_id: str) -> str:
        method_name = f"hardcode_{section}"
        if hasattr(self, method_name):
            return getattr(self, method_name)(user_id)
        else:
            raise ValueError(f"No hardcoding method for section: {section}")

    def get_portfolio(self, user_id: str):
        with self.uow:
            portfolio = self.uow.portfolio.get_by_user_id(user_id)
            if not portfolio:
                raise ValueError(f"Portfolio not found for user {user_id}")
            return portfolio

    def hardcode_personal_information(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        return self.tex_loader.safe_format_template('personal_information', **portfolio.personal_information)

    def hardcode_career_summary(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        personal_info = portfolio.personal_information
        
        return self.tex_loader.safe_format_template(
            'career_summary', 
            summary=escape_latex(portfolio.career_summary),
            job_title=escape_latex(personal_info.get('job_title', 'Professional')),
            years_of_experience=escape_latex(str(personal_info.get('years_of_experience', '5+')))
        )

    def hardcode_skills(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        skills_content = ""
        for skill_category in portfolio.skills:
            for category, skill_list in skill_category.items():
                escaped_category = escape_latex(category)
                escaped_skills = ', '.join(map(escape_latex, skill_list))
                skills_content += f"    \\resumeSkillHeading{{{escaped_category}}}{{{escaped_skills}}}\n"
        return self.tex_loader.safe_format_template('skills', skills_content=skills_content)

    def hardcode_work_experience(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        experience_content = ""
        for exp in portfolio.work_experience:
            responsibilities = exp.get('responsibilities', [])
            responsibilities_content = "\n".join([f"        \\resumeItem{{{escape_latex(r)}}}" for r in responsibilities])
            exp_data = {
                'job_title': escape_latex(exp.get('job_title', '')),
                'time': escape_latex(exp.get('time', '')),
                'company': escape_latex(exp.get('company', '')),
                'location': escape_latex(exp.get('location', '')),
                'responsibilities': responsibilities_content
            }
            exp_content = self.tex_loader.safe_format_template('work_experience_item', **exp_data)
            experience_content += exp_content
        return self.tex_loader.safe_format_template('work_experience', experience_content=experience_content)

    def hardcode_education(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        education_content = "\\resumeSubHeadingListStart\n"
        for edu in portfolio.education:
            edu_data = {
                'university': escape_latex(edu.get('university_name', 'University Name')),
                'location': escape_latex(edu.get('location', '')),
                'degree': escape_latex(f"{edu.get('degree_type', '')} in {edu.get('degree', '')}".strip()),
                'time': escape_latex(edu.get('time', '')),
                'key_courses': escape_latex(f"Key Courses: {', '.join(edu.get('transcript', []))}")
            }
            education_content += self.tex_loader.safe_format_template('education_item', **edu_data)
        education_content += "\\resumeSubHeadingListEnd"
        return self.tex_loader.safe_format_template('education', education_content=education_content)

    def hardcode_projects(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        projects_content = "\\resumeSubHeadingListStart\n"
        for project in portfolio.projects:
            bullet_points = project.get('bullet_points', [])
            bullet_points_content = "\n".join([f"    \\resumeItem{{{escape_latex(point)}}}" for point in bullet_points])
            
            name = escape_latex(project.get('name', ''))
            technologies = escape_latex(project.get('technologies', ''))
            
            # Separate name and technologies
            name_and_tech = f"{name}" + (f" \\textbullet{{}} {technologies}" if technologies else "")
            
            project_data = {
                'name_and_tech': name_and_tech,
                'date': escape_latex(project.get('date', '')),
                'bullet_points': bullet_points_content
            }
            project_content = self.tex_loader.safe_format_template('project_item', **project_data)
            projects_content += project_content
        projects_content += "\\resumeSubHeadingListEnd"
        return self.tex_loader.safe_format_template('projects', projects_content=projects_content)

    def hardcode_awards(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        awards_content = ""
        for award in portfolio.awards:
            award_data = {
                'name': escape_latex(award['name']),
                'explanation': escape_latex(award['explanation'])
            }
            awards_content += self.tex_loader.safe_format_template('award_item', **award_data)
        return self.tex_loader.safe_format_template('awards', awards_content=awards_content)

    def hardcode_publications(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        publications_content = ""
        for pub in portfolio.publications:
            pub_data = {
                'name': escape_latex(pub['name']),
                'publisher': escape_latex(pub['publisher']),
                'Year': escape_latex(pub['Year']),
                'link': escape_latex(pub['link'])
            }
            publications_content += self.tex_loader.safe_format_template('publication_item', **pub_data)
        return self.tex_loader.safe_format_template('publications', publications_content=publications_content)
