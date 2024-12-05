import streamlit as st
from src.core.database.factory import get_unit_of_work
from config.logger_config import setup_logger

logger = setup_logger(__name__)

class SectionManagerPage:
    def __init__(self, section_selector):
        self.section_selector = section_selector

    def render(self):
        st.title("📋 Section Manager")
        
        tab1, tab2, tab3 = st.tabs([
            "Default Sections", 
            "Custom Sections", 
            "Section Templates"
        ])
        
        with tab1:
            self._render_default_sections()
        
        with tab2:
            self._render_custom_sections()
        
        with tab3:
            self._render_section_templates()

    def _render_default_sections(self):
        st.header("Default Section Configuration")
        user_sections = self.section_selector.get_user_section_selection()
        
        if st.button("Save Default Configuration"):
            with get_unit_of_work() as uow:
                uow.users.update_section_preferences(
                    st.session_state['user_id'],
                    user_sections
                )
                st.success("Default sections saved!")

    def _render_custom_sections(self):
        st.header("Custom Sections")
        # Add custom section management here

    def _render_section_templates(self):
        st.header("Section Templates")
        # Add template management here 