import os
import logging
import streamlit as st
from utils.database_manager import DatabaseManager
from utils.document_utils import check_clearance_requirement, create_output_directory, get_or_create_folder_name
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.runners import OpenAIRunner, ClaudeRunner
from engine.resume_creator import ResumeCreator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Resume and Cover Letter Generator")
    st.title("Resume and Cover Letter Generator")

    # Initialize database manager
    db_manager = DatabaseManager()

    # Get job description from user
    job_description = st.text_area("Enter the job description:", height=200)

    # Check for clearance requirement
    if check_clearance_requirement(job_description):
        st.warning("This job may require a security clearance or US citizenship. Please review the requirements carefully before proceeding.")

    # Add model selection
    model_type = st.selectbox("Select AI model:", ["OpenAI", "Claude"])
    model_name = st.selectbox("Select OpenAI model:", ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06", "o1-mini"]) if model_type == "OpenAI" else st.selectbox("Select Claude model:", ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229"])

    # Add temperature slider
    temperature = st.slider("Set temperature:", min_value=0.0, max_value=1.0, value=0.1, step=0.1)

    # Initialize common components
    json_loader = JsonLoader("files/information.json")
    prompt_loader = PromptLoader('prompts/')
    system_prompt = prompt_loader.get_system_prompt()

    # Initialize the appropriate runner based on model_type
    if model_type == "OpenAI":
        runner = OpenAIRunner(model_name, temperature, system_prompt)
    else:
        runner = ClaudeRunner(model_name, temperature, system_prompt)

    # Extract company name and job title from job description
    company_name, job_title = get_or_create_folder_name(job_description, runner, prompt_loader)

    # Display extracted information
    st.write(f"Extracted Company Name: {company_name}")
    st.write(f"Extracted Job Title: {job_title}")

    if st.button("Generate Resume"):
        if not job_description:
            st.error("Please enter a job description.")
        else:
            resume_creator = ResumeCreator(runner, json_loader, prompt_loader, db_manager)
            result = resume_creator.generate_resume(
                job_description, 
                company_name, 
                job_title, 
                model_type, 
                runner.__class__.__name__,
                temperature
            )
            st.write(result)

            # Display download button for the generated resume
            output_dir = create_output_directory(f"{company_name}_{job_title}".replace(" ", "_").lower())
            pdf_path = os.path.join(output_dir, 'resume.pdf')
            if os.path.exists(pdf_path):
                with open(pdf_path, "rb") as file:
                    btn = st.download_button(
                        label="Download Resume PDF",
                        data=file,
                        file_name="resume.pdf",
                        mime="application/pdf"
                    )

if __name__ == "__main__":
    main()