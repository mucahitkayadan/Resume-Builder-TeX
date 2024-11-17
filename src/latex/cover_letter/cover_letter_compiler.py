from typing import Optional, Tuple

from config.logger_config import setup_logger
from ..latex_compiler import LatexCompiler
from ..utils.latex_escaper import LatexEscaper
from src.core.database.factory import get_unit_of_work

logger = setup_logger(__name__)

class CoverLetterLatexCompiler(LatexCompiler):
    """Compiler for cover letter LaTeX documents."""

    def __init__(self):
        super().__init__()
        self.uow = get_unit_of_work()

    def generate_pdf(self, content: str, user_id: str, resume_id: str) -> Tuple[Optional[bytes], str]:
        """Generate PDF from cover letter content."""
        tex_content = self._generate_tex_content(content, user_id, resume_id)
        pdf_content = self.compile_pdf(
            self.output_dir / "cover_letter.tex", 
            tex_content
        )
        return pdf_content, tex_content

    def _generate_tex_content(self, content: str, user_id: str, resume_id: str) -> str:
        """Generate LaTeX content for cover letter."""
        with self.uow:
            preamble = self.uow.get_cover_letter_preamble()
            resume = self.uow.resumes.get_by_id(resume_id)
            portfolio = self.uow.portfolio.get_by_user_id(user_id)
            signature = self.uow.get_user_signature(user_id)

            if not all([preamble, resume, portfolio]):
                raise ValueError("Missing required data for cover letter generation")

            tex_content = preamble.content
            personal_info = portfolio.personal_information

            # Handle signature if exists
            if signature:
                signature_path = self.output_dir / "signature.jpg"
                signature_path.write_bytes(signature)
                tex_content = tex_content.replace(
                    '\\usepackage{graphicx}',
                    f'\\usepackage{{graphicx}}\n\\graphicspath{{{{{self.output_dir}/}}}}'
                )

            # Replace placeholders
            replacements = {
                'NAME': personal_info.get('name', ''),
                'PHONE': personal_info.get('phone', ''),
                'EMAIL': personal_info.get('email', ''),
                'LINKEDIN': personal_info.get('linkedin', ''),
                'GITHUB': personal_info.get('github', ''),
                'ADDRESS': personal_info.get('address', ''),
                'COMPANY_NAME': resume.company_name,
                'JOB_TITLE': resume.job_title,
                'COVER_LETTER_CONTENT': content
            }

            for key, value in replacements.items():
                tex_content = tex_content.replace(
                    f'{{{{{key}}}}}', 
                    LatexEscaper.escape_text(str(value))
                )

            return tex_content