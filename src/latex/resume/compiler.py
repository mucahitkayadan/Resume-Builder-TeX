from typing import Dict, Optional
from pathlib import Path
from src.core.database.unit_of_work import MongoUnitOfWork
from ..compiler import LatexCompiler

class ResumeLatexCompiler(LatexCompiler):
    def __init__(self, uow: MongoUnitOfWork, output_dir: str):
        super().__init__(output_dir)
        self.uow = uow
    
    def generate_pdf(self, content_dict: Dict[str, str], 
                    filename: str = 'resume.tex') -> Optional[bytes]:
        tex_path = self.output_dir / filename
        
        with self.uow:
            preamble = self.uow.get_resume_preamble()
            if not preamble:
                return None
                
            tex_content = self._generate_tex_content(preamble.content, content_dict)
            tex_path.write_text(tex_content)
            
            return self.compile_pdf(str(tex_path)) 