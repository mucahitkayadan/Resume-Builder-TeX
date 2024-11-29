import logging
import os
from pathlib import Path

from src.resume.hardcode_sections import HardcodeSections
from src.core.database.factory import get_unit_of_work
from src.latex.resume.resume_compiler import ResumeLatexCompiler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def hardcode_sections_demo():
    # Setup paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    output_dir = os.path.join(project_root, "test_output")
    os.makedirs(output_dir, exist_ok=True)
    latex_compiler = ResumeLatexCompiler()

    # Initialize UnitOfWork and components
    uow = get_unit_of_work()
    hardcoder = HardcodeSections()

    with uow:
        # Get latest resume for testing
        test_resume = uow.resumes.get_latest_resume('mujakayadan')
        if not test_resume:
            logger.error("No resume found in database for testing")
            return

        # Generate content dictionary from resume
        content_dict = {}
        sections = [
            'personal_information', 'career_summary', 'skills',
            'work_experience', 'education', 'projects',
            'awards', 'publications'
        ]

        for section in sections:
            try:
                method = getattr(hardcoder, f"hardcode_{section}", None)
                if not method:
                    logger.error(f"No hardcode method for section: {section}")
                    continue
                content_dict[section] = method(test_resume)
                logger.info(f"Successfully hardcoded section: {section}")
            except Exception as e:
                logger.error(f"Error hardcoding section {section}: {str(e)}")

        # Generate PDF
        try:
            pdf_content = latex_compiler.generate_pdf(content_dict, Path(output_dir))
            if pdf_content:
                logger.info("PDF generated successfully")
            else:
                logger.error("PDF generation returned None")
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")

if __name__ == '__main__':
    hardcode_sections_demo()
