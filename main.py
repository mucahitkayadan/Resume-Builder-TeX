import os
import logging
import streamlit as st
from stqdm import stqdm
from tqdm import tqdm
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from loaders.tex_loader import TexLoader
from engine.runners import Runner
from utils.utils import Utils

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Resume Generator")
    st.title("Resume Generator")

    # Get job description from user
    job_description = st.text_area("Enter the job description:", height=200)

    # Add model selection
    model_type = st.selectbox("Select AI model:", ["OpenAI", "Claude"])
    if model_type == "OpenAI":
        model_name = st.selectbox("Select OpenAI model:", ["gpt-4o", "gpt-4o-mini", "gpt-4o-2024-08-06", "o1-mini"])
    else:
        model_name = st.selectbox("Select Claude model:", ["claude-3-5-sonnet-20240620","claude-3-opus-20240229", "claude-3-sonnet-20240229"])

    if st.button("Generate Resume"):
        if not job_description:
            logger.warning("Job description not provided")
            st.error("Please enter a job description.")
            return

        logger.info(f"Generating resume with {model_type} model: {model_name}")

        # Initialize loaders
        json_loader = JsonLoader("files/information.json")
        prompt_loader = PromptLoader("prompts")
        system_prompt = prompt_loader.get_system_prompt()
        folder_name_prompt = prompt_loader.get_folder_name_prompt()
        tex_loader = TexLoader(base_path="tex_template")

        # Initialize runner
        runner_type = "openai" if model_type == "OpenAI" else "claude"
        runner = Runner(runner_type=runner_type, model=model_name, system_prompt=system_prompt)

        # Get folder name from Runner
        folder_name = runner.create_folder_name(folder_name_prompt, job_description)
        logger.info(f"Created folder name: {folder_name}")

        if not os.path.exists("created_resumes"):
            os.makedirs("created_resumes")
            logger.info("Created 'created_resumes' directory")
        # Create output directory under created_resumes folder
        output_dir = os.path.join("created_resumes", folder_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")

        # Copy tex header files
        tex_headers_dir = "tex_headers"
        Utils.copy_tex_headers(tex_headers_dir, output_dir)
        logger.info(f"Copied tex headers from {tex_headers_dir} to {output_dir}")

        # Save job description to a file
        job_description_file = os.path.join(output_dir, "job_description.txt")
        with open(job_description_file, "w", encoding="utf-8") as f:
            f.write(job_description)
        logger.info(f"Saved job description to {job_description_file}")

        # Process each section with progress bars
        sections = [
            "personal_information",
            "skills",
            "work_experience",
            "education",
            "projects",
            # "awards",
            # "publications"
        ]

        content_dict = {}

        # Create a Streamlit progress bar
        progress_bar = st.progress(0)

        # Combined progress bar with tqdm for console
        for index, section in enumerate(tqdm(sections, desc="Processing sections")):
            prompt = getattr(prompt_loader, f"get_{section}_prompt")()
            data = getattr(json_loader, f"get_{section}")()
            processed_content = runner.process_section(prompt, data, job_description)
            content_dict[section] = processed_content
            logger.info(f"Processed {section} section")

            # Update Streamlit progress bar
            progress_bar.progress((index + 1) / len(sections))

        # Write content to individual tex files
        for section in sections:
            output_file = os.path.join(output_dir, f"{section}.tex")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content_dict[section])
            st.write(f"Content for {section} has been saved to {output_file}")
            logger.info(f"Content for {section} has been saved to {output_file}")

        # Process career summary with all sections' content
        career_summary_prompt = prompt_loader.get_career_summary_prompt()
        career_summary_data = json_loader.get_career_summary()
        tex_loader_instance = TexLoader(output_dir)  # Create a new TexLoader instance with the correct directory
        career_summary_section = runner.process_career_summary(
            career_summary_prompt,
            career_summary_data,
            job_description,
            tex_loader_instance
        )
        logger.info("Processed career summary section")

        # Save career summary to tex file
        career_summary_file = os.path.join(output_dir, "career_summary.tex")
        with open(career_summary_file, "w", encoding="utf-8") as f:
            f.write(career_summary_section)
        st.write(f"Career summary has been saved to {career_summary_file}")
        logger.info(f"Career summary has been saved to {career_summary_file}")

        # After writing all the content
        logger.info("Generating PDF")
        os.system(f"cd {output_dir} && pdflatex muja_kayadan_resume.tex")
        st.success(f"Resume generated successfully in {output_dir}")
        logger.info(f"Resume generated successfully in {output_dir}")

if __name__ == '__main__':
    main()
