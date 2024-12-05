from dataclasses import dataclass
from src.llms.runner import LLMRunner
from src.loaders.prompt_loader import PromptLoader

@dataclass
class JobInfo:
    company_name: str
    job_title: str
    job_description: str

    @classmethod
    def extract_from_description(cls, 
                               job_description: str,
                               llm_runner: LLMRunner,
                               prompt_loader: PromptLoader) -> 'JobInfo':
        """Extract job information from description using LLM."""
        company_name, job_title = llm_runner.create_company_name_and_job_title(
            prompt_loader.get_folder_name_prompt(), 
            job_description
        )
        return cls(
            company_name=company_name,
            job_title=job_title,
            job_description=job_description
        ) 