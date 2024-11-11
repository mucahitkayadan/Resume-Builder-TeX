import logging
import os
from engine.hardcode_sections import HardcodeSections
from src.loaders.tex_loader import TexLoader
from src.core.database.factory import get_unit_of_work
from utils.latex_compiler import generate_resume_pdf

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_hardcode_sections():
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_dir = os.path.join(project_root, "test_output")
    os.makedirs(output_dir, exist_ok=True)

    # Initialize UnitOfWork and components
    uow = get_unit_of_work()
    tex_loader = TexLoader(uow)
    hardcoder = HardcodeSections(uow, tex_loader)

    with uow:
        # Get latest resume for testing
        test_resume = uow.resumes.get_latest_resume()
        if not test_resume:
            logger.error("No resume found in database for testing")
            return

        # Generate content dictionary from resume
        content_dict = {
            'personal_information': hardcoder.hardcode_personal_information(test_resume),
            'career_summary': hardcoder.hardcode_career_summary(test_resume),
            'skills': hardcoder.hardcode_skills(test_resume),
            'work_experience': hardcoder.hardcode_work_experience(test_resume),
            'education': hardcoder.hardcode_education(test_resume),
            'projects': hardcoder.hardcode_projects(test_resume),
            'awards': hardcoder.hardcode_awards(test_resume),
            'publications': hardcoder.hardcode_publications(test_resume)
        }

        # Generate PDF
        try:
            pdf_content = generate_resume_pdf(uow, content_dict, output_dir)
            if pdf_content:
                logger.info("PDF generation successful")
            else:
                logger.error("PDF generation failed")
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")

if __name__ == '__main__':
    test_hardcode_sections()
