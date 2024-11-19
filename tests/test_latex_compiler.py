import unittest
import os
from __legacy__.utils.latex_compiler import generate_resume_pdf
from __legacy__.database_manager import DatabaseManager

class TestLatexCompiler(unittest.TestCase):

    def setUp(self):
        self.db_manager = DatabaseManager()
        self.content_dict = {
            "personal_information": "John Doe",
            "career_summary": "Experienced software engineer",
            "skills": "Python, C++",
            "work_experience": "Software Engineer at XYZ",
            "education": "B.Sc in Computer Science",
            "projects": "AI Project",
            "awards": "Best Developer Award",
            "publications": "Research Paper"
        }
        self.output_dir = "test_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def test_generate_resume_pdf(self):
        pdf_content = generate_resume_pdf(self.db_manager, self.content_dict, self.output_dir)
        self.assertIsNotNone(pdf_content)
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, 'resume.pdf')))

if __name__ == '__main__':
    unittest.main()