import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from config.logger_config import setup_logger

logger = setup_logger(__name__)

class LatexCompiler(ABC):
    """Abstract base class for LaTeX compilation."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def _generate_tex_content(self, *args, **kwargs) -> str:
        """Generate LaTeX content. Must be implemented by subclasses."""
        pass

    def compile_pdf(self, tex_path: Path, content: Optional[str] = None) -> Optional[bytes]:
        """
        Compile LaTeX content to PDF.
        
        Args:
            tex_path: Path to the tex file
            content: Optional content to write to tex file before compilation
        """
        try:
            if content:
                tex_path.write_text(content)
                
            process = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 
                 '-output-directory', str(self.output_dir), str(tex_path)],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info("LaTeX compilation output: %s", process.stdout)
            
            pdf_path = self.output_dir / tex_path.with_suffix('.pdf').name
            if not pdf_path.exists():
                logger.error("PDF file not found at: %s", pdf_path)
                return None
                
            return pdf_path.read_bytes()
            
        except subprocess.CalledProcessError as e:
            logger.error("LaTeX compilation failed: %s", e.stderr)
            return None
        except Exception as e:
            logger.error("Failed to compile PDF: %s", str(e))
            return None
        finally:
            self._cleanup_temp_files(tex_path)

    def _cleanup_temp_files(self, tex_path: Path) -> None:
        """Clean up temporary LaTeX files."""
        extensions = ['.aux', '.log', '.out']
        for ext in extensions:
            temp_file = self.output_dir / tex_path.with_suffix(ext).name
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_file}: {e}")