from dataclasses import dataclass
from typing import List, Dict, Any
from src.latex.utils.latex_escaper import LatexEscaper

@dataclass
class BaseDTO:
    @staticmethod
    def escape_text(text: str, escaper: LatexEscaper) -> str:
        return escaper.escape_text(str(text))
