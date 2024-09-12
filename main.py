import os
from loaders.tex_loader import TexLoader
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from src.process_section import OpenAIRunner
from loaders.job_description_loader import JobDescriptionLoader

# def parse_personal_info(info_string):
#     info_dict = {}
#     lines = info_string.strip().split('\n')
#     for line in lines:
#         if ':' in line:
#             key, value = line.split(':', 1)
#             info_dict[key.strip()] = value.strip()
#     return info_dict

def main():
    # Initialize loaders
    job_description_loader = JobDescriptionLoader("../files/job_description.txt")
    job_description = job_description_loader.get_job_description()
    tex_loader = TexLoader("tex_template")
    json_loader = JsonLoader("files/information.json")
    prompt_loader = PromptLoader("prompts")
    openai_runner = OpenAIRunner()


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

    # Create output directory if it doesn't exist
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write content to individual tex files
    for section in sections:
        output_file = os.path.join(output_dir, f"{section}.tex")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content_dict[section])
        print(f"Content for {section} has been saved to {output_file}")

    # Load and write main LaTeX template
    main_template = tex_loader.get_main()
    main_output_file = os.path.join(output_dir, "main.tex")
    with open(main_output_file, "w", encoding="utf-8") as f:
        f.write(main_template)
    print(f"Main LaTeX template has been saved to {main_output_file}")

if __name__ == '__main__':
    main()
