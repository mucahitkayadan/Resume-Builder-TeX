import unittest
from engine.hardcode_sections import HardcodeSections
from loaders.json_loader import JsonLoader
from loaders.tex_loader import TexLoader
from utils.database_manager import DatabaseManager
import os

class TestHardcodeSections(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        json_path = os.path.join(project_root, 'files', 'information.json')
        db_path = os.path.join(project_root, 'resumes_backup.db')
        
        self.json_loader = JsonLoader(json_path)
        self.db_manager = DatabaseManager(db_path)
        self.tex_loader = TexLoader(self.db_manager)
        self.hardcoder = HardcodeSections(self.json_loader, self.tex_loader)

    def test_hardcode_personal_information(self):
        result = self.hardcoder.hardcode_personal_information()
        self.assertIn("\\personalinfo", result)
        self.assertIn("Muja Kayadan", result)
        self.assertIn("mujakayadan@outlook.com", result)

    def test_hardcode_career_summary(self):
        result = self.hardcoder.hardcode_career_summary()
        self.assertIn("\\section{Career Summary}", result)
        self.assertIn("\\careerSummary", result)
        self.assertIn("Software Engineer", result)

    def test_hardcode_skills(self):
        result = self.hardcoder.hardcode_skills()
        self.assertIn("\\section{Skills}", result)
        self.assertIn("\\resumeSkillHeading", result)
        self.assertIn("Languages", result)
        self.assertIn("Python", result)

    def test_hardcode_work_experience(self):
        result = self.hardcoder.hardcode_work_experience()
        self.assertIn("\\section{Work Experience}", result)
        self.assertIn("\\resumeSubheading", result)
        self.assertIn("Machine Learning Engineer", result)
        self.assertIn("Go Global World Inc.", result)

    def test_hardcode_education(self):
        result = self.hardcoder.hardcode_education()
        self.assertIn("\\section{Education}", result)
        self.assertIn("\\resumeEducationHeading", result)
        self.assertIn("Maharishi International University", result)

    def test_hardcode_projects(self):
        result = self.hardcoder.hardcode_projects()
        self.assertIn("\\section{Projects}", result)
        self.assertIn("\\resumeProjectHeading", result)
        self.assertIn("NFS Most Wanted Self-Driving Car", result)

    def test_hardcode_awards(self):
        result = self.hardcoder.hardcode_awards()
        self.assertIn("\\section{Awards \\& Achievements}", result)
        self.assertIn("\\resumeAwardHeading", result)
        self.assertIn("68th Iowa Reserve Chess Championship Winner", result)

    def test_hardcode_publications(self):
        result = self.hardcoder.hardcode_publications()
        self.assertIn("\\section{Publications}", result)
        self.assertIn("\\resumeProjectHeading", result)
        self.assertIn("High Accuracy Gender Determination Using the Egg Shape Index", result)

    def test_hardcode_section(self):
        sections = ["personal_information", "career_summary", "skills", "work_experience", 
                    "education", "projects", "awards", "publications"]
        for section in sections:
            with self.subTest(section=section):
                result = self.hardcoder.hardcode_section(section)
                self.assertIsNotNone(result)
                self.assertIsInstance(result, str)

        with self.assertRaises(ValueError):
            self.hardcoder.hardcode_section("non_existent_section")

if __name__ == '__main__':
    unittest.main()
