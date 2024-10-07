import os
import logging
from typing import List, Dict, Tuple, Any
from tqdm import tqdm
import streamlit as st
from loaders.tex_loader import TexLoader
import re

logger = logging.getLogger(__name__)

def check_clearance_requirement(job_description: str) -> bool:
    """
    Check if the job description contains keywords related to security clearance requirements.

    Args:
        job_description (str): The job description text.

    Returns:
        bool: True if clearance-related keywords are found, False otherwise.
    """
    clearance_keywords = ["security clearance", "clearance required", "US citizen only", "US Citizen", "Permanent Resident"]
    return any(keyword.lower() in job_description.lower() for keyword in clearance_keywords)

def create_output_directory(folder_name: str) -> str:
    """
    Create an output directory for storing resume files.

    Args:
        folder_name (str): The name of the folder to create.

    Returns:
        str: The path to the created output directory.
    """
    if not os.path.exists("created_resumes"):
        os.makedirs("created_resumes")
        logger.info("Created 'created_resumes' directory")
    output_dir = os.path.join("created_resumes", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    return output_dir

def save_job_description(job_description: str, output_dir: str) -> None:
    """
    Save the job description to a file in the output directory.

    Args:
        job_description (str): The job description text.
        output_dir (str): The path to the output directory.
    """
    job_description_file = os.path.join(output_dir, "job_description.txt")
    with open(job_description_file, "w", encoding="utf-8") as f:
        f.write(job_description)
    logger.info(f"Saved job description to {job_description_file}")

def process_sections(sections: List[str], runner: Any, prompt_loader: Any, json_loader: Any, job_description: str) -> Dict[str, str]:
    """
    Process each section of the resume using the provided runner and loaders.

    Args:
        sections (List[str]): List of section names to process.
        runner (Any): The runner object for processing sections.
        prompt_loader (Any): The prompt loader object.
        json_loader (Any): The JSON loader object.
        job_description (str): The job description text.

    Returns:
        Dict[str, str]: A dictionary containing processed content for each section.
    """
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

def write_sections_to_files(sections: List[str], content_dict: Dict[str, str], output_dir: str) -> None:
    """
    Write the processed content of each section to individual files.

    Args:
        sections (List[str]): List of section names.
        content_dict (Dict[str, str]): Dictionary containing processed content for each section.
        output_dir (str): The path to the output directory.
    """
    for section in sections:
        output_file = os.path.join(output_dir, f"{section}.tex")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content_dict[section])
        st.write(f"Content for {section} has been saved to {output_file}")
        logger.info(f"Content for {section} has been saved to {output_file}")

def generate_pdf(output_dir: str, tex_file: str) -> None:
    """
    Generate a PDF from the LaTeX file.

    Args:
        output_dir (str): The path to the output directory.
        tex_file (str): The name of the LaTeX file.
    """
    logger.info("Generating PDF")
    os.system(f"cd {output_dir} && pdflatex {tex_file}")
    logger.info(f"PDF generated successfully in {output_dir}")

def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename by removing invalid characters.

    Args:
        name (str): The original string.

    Returns:
        str: The sanitized string.
    """
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def get_or_create_folder_name(job_description: str, runner: Any, prompt_loader: Any) -> Tuple[str, str]:
    """
    Generate a folder name based on the job description.

    Args:
        job_description (str): The job description text.
        runner (Any): The runner object for creating folder names.
        prompt_loader (Any): The prompt loader object.

    Returns:
        Tuple[str, str]: A tuple containing the company name and job title.
    """
    folder_name_prompt = prompt_loader.get_folder_name_prompt()
    result = runner.create_folder_name(folder_name_prompt, job_description)
    
    try:
        company_name, job_title = result.split('|')
        company_name = sanitize_filename(company_name.strip())
        job_title = sanitize_filename(job_title.strip())
    except ValueError:
        logger.warning(f"Unexpected format returned by create_folder_name: {result}")
        company_name = "Unknown_Company"
        job_title = sanitize_filename(job_description[:50].replace(" ", "_"))

    if not company_name:
        company_name = "Unknown_Company"
    if not job_title:
        job_title = "Unknown_Position"

    company_name = company_name[:50]
    job_title = job_title[:50]

    folder_name = f"{company_name}_{job_title}"
    logger.info(f"Created folder name: {folder_name}")
    return company_name, job_title

def process_career_summary(runner: Any, prompt_loader: Any, json_loader: Any, job_description: str) -> str:
    """
    Process the career summary section.

    Args:
        runner (Any): The runner object for processing sections.
        prompt_loader (Any): The prompt loader object.
        json_loader (Any): The JSON loader object.
        job_description (str): The job description text.

    Returns:
        str: The processed career summary section.
    """
    career_summary_prompt = prompt_loader.get_career_summary_prompt()
    career_summary_data = json_loader.get_career_summary()
    career_summary_section = runner.process_career_summary(
        career_summary_prompt,
        career_summary_data,
        job_description
    )
    return career_summary_section