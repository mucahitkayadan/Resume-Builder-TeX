import logging
from typing import Dict, Generator, Tuple

from src.core.database.models.resume import Resume
from src.llms.runner import LLMRunner
from src.latex.resume.resume_compiler import ResumeLatexCompiler
from src.loaders.prompt_loader import PromptLoader
from src.loaders.tex_loader import TexLoader
from src.resume.hardcode_sections import HardcodeSections
from src.loaders.portfolio_loader import PortfolioLoader
from src.core.database.factory import get_unit_of_work
from src.resume.utils.output_manager import OutputManager

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
                        selected_sections: Dict[str, str],
                        output_manager: OutputManager):
        """Generate a résumé based on the provided job description and settings."""
        logger.info("Starting resume generation process")
        
        try:
            # Save job description
            output_manager.save_job_description(job_description)
            logger.debug("Saved job description")
            
            # Initialize all sections with empty strings
            all_sections = {
                'personal_information': '',
                'career_summary': '',
                'skills': '',
                'work_experience': '',
                'education': '',
                'projects': '',
                'awards': '',
                'publications': ''
            }
            
            # Process each section
            total_sections = len(selected_sections)
            logger.debug(f"Processing {total_sections} sections")
            
            for i, (section, process_type) in enumerate(selected_sections.items(), 1):
                progress = i / (total_sections + 1)  # +1 for PDF generation
                logger.debug(f"Processing section {section} with type {process_type}")
                yield f"Processing {section}...", progress
                
                if process_type != 'skip':
                    try:
                        content = self.process_section(section, process_type, job_description)
                        if content and content.strip():  # Check for non-empty content
                            all_sections[section] = content
                            logger.debug(f"Successfully processed section {section}")
                        else:
                            logger.warning(f"No content generated for section {section}")
                    except Exception as e:
                        logger.error(f"Error processing section {section}: {str(e)}", exc_info=True)
                        raise
                else:
                    logger.debug(f"Skipping section {section}")

            # Check if we have at least one non-empty required section
            required_sections = ['personal_information', 'career_summary', 'skills']
            has_required_content = any(
                all_sections[section].strip() 
                for section in required_sections
            )
            
            if not has_required_content:
                logger.error("No content for required sections (personal_information, career_summary, or skills)")
                raise ValueError("Missing required resume sections")

            # Generate and save resume
            logger.info("Generating and saving resume")
            resume = self._generate_and_save_resume(
                content_dict=all_sections,
                output_manager=output_manager
            )
            
            if not resume:
                logger.error("Resume generation returned None")
                raise ValueError("Resume generation failed")
            
            logger.info(f"Resume generated successfully with ID: {resume.id}")
            yield "Resume generated successfully!", 1.0
            yield resume

        except Exception as e:
            logger.error(f"Failed to generate resume: {str(e)}", exc_info=True)
            raise

    def _generate_and_save_resume(self, content_dict: Dict[str, str], output_manager: OutputManager) -> Resume:
        try:
            job_info = output_manager.get_job_info()

            # Log content for each section
            for section, content in content_dict.items():
                if content:
                    logger.debug(f"Section {section} has content of length {len(content)}")
                else:
                    logger.warning(f"Section {section} is empty")

            logger.debug("Generating PDF")
            # Generate PDF
            generated_pdf = self.latex_compiler.generate_pdf(
                content_dict=content_dict,
                output_manager=output_manager
            )
            if not generated_pdf:
                logger.error("PDF generation failed")
                raise Exception("PDF generation failed")

            logger.debug("Creating resume object")
            # Create and save resume object
            resume = Resume(
                id=None,
                user_id=self.user_id,
                company_name=job_info.company_name,
                job_title=job_info.job_title,
                job_description=job_info.job_description,
                **content_dict,
                resume_pdf=generated_pdf,
                model_type=self.llm_runner.get_config().get('type'),
                model_name=self.llm_runner.strategy.__class__.__name__,
                temperature=self.llm_runner.get_config().get('temperature')
            )

            logger.debug("Saving resume to database")
            with self.uow:
                self.uow.resumes.add(resume)
                self.uow.commit()

            logger.info(f"Resume saved successfully with ID: {resume.id}")
            return resume
            
        except Exception as e:
            logger.error(f"Failed to generate and save resume: {str(e)}", exc_info=True)
            raise

    def process_section(self, section: str, process_type: str, job_description: str) -> str:
        """Process a single section based on the process type."""
        logger.debug(f"Processing section {section} with type {process_type}")
        
        if process_type == "skip":
            logger.debug(f"Skipping section {section}")
            return ""  # Return empty string for skipped sections
            
        elif process_type == "hardcode":
            logger.debug(f"Hardcoding section {section}")
            try:
                content = self.hardcoder.hardcode_section(section)
                if content:
                    logger.debug(f"Successfully hardcoded section {section}, content length: {len(content)}")
                    return content
                else:
                    logger.warning(f"Hardcoder returned empty content for section {section}")
                    return ""
            except Exception as e:
                logger.error(f"Error in hardcoding section {section}: {str(e)}", exc_info=True)
                raise
            
        elif process_type == "process":
            logger.debug(f"AI processing section {section}")
            try:
                # Get the prompt template for this section
                prompt = self.prompt_loader.get_section_prompt(section)
                logger.debug(f"Got prompt for section {section}")
                
                # Get the section data using portfolio_loader
                section_data = self.portfolio_loader.get_section_data(section)
                if not section_data:
                    logger.warning(f"No data found for section {section} in portfolio")
                    return ""
                
                logger.debug(f"Got data for section {section}")
                
                # Format skills data if this is the skills section
                if section == 'skills':
                    formatted_data = []
                    for skill_category in section_data:
                        for category, skills in skill_category.items():
                            formatted_data.append(f"{category}:\n- {', '.join(skills)}")
                    section_data = "\n\n".join(formatted_data)
                    logger.debug("Formatted skills data")
                else:
                    section_data = str(section_data)
                
                # Generate content using the prompt and portfolio data
                logger.debug(f"Generating content for section {section}")
                content = self.llm_runner.generate_content(prompt, section_data, job_description)
                
                if content:
                    logger.debug(f"Successfully generated content for section {section}, length: {len(content)}")
                    return content
                else:
                    logger.warning(f"AI returned empty content for section {section}")
                    return ""
                
            except Exception as e:
                logger.error(f"Error processing section {section} with AI: {str(e)}", exc_info=True)
                raise
        else:
            error_msg = f"Invalid process type: {process_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)