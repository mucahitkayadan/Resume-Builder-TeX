import streamlit as st
from typing import Dict

class SectionSelector:
    def __init__(self):
        self.sections = [
            "personal_information", "career_summary", "skills", "work_experience",
            "education", "projects", "awards", "publications"
        ]
        self.options = ["Process", "Hardcode", "Skip"]

    def get_user_section_selection(self) -> Dict[str, str]:
        """
        Creates a UI for selecting how to handle each resume section.
        
        Returns:
            Dict[str, str]: Dictionary mapping section names to their selected handling method
        """
        selected_sections = {}
        
        st.subheader("Section Handling")

        # Create column headers
        col1, col2 = st.columns([2, 3])
        col1.write("**Section**")
        col2.write("**Action**")

        # Create rows for each section
        for section in self.sections:
            col1, col2 = st.columns([2, 3])
            col1.write(section.replace("_", " ").title())

            # Create radio buttons for each option
            selected_option = col2.radio(
                f"Select action for {section}",
                self.options,
                index=0,  # Default to "Process"
                key=f"section_{section}",
                label_visibility="collapsed",
                horizontal=True
            )

            selected_sections[section] = selected_option.lower()

        return selected_sections
