from typing import Dict, Optional
from pathlib import Path
from src.core.database.unit_of_work import MongoUnitOfWork
from ..base_compiler import LatexCompiler
from ..utils import LatexEscaper, LatexPlaceholder

class ResumeLatexCompiler(LatexCompiler):
    def __init__(self, uow: MongoUnitOfWork, output_dir: Path):
        super().__init__(output_dir)
        self.uow = uow
        self.escaper = LatexEscaper()
        self.placeholder = LatexPlaceholder()
    
    def generate_pdf(self, content_dict: Dict[str, str], 
                    filename: str = 'resume.tex') -> Optional[bytes]:
        tex_path = self.output_dir / filename
        
        with self.uow:
            preamble = self.uow.get_resume_preamble()
            if not preamble:
                return None
                
            tex_content = self._generate_tex_content(preamble.content, content_dict)
            return self.compile_pdf(tex_path, tex_content)
    
    def _generate_tex_content(self, preamble: str, content_dict: Dict[str, str]) -> str:
        """Generate LaTeX content for resume."""
        escaped_content = {
            k: self.escaper.escape_text(v)
            for k, v in content_dict.items()
        }
        
        tex_content = [preamble, '\\begin{document}']
        
        section_order = [
            'personal_information', 'career_summary', 'skills', 
            'work_experience', 'education', 'projects', 
            'awards', 'publications'
        ]
        
        for section in section_order:
            if section in escaped_content:
                tex_content.append(f'\n% {section.replace("_", " ").title()}')
                tex_content.append(escaped_content[section])
        
        tex_content.append('\\end{document}')
        return '\n'.join(tex_content) 