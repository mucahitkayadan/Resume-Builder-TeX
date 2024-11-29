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
                                            # Store the resume ID in session state for later use
                                            st.session_state['last_resume_id'] = generated_resume.id
                                except Exception as e:
                                    logger.error(f"Resume generation failed: {str(e)}")
                                    st.error(f"Resume generation failed: {str(e)}")
                                    raise

                            if generation_option in ["Cover Letter", "Both"]:
                                logger.info("Starting cover letter generation process")
                                try:
                                    cover_letter_generator = CoverLetterGenerator(self.llm_runner, st.session_state['user_id'])
                                    
                                    # If generating only cover letter, try to use the last resume
                                    if generation_option == "Cover Letter" and 'last_resume_id' in st.session_state:
                                        generated_resume_id = st.session_state['last_resume_id']
                                        # Get the resume from database
                                        with get_unit_of_work() as uow:
                                            last_resume = uow.resumes.get_by_id(generated_resume_id)
                                            if last_resume:
                                                generated_resume = last_resume
                                                # Use the same job info and output manager as the resume
                                                job_info = JobInfo(
                                                    company_name=last_resume.company_name,
                                                    job_title=last_resume.job_title,
                                                    job_description=job_description
                                                )
                                                output_manager = OutputManager(job_info)
                                                logger.info(f"Using existing resume ID: {generated_resume_id}")

                                    result = cover_letter_generator.generate_cover_letter(
                                        job_description=job_description,
                                        resume_id=generated_resume.id if generated_resume else None,
                                        output_manager=output_manager
                                    )
                                    
                                    # Update resume with cover letter info
                                    if generated_resume and "successfully" in result.lower():
                                        with get_unit_of_work() as uow:
                                            resume = uow.resumes.get_by_id(generated_resume.id)
                                            if resume:
                                                # Get the cover letter content and PDF from output manager
                                                cover_letter_path = output_manager.get_cover_letter_path()
                                                if cover_letter_path.exists():
                                                    # Read the content
                                                    cover_letter_content = cover_letter_path.read_text()
                                                    # Read the PDF if it exists
                                                    pdf_path = output_manager.output_dir / "cover_letter.pdf"
                                                    cover_letter_pdf = pdf_path.read_bytes() if pdf_path.exists() else None
                                                    
                                                    # Update resume with cover letter information
                                                    resume.cover_letter_content = cover_letter_content
                                                    resume.cover_letter_pdf = cover_letter_pdf
                                                    resume.has_cover_letter = True
                                                    resume.cover_letter_path = str(output_manager.output_dir)
                                                    
                                                    uow.resumes.update(resume)
                                                    logger.info(f"Updated resume {resume.id} with cover letter content and PDF")
                                    
                                    logger.info(f"Cover letter generation result: {result}")
                                    if "failed" in result.lower():
                                        st.warning(result)
                                    else:
                                        st.success(result)
                                except Exception as e:
                                    logger.error(f"Cover letter generation failed: {str(e)}", exc_info=True)
                                    st.error(f"Failed to generate cover letter: {str(e)}")

                            if generation_option == "Both":
                                logger.info("Generating both resume and cover letter...")
                                if generated_resume and generated_resume.id:
                                    logger.info(f"Resume generated and saved with ID: {generated_resume.id}")
                                    if resume.cover_letter_content and resume.cover_letter_pdf:
                                        logger.info(f"Cover letter added to resume {generated_resume.id}")
                                    else:
                                        logger.warning(f"Cover letter not properly saved to resume {generated_resume.id}")

                            logger.info("Generation completed successfully")
                            st.success("Generation complete: " + str(output_manager.output_dir))
                            
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
