from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class LatexConfig:
    """Configuration for LaTeX compilation."""
    output_dir: Path
    compiler_path: str = 'pdflatex'
    temp_extensions: List[str] = ('.aux', '.log', '.out')
    compiler_options: List[str] = ('-interaction=nonstopmode',)
    cleanup_temp_files: bool = True