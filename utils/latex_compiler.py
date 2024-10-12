import os
import subprocess
import logging
from typing import Dict, Optional, Any, Tuple
from loaders.json_loader import JsonLoader
import shutil

logger = logging.getLogger(__name__)

def generate_resume_pdf(db_manager: Any, content_dict: Dict[str, str], output_dir: str) -> Optional[bytes]:
    """
    Generate a PDF resume from the given content dictionary.

    Args:
        db_manager (Any): Database manager object to retrieve the preamble.
        content_dict (Dict[str, str]): Dictionary containing resume content sections.
        output_dir (str): Directory to output the generated files.

    Returns:
        Optional[bytes]: The content of the generated PDF file, or None if generation fails.

    Raises:
        subprocess.CalledProcessError: If LaTeX compilation fails.
        FileNotFoundError: If the generated PDF file is not found.
    """
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


def generate_cover_letter_pdf(db_manager: Any, cover_letter_content: str, resume_id: int, output_dir: str, company_name: str, job_title: str, json_loader: JsonLoader) -> Tuple[bytes, str]:
    """
    Generate a PDF cover letter based on the given content and information.

    Args:
        db_manager (Any): Database manager object to retrieve the cover letter template.
        cover_letter_content (str): The main content of the cover letter.
        resume_id (int): The ID of the associated resume.
        output_dir (str): Directory to output the generated files.
        company_name (str): Name of the company the cover letter is addressed to.
        job_title (str): Title of the job being applied for.
        json_loader (JsonLoader): JsonLoader object to retrieve personal information.

    Returns:
        Tuple[bytes, str]: The content of the generated PDF file and the LaTeX content.

    Raises:
        ValueError: If the cover letter template or personal information is not found.
        subprocess.CalledProcessError: If LaTeX compilation fails.
    """
    logger.info("Starting cover letter PDF generation")
    tex_file_path = os.path.join(output_dir, "cover_letter.tex")
    logger.info(f"TeX file path: {tex_file_path}")
    
    # Get the cover letter template (id 2)
    logger.info("Fetching cover letter template")
    template = db_manager.get_preamble(2)
    if template is None:
        logger.error("Cover letter template not found")
        raise ValueError("Cover letter template not found")
    logger.info("Cover letter template fetched successfully")
    
    # Get personal information from JsonLoader
    logger.info("Fetching personal information from JsonLoader")
    personal_info = json_loader.get_personal_information()
    if not personal_info:
        logger.error("Personal information not found in JsonLoader")
        raise ValueError("Personal information not found in JsonLoader")
    logger.info("Personal information fetched successfully")
    
    # Extract personal information
    name = personal_info.get('name', 'Candidate Name')
    phone = personal_info.get('phone', '')
    email = personal_info.get('email', '')
    linkedin = personal_info.get('LinkedIn', '')
    github = personal_info.get('GitHub', '')
    address = personal_info.get('address', '')
    
    # Replace placeholders in the template
    logger.info("Replacing placeholders in the template")
    replacements = {
        "{{COMPANY_NAME}}": company_name,
        "{{JOB_TITLE}}": job_title,
        "{{NAME}}": name,
        "{{PHONE}}": phone,
        "{{EMAIL}}": email,
        "{{LINKEDIN}}": linkedin,
        "{{GITHUB}}": github,
        "{{ADDRESS}}": address,
        "{{COVER_LETTER_CONTENT}}": cover_letter_content
    }
    
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    
    # Handle signature
    signature_path = "files/signature.jpg"
    if os.path.exists(signature_path):
        logger.info("Signature file found")
        # Copy signature file to output directory
        output_signature_path = os.path.join(output_dir, "signature.jpg")
        shutil.copy(signature_path, output_signature_path)
        signature_replacement = f"\n\n\\includegraphics[width=2cm]{{signature.jpg}}\n\n{name}\n"
        template = template.replace("{{SIGNATURE}}", signature_replacement)
    else:
        # Remove the signature placeholder if no signature is available
        template = template.replace("{{SIGNATURE}}", "")

    logger.debug(f"Full LaTeX content:\n{template}")
    
    # Write full LaTeX content to .tex file
    logger.info(f"Writing LaTeX content to file: {tex_file_path}")
    with open(tex_file_path, "w", encoding="utf-8") as f:
        f.write(template)
    logger.info("LaTeX content written to file successfully")
    
    # Compile LaTeX to PDF
    logger.info("Compiling LaTeX to PDF")
    try:
        # Run pdflatex twice to ensure proper compilation
        for i in range(2):
            logger.info(f"Running pdflatex (attempt {i+1})")
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', '-output-directory', output_dir, tex_file_path],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"pdflatex output: {result.stdout[:500]}...")  # Log first 500 characters
        logger.info("LaTeX compilation successful")
    except subprocess.CalledProcessError as e:
        logger.error(f"LaTeX compilation failed: {e}")
        logger.error(f"LaTeX stdout: {e.stdout}")
        logger.error(f"LaTeX stderr: {e.stderr}")
        raise

    # Read the generated PDF
    pdf_path = os.path.join(output_dir, "cover_letter.pdf")
    logger.info(f"Reading generated PDF: {pdf_path}")
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()
        logger.info("Successfully read PDF content")
    except Exception as e:
        logger.error(f"Failed to read PDF content: {str(e)}")
        raise

    logger.info("Cover letter PDF generation completed")
    return pdf_content, template