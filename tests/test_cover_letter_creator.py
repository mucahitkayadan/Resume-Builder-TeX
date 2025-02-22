import logging
import os

from __legacy__.database_manager import DatabaseManager
from __legacy__.engine import (  # Import the actual AI strategy you're using
    AIRunner,
    CoverLetterCreator,
    OpenAIStrategy,
)
from __legacy__.json_loader import JsonLoader
from src.loaders.prompt_loader import PromptLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestCoverLetterCreator:
    # class TestCoverLetterCreator(unittest.TestCase):
    # def setUp(self):
    #     # Mock dependencies
    #     self.ai_runner = Mock(spec=AIRunner)
    #     self.json_loader = Mock(spec=JsonLoader)
    #     self.prompt_loader = Mock(spec=PromptLoader)
    #     self.db_manager = Mock(spec=DatabaseManager)
    #
    #     # Create CoverLetterCreator instance
    #     self.cover_letter_creator = CoverLetterCreator(
    #         self.ai_runner,
    #         self.json_loader,
    #         self.prompt_loader,
    #         self.db_manager
    #     )
    #
    # def test_generate_cover_letter_success(self):
    #     # Mock input data
    #     job_description = "Software Engineer position"
    #     resume_id = 1
    #     company_name = "Tech Corp"
    #     job_title = "Software Engineer"
    #
    #     # Mock dependencies behavior
    #     self.db_manager.get_resume.return_value = {"content": "Resume content"}
    #     self.prompt_loader.get_cover_letter_prompt.return_value = "Cover letter prompt"
    #     self.ai_runner.process_section.return_value = "Generated cover letter content"
    #
    #     # Mock PDF generation
    #     with patch('engine.cover_letter_creator.generate_cover_letter_pdf') as mock_generate_pdf:
    #         mock_generate_pdf.return_value = (b'PDF content', 'LaTeX content')
    #
    #         # Call the method
    #         result = self.cover_letter_creator.generate_cover_letter(
    #             job_description, resume_id, company_name, job_title
    #         )
    #
    #     # Assertions
    #     self.assertIn("Cover letter generated and saved successfully", result)
    #     self.db_manager.get_resume.assert_called_once_with(resume_id)
    #     self.prompt_loader.get_cover_letter_prompt.assert_called_once()
    #     self.ai_runner.process_section.assert_called_once()
    #     self.db_manager.update_cover_letter.assert_called_once()
    #
    # def test_generate_cover_letter_no_job_description(self):
    #     result = self.cover_letter_creator.generate_cover_letter("", 1, "Company", "Job")
    #     self.assertEqual(result, "Please enter a job description.")
    #
    # def test_generate_cover_letter_resume_not_found(self):
    #     self.db_manager.get_resume.return_value = None
    #     result = self.cover_letter_creator.generate_cover_letter("Job description", 1, "Company", "Job")
    #     self.assertIn("Resume with ID 1 not found", result)
    #
    # def test_generate_cover_letter_ai_processing_error(self):
    #     self.db_manager.get_resume.return_value = {"content": "Resume content"}
    #     self.ai_runner.process_section.side_effect = Exception("AI processing error")
    #     result = self.cover_letter_creator.generate_cover_letter("Job description", 1, "Company", "Job")
    #     self.assertIn("Failed to process cover letter", result)
    #
    # def test_generate_cover_letter_pdf_generation_error(self):
    #     self.db_manager.get_resume.return_value = {"content": "Resume content"}
    #     self.ai_runner.process_section.return_value = "Generated cover letter content"
    #
    #     with patch('engine.cover_letter_creator.generate_cover_letter_pdf') as mock_generate_pdf:
    #         mock_generate_pdf.side_effect = Exception("PDF generation error")
    #         result = self.cover_letter_creator.generate_cover_letter("Job description", 1, "Company", "Job")
    #
    #     self.assertIn("Cover letter content saved, but PDF generation failed", result)
    #
    # def test_ensure_string_method(self):
    #     # Test dictionary input
    #     dict_input = {"key": "value"}
    #     self.assertIsInstance(self.cover_letter_creator._ensure_string(dict_input), str)
    #
    #     # Test bytes input
    #     bytes_input = b"Test bytes"
    #     self.assertIsInstance(self.cover_letter_creator._ensure_string(bytes_input), str)
    #
    #     # Test non-string, non-dict input
    #     int_input = 123
    #     self.assertIsInstance(self.cover_letter_creator._ensure_string(int_input), str)
    #
    #     # Test string input
    #     str_input = "Test string"
    #     self.assertEqual(self.cover_letter_creator._ensure_string(str_input), str_input)

    def generate_cover_letter_with_values(
        self, job_description, company_name, job_title
    ):
        # Use actual instances
        db_manager = DatabaseManager("../__legacy__/db/resumes.db")
        json_loader = JsonLoader("../__legacy__/files/information.json")
        prompt_loader = PromptLoader("../prompts")
        ai_strategy = OpenAIStrategy(
            "gpt-3.5-turbo", 0.2, system_prompt=prompt_loader.get_system_prompt()
        )
        ai_runner = AIRunner(ai_strategy)

        cover_letter_creator = CoverLetterCreator(
            ai_runner, json_loader, prompt_loader, db_manager
        )

        # Get the last resume from the database
        last_resume = db_manager.get_latest_resume()
        if not last_resume:
            raise ValueError("No resumes found in the database")

        resume_id = last_resume["id"]
        logger.info(f"Using resume ID: {resume_id}")

        # Fetch the resume data for cover letter
        resume_data = db_manager.get_resume_for_cover_letter(resume_id)
        if not resume_data:
            raise ValueError(f"No resume data found for resume ID: {resume_id}")

        logger.info("Retrieved resume data for cover letter:")
        for key, value in resume_data.items():
            logger.info(
                f"{key}: {value[:50]}..." if value else f"{key}: None"
            )  # Log first 50 characters of each field

        # Generate the cover letter
        result = cover_letter_creator.generate_cover_letter(
            job_description, resume_id, company_name, job_title
        )

        # Check the database for the generated cover letter
        updated_resume = db_manager.get_resume_for_cover_letter(resume_id)
        if updated_resume and updated_resume.get("cover_letter"):
            logger.info("Cover letter LaTeX content found in database")
            latex_content = updated_resume["cover_letter"]
        else:
            logger.warning("Cover letter LaTeX content not found in database")
            latex_content = None

        output_dir = os.path.join("created_resumes", f"{company_name}_{job_title}")
        latex_path = os.path.join(output_dir, "cover_letter.tex")
        pdf_path = os.path.join(output_dir, "cover_letter.pdf")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # If we have LaTeX content, save it to a file
        if latex_content:
            with open(latex_path, "w", encoding="utf-8") as f:
                f.write(latex_content)
            logger.info(f"LaTeX file saved to: {latex_path}")

            # Here you would typically compile the LaTeX to PDF
            # For this test, we'll just check if the PDF exists after generation
            if os.path.exists(pdf_path):
                logger.info(f"PDF file exists at: {pdf_path}")
                logger.info(f"PDF file size: {os.path.getsize(pdf_path)} bytes")
            else:
                logger.warning("PDF file does not exist at the expected location")
        else:
            logger.warning("Could not save LaTeX: No LaTeX content available")

        return result, latex_path, pdf_path


if __name__ == "__main__":
    # unittest.main()
    test_instance = TestCoverLetterCreator()
    result, latex_path, pdf_path = test_instance.generate_cover_letter_with_values(
        job_description="We are seeking a Python developer with 5+ years of experience in AI and machine learning.",
        company_name="AI Solutions Inc.",
        job_title="Senior AI Engineer",
    )

    print(result)
    print(f"LaTeX generated at: {latex_path}")
    print(f"PDF should be at: {pdf_path}")
