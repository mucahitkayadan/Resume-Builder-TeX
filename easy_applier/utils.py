import os

def create_output_directory(company_name, job_title):
    folder_name = f"{company_name}_{job_title}".replace(" ", "_")
    output_dir = os.path.join("created_resumes", folder_name)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def get_latest_resume_path(output_dir):
    pdf_files = [f for f in os.listdir(output_dir) if f.endswith('.pdf')]
    if not pdf_files:
        return None
    return os.path.join(output_dir, max(pdf_files))

