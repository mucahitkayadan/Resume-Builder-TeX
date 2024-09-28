import logging
import os
import streamlit as st
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from loaders.tex_loader import TexLoader
from engine.runners import Runner
from utils.utils import Utils
from utils.document_utils import (
    check_clearance_requirement,
    create_output_directory,
    save_job_description,
    process_sections,
    write_sections_to_files,
    generate_pdf,
    get_or_create_folder_name,
    process_career_summary
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Resume and Cover Letter Generator")
    st.title("Resume and Cover Letter Generator")

    # Get job description from user
    job_description = st.text_area("Enter the job description:", height=200)

    # Check for clearance requirement
    if check_clearance_requirement(job_description):
        st.warning("This job may require a security clearance or US citizenship. Please review the requirements carefully before proceeding.")

    # Add model selection
    model_type = st.selectbox("Select AI model:", ["OpenAI", "Claude"])
    if model_type == "OpenAI":
        model_name = st.selectbox("Select OpenAI model:", ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06", "o1-mini"])
    else:
        model_name = st.selectbox("Select Claude model:", ["claude-3-5-sonnet-20240620","claude-3-opus-20240229", "claude-3-sonnet-20240229"])

    # Add temperature slider
    temperature = st.slider("Set temperature:", min_value=0.0, max_value=1.0, value=0.1, step=0.1)

    # Initialize common components
    json_loader = JsonLoader("files/information.json")
    prompt_loader = PromptLoader("prompts")
    system_prompt = prompt_loader.get_system_prompt()
    runner_type = "openai" if model_type == "OpenAI" else "claude"
    runner = Runner(runner_type=runner_type, model=model_name, system_prompt=system_prompt, temperature=temperature)

    # Generate folder name once
    folder_name = get_or_create_folder_name(job_description, runner, prompt_loader)

    # Add radio button for document selection
    document_choice = st.radio(
        "Choose what to generate:",
        ("Resume Only", "Resume and Cover Letter")
    )

    if st.button("Generate"):
        if not job_description:
            st.error("Please enter a job description.")
        elif check_clearance_requirement(job_description):
            st.error("This job requires a security clearance or US citizenship. Unable to proceed with generation.")
        else:
            if document_choice == "Resume Only":
                generate_resume(job_description, runner, json_loader, prompt_loader, folder_name)
            else:
                generate_resume_and_cover_letter(job_description, runner, json_loader, prompt_loader, folder_name)

def generate_resume(job_description, runner, json_loader, prompt_loader, folder_name):
    if not job_description:
        logger.warning("Job description not provided")
        st.error("Please enter a job description.")
        return

    logger.info(f"Generating resume with {runner.runner_type} model: {runner.model}")

    output_dir = create_output_directory(folder_name)

    # Copy tex header files
    Utils.copy_tex_headers("tex_headers", output_dir)

    # Save job description
    save_job_description(job_description, output_dir)

    # Process sections
    sections = ["personal_information", "skills", "work_experience", "education", "projects"]
    content_dict = process_sections(sections, runner, prompt_loader, json_loader, job_description)

    # Write content to individual tex files
    write_sections_to_files(sections, content_dict, output_dir)

    # Process career summary
    career_summary_file = process_career_summary(runner, prompt_loader, json_loader, job_description, output_dir)
    st.write(f"Career summary has been saved to {career_summary_file}")
    logger.info(f"Career summary has been saved to {career_summary_file}")

    # Generate PDF
    generate_pdf(output_dir, "muja_kayadan_resume.tex")
    st.success(f"Resume generated successfully in {output_dir}")

def generate_resume_and_cover_letter(job_description, runner, json_loader, prompt_loader, folder_name):
    generate_resume(job_description, runner, json_loader, prompt_loader, folder_name)
    generate_cover_letter(job_description, runner, json_loader, prompt_loader, folder_name)

def generate_cover_letter(job_description, runner, json_loader, prompt_loader, folder_name):
    if not job_description:
        logger.warning("Job description not provided")
        st.error("Please enter a job description.")
        return

    logger.info(f"Generating cover letter with {runner.runner_type} model: {runner.model}")

    output_dir = create_output_directory(folder_name)

    cover_letter_prompt = prompt_loader.get_cover_letter_prompt()
    tex_loader_instance = TexLoader(output_dir)
    cover_letter_content = runner.process_cover_letter(cover_letter_prompt, tex_loader_instance, job_description)

    # Save cover letter to tex file
    cover_letter_file = os.path.join(output_dir, "cover_letter.tex")
    with open(cover_letter_file, "w", encoding="utf-8") as f:
        f.write(cover_letter_content)
    st.write(f"Cover letter has been saved to {cover_letter_file}")
    logger.info(f"Cover letter has been saved to {cover_letter_file}")

    # Generate PDF
    generate_pdf(output_dir, "cover_letter.tex")
    st.success(f"Cover letter generated successfully in {output_dir}")

if __name__ == '__main__':
    main()
