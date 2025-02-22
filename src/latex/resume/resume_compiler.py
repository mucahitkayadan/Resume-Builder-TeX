from typing import Dict, Optional
from ..latex_compiler import LatexCompiler
from ..utils import LatexEscaper, LatexPlaceholder
import logging
from src.core.database.factory import get_unit_of_work
from src.latex.latex_compiler import OutputManager

logger = logging.getLogger(__name__)

class ResumeLatexCompiler(LatexCompiler):
    def __init__(self):
        super().__init__()
        self.uow = get_unit_of_work()
        self.escaper = LatexEscaper()
        self.placeholder = LatexPlaceholder()

    def generate_pdf(self, content_dict: Dict[str, str], output_manager: OutputManager) -> Optional[bytes]:
        """Generate PDF from resume content."""
        try:
            tex_path = output_manager.get_resume_path()
            
            with self.uow:
                preamble = self.uow.get_resume_preamble()
                if not preamble:
                    logger.error("Preamble not found in database")
                    return None

                tex_content = self._generate_tex_content(preamble, content_dict)
                return self.compile_pdf(tex_path, tex_content, output_manager)
                
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            return None
    
    def _generate_tex_content(self, preamble: str, content_dict: Dict[str, str]) -> str:
        """Generate LaTeX content for resume."""
        tex_content = [preamble, '\\begin{document}']
        
        section_order = [
            'personal_information', 'career_summary', 'skills', 
            'work_experience', 'education', 'projects', 
            'awards', 'publications'
        ]
        
        for section in section_order:
            if section in content_dict:
                tex_content.append(f'\n% {section.replace("_", " ").title()}')
                tex_content.append(content_dict[section])
        
        tex_content.append('\\end{document}')
        return '\n'.join(tex_content) 