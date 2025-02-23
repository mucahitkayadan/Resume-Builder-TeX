import os
from pathlib import Path
from typing import Optional, Tuple

from config.logger_config import setup_logger
from src.core.database.factory import get_unit_of_work
from src.generator.utils.output_manager import OutputManager

from ..latex_compiler import LatexCompiler
from ..utils.latex_escaper import LatexEscaper

logger = setup_logger(__name__)


class CoverLetterLatexCompiler(LatexCompiler):
    """Compiler for cover letter LaTeX documents."""

    def __init__(self):
        super().__init__()
        self.uow = get_unit_of_work()

    def generate_pdf(
        self, content: str, output_manager: OutputManager, user_id: str, resume_id: str
    ) -> Tuple[Optional[bytes], str]:
        """Generate PDF from cover letter content."""
        logger.info("Starting cover letter PDF generation")
        signature_path = None
        try:
            logger.debug("Generating LaTeX content")
            tex_content, signature_path = self._generate_tex_content(
                content, user_id, resume_id, output_manager
            )

            logger.debug("Getting cover letter path")
            tex_path = output_manager.get_cover_letter_path()

            logger.debug(f"Compiling PDF at path: {tex_path}")
            pdf_content = self.compile_pdf(tex_path, tex_content, output_manager)

            if pdf_content:
                logger.info("PDF generation successful")
            else:
                logger.error("PDF generation failed - no content returned")

            return pdf_content, tex_content
        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}", exc_info=True)
            raise
        finally:
            # Clean up signature file if it exists
            if signature_path and signature_path.exists():
                try:
                    os.remove(signature_path)
                    logger.debug(f"Cleaned up signature file: {signature_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up signature file: {e}")

    def _generate_tex_content(
        self, content: str, user_id: str, resume_id: str, output_manager: OutputManager
    ) -> Tuple[str, Optional[Path]]:
        """Generate LaTeX content for cover letter."""
        signature_path = None
        try:
            with self.uow:
                preamble = self.uow.get_cover_letter_preamble()
                profile = self.uow.profiles.get_by_user_id(user_id)
                signature = self.uow.get_user_signature(user_id)
                job_info = output_manager.get_job_info()

                if not all([preamble, profile]):
                    raise ValueError(
                        "Missing required data for cover letter generation"
                    )

                tex_content = preamble
                personal_info = profile.personal_information

                # Handle signature if exists
                if signature and hasattr(signature, "image"):
                    signature_path = output_manager.output_dir / "signature.jpg"
                    signature_bytes = signature.image
                    if hasattr(signature_bytes, "binary"):
                        signature_bytes = signature_bytes.binary
                    signature_path.write_bytes(signature_bytes)

                # Format the cover letter content with proper paragraph style
                formatted_content = content.replace(
                    "\n", "\n\n"
                )  # Ensure proper paragraph breaks

                # Replace placeholders with escaped values
                replacements = {
                    "NAME": personal_info.get("full_name", ""),
                    "PHONE": personal_info.get("phone", ""),
                    "EMAIL": personal_info.get("email", ""),
                    "LINKEDIN": personal_info.get("linkedin", ""),
                    "GITHUB": personal_info.get("github", ""),
                    "WEBSITE": personal_info.get("website", ""),
                    "ADDRESS": personal_info.get("address", ""),
                    "COMPANY_NAME": job_info.company_name,
                    "JOB_TITLE": job_info.job_title,
                    "COVER_LETTER_CONTENT": formatted_content,
                }

                # Replace all placeholders in one go
                for key, value in replacements.items():
                    tex_content = tex_content.replace(
                        f"{{{{{key}}}}}", LatexEscaper.escape_text(str(value))
                    )

                return tex_content, signature_path

        except Exception as e:
            # Clean up signature file if something goes wrong
            if signature_path and signature_path.exists():
                try:
                    os.remove(signature_path)
                except Exception:
                    pass  # If cleanup fails during error, just continue with the original error
            logger.error(f"Failed to generate TeX content: {str(e)}", exc_info=True)
            raise
