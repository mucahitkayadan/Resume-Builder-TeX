import logging
import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)

from engine.hardcode_sections import HardcodeSections
from loaders.json_loader import JsonLoader
from loaders.tex_loader import TexLoader
from utils.database_manager import DatabaseManager
from utils.latex_compiler import generate_resume_pdf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hardcode_sections_pdf():
    # Initialize loaders and hardcoder
    json_loader = JsonLoader(os.path.join(project_root, "files", "information.json"))
    
    # Initialize DatabaseManager with the correct path
    db_path = os.path.join(project_root, "resumes_backup.db")
    db_manager = DatabaseManager(db_path)
    
    # Initialize TexLoader with the DatabaseManager instance
    tex_loader = TexLoader(db_manager)
    
    hardcoder = HardcodeSections(json_loader, tex_loader)

    # Get preamble from database
    preamble = db_manager.get_preamble()

    # Hardcode all sections
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
        try:
            content_dict[section] = hardcoder.hardcode_section(section)
        except ValueError as e:
            logger.warning(f"Warning: {str(e)}")
            content_dict[section] = f"% {section} section not implemented"

    # Combine preamble and content
    full_content = preamble + "\n\\begin{document}\n\n"
    for section_content in content_dict.values():
        full_content += section_content + "\n\n"
    full_content += "\n\\end{document}"

    # Save the full content to a file
    output_dir = os.path.join(project_root, "test_output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "test_resume.tex")
    with open(output_file, "w") as f:
        f.write(full_content)

    logger.info(f"Test resume content saved to {output_file}")

    # Generate PDF
    try:
        pdf_content = generate_resume_pdf(db_manager, content_dict, output_dir)
        logger.info("PDF generation successful")
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")

if __name__ == "__main__":
    test_hardcode_sections_pdf()
