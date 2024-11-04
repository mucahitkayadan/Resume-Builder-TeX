import streamlit as st
import pandas as pd
from utils.database_manager import DatabaseManager
from streamlit_pdf_viewer import pdf_viewer

def view_database():
    st.title("Resume Database Viewer")

    # Initialize DatabaseManager
    db_manager = DatabaseManager()

    # Fetch all resumes from the database
    resumes = db_manager.get_all_resumes()

    if not resumes:
        st.write("No resumes found in the database.")
    else:
        # Convert the resumes data to a pandas DataFrame
        df = pd.DataFrame(resumes, columns=['ID', 'Company Name', 'Job Title', 'Creation Date'])
        
        # Sort the DataFrame by ID in descending order
        df = df.sort_values('ID', ascending=False)

        # Display the DataFrame
        st.dataframe(df)

        # Allow user to select a resume to view details
        selected_resume_id = st.selectbox("Select a resume to view details:", df['ID'], index=0)

        if selected_resume_id:
            resume_details = db_manager.get_resume_full(selected_resume_id)
            if resume_details:
                st.subheader(f"Details for Resume ID: {selected_resume_id}")
                for key, value in resume_details.items():
                    if key not in ['pdf_content', 'cover_letter_pdf']:
                        st.text_area(key, value, height=100)
                
                # Add buttons to download PDF content
                if resume_details.get('pdf_content'):
                    st.download_button(
                        label="Download Resume PDF",
                        data=resume_details['pdf_content'],
                        file_name=f"resume_{selected_resume_id}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Display the PDF using streamlit-pdf-viewer
                    pdf_viewer(resume_details['pdf_content'])

                if resume_details.get('cover_letter_pdf'):
                    st.download_button(
                        label="Download Cover Letter PDF",
                        data=resume_details['cover_letter_pdf'],
                        file_name=f"cover_letter_{selected_resume_id}.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    view_database()
