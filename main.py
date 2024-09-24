import os
import logging
import streamlit as st
from tqdm import tqdm
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from loaders.tex_loader import TexLoader
from engine.runners import Runner
from utils.utils import Utils

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_or_create_folder_name(job_description, runner, prompt_loader):
    folder_name_prompt = prompt_loader.get_folder_name_prompt()
    folder_name = runner.create_folder_name(folder_name_prompt, job_description)
    return folder_name

def main():
    logger.info("Starting Resume and Cover Letter Generator")
    st.title("Resume and Cover Letter Generator")

    # Get job description from user
    job_description = st.text_area("Enter the job description:", height=200)

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
    process_career_summary(runner, prompt_loader, json_loader, job_description, output_dir)

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

def create_output_directory(folder_name):
    if not os.path.exists("created_resumes"):
        os.makedirs("created_resumes")
        logger.info("Created 'created_resumes' directory")
    output_dir = os.path.join("created_resumes", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir

def save_job_description(job_description, output_dir):
    job_description_file = os.path.join(output_dir, "job_description.txt")
    with open(job_description_file, "w", encoding="utf-8") as f:
        f.write(job_description)
    logger.info(f"Saved job description to {job_description_file}")

def process_sections(sections, runner, prompt_loader, json_loader, job_description):
    content_dict = {}
    progress_bar = st.progress(0)
    for index, section in enumerate(tqdm(sections, desc="Processing sections")):
        prompt = getattr(prompt_loader, f"get_{section}_prompt")()
        data = getattr(json_loader, f"get_{section}")()
        processed_content = runner.process_section(prompt, data, job_description)
        content_dict[section] = processed_content
        logger.info(f"Processed {section} section")
        progress_bar.progress((index + 1) / len(sections))
    return content_dict

def write_sections_to_files(sections, content_dict, output_dir):
    for section in sections:
        output_file = os.path.join(output_dir, f"{section}.tex")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content_dict[section])
        st.write(f"Content for {section} has been saved to {output_file}")
        logger.info(f"Content for {section} has been saved to {output_file}")

def process_career_summary(runner, prompt_loader, json_loader, job_description, output_dir):
    career_summary_prompt = prompt_loader.get_career_summary_prompt()
    career_summary_data = json_loader.get_career_summary()
    tex_loader_instance = TexLoader(output_dir)
    career_summary_section = runner.process_career_summary(
        career_summary_prompt,
        career_summary_data,
        job_description,
        tex_loader_instance
    )
    logger.info("Processed career summary section")
    career_summary_file = os.path.join(output_dir, "career_summary.tex")
    with open(career_summary_file, "w", encoding="utf-8") as f:
        f.write(career_summary_section)
    st.write(f"Career summary has been saved to {career_summary_file}")
    logger.info(f"Career summary has been saved to {career_summary_file}")

def generate_pdf(output_dir, tex_file):
    logger.info("Generating PDF")
    os.system(f"cd {output_dir} && pdflatex {tex_file}")
    logger.info(f"PDF generated successfully in {output_dir}")

if __name__ == '__main__':
    main()
