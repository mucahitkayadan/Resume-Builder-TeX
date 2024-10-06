import os
import subprocess
import logging
from pylatex import Document, Package, Command, NewPage
from pylatex.utils import NoEscape

logger = logging.getLogger(__name__)

def generate_resume_pdf(db_manager, content_dict, output_dir):
    logger.info("Starting PDF generation process")
    
    # Create the content of the .tex file manually
    tex_content = []

    # Add preamble
    preamble = db_manager.get_preamble()
    if preamble:
        tex_content.extend(preamble.split('\n'))
    else:
        logger.error("Preamble not found in database")
        return None

    # Begin the document
    tex_content.append('\\begin{document}')

    # Add sections in the order specified
    section_order = ['personal_information', 'career_summary', 'skills', 'work_experience', 'education', 'projects', 'awards', 'publications']
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
    tex_path = os.path.join(output_dir, 'resume.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(full_tex_content)

    logger.info(f"Generated .tex file at {tex_path}")
    
    # Log the content of the .tex file
    logger.info(f"Generated .tex file content:\n{full_tex_content}")

    # Compile the .tex file
    pdf_path = os.path.join(output_dir, 'resume.pdf')
    try:
        for _ in range(2):  # Run twice to resolve references
            process = subprocess.Popen(['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_path], 
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate(timeout=30)
            if process.returncode != 0:
                logger.error(f"pdflatex returned non-zero exit status. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
                raise subprocess.CalledProcessError(process.returncode, process.args)
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error("pdflatex process timed out after 30 seconds")
        raise
    except Exception as e:
        logger.error(f"Error compiling LaTeX: {str(e)}")
        raise

    logger.info("pdflatex compilation completed")

    # Check if PDF was generated
    if not os.path.exists(pdf_path):
        logger.error(f"PDF file not found at expected path: {pdf_path}")
        raise FileNotFoundError(f"PDF file not generated at {pdf_path}")

    # Read the generated PDF
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        logger.info("Successfully read PDF content")
    except Exception as e:
        logger.error(f"Failed to read PDF content: {str(e)}")
        raise

    logger.info("PDF generation process completed")
    return pdf_content