import streamlit as st

from config.config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD
from config.logger_config import setup_logger
from config.settings import APP_CONSTANTS, FEATURE_FLAGS
from easy_applier.job_extractor import JobExtractor
from src.core.database.factory import get_unit_of_work
from src.generator.generator_manager import GenerationType
from src.generator.utils.job_analysis import check_clearance_requirement
from src.generator.utils.job_info import JobInfo
from src.generator.utils.output_manager import OutputManager

logger = setup_logger(__name__)


class HomePage:
    def __init__(self, model_selector, generator_manager):
        self.model_selector = model_selector
        self.generator_manager = generator_manager
        self.job_extractor = JobExtractor(LINKEDIN_EMAIL, LINKEDIN_PASSWORD)
        # Load saved preferences
        self._load_user_preferences()

    def _load_user_preferences(self):
        """Load user preferences from database"""
        try:
            with get_unit_of_work() as uow:
                user = uow.users.get_by_user_id(st.session_state["user_id"])
                if user and user.preferences:
                    # Set LLM preferences
                    llm_prefs = user.preferences.llm_preferences
                    if llm_prefs:
                        self.generator_manager.configure_llm(
                            model_type=llm_prefs.model_type,
                            model_name=llm_prefs.model_name,
                            temperature=llm_prefs.temperature,
                        )
                        logger.debug(f"Configured LLM with: {llm_prefs}")

                    # Set section preferences - convert Pydantic model to dict
                    section_prefs = user.preferences.section_preferences
                    if section_prefs:
                        st.session_state["section_preferences"] = (
                            section_prefs.model_dump()
                        )
                        logger.debug(
                            f"Loaded section preferences: {section_prefs.model_dump()}"
                        )

                    logger.debug("User preferences loaded successfully")
        except Exception as e:
            logger.error(f"Error loading user preferences: {e}")
            # Set default preferences if loading fails
            self.generator_manager.configure_llm(
                model_type="Claude",
                model_name="claude-3-5-sonnet-20240620",
                temperature=0.1,
            )

    def render(self):
        try:
            clearance_blocked = False
            left_col, right_col = st.columns([2, 1])

            with left_col:
                st.markdown("### 📋 Job Description")

                # Add tabs for different input methods
                input_tab1, input_tab2 = st.tabs(["📝 Manual Entry", "🔗 LinkedIn URL"])

                # Initialize job_description as None
                job_description = None

                with input_tab1:
                    manual_description = st.text_area(
                        "Enter the job description:",
                        height=200,
                        placeholder="Paste the job description here...",
                        help="Copy and paste the complete job description from the job posting",
                        key="manual_text_area",
                    )
                    if manual_description:
                        job_description = manual_description

                with input_tab2:
                    job_url = st.text_input(
                        "Enter LinkedIn job URL:",
                        placeholder="https://www.linkedin.com/jobs/...",
                        help="Enter the URL of the LinkedIn job posting",
                        key="url_input",
                    )
                    if job_url:
                        if not job_url.startswith("https://www.linkedin.com/"):
                            st.error(
                                "⚠️ Only LinkedIn job URLs are supported at this time."
                            )
                        else:
                            try:
                                url_description = str(
                                    self.job_extractor.extract_job_details(job_url)
                                )
                                job_description = url_description
                            except Exception as e:
                                st.error(f"Failed to extract job details: {str(e)}")
                                logger.error(f"LinkedIn extraction error: {e}")

                # Add clearance requirement check if feature is enabled
                if job_description and FEATURE_FLAGS["check_clearance"]:
                    clearance_required = check_clearance_requirement(
                        job_description, APP_CONSTANTS["clearance_keywords"]
                    )
                    if clearance_required:
                        logger.warning("Security clearance requirement detected")
                        st.error(
                            "🔒 This position requires security clearance. Generation will be disabled."
                        )
                        clearance_blocked = True

                st.markdown("### 🎯 Generation Options")
                generation_option = st.selectbox(
                    "What would you like to generate?",
                    ["Resume", "Cover Letter", "Both"],
                    format_func=lambda x: f"Generate {x}",
                )

                # Move generate button here, inside left column
                st.markdown(
                    "<div style='height: 20px;'></div>", unsafe_allow_html=True
                )  # Add some spacing
                generate_button = st.button(
                    (
                        "🚀 Generate"
                        if not clearance_blocked
                        else "🔒 Generation Disabled"
                    ),
                    use_container_width=True,
                    disabled=clearance_blocked,
                )

            with right_col:
                # Show current configuration (read-only)
                st.markdown("### ⚙️ Current Configuration")
                with st.expander("Model Settings"):
                    # Get preferences from database
                    with get_unit_of_work() as uow:
                        user = uow.users.get_by_user_id(st.session_state["user_id"])
                        if user and user.preferences.llm_preferences:
                            llm_prefs = user.preferences.llm_preferences
                            st.text(f"Model Type: {llm_prefs.model_type}")
                            st.text(f"Model: {llm_prefs.model_name}")
                            st.text(f"Temperature: {llm_prefs.temperature}")
                        else:
                            # Fallback to model_selector defaults
                            model_type, model_name, temperature = (
                                self.model_selector.get_model_settings()
                            )
                            st.text(f"Model Type: {model_type}")
                            st.text(f"Model: {model_name}")
                            st.text(f"Temperature: {temperature}")

                with st.expander("Section Settings"):
                    section_prefs = st.session_state.get("section_preferences", {})
                    if section_prefs:
                        for section, handling in section_prefs.items():
                            st.text(f"{section}: {handling}")
                    else:
                        # Get default sections from section_selector
                        default_sections = (
                            self.section_selector.get_user_section_selection()
                        )
                        for section, handling in default_sections.items():
                            st.text(f"{section}: {handling}")

                st.markdown(
                    """
                    ℹ️ To change settings, use the Settings and Section Manager pages 
                    from the sidebar navigation.
                """
                )

            # Handle generation when button is clicked
            if generate_button:
                self._handle_generation(
                    job_description,
                    generation_option,
                    st.session_state.get("section_preferences", {}),
                )

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
                    job_description, self.generator_manager.llm_runner
                )

                # Create output manager directly
                output_manager = OutputManager(job_info)
                logger.info(f"Output manager working at: {output_manager.output_dir}")

                generation_type = GenerationType(
                    generation_option.lower().replace(" ", "_")
                )

                for result in self.generator_manager.generate(
                    generation_type=generation_type,
                    job_description=job_description,
                    selected_sections=selected_sections,
                    output_manager=output_manager,
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
