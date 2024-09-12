from openai import OpenAI
import os
from typing import Any, Dict, List, Union
import re

class OpenAIRunner:
    """
    A class to handle interactions with the OpenAI API for processing various sections of a resume.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        """
        Initialize the OpenAIRunner.

        Args:
            model (str): The name of the OpenAI model to use. Defaults to "gpt-4".
        """
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        """
        Process a section of the resume using the OpenAI API.

        Args:
            prompt (str): The system prompt to guide the AI's response.
            data (str): The content to be processed.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed content returned by the AI.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer. Do not add external text to your answers, answer only with asked latex content, no introduction or explanation."},
                    {"role": "user", "content": f"Prompt: {prompt}\n\nData: {data}\n\nJob Description: {job_description}"}
                ],
                temperature=0.2,  # Lower temperature for more focused outputs
                presence_penalty=-0.5,  # Discourage introducing new topics
                frequency_penalty=0.5   # Encourage diversity in word choice
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error processing section: {e}")
            return ""

    def process_personal_information(self, prompt: str, personal_info: Dict[str, str], job_description: str) -> str:
        """
        Process the personal information section of the resume.

        Args:
            prompt (str): The system prompt for processing personal information.
            personal_info (Dict[str, str]): A dictionary containing personal information details.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed personal information content.
        """
        return self.process_section(prompt, str(personal_info), job_description)

    # def process_header(self, prompt: str, personal_info: Dict[str, str], job_description: str) -> str:
    #     """
    #     Process the header section of the resume.
    #
    #     Args:
    #         prompt (str): The system prompt for processing the header.
    #         personal_info (Dict[str, str]): A dictionary containing personal information.
    #         job_description (str): The job description to be included in the processing.
    #
    #     Returns:
    #         str: The processed header content.
    #     """
    #     return self.process_section(prompt, str(personal_info), job_description)

    def process_career_summary(self, prompt: str, data: dict, job_description: str) -> str:
        # Extract job titles and years of experience from the career_summary dict
        job_titles = ', '.join(data.get('job_titles', []))
        years_experience = data.get('years_of_experience', '')

        # Prepare the prompt with career summary information
        prepared_prompt = prompt.replace('{{job_titles}}', job_titles)
        prepared_prompt = prepared_prompt.replace('{{years_of_experience}}', years_experience)

        # Process the section using the prepared prompt and job description
        return self.process_section(prepared_prompt, '', job_description)

        # Escape special LaTeX characters in the summary
        # special_chars = ['%', '&', '#', '$', '_', '{', '}', '~', '^', '\\']
        # for char in special_chars:
        #     summary = summary.replace(char, f'\\{char}')
        # Format the response to match the LaTeX command
        # formatted_response = f"\\careerSummary{{{selected_job_title}}}{{{generated_years_experience}}}{{{summary}}}"

    def process_work_experience(self, prompt: str, work_experience: List[Dict[str, Any]], job_description: str) -> str:
        """
        Process the work experience section of the resume.

        Args:
            prompt (str): The system prompt for processing work experience.
            work_experience (List[Dict[str, Any]]): A list of dictionaries containing work experience details.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed work experience content.
        """
        return self.process_section(prompt, str(work_experience), job_description)

    def process_skills(self, prompt: str, skills: Dict[str, Any], job_description: str) -> str:
        """
        Process the skills section of the resume.

        Args:
            prompt (str): The system prompt for processing the skills.
            skills (List[str]): A list of skills.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed skills content.
        """
        return self.process_section(prompt, str(skills), job_description)

    def process_education(self, prompt: str, education: List[Dict[str, str]], job_description: str) -> str:
        """
        Process the education section of the resume.

        Args:
            prompt (str): The system prompt for processing education.
            education (List[Dict[str, str]]): A list of dictionaries containing education details.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed education content.
        """
        return self.process_section(prompt, str(education), job_description)

    def process_projects(self, prompt: str, projects: List[Dict[str, Union[str, List[str]]]], job_description: str) -> str:
        """
        Process the projects section of the resume.

        Args:
            prompt (str): The system prompt for processing projects.
            projects (List[Dict[str, Union[str, List[str]]]]): A list of dictionaries containing project details.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed projects content.
        """
        return self.process_section(prompt, str(projects), job_description)

    def process_awards(self, prompt: str, awards: List[Dict[str, str]], job_description: str) -> str:
        """
        Process the awards section of the resume.

        Args:
            prompt (str): The system prompt for processing awards.
            awards (List[Dict[str, str]]): A list of dictionaries containing award details.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed awards content.
        """
        return self.process_section(prompt, str(awards), job_description)

    def process_publications(self, prompt: str, publications: List[Dict[str, str]], job_description: str) -> str:
        """
        Process the publications section of the resume.

        Args:
            prompt (str): The system prompt for processing publications.
            publications (List[Dict[str, str]]): A list of dictionaries containing publication details.
            job_description (str): The job description to be included in the processing.

        Returns:
            str: The processed publications content.
        """
        return self.process_section(prompt, str(publications), job_description)

    def process_job_titles(self, prompt: str, job_titles: List[str], job_description: str) -> str:
        return self.process_section(prompt, str(job_titles), job_description)
