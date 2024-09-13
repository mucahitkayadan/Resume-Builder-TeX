import os
import streamlit as st
from loaders.tex_loader import TexLoader
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from engine.process_section import OpenAIRunner
from utils.utils import Utils

def main():
    st.title("Resume Generator")

    # Get job description from user
    job_description = st.text_area("Enter the job description:", height=200)

    if st.button("Generate Resume"):
        if not job_description:
            st.error("Please enter a job description.")
            return

        # Initialize loaders
        json_loader = JsonLoader("files/information.json")
        prompt_loader = PromptLoader("prompts")
        system_prompt = prompt_loader.get_system_prompt()
        folder_name_prompt = prompt_loader.get_folder_name_prompt()
        openai_runner = OpenAIRunner(system_prompt=system_prompt)

        # Get folder name from OpenAIRunner
        folder_name = openai_runner.create_folder_name(folder_name_prompt, job_description)

        if not os.path.exists("created_resumes"):
            os.makedirs("created_resumes")
        # Create output directory under created_resumes folder
        output_dir = os.path.join("created_resumes", folder_name)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Copy tex header files
        tex_headers_dir = "tex_headers"
        Utils.copy_tex_headers(tex_headers_dir, output_dir)

        # Save job description to a file
        job_description_file = os.path.join(output_dir, "job_description.txt")
        with open(job_description_file, "w") as f:
            f.write(job_description)

        # Process each section
        sections = [
            "personal_information",
            "career_summary",
            "skills",
            "work_experience",
            "education",
            "projects",
            "awards",
            "publications"
        ]

        content_dict = {}

        for section in sections:
            prompt = getattr(prompt_loader, f"get_{section}_prompt")()
            data = getattr(json_loader, f"get_{section}")()
            processed_content = getattr(openai_runner, f"process_{section}")(prompt, data, job_description)
            content_dict[section] = processed_content

        # Write content to individual tex files
        for section in sections:
            output_file = os.path.join(output_dir, f"{section}.tex")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(content_dict[section])
            st.write(f"Content for {section} has been saved to {output_file}")

        # After writing all the content
        os.system(f"cd {output_dir} && pdflatex muja_kayadan_resume.tex")
        st.success(f"Resume generated successfully in {output_dir}")

if __name__ == '__main__':
    main()
