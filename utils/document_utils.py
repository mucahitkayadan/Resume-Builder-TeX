import os
import logging
from tqdm import tqdm
import streamlit as st
from loaders.tex_loader import TexLoader
import re

logger = logging.getLogger(__name__)

def check_clearance_requirement(job_description):
    clearance_keywords = ["security clearance", "clearance required", "US citizen only", "US Citizen", "Permanent Resident"]
    return any(keyword.lower() in job_description.lower() for keyword in clearance_keywords)

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

def generate_pdf(output_dir, tex_file):
    logger.info("Generating PDF")
    os.system(f"cd {output_dir} && pdflatex {tex_file}")
    logger.info(f"PDF generated successfully in {output_dir}")

def sanitize_filename(name):
    # Remove or replace characters that are invalid in filenames
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def get_or_create_folder_name(job_description, runner, prompt_loader):
    folder_name_prompt = prompt_loader.get_folder_name_prompt()
    result = runner.create_folder_name(folder_name_prompt, job_description)
    
    try:
        company_name, job_title = result.split('|')
        company_name = sanitize_filename(company_name.strip())
        job_title = sanitize_filename(job_title.strip())
    except ValueError:
        logger.warning(f"Unexpected format returned by create_folder_name: {result}")
        # Fallback: Use a generic name and the first 50 characters of the job description
        company_name = "Unknown_Company"
        job_title = sanitize_filename(job_description[:50].replace(" ", "_"))

    # Ensure we have non-empty values
    if not company_name:
        company_name = "Unknown_Company"
    if not job_title:
        job_title = "Unknown_Position"

    # Limit the length of each part
    company_name = company_name[:50]
    job_title = job_title[:50]

    folder_name = f"{company_name}_{job_title}"
    logger.info(f"Created folder name: {folder_name}")
    return company_name, job_title

def process_career_summary(runner, prompt_loader, json_loader, job_description):
    career_summary_prompt = prompt_loader.get_career_summary_prompt()
    career_summary_data = json_loader.get_career_summary()
    career_summary_section = runner.process_career_summary(
        career_summary_prompt,
        career_summary_data,
        job_description
    )
    return career_summary_section