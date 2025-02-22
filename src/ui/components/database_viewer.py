from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

from src.core.database.factory import get_unit_of_work


class DatabaseViewer:
    def __init__(self):
        self.uow = get_unit_of_work()

    def get_display_name(self, resume) -> str:
        """Generate a display name for the resume"""
        if isinstance(resume.personal_information, dict):
            # For structured data
            name = resume.personal_information.get("name", "Unnamed")
        else:
            # For LaTeX format
            name = resume.title or "Unnamed"

        return f"{name}_{resume.created_at.strftime('%Y%m%d')}"

    def render(self):
        st.title("📊 Resume Database")

        with self.uow:
            # Fetch all resumes from the database
            resumes = self.uow.resumes.get_all()

            if not resumes:
                st.info("🔍 No resumes found in the database.")
                return

            # Calculate statistics
            total_resumes = len(resumes)
            today = datetime.now().date()
            today_resumes = sum(1 for r in resumes if r.created_at.date() == today)
            last_7_days = sum(
                1 for r in resumes if (today - r.created_at.date()).days <= 7
            )

            # Display statistics in columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Total Resumes", total_resumes, help="Total number of resumes"
                )

            with col2:
                st.metric(
                    "Today's Resumes", today_resumes, help="Resumes created today"
                )

            with col3:
                st.metric("Last 7 Days", last_7_days, help="Resumes in the last week")

            # Add a separator
            st.divider()

            # Convert resumes to DataFrame format
            df_data = [
                {
                    "ID": resume.id,
                    "Display Name": self.get_display_name(resume),
                    "Title": resume.title,
                    "Version": resume.version,
                    "Created At": resume.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for resume in resumes
            ]
            df = pd.DataFrame(df_data)

            # Sort by creation date in descending order
            df = df.sort_values("Created At", ascending=False)

            # Display the DataFrame
            st.dataframe(
                df[["Display Name", "Title", "Version", "Created At"]],
                use_container_width=True,
            )

            # Allow user to select a resume by display name
            selected_display_name = st.selectbox(
                "Select a resume to view details:", df["Display Name"].tolist(), index=0
            )

            # Get the corresponding ID
            selected_resume_id = df[df["Display Name"] == selected_display_name][
                "ID"
            ].iloc[0]

            if selected_resume_id:
                resume = self.uow.resumes.get_by_id(selected_resume_id)
                if resume:
                    # Create tabs for different views
                    tab1, tab2 = st.tabs(["📝 Content", "📄 Documents"])

                    with tab1:
                        st.subheader(f"Details for: {selected_display_name}")

                        # Display resume sections in expanders
                        sections = [
                            ("Personal Information", resume.personal_information),
                            ("Career Summary", resume.career_summary),
                            ("Skills", resume.skills),
                            ("Work Experience", resume.work_experience),
                            ("Education", resume.education),
                            ("Projects", resume.projects),
                            ("Awards", resume.awards),
                            ("Publications", resume.publications),
                        ]

                        for section_name, content in sections:
                            if content:
                                with st.expander(section_name):
                                    if isinstance(content, (dict, list)):
                                        st.json(content)
                                    else:
                                        st.markdown(content)

                    with tab2:
                        if resume.resume_pdf:
                            st.subheader("Resume PDF")
                            st.download_button(
                                "⬇️ Download Resume PDF",
                                resume.resume_pdf,
                                file_name=f"{selected_display_name}_resume.pdf",
                                mime="application/pdf",
                            )
                            # Display PDF
                            pdf_viewer(resume.resume_pdf)

                        if resume.cover_letter_pdf:
                            st.subheader("Cover Letter PDF")
                            st.download_button(
                                "⬇️ Download Cover Letter PDF",
                                resume.cover_letter_pdf,
                                file_name=f"{selected_display_name}_cover_letter.pdf",
                                mime="application/pdf",
                            )
                            # Display PDF
                            pdf_viewer(resume.cover_letter_pdf)
