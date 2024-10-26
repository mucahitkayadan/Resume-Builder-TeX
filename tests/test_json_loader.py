import unittest
from loaders.json_loader import JsonLoader

class TestJsonLoader(unittest.TestCase):

    def setUp(self):
        self.json_loader = JsonLoader("../files/information.json")

    def test_get_personal_information(self):
        personal_info = self.json_loader.get_personal_information()
        self.assertIsInstance(personal_info, dict)
        self.assertIn("name", personal_info)

    def test_get_career_summary(self):
        career_summary = self.json_loader.get_career_summary()
        self.assertIsInstance(career_summary, dict)
        self.assertIn("job_titles", career_summary)

if __name__ == '__main__':
    unittest.main()