import os
import logging
import streamlit as st
from utils.database_manager import DatabaseManager
from utils.document_utils import check_clearance_requirement, create_output_directory, get_or_create_folder_name
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.runners import OpenAIRunner, ClaudeRunner
from engine.resume_creator import ResumeCreator
from engine.cover_letter_creator import CoverLetterCreator

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
    clearance_required = check_clearance_requirement(job_description)

    # Add model selection
    model_type = st.selectbox("Select AI model:", ["OpenAI", "Claude"])
    model_name = st.selectbox("Select OpenAI model:", ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06", "o1-mini", "gpt-4o-2024-05-13"]) \
        if model_type == "OpenAI" else (
        st.selectbox("Select Claude model:",
                     ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229"]))

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

    generation_option = st.selectbox("Choose generation option", ["Resume", "Cover Letter", "Both"])
    
    if st.button("Generate"):
        if clearance_required:
            st.error("This job requires a security clearance or US citizenship. Resume generation is not available for this job.")
        else:
            progress_bar = st.progress(0)
            status_area = st.empty()
            resume_id = None
            generation_completed = False

            if generation_option in ["Resume", "Both"]:
                try:
                    resume_creator = ResumeCreator(runner, json_loader, prompt_loader, db_manager)
                    for update, progress in resume_creator.generate_resume(job_description, company_name, job_title, model_type, model_name, temperature):
                        progress_bar.progress(progress * 0.5 if generation_option == "Both" else progress)
                        status_area.info(update)
                    
                    resume_id = db_manager.get_latest_resume_id()
                    generation_completed = True
                except Exception as e:
                    st.error(f"Error generating resume: {str(e)}")
                    resume_id = None

            if generation_option in ["Cover Letter", "Both"]:
                if resume_id is None and generation_option == "Both":
                    st.error("Failed to generate resume. Cannot proceed with cover letter generation.")
                elif resume_id is None:
                    st.error("Please generate a resume first.")
                else:
                    try:
                        cover_letter_creator = CoverLetterCreator(runner, json_loader, prompt_loader, db_manager)
                        cover_letter_result = cover_letter_creator.generate_cover_letter(
                            job_description, 
                            resume_id, 
                            company_name, 
                            job_title
                        )
                        st.write(cover_letter_result)
                        progress_bar.progress(1.0)
                        status_area.info("Cover letter generated successfully")
                        generation_completed = True
                    except Exception as e:
                        st.error(f"Error generating cover letter: {str(e)}")

            if generation_completed:
                st.success("Generation completed!")
            else:
                st.warning("Generation was not completed due to errors.")

if __name__ == "__main__":
    main()