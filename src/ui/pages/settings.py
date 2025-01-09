"""
Settings page module for managing user preferences and configurations.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime
import streamlit as st

from src.core.database.factory import get_unit_of_work
from src.core.database.models.profile import Profile
from src.ui.components.model_selector import ModelSelector

logger = logging.getLogger(__name__)

class SettingsPage:
    """
    A class to handle the settings page functionality in the Streamlit application.
    
    This page allows users to configure:
    - LLM Configuration: AI model selection and parameters
    - User Preferences: Resume sections, life story, and formatting options
    - Feature Flags: System-wide feature toggles
    
    Args:
        model_selector (ModelSelector): Component for selecting AI models
    """
    
    def __init__(self, model_selector: ModelSelector) -> None:
        """Initialize SettingsPage with required components."""
        self.model_selector = model_selector

    def render(self) -> None:
        """Render the settings page with all configuration tabs."""
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

    def _render_llm_settings(self) -> None:
        """
        Render LLM configuration settings.
        
        Handles:
        - Model type selection
        - Model name selection
        - Temperature configuration
        """
        st.header("LLM Settings")
        
        # Get current preferences from database
        with get_unit_of_work() as uow:
            preferences = uow.users.get_preferences(st.session_state['user_id'])
            current_prefs = preferences.get('llm_preferences', {}) if preferences else {}
        
        # Model type selection
        model_type = st.selectbox(
            "Select Model Type",
            self.model_selector.model_types,
            index=self.model_selector.model_types.index(current_prefs.get('model_type', "Claude")),
            key="model_type_select"
        )

        # Model name selection based on type
        model_name = st.selectbox(
            "Select Model",
            self.model_selector.model_options[model_type],
            index=self.model_selector.model_options[model_type].index(
                current_prefs.get('model_name', "claude-3-5-sonnet-20240620")
            ) if current_prefs.get('model_name') in self.model_selector.model_options[model_type] else 0,
            key="model_name_select"
        )

        # Temperature slider
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=current_prefs.get('temperature', 0.1),
            step=0.1,
            help="Higher values make the output more creative but less focused",
            key="temperature_slider"
        )
        
        if st.button("Save LLM Settings", key="save_llm_button"):
            self._save_llm_settings(model_type, model_name, temperature)

    def _save_llm_settings(self, model_type: str, model_name: str, temperature: float) -> None:
        """
        Save LLM settings to database and update session state.
        
        Args:
            model_type: Selected model type
            model_name: Selected model name
            temperature: Selected temperature value
        """
        with get_unit_of_work() as uow:
            try:
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
            except Exception as e:
                logger.error(f"Failed to save LLM settings: {str(e)}")
                st.error(f"❌ Failed to save LLM settings: {str(e)}")

    def _render_user_preferences(self) -> None:
        """
        Render and handle user preferences section.
        
        This method handles:
        - Life story input
        - Resume section configurations
        - Section processing preferences
        - Saving preferences to database
        """
        st.header("User Preferences")
        
        with get_unit_of_work() as uow:
            user = uow.users.get_by_user_id(st.session_state['user_id'])
            if not user:
                st.error("User not found")
                return
            
            # Get user profile and preferences
            profile = uow.profiles.get_by_user_id(st.session_state['user_id'])
            
            # Convert Pydantic model to dict if needed
            preferences: Dict[str, Any] = (
                user.preferences.model_dump() 
                if hasattr(user.preferences, 'model_dump') 
                else user.preferences
            )
            
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

            # Section Processing
            with st.expander("Section Processing"):
                st.subheader("Section Processing Preferences")
                section_preferences = preferences.get('section_preferences', {})
                section_values = {}
                for section in [
                    'personal_information', 'career_summary', 'skills',
                    'work_experience', 'education', 'projects', 'awards', 'publications'
                ]:
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
                    'section_preferences': section_values
                }
                
                self._save_preferences(uow, profile, new_preferences, life_story)

    def _render_feature_flags(self) -> None:
        """
        Render feature flags configuration.
        
        Handles:
        - Security clearance check toggle
        - Auto-save toggle
        """
        st.header("Feature Flags")
        
        with get_unit_of_work() as uow:
            preferences = uow.users.get_preferences(st.session_state['user_id'])
            current_flags = preferences.get('feature_preferences', {}) if preferences else {}
            
            # Clearance Check
            clearance_enabled = st.toggle(
                "Security Clearance Check",
                value=current_flags.get('check_clearance', True),
                help="Enable/disable checking for security clearance requirements",
                key="feature_flags_clearance_toggle"
            )
            
            # Auto-save
            auto_save = st.toggle(
                "Auto-save",
                value=current_flags.get('auto_save', True),
                help="Automatically save generated documents",
                key="feature_flags_auto_save_toggle"
            )
            
            if st.button("Save Feature Settings", key="save_features_button"):
                try:
                    uow.users.update_feature_preferences(
                        st.session_state['user_id'],
                        {
                            'check_clearance': clearance_enabled,
                            'auto_save': auto_save
                        }
                    )
                    st.success("✅ Feature settings saved successfully!")
                except Exception as e:
                    logger.error(f"Failed to save feature settings: {str(e)}")
                    st.error(f"❌ Failed to save feature settings: {str(e)}")

    def _save_preferences(self, uow: Any, profile: Optional[Profile], preferences: Dict[str, Any], life_story: str) -> None:
        """Save the updated preferences to the database."""
        try:
            # Update life story in profile
            if profile:
                profile.life_story = life_story
                profile.updated_at = datetime.utcnow()
                uow.profiles.update(profile)
            else:
                # Create new profile if it doesn't exist
                new_profile = Profile(
                    id=None,  # MongoDB will generate this
                    user_id=st.session_state['user_id'],
                    life_story=life_story,
                    personal_information={},  # Empty dict for new profile
                    updated_at=datetime.utcnow()
                )
                uow.profiles.create(new_profile)
            
            # Update preferences
            uow.users.update_preferences(st.session_state['user_id'], preferences)
            
            st.success("✅ Preferences saved successfully!")
            logger.info(f"Preferences updated for user {st.session_state['user_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save preferences: {str(e)}")
            st.error(f"❌ Failed to save preferences: {str(e)}")