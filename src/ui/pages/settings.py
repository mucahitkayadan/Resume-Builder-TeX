import streamlit as st
from src.core.database.factory import get_unit_of_work
from config.logger_config import setup_logger
from config.settings import FEATURE_FLAGS
from src.core.database.models.user_preferences import (
    UserPreferences, ProjectDetails, WorkExperienceDetails,
    SkillsDetails, CareerSummaryDetails, EducationDetails,
    CoverLetterDetails, AwardsDetails, PublicationsDetails,
    FeaturePreferences, SectionPreferences
)

logger = setup_logger(__name__)

class SettingsPage:
    def __init__(self, model_selector):
        self.model_selector = model_selector

    def render(self):
        st.title("⚙️ Settings")
        
        tab1, tab2, tab3 = st.tabs([
            "LLM Configuration",
            "User Preferences",
            "Feature Flags"
        ])
        
        with tab1:
            self._render_llm_settings()
        
        with tab2:
            self._render_user_preferences()
        
        with tab3:
            self._render_feature_flags()

    def _render_llm_settings(self):
        st.header("LLM Settings")
        
        # Get current preferences from database
        with get_unit_of_work() as uow:
            preferences = uow.users.get_preferences(st.session_state['user_id'])
            current_prefs = preferences.get('llm_preferences', {}) if preferences else {}
        
        # Model type selection
        model_type = st.selectbox(
            "Select Model Type",
            self.model_selector.model_types,
            index=self.model_selector.model_types.index(current_prefs.get('model_type', "Claude"))
        )

        # Model name selection based on type
        model_name = st.selectbox(
            "Select Model",
            self.model_selector.model_options[model_type],
            index=self.model_selector.model_options[model_type].index(
                current_prefs.get('model_name', "claude-3-5-sonnet-20240620")
            ) if current_prefs.get('model_name') in self.model_selector.model_options[model_type] else 0
        )

        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=current_prefs.get('temperature', 0.1),
            step=0.1,
            help="Higher values make the output more creative but less focused"
        )
        
        # Save button
        if st.button("Save LLM Settings"):
            with get_unit_of_work() as uow:
                uow.users.update_llm_preferences(
                    st.session_state['user_id'],
                    {
                        'model_type': model_type,
                        'model_name': model_name,
                        'temperature': temperature
                    }
                )
                # Update session state
                st.session_state['model_type'] = model_type
                st.session_state['model_name'] = model_name
                st.session_state['temperature'] = temperature
                
                st.success("✅ LLM settings saved successfully!")
                logger.info(f"LLM preferences updated for user {st.session_state['user_id']}")

    def _render_user_preferences(self):
        st.header("User Preferences")
        
        with get_unit_of_work() as uow:
            user = uow.users.get_by_user_id(st.session_state['user_id'])
            if not user:
                st.error("User not found")
                return
            
            # Get user profile and preferences
            profile = uow.profiles.get_by_user_id(st.session_state['user_id'])
            
            # Convert Pydantic model to dict if needed
            if hasattr(user.preferences, 'model_dump'):
                preferences = user.preferences.model_dump()
            else:
                preferences = user.preferences
            
            # Life Story Section
            with st.expander("Life Story"):
                life_story = st.text_area(
                    "Your Life Story",
                    value=profile.life_story if profile else "",
                    height=200,
                    help="This will be used to personalize your cover letter",
                    key="life_story_input"
                )
            
            # Resume Section Preferences
            with st.expander("Resume Section Preferences"):
                # Projects
                st.subheader("Projects")
                project_details = preferences.get('project_details', {})
                max_projects = st.number_input(
                    "Maximum Projects",
                    min_value=1,
                    max_value=10,
                    value=project_details.get('max_projects', 5),
                    key="max_projects_input"
                )
                bullet_points_per_project = st.number_input(
                    "Bullet Points per Project",
                    min_value=1,
                    max_value=5,
                    value=project_details.get('bullet_points_per_project', 3),
                    key="bullet_points_per_project_input"
                )
                
                # Work Experience
                st.subheader("Work Experience")
                work_exp_details = preferences.get('work_experience_details', {})
                max_jobs = st.number_input(
                    "Maximum Jobs",
                    min_value=1,
                    max_value=10,
                    value=work_exp_details.get('max_jobs', 5),
                    key="max_jobs_input"
                )
                bullet_points_per_job = st.number_input(
                    "Bullet Points per Job",
                    min_value=1,
                    max_value=5,
                    value=work_exp_details.get('bullet_points_per_job', 3),
                    key="bullet_points_per_job_input"
                )
                
                # Skills
                st.subheader("Skills")
                skills_details = preferences.get('skills_details', {})
                max_categories = st.number_input(
                    "Maximum Skill Categories",
                    min_value=1,
                    max_value=10,
                    value=skills_details.get('max_categories', 5),
                    key="max_categories_input"
                )
                min_skills = st.number_input(
                    "Minimum Skills per Category",
                    min_value=1,
                    max_value=15,
                    value=skills_details.get('min_skills_per_category', 3),
                    key="min_skills_input"
                )
                max_skills = st.number_input(
                    "Maximum Skills per Category",
                    min_value=1,
                    max_value=15,
                    value=skills_details.get('max_skills_per_category', 7),
                    key="max_skills_input"
                )
                
                # Career Summary
                st.subheader("Career Summary")
                career_summary_details = preferences.get('career_summary_details', {})
                min_words = st.number_input(
                    "Minimum Words",
                    min_value=10,
                    max_value=50,
                    value=career_summary_details.get('min_words', 25),
                    key="min_words_input"
                )
                max_words = st.number_input(
                    "Maximum Words",
                    min_value=10,
                    max_value=50,
                    value=career_summary_details.get('max_words', 35),
                    key="max_words_input"
                )
                
                # Education
                st.subheader("Education")
                education_details = preferences.get('education_details', {})
                max_education = st.number_input(
                    "Maximum Education Entries",
                    min_value=1,
                    max_value=5,
                    value=education_details.get('max_entries', 3),
                    key="max_education_input"
                )
                max_courses = st.number_input(
                    "Maximum Courses Listed",
                    min_value=1,
                    max_value=10,
                    value=education_details.get('max_courses', 5),
                    key="max_courses_input"
                )

            # Feature Flags
            with st.expander("Feature Flags"):
                st.subheader("Features")
                feature_preferences = preferences.get('feature_preferences', {})
                check_clearance = st.toggle(
                    "Security Clearance Check",
                    value=feature_preferences.get('check_clearance', True),
                    help="Enable/disable checking for security clearance requirements",
                    key="check_clearance_toggle"
                )
                auto_save = st.toggle(
                    "Auto-save",
                    value=feature_preferences.get('auto_save', True),
                    help="Automatically save generated documents",
                    key="auto_save_toggle"
                )
                dark_mode = st.toggle(
                    "Dark Mode",
                    value=feature_preferences.get('dark_mode', False),
                    help="Enable/disable dark mode",
                    key="dark_mode_toggle"
                )

            # Section Preferences
            with st.expander("Section Processing"):
                st.subheader("Section Processing Preferences")
                section_preferences = preferences.get('section_preferences', {})
                section_values = {}
                for section in ['personal_information', 'career_summary', 'skills', 
                              'work_experience', 'education', 'projects', 'awards', 'publications']:
                    section_values[section] = st.selectbox(
                        f"{section.replace('_', ' ').title()}",
                        options=["Process", "Hardcode", "Skip"],
                        key=f"section_preference_{section}",
                        index=0 if section_preferences.get(section) == "Process" 
                              else 1 if section_preferences.get(section) == "Hardcode"
                              else 2,
                        help=f"Choose how to handle the {section.replace('_', ' ')} section"
                    )

            if st.button("Save Preferences", key="save_preferences_button"):
                try:
                    # Update preferences with all sections
                    new_preferences = {
                        'project_details': {
                            'max_projects': max_projects,
                            'bullet_points_per_project': bullet_points_per_project
                        },
                        'work_experience_details': {
                            'max_jobs': max_jobs,
                            'bullet_points_per_job': bullet_points_per_job
                        },
                        'skills_details': {
                            'max_categories': max_categories,
                            'min_skills_per_category': min_skills,
                            'max_skills_per_category': max_skills
                        },
                        'career_summary_details': {
                            'min_words': min_words,
                            'max_words': max_words
                        },
                        'education_details': {
                            'max_entries': max_education,
                            'max_courses': max_courses
                        },
                        'feature_preferences': {
                            'check_clearance': check_clearance,
                            'auto_save': auto_save,
                            'dark_mode': dark_mode
                        },
                        'section_preferences': section_values
                    }
                    
                    # Update life story in profile
                    if profile:
                        profile.life_story = life_story
                        uow.profiles.update(profile)
                    else:
                        # Create new profile if it doesn't exist
                        from src.core.database.models.profile import Profile
                        new_profile = Profile(
                            user_id=st.session_state['user_id'],
                            life_story=life_story
                        )
                        uow.profiles.create(new_profile)
                    
                    # Update preferences
                    uow.users.update_preferences(st.session_state['user_id'], new_preferences)
                    
                    st.success("✅ Preferences saved successfully!")
                    logger.info(f"Preferences updated for user {st.session_state['user_id']}")
                    
                except Exception as e:
                    logger.error(f"Failed to save preferences: {str(e)}")
                    st.error(f"❌ Failed to save preferences: {str(e)}")

    def _render_feature_flags(self):
        st.header("Feature Flags")
        
        with get_unit_of_work() as uow:
            preferences = uow.users.get_preferences(st.session_state['user_id'])
            current_flags = preferences.get('feature_preferences', {}) if preferences else {}
            
            # Clearance Check
            clearance_enabled = st.toggle(
                "Security Clearance Check",
                value=current_flags.get('check_clearance', FEATURE_FLAGS['check_clearance']),
                help="Enable/disable checking for security clearance requirements"
            )
            
            # Auto-save
            auto_save = st.toggle(
                "Auto-save",
                value=current_flags.get('auto_save', True),
                help="Automatically save generated documents"
            )
            
            # Save settings if button is clicked
            if st.button("Save Feature Settings"):
                uow.users.update_feature_preferences(
                    st.session_state['user_id'],
                    {
                        'check_clearance': clearance_enabled,
                        'auto_save': auto_save
                    }
                )
                st.success("✅ Feature settings saved successfully!")