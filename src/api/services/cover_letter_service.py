from datetime import datetime
from typing import List, Optional

from src.core.database.factory import get_unit_of_work
from src.generator.cover_letter_generator import CoverLetterGenerator
from src.generator.utils.job_info import JobInfo
from src.generator.utils.output_manager import OutputManager
from src.llms.runner import LLMRunner
from src.loaders.prompt_loader import PromptLoader


class CoverLetterService:
    def __init__(self):
        self.uow = get_unit_of_work()

    async def generate_cover_letter(
        self,
        user_id: str,
        job_description: str,
        resume_id: Optional[str] = None,
        options: Optional[dict] = None,
    ):
        try:
            # Initialize LLM runner with user preferences
            with self.uow:
                user = self.uow.users.get_by_user_id(user_id)
                llm_preferences = user.llm_preferences

            # Update preferences with options if provided
            if options:
                llm_preferences.update(options)

            llm_runner = LLMRunner.from_preferences(llm_preferences)

            # Initialize cover letter generator
            cover_letter_generator = CoverLetterGenerator(llm_runner, user_id)

            # Extract job info using LLM
            prompt_loader = PromptLoader(user_id)
            job_info = JobInfo.extract_from_description(
                job_description=job_description, llm_runner=llm_runner
            )

            # Create output manager
            output_manager = OutputManager(job_info)

            # Generate cover letter
            cover_letter = await cover_letter_generator.generate_cover_letter(
                job_description=job_description,
                resume_id=resume_id,
                output_manager=output_manager,
            )

            return cover_letter

        except Exception as e:
            raise Exception(f"Failed to generate cover letter: {str(e)}")

    async def get_cover_letter(self, user_id: str, cover_letter_id: str):
        with self.uow:
            cover_letter = self.uow.cover_letters.get_by_id(cover_letter_id)
            if cover_letter and cover_letter.user_id == user_id:
                return cover_letter
            return None

    async def list_cover_letters(self, user_id: str) -> List:
        with self.uow:
            return self.uow.cover_letters.get_all_by_user(user_id)
