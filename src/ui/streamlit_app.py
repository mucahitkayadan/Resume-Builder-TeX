import streamlit as st
import logging
from config.logger_config import setup_logger

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
from src.resume.utils.output_manager import OutputManager
from src.resume.utils.job_info import JobInfo
from src.core.database.models import Resume
from src.core.database.factory import get_unit_of_work
from src.resume.combined_generator import CombinedGenerator

logger = setup_logger(__name__, level=logging.INFO)

class StreamlitApp:
    def __init__(self):
        # Always initialize session state first
        self.setup_session_state()
        
        # Initialize components if not already in session state
        if 'components_initialized' not in st.session_state:
            logger.info("Initializing StreamlitApp components")
            self._initialize_components()
            st.session_state['components_initialized'] = True
        
        # Get components from session state
        self._get_components()

    def _initialize_components(self):
        """Initialize all components and store in session state"""
        st.session_state['model_selector'] = ModelSelector()
        st.session_state['section_selector'] = SectionSelector()
        st.session_state['prompt_loader'] = PromptLoader()
        
        logger.info("Creating LLMRunner with default OpenAI configuration")
        st.session_state['llm_runner'] = LLMRunner.create_with_config(
            model_type="OpenAI",
            model_name=LLMConfig.OPENAI_MODEL.name,
            temperature=LLMConfig.OPENAI_MODEL.default_temperature,
            prompt_loader=st.session_state['prompt_loader']
        )

    def _get_components(self):
        """Get components from session state"""
        self.model_selector = st.session_state['model_selector']
        self.section_selector = st.session_state['section_selector']
        self.prompt_loader = st.session_state['prompt_loader']
        self.llm_runner = st.session_state['llm_runner']

    @staticmethod
    @st.cache_resource
    def setup_session_state():
        logger.info("Setting up session state")
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
            logger.info("Showing resume generator page")
            self.show_resume_generator()
        else:
            logger.info("Showing database viewer page")
            self.show_database_viewer()

    def show_resume_generator(self):
        logger.info("Showing resume generator interface")
        try:
            # Get model settings
            model_type, model_name, temperature = self.model_selector.get_model_settings()
            
            # Only log when configuration actually changes
            if ('last_model_config' not in st.session_state or 
                st.session_state['last_model_config'] != (model_type, model_name, temperature)):
                logger.info(f"Updating LLM configuration: {model_type}, {model_name}, {temperature}")
                st.session_state['last_model_config'] = (model_type, model_name, temperature)
                self.llm_runner.update_config(
                    model_type=model_type,
                    model_name=model_name,
                    temperature=temperature
                )
            
            # Get job description
            job_description = st.text_area("Enter the job description:", height=200)
            
            # Get selected sections
            selected_sections = self.section_selector.get_user_section_selection()
            
            # Check clearance requirement
            clearance_required = check_clearance_requirement(job_description, APP_CONSTANTS.get('clearance_keywords'))
            
            # Select generation option
            generation_option = st.selectbox(
                "What would you like to generate?",
                ["Resume", "Cover Letter", "Both"]
            )

            # Generate content based on selected sections
            if st.button("Generate"):
                with st.spinner("Generating..."):
                    progress_bar = st.progress(0)
                    status_area = st.empty()

                    try:
                        # Create job info and output manager
                        job_info = JobInfo.extract_from_description(
                            job_description,
                            self.llm_runner,
                            self.prompt_loader
                        )
                        output_manager = OutputManager(job_info)
                        logger.info(f"Output manager working at: {output_manager.output_dir}")

                        if generation_option == "Resume":
                            # Generate only resume
                            resume_generator = ResumeGenerator(self.llm_runner, st.session_state['user_id'])
                            for result in resume_generator.generate_resume(
                                job_description=job_description,
                                selected_sections=selected_sections,
                                output_manager=output_manager
                            ):
                                if isinstance(result, tuple):
                                    status_msg, progress = result
                                    progress_bar.progress(progress)
                                    status_area.text(status_msg)

                        elif generation_option == "Cover Letter":
                            # Generate cover letter using latest resume
                            cover_letter_generator = CoverLetterGenerator(self.llm_runner, st.session_state['user_id'])
                            result = cover_letter_generator.generate_cover_letter(
                                job_description=job_description,
                                resume_id=None,
                                output_manager=output_manager
                            )
                            # Handle result

                        else:  # "Both"
                            # Create generators
                            resume_generator = ResumeGenerator(self.llm_runner, st.session_state['user_id'])
                            cover_letter_generator = CoverLetterGenerator(self.llm_runner, st.session_state['user_id'])
                            combined_generator = CombinedGenerator(resume_generator, cover_letter_generator)
                            
                            # Generate both
                            for result in combined_generator.generate_both(
                                job_description=job_description,
                                selected_sections=selected_sections,
                                output_manager=output_manager
                            ):
                                if isinstance(result, tuple):
                                    status_msg, progress = result
                                    progress_bar.progress(progress)
                                    status_area.text(status_msg)

                        logger.info("Generation completed successfully")
                        st.success(f"Generation complete: {output_manager.output_dir}")

                    except Exception as e:
                        logger.error(f"Generation failed: {e}")
                        st.error(str(e))
        except Exception as e:
            logger.error(f"Error during resume generation: {str(e)}", exc_info=True)
            st.error(f"An error occurred during resume generation: {str(e)}")

    def show_database_viewer(self):
        logger.info("Showing database viewer interface")
        DatabaseViewer().render()
