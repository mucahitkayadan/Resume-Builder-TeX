import os
import subprocess
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LatexCompiler:
    """Base class for LaTeX compilation."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def compile_pdf(self, tex_path: str) -> Optional[bytes]:
        """Compile LaTeX to PDF."""
        pdf_path = self.output_dir / f"{Path(tex_path).stem}.pdf"
        
        try:
            process = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 
                 '-output-directory', str(self.output_dir), tex_path],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info("LaTeX compilation output: %s", process.stdout)
            
            if not pdf_path.exists():
                logger.error("PDF file not found at: %s", pdf_path)
                return None
                
            return pdf_path.read_bytes()
            
        except subprocess.CalledProcessError as e:
            logger.error("LaTeX compilation failed: %s", e.stderr)
            return None
        except Exception as e:
            logger.error("Failed to read PDF: %s", str(e))
            return None 