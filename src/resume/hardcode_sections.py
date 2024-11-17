from src.latex.utils import LatexEscaper
from src.loaders.tex_loader import TexLoader
from src.core.database.factory import get_unit_of_work

class HardcodeSections:
    def __init__(self):
        self.uow = get_unit_of_work()
        self.tex_loader = TexLoader()
        self.latex_escaper = LatexEscaper()
        
    def hardcode_section(self, section: str, user_id: str) -> str:
        method = getattr(self, f"hardcode_{section}", None)
        if not method:
            raise ValueError(f"No hardcode method for section: {section}")
        return method(user_id)

    def get_portfolio(self, user_id: str):
        with self.uow:
            portfolio = self.uow.portfolio.get_by_user_id(user_id)
            if not portfolio:
                raise ValueError(f"Portfolio not found for user {user_id}")
            return portfolio

    def hardcode_personal_information(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        return self.tex_loader.safe_format_template('personal_information', 
            escape_latex=False, 
            **portfolio.personal_information
        )

    def hardcode_career_summary(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        personal_info = portfolio.personal_information
        
        return self.tex_loader.safe_format_template(
            'career_summary',
            escape_latex=False,
            job_title=self.latex_escaper.escape_text(personal_info.get('job_title', 'Professional')),
            years_of_experience=str(personal_info.get('years_of_experience', '5+')),
            summary=self.latex_escaper.escape_text(portfolio.career_summary)
        )

    def hardcode_skills(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        skills_content = ""
        for skill_category in portfolio.skills:
            for category, skill_list in skill_category.items():
                escaped_category = self.latex_escaper.escape_text(category)
                escaped_skills = ', '.join(map(self.latex_escaper.escape_text, skill_list))
                skills_content += f"    \\resumeSkillHeading{{{escaped_category}}}{{{escaped_skills}}}\n"
        return self.tex_loader.safe_format_template('skills', skills_content=skills_content)

    def hardcode_work_experience(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        experience_content = ""
        for exp in portfolio.work_experience:
            responsibilities = exp.get('responsibilities', [])
            responsibilities_content = "\n".join([
                f"        \\resumeItem{{{self.latex_escaper.escape_text(r)}}}"
                for r in responsibilities
            ])
            exp_data = {
                'job_title': self.latex_escaper.escape_text(exp.get('job_title', '')),
                'time': self.latex_escaper.escape_text(exp.get('time', '')),
                'company': self.latex_escaper.escape_text(exp.get('company', '')),
                'location': self.latex_escaper.escape_text(exp.get('location', '')),
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
                'university': self.latex_escaper.escape_text(edu.get('university_name', 'University Name')),
                'location': self.latex_escaper.escape_text(edu.get('location', '')),
                'degree': self.latex_escaper.escape_text(f"{edu.get('degree_type', '')} in {edu.get('degree', '')}".strip()),
                'time': self.latex_escaper.escape_text(edu.get('time', '')),
                'key_courses': self.latex_escaper.escape_text(f"Key Courses: {', '.join(edu.get('transcript', []))}")
            }
            education_content += self.tex_loader.safe_format_template('education_item', **edu_data)
        education_content += "\\resumeSubHeadingListEnd"
        return self.tex_loader.safe_format_template('education', education_content=education_content)

    def hardcode_projects(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        projects_content = "\\resumeSubHeadingListStart\n"
        for project in portfolio.projects:
            bullet_points = project.get('bullet_points', [])
            bullet_points_content = "\n".join([
                f"    \\resumeItem{{{self.latex_escaper.escape_text(point)}}}"
                for point in bullet_points
            ])
            
            name = self.latex_escaper.escape_text(project.get('name', ''))
            technologies = self.latex_escaper.escape_text(project.get('technologies', ''))
            
            # Separate name and technologies
            name_and_tech = f"{name}" + (f" \\textbullet{{}} {technologies}" if technologies else "")
            
            project_data = {
                'name_and_tech': name_and_tech,
                'date': self.latex_escaper.escape_text(project.get('date', '')),
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
                'name': self.latex_escaper.escape_text(award['name']),
                'explanation': self.latex_escaper.escape_text(award['explanation'])
            }
            awards_content += self.tex_loader.safe_format_template('award_item', **award_data)
        return self.tex_loader.safe_format_template('awards', awards_content=awards_content)

    def hardcode_publications(self, user_id: str) -> str:
        portfolio = self.get_portfolio(user_id)
        publications_content = ""
        for pub in portfolio.publications:
            pub_data = {
                'name': self.latex_escaper.escape_text(pub['name']),
                'publisher': self.latex_escaper.escape_text(pub['publisher']),
                'Year': self.latex_escaper.escape_text(pub['Year']),
                'link': self.latex_escaper.escape_text(pub['link'])
            }
            publications_content += self.tex_loader.safe_format_template('publication_item', **pub_data)
        return self.tex_loader.safe_format_template('publications', publications_content=publications_content)

    # ... continue with other methods following the same pattern