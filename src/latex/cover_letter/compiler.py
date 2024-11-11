from typing import Optional, Tuple
from pathlib import Path
from src.core.database.unit_of_work import MongoUnitOfWork
from ..compiler import LatexCompiler

class CoverLetterLatexCompiler(LatexCompiler):
    def __init__(self, uow: MongoUnitOfWork, output_dir: str):
        super().__init__(output_dir)
        self.uow = uow
    
    def generate_pdf(self, content: str, user_id: str, 
                    resume_id: str) -> Tuple[Optional[bytes], str]:
        tex_path = self.output_dir / 'cover_letter.tex'
        
        with self.uow:
            tex_content = self._generate_tex_content(content, user_id, resume_id)
            tex_path.write_text(tex_content)
            
            pdf_content = self.compile_pdf(str(tex_path))
            return pdf_content, tex_content 