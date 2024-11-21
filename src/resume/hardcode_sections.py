from src.latex.utils import LatexEscaper
from src.loaders.tex_loader import TexLoader
from src.core.database.factory import get_unit_of_work
from src.core.dto.portfolio.portfolio import PortfolioDTO

class HardcodeSections:
    def __init__(self, user_id: str):
        self.uow = get_unit_of_work()
        self.tex_loader = TexLoader()
        self.latex_escaper = LatexEscaper()
        with self.uow:
            raw_portfolio = self.uow.portfolio.get_by_user_id(user_id)
            if not raw_portfolio:
                raise ValueError(f"Portfolio not found for user {user_id}")
            self.portfolio = PortfolioDTO.from_db_model(raw_portfolio, self.latex_escaper)

    def hardcode_section(self, section: str) -> str:
        method = getattr(self, f"hardcode_{section}", None)
        if not method:
            raise ValueError(f"No hardcode method for section: {section}")
        return method()

    def hardcode_personal_information(self) -> str:
        personal_info = {
            'name': self.portfolio.personal_information.name,
            'email': self.portfolio.personal_information.email,
            'phone': self.portfolio.personal_information.phone,
            'address': self.portfolio.personal_information.address,
            'LinkedIn': self.portfolio.personal_information.linkedin,
            'GitHub': self.portfolio.personal_information.github
        }
        return self.tex_loader.safe_format_template('personal_information', 
            escape_latex=False, 
            **personal_info
        )

    def hardcode_career_summary(self) -> str:
        # Get the first job title from the list or use default
        job_title = self.portfolio.career_summary.job_titles[0] if self.portfolio.career_summary.job_titles else 'Professional'
        
        return self.tex_loader.safe_format_template(
            'career_summary',
            escape_latex=False,
            job_title=self.latex_escaper.escape_text(job_title),
            years_of_experience=str(self.portfolio.career_summary.years_of_experience),
            summary=self.latex_escaper.escape_text(self.portfolio.career_summary.default_summary)
        )

    def hardcode_skills(self) -> str:
        skills_content = ""
        for skill_category in self.portfolio.skills:
            for category, skill_list in skill_category.items():
                escaped_category = self.latex_escaper.escape_text(category)
                escaped_skills = ', '.join(map(self.latex_escaper.escape_text, skill_list))
                skills_content += f"    \\resumeSkillHeading{{{escaped_category}}}{{{escaped_skills}}}\n"
        return self.tex_loader.safe_format_template('skills', skills_content=skills_content)

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
                'Year': pub.date,
                'link': pub.description
            }
            publications_content += self.tex_loader.safe_format_template('publication_item', **pub_data)
        return self.tex_loader.safe_format_template('publications', publications_content=publications_content)
