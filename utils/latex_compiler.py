import os
import subprocess
import logging
from typing import Dict, Optional, Any, Tuple
import unicodedata
from core.database.unit_of_work.mongo_unit_of_work import MongoUnitOfWork

logger = logging.getLogger(__name__)

def generate_resume_pdf(uow: MongoUnitOfWork, content_dict: Dict[str, str], output_dir: str, filename: str = 'resume.tex') -> Optional[bytes]:
    """
    Generate a PDF resume from the given content dictionary.
    """
    logger.info("Starting PDF generation process")
    
    # Create the content of the .tex file manually
    tex_content = []

    # Add preamble
    with uow:
        preamble = uow.get_resume_preamble()
        if preamble:
            tex_content.extend(preamble.content.split('\n'))
        else:
            logger.error("Preamble not found in database")
            return None

    # Begin the document
    tex_content.append('\\begin{document}')

    # Add sections in the order specified
    section_order = ['personal_information', 'career_summary', 'skills', 'work_experience', 
                    'education', 'projects', 'awards', 'publications']
    for section in section_order:
        if section in content_dict:
            tex_content.append(f'\n% {section.replace("_", " ").title()}')
            tex_content.append(content_dict[section])
            logger.info(f"Added {section} to tex content")
        else:
            logger.warning(f"{section} not found in content_dict")

    # End the document
    tex_content.append('\\end{document}')

    # Join all lines
    full_tex_content = '\n'.join(tex_content)

    # Write to .tex file
    tex_path = os.path.join(output_dir, filename)
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(full_tex_content)

    logger.info(f"Generated .tex file at {tex_path}")

    # Compile the .tex file and handle the rest of the PDF generation process
    return _compile_pdf(tex_path, output_dir)

def generate_cover_letter_pdf(
    uow: MongoUnitOfWork,
    cover_letter_content: str,
    output_dir: str,
    user_id: str
) -> Tuple[Optional[bytes], str]:
    """Generate a PDF cover letter from the given content."""
    logger.info("Starting cover letter PDF generation process")
    
    with uow:
        # Get preamble
        preamble = uow.get_cover_letter_preamble()
        if preamble:
            tex_content = preamble.content
        else:
            logger.error("Cover letter preamble not found in database")
            return None, ""
            
        # Get user's portfolio for personal information
        portfolio = uow.portfolio.get_by_user_id(user_id)
        if not portfolio:
            logger.error("Portfolio not found for user")
            return None, ""

        personal_info = portfolio.personal_information
        
        # Replace placeholders in the preamble
        tex_content = tex_content.replace('{{NAME}}', personal_info.get('name', ''))
        tex_content = tex_content.replace('{{PHONE}}', personal_info.get('phone', ''))
        tex_content = tex_content.replace('{{EMAIL}}', personal_info.get('email', ''))
        tex_content = tex_content.replace('{{LINKEDIN}}', personal_info.get('linkedin', ''))
        tex_content = tex_content.replace('{{GITHUB}}', personal_info.get('github', ''))
        tex_content = tex_content.replace('{{ADDRESS}}', personal_info.get('address', ''))
        tex_content = tex_content.replace('{{COVER_LETTER_CONTENT}}', cover_letter_content)

    # Write to .tex file
    tex_path = os.path.join(output_dir, 'cover_letter.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(tex_content)

    # Compile the PDF
    pdf_content = _compile_pdf(tex_path, output_dir)
    
    return pdf_content, tex_content

def _compile_pdf(tex_path: str, output_dir: str) -> Optional[bytes]:
    """Helper function to compile LaTeX to PDF"""
    pdf_path = os.path.join(output_dir, os.path.splitext(os.path.basename(tex_path))[0] + '.pdf')
    try:
        process = subprocess.run(
            ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("LaTeX compilation output:")
        logger.info(process.stdout)
    except subprocess.CalledProcessError as e:
        logger.error("LaTeX compilation failed with error:")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Standard output: {e.stdout}")
        logger.error(f"Standard error: {e.stderr}")
        return None

    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found at expected path: {pdf_path}")
        return None

    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
            logger.info(f"Successfully read PDF content ({len(pdf_content)} bytes)")
            return pdf_content
    except Exception as e:
        logger.error(f"Failed to read PDF content: {str(e)}")
        return None

def sanitize_text(text: str) -> str:
    """Sanitize text by removing problematic characters"""
    return ''.join(char for char in unicodedata.normalize('NFKD', text)
                   if unicodedata.category(char)[0] != 'C')
