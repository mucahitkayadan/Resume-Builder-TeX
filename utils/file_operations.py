import os

def create_output_directory(folder_name: str) -> str:
    output_dir = os.path.join("created_resumes", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def save_job_description(job_description: str, output_dir: str) -> None:
    with open(os.path.join(output_dir, "job_description.txt"), "w") as f:
        f.write(job_description)

