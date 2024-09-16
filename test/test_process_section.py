from engine.runners import Runner
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from loaders.tex_loader import TexLoader
from loaders.job_description_loader import JobDescriptionLoader

job_description_loader = JobDescriptionLoader("../files/job_description.txt")
job_description = job_description_loader.get_job_description()
prompt_loader = PromptLoader("../prompts")
json_loader = JsonLoader("../files/information.json")
system_prompt = prompt_loader.get_system_prompt()
tex_loader = TexLoader("../created_resumes/ibm_firmware_engineer")

class TestProcessSection:
    def __init__(self):
        self.runner = Runner(runner_type="openai", model="gpt-4o", system_prompt=system_prompt)

    def test_skills(self, data, prompt, job_description):
        result = self.runner.process_skills(prompt, data, job_description)
        print(f"Result of process_skills: {result}")

    def test_education(self, data, prompt, job_description):
        result = self.runner.process_education(prompt, data, job_description)
        print(f"Result of process_education: {result}")

    def test_folder_name(self, prompt, job_description):
        result = self.runner.create_folder_name(prompt, job_description)
        print(f"Result of create_folder_name: {result}")

    def test_career_summary(self, prompt, data, job_description, tex_loader):
        # Use the collect_resume_content method from BaseRunner
        result = self.runner.process_career_summary(prompt, data, job_description, tex_loader)
        print(f"Prompt: {prompt}\n\nData: {data}\n\nJob Description: {job_description}\n\n")
        print(f"Result of process_career_summary: {result}")

    def test_work_experience(self, data, prompt, job_description):
        result = self.runner.process_work_experience(prompt, data, job_description)
        print(f"Result of process_work_experience: {result}")


test_process_section = TestProcessSection()
test_process_section.test_career_summary(prompt=prompt_loader.get_career_summary_prompt(),
                                         data=JsonLoader("../files/information.json").get_career_summary(),
                                         job_description=JobDescriptionLoader("../created_resumes/ibm_firmware_engineer/job_description.txt").get_job_description(),
                                         tex_loader=TexLoader("../created_resumes/ibm_firmware_engineer")
                                         )