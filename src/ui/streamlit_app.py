import streamlit as st
import logging

from src.resume.resume_generator import ResumeGenerator
from src.resume.cover_letter_generator import CoverLetterGenerator
from src.ui.components.section_selector import SectionSelector
from src.ui.components.model_selector import ModelSelector
from src.ui.components.database_viewer import DatabaseViewer
from src.loaders.prompt_loader import PromptLoader
from src.llms.runner import LLMRunner
from src.resume.utils.job_analysis import check_clearance_requirement
from config.settings import APP_CONSTANTS
from config.llm_config import LLMConfig
from src.core.database.models.resume import Resume

logger = logging.getLogger(__name__)

class StreamlitApp:
    def __init__(self):
        logger.info("Initializing StreamlitApp")
        self.setup_session_state()
        self.model_selector = ModelSelector()
        self.section_selector = SectionSelector()
        self.prompt_loader = PromptLoader()
        
        # Initialize LLMRunner with default OpenAI configuration
        logger.debug("Creating LLMRunner with default OpenAI configuration")
        self.llm_runner = LLMRunner.create_with_config(
            model_type="OpenAI",
            model_name=LLMConfig.OPENAI_MODEL.name,
            temperature=LLMConfig.OPENAI_MODEL.default_temperature,
            prompt_loader=self.prompt_loader
        )

    def setup_session_state(self):
        logger.debug("Setting up session state")
        if 'user_id' not in st.session_state:
            st.session_state['user_id'] = "mujakayadan"
        if 'portfolio_initialized' not in st.session_state:
            st.session_state['portfolio_initialized'] = False

    def run(self):
        logger.info("Starting StreamlitApp")
        st.title("Resume and Cover Letter Generator")
        
        # Sidebar navigation
        page = st.sidebar.radio("Go to", ["Resume Generator", "Database Viewer"])
        
        if page == "Resume Generator":
            logger.debug("Showing resume generator page")
            self.show_resume_generator()
        else:
            logger.debug("Showing database viewer page")
            self.show_database_viewer()

    def show_resume_generator(self):
        logger.info("Showing resume generator interface")
        try:
            # Get model settings
            model_type, model_name, temperature = self.model_selector.get_model_settings()
            logger.debug(f"Selected model settings - Type: {model_type}, Model: {model_name}, Temp: {temperature}")
            
            # Update LLM configuration
            logger.debug(f"Updating LLM config: type={model_type}, model={model_name}, temp={temperature}")
            self.llm_runner.update_config(
                model_type=model_type,
                model_name=model_name,
                temperature=temperature
            )
            
            # Get job description
            job_description = st.text_area("Enter the job description:", height=200)
            if job_description:
                logger.debug(f"Received job description (length: {len(job_description)})")
            
            # Get selected sections
            selected_sections = self.section_selector.get_user_section_selection()
            logger.debug(f"Selected sections: {selected_sections}")
            
            # Check clearance requirement
            clearance_required = check_clearance_requirement(job_description, APP_CONSTANTS.get('clearance_keywords'))
            
            # Select generation option
            generation_option = st.selectbox("Choose generation option", ["Resume", "Cover Letter", "Both"])

            # Generate content based on selected sections
            if st.button("Generate"):
                if clearance_required:
                    logger.warning("Job requires security clearance - generation blocked")
                    st.error("This job requires a security clearance or US citizenship. Resume generation is not available for this job.")
                elif not job_description:
                    logger.warning("No job description provided")
                    st.warning("Please enter a job description")
                elif not selected_sections:
                    logger.warning("No sections selected")
                    st.warning("Please select at least one section to generate")
                else:
                    logger.info("Starting content generation")
                    # Extract company name and job title
                    company_name, job_title = self.llm_runner.create_company_name_and_job_title(self.prompt_loader.get_folder_name_prompt(), job_description)
                    logger.debug(f"Extracted company: {company_name}, job title: {job_title}")
                    
                    progress_bar = st.progress(0)
                    status_area = st.empty()
                    
                    try:
                        generated_resume = None
                        if generation_option in ["Resume", "Both"]:
                            logger.info("Generating resume")
                            resume_generator = ResumeGenerator(self.llm_runner, st.session_state['user_id'])
                            try:
                                for status_msg, progress in resume_generator.generate_resume(
                                    job_description=job_description,
                                    selected_sections=selected_sections
                                ):
                                    progress_bar.progress(progress)
                                    status_area.text(status_msg)
                                    if isinstance(status_msg, Resume):  # Capture the returned Resume object
                                        generated_resume = status_msg
                            except Exception as e:
                                logger.error(f"Resume generation failed: {str(e)}")
                                st.error(f"Resume generation failed: {str(e)}")

                        if generation_option in ["Cover Letter", "Both"] and generated_resume:
                            logger.info("Generating cover letter")
                            cover_letter_generator = CoverLetterGenerator(self.llm_runner, st.session_state['user_id'])
                            cover_letter_generator.generate_cover_letter(
                                job_description=job_description,
                                resume_id=generated_resume.id,
                                company_name=company_name,
                                job_title=job_title
                            )

                        logger.info("Generation completed successfully")
                        st.success("Generation complete!")
                        
                    except Exception as e:
                        logger.error(f"Error during generation: {str(e)}", exc_info=True)
                        st.error(f"An error occurred during generation: {str(e)}")
                    finally:
                        progress_bar.empty()
                        status_area.empty()
        except Exception as e:
            logger.error(f"Error during resume generation: {str(e)}", exc_info=True)
            st.error(f"An error occurred during resume generation: {str(e)}")

    def show_database_viewer(self):
        logger.info("Showing database viewer interface")
        DatabaseViewer().render()
