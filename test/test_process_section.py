from engine.process_section import OpenAIRunner
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from loaders.job_description_loader import JobDescriptionLoader

job_description_loader = JobDescriptionLoader("../files/job_description.txt")
job_description = job_description_loader.get_job_description()
prompt_loader = PromptLoader("../prompts")
json_loader = JsonLoader("../files/information.json")
system_prompt = prompt_loader.get_system_prompt()


class TestProcessSection:
    def __init__(self):
        self.processor = OpenAIRunner(system_prompt=system_prompt)

    def test_skills(self):
        data = json_loader.get_skills()
        prompt = prompt_loader.get_skills_prompt()

        result = self.processor.process_skills(prompt, data, job_description)
        print(f"Prompt: {prompt}\n\nData: {data}\n\nJob Description: {job_description}\n\n")

        print("Result of process_skills:")
        print(result)

    def test_education(self):
        data = json_loader.get_education()
        prompt = prompt_loader.get_education_prompt()

        result = self.processor.process_education(prompt, data, job_description)
        print(f"Prompt: {prompt}\n\nData: {data}\n\nJob Description: {job_description}\n\n")
        print("Result of process_skills:")
        print(result)
    
    def test_folder_name(self):
        prompt = prompt_loader.get_folder_name_prompt()

        result = self.processor.create_folder_name(prompt, job_description)
        print(f"Prompt: {prompt}\n\nJob Description: {job_description}\n\n")
        print("Result of create_folder_name:")
        print(result)

test_process_section = TestProcessSection()
test_process_section.test_folder_name()