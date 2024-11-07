from typing import Dict, Any, Optional
from datetime import datetime

class ResumeManager:
    """Handles all resume-related database operations"""
    def __init__(self, connection):
        self.conn = connection
        
    def insert_resume(
        self,
        company_name: str,
        job_title: str,
        job_description: str,
        content_dict: Dict[str, str],
        pdf_content: bytes,
        model_type: str,
        model_name: str,
        temperature: float
    ) -> int:
        """Insert a new resume into the database"""
        cursor = self.conn.cursor()
        created_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO resumes (
                company_name, job_title, job_description, content_dict,
                pdf_content, model_type, model_name, temperature, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (company_name, job_title, job_description, str(content_dict),
              pdf_content, model_type, model_name, temperature, created_at))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_resume(self, resume_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a resume by its ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM resumes WHERE id = ?', (resume_id,))
        result = cursor.fetchone()
        
        if result is None:
            return None
            
        return {
            'id': result[0],
            'company_name': result[1],
            'job_title': result[2],
            'job_description': result[3],
            'content_dict': eval(result[4]),
            'pdf_content': result[5],
            'model_type': result[6],
            'model_name': result[7],
            'temperature': result[8],
            'created_at': result[9]
        }