import streamlit as st
from src.core.database.factory import get_unit_of_work
from config.logger_config import setup_logger
from config.settings import FEATURE_FLAGS

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
        # Add user-specific settings here

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