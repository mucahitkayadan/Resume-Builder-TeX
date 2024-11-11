import streamlit as st
import pandas as pd
from src.core.database.factory import get_unit_of_work
from streamlit_pdf_viewer import pdf_viewer


def view_database():
    st.title("Resume Database Viewer")

    # Initialize UnitOfWork
    uow = get_unit_of_work()

    with uow:
        # Fetch all resumes from the database
        resumes = uow.resumes.get_all()

        if not resumes:
            st.write("No resumes found in the database.")
        else:
            # Convert resumes to DataFrame format
            df_data = [
                {
                    'ID': resume.id,
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
            st.dataframe(df)

            # Allow user to select a resume
            selected_resume_id = st.selectbox("Select a resume to view details:", df['ID'].tolist(), index=0)

            if selected_resume_id:
                resume = uow.resumes.get_by_id(selected_resume_id)
                if resume:
                    st.subheader(f"Details for Resume ID: {selected_resume_id}")
                    
                    # Display resume sections
                    sections = [
                        'personal_information', 'career_summary', 'skills',
                        'work_experience', 'education', 'projects',
                        'awards', 'publications'
                    ]
                    
                    for section in sections:
                        content = getattr(resume, section)
                        if content:
                            st.text_area(section.replace('_', ' ').title(), content, height=100)

                    # Handle PDF content
                    if resume.resume_pdf:
                        st.download_button(
                            label="Download Resume PDF",
                            data=resume.resume_pdf,
                            file_name=f"resume_{selected_resume_id}.pdf",
                            mime="application/pdf"
                        )
                        
                        # Display PDF using streamlit-pdf-viewer
                        pdf_viewer(resume.resume_pdf)

                    if resume.cover_letter_pdf:
                        st.download_button(
                            label="Download Cover Letter PDF",
                            data=resume.cover_letter_pdf,
                            file_name=f"cover_letter_{selected_resume_id}.pdf",
                            mime="application/pdf"
                        )

if __name__ == "__main__":
    view_database()
