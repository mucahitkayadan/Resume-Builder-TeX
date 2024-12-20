from typing import Optional, Dict, List
from src.core.database.factory import get_unit_of_work
from src.generator.resume_generator import ResumeGenerator
from src.generator.utils.output_manager import OutputManager
from src.generator.utils.job_info import JobInfo
from src.llms.runner import LLMRunner
from src.loaders.prompt_loader import PromptLoader

class ResumeService:
    def __init__(self):
        self.uow = get_unit_of_work()
        
    async def generate_resume(
        self,
        user_id: str,
        job_description: str,
        options: Optional[Dict] = None
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
            
            # Initialize resume generator
            resume_generator = ResumeGenerator(llm_runner, user_id)
            
            # Extract job info using LLM
            prompt_loader = PromptLoader(user_id)
            job_info = JobInfo.extract_from_description(
                job_description=job_description,
                llm_runner=llm_runner
            )
            
            # Create output manager
            output_manager = OutputManager(job_info)
            
            # Generate resume
            resume = await resume_generator.generate_resume(
                job_description=job_description,
                selected_sections=options.get('selected_sections', {}),
                output_manager=output_manager
            )
            
            return resume
            
        except Exception as e:
            raise Exception(f"Failed to generate resume: {str(e)}")
    
    async def get_resume(self, user_id: str, resume_id: str):
        with self.uow:
            resume = self.uow.resumes.get_by_id(resume_id)
            if resume and resume.user_id == user_id:
                return resume
            return None
    
    async def list_resumes(self, user_id: str) -> List:
        with self.uow:
            return self.uow.resumes.get_all_by_user(user_id) 