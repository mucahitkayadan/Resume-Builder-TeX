import os

def create_output_directory(company_name: str, job_title: str) -> str:
    """
    Create an output directory for storing generated files.
    
    Args:
        company_name (str): Name of the company
        job_title (str): Title of the job position
        
    Returns:
        str: Path to the created output directory
    """
    folder_name = f"{company_name}_{job_title}".replace(" ", "_")
    output_dir = os.path.join("created_resumes", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def get_latest_resume_path(output_dir):
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    if not pdf_files:
        return None
    return os.path.join(output_dir, max(pdf_files))

def save_job_description(job_description: str, output_dir: str) -> None:
    file_path = os.path.join(output_dir, 'job_description.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(job_description)
