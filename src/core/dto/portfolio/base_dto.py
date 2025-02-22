from dataclasses import dataclass
from typing import Any, Dict, List

from src.latex.utils.latex_escaper import LatexEscaper


@dataclass
class BaseDTO:
    @staticmethod
    def escape_text(text: str) -> str:
        """Use LatexEscaper to properly escape text for LaTeX."""
        return LatexEscaper.escape_text(str(text))
