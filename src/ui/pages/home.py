import streamlit as st
from src.resume.utils.job_analysis import check_clearance_requirement
from src.resume.utils.job_info import JobInfo
from src.resume.generator_manager import GenerationType
from config.settings import APP_CONSTANTS, FEATURE_FLAGS
from config.logger_config import setup_logger
from src.core.database.factory import get_unit_of_work
from src.resume.utils.output_manager import OutputManager

logger = setup_logger(__name__)

class HomePage:
    def __init__(self, model_selector, section_selector, generator_manager):
        self.model_selector = model_selector
        self.section_selector = section_selector
        self.generator_manager = generator_manager
        # Load saved preferences
        self._load_user_preferences()
        
    def _load_user_preferences(self):
        """Load user preferences from database"""
        try:
            with get_unit_of_work() as uow:
                preferences = uow.users.get_preferences(st.session_state['user_id'])
                if preferences:
                    # Set LLM preferences
                    llm_prefs = preferences.get('llm_preferences', {})
                    if llm_prefs:
                        self.generator_manager.configure_llm(
                            llm_prefs['model_type'],
                            llm_prefs['model_name'],
                            llm_prefs['temperature']
                        )
                    
                    # Set section preferences
                    section_prefs = preferences.get('section_preferences', {})
                    if section_prefs:
                        st.session_state['section_preferences'] = section_prefs
                    
                    logger.debug("User preferences loaded successfully")
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
        
    def render(self):
        try:
            # Add state variable for clearance check
            clearance_blocked = False
            
            # Create two columns for better layout
            left_col, right_col = st.columns([2, 1])
            
            with left_col:
                st.markdown("### 📋 Job Description")
                job_description = st.text_area(
                    "Enter the job description:",
                    height=200,
                    placeholder="Paste the job description here...",
                    help="Copy and paste the complete job description from the job posting"
                )
                
                # Add clearance requirement check if feature is enabled
                if job_description and FEATURE_FLAGS['check_clearance']:
                    clearance_required = check_clearance_requirement(
                        job_description, 
                        APP_CONSTANTS['clearance_keywords']
                    )
                    if clearance_required:
                        logger.warning("Security clearance requirement detected")
                        st.error("🔒 This position requires security clearance. Generation will be disabled.")
                        clearance_blocked = True
                
                st.markdown("### 🎯 Generation Options")
                generation_option = st.selectbox(
                    "What would you like to generate?",
                    ["Resume", "Cover Letter", "Both"],
                    format_func=lambda x: f"Generate {x}"
                )
                
                # Move generate button here, inside left column
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)  # Add some spacing
                generate_button = st.button(
                    "🚀 Generate" if not clearance_blocked else "🔒 Generation Disabled",
                    use_container_width=True,
                    disabled=clearance_blocked
                )
            
            with right_col:
                # Show current configuration (read-only)
                st.markdown("### ⚙️ Current Configuration")
                with st.expander("Model Settings"):
                    # Get preferences from database
                    with get_unit_of_work() as uow:
                        preferences = uow.users.get_preferences(st.session_state['user_id'])
                        if preferences and preferences.get('llm_preferences'):
                            llm_prefs = preferences['llm_preferences']
                            st.text(f"Model Type: {llm_prefs['model_type']}")
                            st.text(f"Model: {llm_prefs['model_name']}")
                            st.text(f"Temperature: {llm_prefs['temperature']}")
                        else:
                            # Fallback to model_selector defaults
                            model_type, model_name, temperature = self.model_selector.get_model_settings()
                            st.text(f"Model Type: {model_type}")
                            st.text(f"Model: {model_name}")
                            st.text(f"Temperature: {temperature}")
                
                with st.expander("Section Settings"):
                    section_prefs = st.session_state.get('section_preferences', {})
                    if section_prefs:
                        for section, handling in section_prefs.items():
                            st.text(f"{section}: {handling}")
                    else:
                        # Get default sections from section_selector
                        default_sections = self.section_selector.get_user_section_selection()
                        for section, handling in default_sections.items():
                            st.text(f"{section}: {handling}")
                
                st.markdown("""
                    ℹ️ To change settings, use the Settings and Section Manager pages 
                    from the sidebar navigation.
                """)
            
            # Handle generation when button is clicked
            if generate_button:
                self._handle_generation(job_description, generation_option, st.session_state.get('section_preferences', {}))

        except Exception as e:
            logger.error(f"Error in home page: {str(e)}", exc_info=True)
            st.error(f"❌ An unexpected error occurred: {str(e)}")

    def _handle_generation(self, job_description, generation_option, selected_sections):
        if not job_description:
            logger.warning("Generation attempted without job description")
            st.error("❌ Please enter a job description first.")
            return
            
        with st.spinner("🔄 Generating your documents..."):
            progress_bar = st.progress(0)
            status_area = st.empty()

            try:
                # Get job info
                job_info = JobInfo.extract_from_description(
                    job_description,
                    self.generator_manager.llm_runner,
                    self.generator_manager._prompt_loader
                )
                
                # Create output manager directly
                output_manager = OutputManager(job_info)
                logger.info(f"Output manager working at: {output_manager.output_dir}")

                generation_type = GenerationType(generation_option.lower().replace(" ", "_"))
                
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

                st.success("✨ Generation completed successfully!")
                st.balloons()
                logger.info("Generation completed successfully")
                st.success(f"Generation complete: {output_manager.output_dir}")

            except Exception as e:
                logger.error(f"Generation failed: {e}")
                st.error(f"❌ {str(e)}") 