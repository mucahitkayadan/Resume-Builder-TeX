from typing import Dict, Any, List
from loaders.json_loader import JsonLoader
from loaders.tex_loader import TexLoader
import logging
from utils.latex_utils import escape_latex

logger = logging.getLogger(__name__)

class HardcodeSections:
    def __init__(self, json_loader: JsonLoader, tex_loader: TexLoader):
        self.json_loader = json_loader
        self.tex_loader = tex_loader

    def hardcode_section(self, section: str) -> str:
        method_name = f"hardcode_{section}"
        if hasattr(self, method_name):
            return getattr(self, method_name)()
        else:
            raise ValueError(f"No hardcoding method for section: {section}")

    def hardcode_personal_information(self) -> str:
        info = self.json_loader.get_personal_information()
        return self.tex_loader.safe_format_template('personal_information', **info)

    def hardcode_career_summary(self) -> str:
        summary = self.json_loader.get_career_summary()
        job_titles = summary.get("job_titles", ["Professional"])
        
        primary_title = job_titles[0] if job_titles else "Professional"
        additional_titles = " / ".join(job_titles[1:]) if len(job_titles) > 1 else ""
        
        escaped_summary = {
            "job_title": escape_latex(primary_title),
            "additional_titles": escape_latex(additional_titles),
            "years_of_experience": escape_latex(str(summary.get("years_of_experience", "0"))),
            "summary": escape_latex(summary.get("summary", "A motivated professional seeking new opportunities."))
        }
        logging.debug(f"Escaped summary: {escaped_summary}")
        result = self.tex_loader.safe_format_template('career_summary', **escaped_summary)
        logging.debug(f"Result of hardcode_career_summary: {result}")
        logging.info("Returning from hardcode_career_summary")
        return result

    def hardcode_skills(self) -> str:
        skills = self.json_loader.get_skills()
        skills_content = ""
        for category, skill_list in skills.items():
            escaped_category = escape_latex(category)
            escaped_skills = ', '.join(map(escape_latex, skill_list))
            skills_content += f"    \\resumeSkillHeading{{{escaped_category}}}{{{escaped_skills}}}\n"
        return self.tex_loader.safe_format_template('skills', skills_content=skills_content)

    def hardcode_work_experience(self) -> str:
        experiences = self.json_loader.get_work_experience()
        experience_content = ""
        for exp in experiences:
            responsibilities = exp.pop('responsibilities', [])
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

    def hardcode_education(self) -> str:
        education = self.json_loader.get_education()
        education_content = "\\resumeSubHeadingListStart\n"
        for edu in education:
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

    def hardcode_projects(self) -> str:
        projects = self.json_loader.get_projects()
        projects_content = "\\resumeSubHeadingListStart\n"
        for project in projects:
            bullet_points = project.pop('bullet_points', [])
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

    def hardcode_awards(self) -> str:
        awards = self.json_loader.get_awards()
        awards_content = ""
        for award in awards:
            award_data = {
                'name': escape_latex(award['name']),
                'explanation': escape_latex(award['explanation'])
            }
            awards_content += self.tex_loader.safe_format_template('award_item', **award_data)
        return self.tex_loader.safe_format_template('awards', awards_content=awards_content)

    def hardcode_publications(self) -> str:
        publications = self.json_loader.get_publications()
        publications_content = ""
        for pub in publications:
            pub_data = {
                'name': escape_latex(pub['name']),
                'publisher': escape_latex(pub['publisher']),
                'Year': escape_latex(pub['Year']),
                'link': escape_latex(pub['link'])
            }
            publications_content += self.tex_loader.safe_format_template('publication_item', **pub_data)
        return self.tex_loader.safe_format_template('publications', publications_content=publications_content)
