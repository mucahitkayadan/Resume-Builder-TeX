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
from src.resume.combined_generator import CombinedGenerator
from src.resume.generator_manager import GeneratorManager, GenerationType

logger = setup_logger(__name__, level=logging.INFO)

class StreamlitApp:
    def __init__(self):
        # Always initialize session state first
        self.setup_session_state()
        
        # Initialize components
        self.model_selector = ModelSelector()
        self.section_selector = SectionSelector()
        self.generator_manager = GeneratorManager(st.session_state['user_id'])
        
        # Store components in session state if not already there
        if 'components_initialized' not in st.session_state:
            logger.info("Initializing StreamlitApp components")
            self._store_components()
            st.session_state['components_initialized'] = True

    def _store_components(self):
        """Store components in session state"""
        st.session_state['model_selector'] = self.model_selector
        st.session_state['section_selector'] = self.section_selector
        st.session_state['generator_manager'] = self.generator_manager
        logger.debug("Components stored in session state")

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
        try:
            # Get model settings and configure LLM
            model_type, model_name, temperature = self.model_selector.get_model_settings()
            self.generator_manager.configure_llm(model_type, model_name, temperature)
            
            # Get job description and sections
            job_description = st.text_area("Enter the job description:", height=200)
            selected_sections = self.section_selector.get_user_section_selection()
            
            # Select generation option
            generation_option = st.selectbox(
                "What would you like to generate?",
                ["Resume", "Cover Letter", "Both"]
            )

            if st.button("Generate"):
                with st.spinner("Generating..."):
                    progress_bar = st.progress(0)
                    status_area = st.empty()

                    try:
                        # Create output manager
                        job_info = JobInfo.extract_from_description(
                            job_description,
                            self.generator_manager.llm_runner,  # Pass LLM runner
                            self.generator_manager._prompt_loader  # Pass prompt loader
                        )
                        output_manager = OutputManager(job_info)
                        logger.info(f"Output manager working at: {output_manager.output_dir}")

                        # Map option to enum
                        generation_type = GenerationType(generation_option.lower().replace(" ", "_"))
                        
                        # Generate content
                        for result in self.generator_manager.generate(
                            generation_type=generation_type,
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
            logger.error(f"Error during generation: {str(e)}", exc_info=True)
            st.error(f"An error occurred: {str(e)}")

    def show_database_viewer(self):
        logger.info("Showing database viewer interface")
        DatabaseViewer().render()
