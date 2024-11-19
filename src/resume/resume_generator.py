import logging
from typing import Dict, Generator, Tuple

from src.core.database.models.resume import Resume
from src.llms.runner import LLMRunner
from src.latex.resume.resume_compiler import ResumeLatexCompiler
from src.loaders.prompt_loader import PromptLoader
from src.loaders.tex_loader import TexLoader
from src.resume.hardcode_sections import HardcodeSections
from src.resume.utils.file_ops import create_output_directory, save_job_description
from src.loaders.portfolio_loader import PortfolioLoader
from src.core.database.factory import get_unit_of_work

logger = logging.getLogger(__name__)

class ResumeGenerator:
    """
    A class for generating resumes based on job descriptions using AI models.
    
    This class handles the entire process of resume generation, including
    content creation, PDF generation, and database storage.
    """

    def __init__(self, llm_runner: LLMRunner, user_id: str):
        """Initialize the ResumeGenerator with necessary parts."""
        self.llm_runner = llm_runner
        self.uow = get_unit_of_work()
        self.user_id = user_id
        self.prompt_loader = PromptLoader()
        self.tex_loader = TexLoader()
        self.portfolio_loader = PortfolioLoader(self.user_id)
        self.hardcoder = HardcodeSections(self.user_id)
        self.latex_compiler = ResumeLatexCompiler()

    def generate_resume(self,
                        job_description: str,
                        selected_sections: Dict[str, str]) -> Generator[Tuple[str, float], None, Resume]:
        """
        Generate a résumé based on the provided job description and settings.
        
        Args:
            job_description: Job description text
            selected_sections: Dictionary of sections to process
            
        Yields:
            Tuple of (status message, progress percentage)
        Returns:
            Resume: The generated resume object
        """
        logger.info("Starting resume generation process")
        logger.info(f"Using LLM strategy: {self.llm_runner.strategy.__class__.__name__}")
        logger.info(f"Selected sections: {selected_sections}")
        
        progress = 0.0  # Initialize progress here
        
        try:
            # Initial progress
            yield "Starting resume generation...", progress
            
            company_name, job_title = self.llm_runner.create_company_name_and_job_title(
                self.prompt_loader.get_folder_name_prompt(), 
                job_description
            )
            logger.info(f"Generated company name: {company_name}, job title: {job_title}")
            progress = 0.2
            yield f"Created folder for {company_name} - {job_title}", progress
            
            # Process sections
            content_dict = {}
            total_sections = len(selected_sections)
            for i, (section, process_type) in enumerate(selected_sections.items(), 1):
                try:
                    content = self.process_section(section, process_type, job_description)
                    if content:
                        content_dict[section] = content
                        logger.info(f"Processed {section} section")
                    progress = 0.2 + (0.6 * (i / total_sections))  # Progress from 20% to 80%
                    yield f"Processed {section} section", progress
                except Exception as e:
                    logger.error(f"Failed to process section {section}: {e}")
                    yield f"Error processing {section}", progress
            
            # Generate and save resume
            yield "Generating final PDF...", 0.9
            resume = self._generate_and_save_resume(
                content_dict=content_dict,
                job_description=job_description,
                company_name=company_name,
                job_title=job_title
            )
            logger.info(f"Resume generated and saved with ID: {resume.id}")
            yield "Resume generation complete!", 1.0
            return resume
            
        except Exception as e:
            logger.error(f"Resume generation failed: {str(e)}", exc_info=True)
            yield f"Error: {str(e)}", 1.0
            raise

    def _process_sections(self,
                          selected_sections: Dict[str, str],
                          job_description: str) -> Generator[Tuple[str, float], None, Dict[str, str]]:
        """Process each selected section.
        
        Args:
            selected_sections: Dictionary mapping section names to their process type
            job_description: The job description text
            
        Yields:
            Tuple[str, float]: Status message and progress percentage
            
        Returns:
            Dict[str, str]: Dictionary of processed section content
        """
        content_dict = {}

        for i, (section, process_type) in enumerate(selected_sections.items()):
            try:
                content = self.process_section(section, process_type, job_description)
                if content:
                    content_dict[section] = content
                    logger.info(f"Processed {section} section")
                yield f"Processed {section} section", (i + 1) / len(selected_sections)
            except Exception as e:
                logger.error(f"Failed to process section {section}: {e}")
                yield f"Error processing {section}: {str(e)}", (i + 1) / len(selected_sections)
        
        return content_dict

    def _generate_and_save_resume(self,
                                  content_dict: Dict[str, str],
                                  job_description: str,
                                  company_name: str,
                                  job_title: str) -> Resume:
        """Generate PDF and save resume to database."""
        try:
            # Create output directory and save job description
            output_dir = create_output_directory(company_name, job_title)
            save_job_description(job_description, output_dir)
            
            # Generate PDF
            generated_pdf = self.latex_compiler.generate_pdf(content_dict, output_dir)
            if not generated_pdf:
                raise Exception("PDF generation failed")

            # Create resume object
            resume = Resume(
                id=None,
                user_id=self.user_id,
                company_name=company_name,
                job_title=job_title,
                job_description=job_description,
                **content_dict,
                resume_pdf=generated_pdf,
                model_type=self.llm_runner.get_config().get('type'),
                model_name=self.llm_runner.strategy.__class__.__name__,
                temperature=self.llm_runner.get_config().get('temperature')
            )

            # Save to database
            with self.uow:
                self.uow.resumes.add(resume)
                self.uow.commit()

            return resume
            
        except Exception as e:
            logger.error(f"Failed to generate and save resume: {e}")
            raise

    def process_section(self,
                        section: str,
                        process_type: str,
                        job_description: str) -> str:
        """Process a single section based on the process type."""
        if process_type == "skip":
            return ""
        elif process_type == "hardcode":
            return self.hardcoder.hardcode_section(section)
        elif process_type == "process":
            # Get the prompt template for this section
            prompt = self.prompt_loader.get_section_prompt(section)
            
            # Get the section data using portfolio_loader
            section_data = self.portfolio_loader.get_section_data(section)
            if not section_data:
                raise ValueError(f"Section {section} not found in portfolio")
            
            # Format skills data if this is the skills section
            if section == 'skills':
                formatted_data = []
                for skill_category in section_data:
                    for category, skills in skill_category.items():
                        formatted_data.append(f"{category}:\n- {', '.join(skills)}")
                section_data = "\n\n".join(formatted_data)
            else:
                section_data = str(section_data)
            
            # Generate content using the prompt and portfolio data
            return self.llm_runner.generate_content(prompt, section_data, job_description)
        else:
            raise ValueError(f"Invalid process type: {process_type}")