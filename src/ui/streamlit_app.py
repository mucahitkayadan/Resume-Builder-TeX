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

logger = setup_logger(__name__, level=logging.INFO)

class StreamlitApp:
    def __init__(self):
        logger.info("Initializing StreamlitApp")
        self.setup_session_state()
        self.model_selector = ModelSelector()
        self.section_selector = SectionSelector()
        self.prompt_loader = PromptLoader()
        
        logger.info("Creating LLMRunner with default OpenAI configuration")
        self.llm_runner = LLMRunner.create_with_config(
            model_type="OpenAI",
            model_name=LLMConfig.OPENAI_MODEL.name,
            temperature=LLMConfig.OPENAI_MODEL.default_temperature,
            prompt_loader=self.prompt_loader
        )

    def setup_session_state(self):
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
            logger.info("Getting model settings")
            model_type, model_name, temperature = self.model_selector.get_model_settings()
            
            logger.info(f"Updating LLM configuration: {model_type}, {model_name}, {temperature}")
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
                    with st.spinner("Generating..."):
                        progress_bar = st.progress(0)
                        status_area = st.empty()
                        
                        try:
                            # Create job info first
                            job_info = JobInfo.extract_from_description(
                                job_description,
                                self.llm_runner,
                                self.prompt_loader
                            )
                            
                            # Create output manager with job info
                            output_manager = OutputManager(job_info)

                            logger.info("Output manager is working at: " + str(output_manager.output_dir))
                            generated_resume = None
                            if generation_option in ["Resume", "Both"]:
                                resume_generator = ResumeGenerator(self.llm_runner, st.session_state['user_id'])
                                try:
                                    for result in resume_generator.generate_resume(
                                        job_description=job_description,
                                        selected_sections=selected_sections,
                                        output_manager=output_manager
                                    ):
                                        if isinstance(result, tuple):
                                            status_msg, progress = result
                                            progress_bar.progress(progress)
                                            status_area.text(status_msg)
                                        else:
                                            generated_resume = result
                                            logger.info(f"Resume generated successfully with ID: {generated_resume.id}")
                                except Exception as e:
                                    logger.error(f"Resume generation failed: {str(e)}")
                                    st.error(f"Resume generation failed: {str(e)}")
                                    raise  # Re-raise to prevent cover letter generation
                                
                            if generation_option in ["Cover Letter", "Both"]:
                                logger.info("Starting cover letter generation process")
                                try:
                                    # Create new output manager for cover letter if needed
                                    if generation_option == "Cover Letter":
                                        job_info = JobInfo.extract_from_description(
                                            job_description,
                                            self.llm_runner,
                                            self.prompt_loader
                                        )
                                        output_manager = OutputManager(job_info)
                                        
                                    cover_letter_generator = CoverLetterGenerator(self.llm_runner, st.session_state['user_id'])
                                    result = cover_letter_generator.generate_cover_letter(
                                        job_description=job_description,
                                        resume_id=generated_resume.id if generated_resume else None,
                                        output_manager=output_manager
                                    )
                                    logger.info(f"Cover letter generation result: {result}")
                                    if "failed" in result.lower():
                                        st.warning(result)
                                    else:
                                        st.success(result)
                                except Exception as e:
                                    logger.error(f"Cover letter generation failed with error: {str(e)}", exc_info=True)
                                    st.error(f"Failed to generate cover letter: {str(e)}")

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
