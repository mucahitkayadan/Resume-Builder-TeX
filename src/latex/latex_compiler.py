import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from config.logger_config import setup_logger
from config.settings import OUTPUT_FOLDER

logger = setup_logger(__name__)

class LatexCompiler(ABC):
    """Abstract base class for LaTeX compilation."""
    
    def __init__(self):
        self.output_dir = OUTPUT_FOLDER
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _generate_tex_content(self, *args, **kwargs) -> str:
        """Generate LaTeX content. Must be implemented by subclasses."""
        pass

    def compile_pdf(self, tex_path: Path, tex_content: str) -> Optional[bytes]:
        """
        Compile LaTeX content to PDF.
        
        Args:
            tex_path: Path where the .tex file should be saved
            tex_content: LaTeX content to compile
            
        Returns:
            Optional[bytes]: PDF content if successful, None otherwise
        """
        try:
            # Write content to file
            tex_path.write_text(tex_content)
            
            # Run pdflatex
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_path.name],
                cwd=tex_path.parent,
                capture_output=True,
                text=True
            )
            
            # Log the actual LaTeX error if compilation fails
            if result.returncode != 0:
                logger.error(f"LaTeX Error Output:\n{result.stderr}")
                logger.error(f"LaTeX Standard Output:\n{result.stdout}")
                return None
            
            # Read the generated PDF
            pdf_path = tex_path.with_suffix('.pdf')
            if pdf_path.exists():
                return pdf_path.read_bytes()
            else:
                logger.error("PDF file not found after compilation")
                return None
            
        except Exception as e:
            logger.error(f"Error during PDF compilation: {str(e)}")
            return None
        finally:
            self._cleanup_temp_files(tex_path)

    def _cleanup_temp_files(self, tex_path: Path) -> None:
        """Clean up temporary LaTeX files."""
        output_dir = tex_path.parent
        extensions = ['.aux', '.log', '.out']
        for ext in extensions:
            temp_file = output_dir / f"{tex_path.stem}{ext}"
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_file}: {e}")