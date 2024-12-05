import streamlit as st
import pandas as pd
from src.core.database.factory import get_unit_of_work
from streamlit_pdf_viewer import pdf_viewer


class DatabaseViewer:
    def __init__(self):
        self.uow = get_unit_of_work()

    def render(self):
        st.title(" Resume Database")
        
        with self.uow:
            # Fetch all resumes from the database
            resumes = self.uow.resumes.get_all()

            if not resumes:
                st.info("🔍 No resumes found in the database.")
            else:
                # Convert resumes to DataFrame format
                df_data = [
                    {
                        'ID': resume.id,
                        'Display Name': f"{resume.company_name}_{resume.job_title}",
                        'Company Name': resume.company_name,
                        'Job Title': resume.job_title,
                        'Creation Date': resume.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    for resume in resumes
                ]
                df = pd.DataFrame(df_data)
                
                # Sort by creation date in descending order
                df = df.sort_values('Creation Date', ascending=False)

                # Display the DataFrame
                st.dataframe(
                    df[['Display Name', 'Company Name', 'Job Title', 'Creation Date']],
                    use_container_width=True
                )

                # Allow user to select a resume by display name
                selected_display_name = st.selectbox(
                    "Select a resume to view details:",
                    df['Display Name'].tolist(),
                    index=0
                )
                
                # Get the corresponding ID
                selected_resume_id = df[df['Display Name'] == selected_display_name]['ID'].iloc[0]

                if selected_resume_id:
                    resume = self.uow.resumes.get_by_id(selected_resume_id)
                    if resume:
                        # Create tabs for different views
                        tab1, tab2 = st.tabs(["📝 Content", "📄 Documents"])
                        
                        with tab1:
                            st.subheader(f"Details for: {selected_display_name}")
                            
                            # Display resume sections in expanders
                            sections = [
                                'personal_information', 'career_summary', 'skills',
                                'work_experience', 'education', 'projects',
                                'awards', 'publications'
                            ]
                            
                            for section in sections:
                                content = getattr(resume, section)
                                if content:
                                    with st.expander(section.replace('_', ' ').title()):
                                        st.markdown(content)
                        
                        with tab2:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if resume.resume_pdf:
                                    st.subheader("Resume PDF")
                                    st.download_button(
                                        "⬇️ Download Resume PDF",
                                        resume.resume_pdf,
                                        file_name=f"{selected_display_name}_resume.pdf",
                                        mime="application/pdf"
                                    )
                                    # Display PDF
                                    pdf_viewer(resume.resume_pdf)
                            
                            with col2:
                                if resume.cover_letter_pdf:
                                    st.subheader("Cover Letter PDF")
                                    st.download_button(
                                        "⬇️ Download Cover Letter PDF",
                                        resume.cover_letter_pdf,
                                        file_name=f"{selected_display_name}_cover_letter.pdf",
                                        mime="application/pdf"
                                    )
                                    # Display PDF
                                    pdf_viewer(resume.cover_letter_pdf)
