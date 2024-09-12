from src.process_section import OpenAIRunner
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from loaders.job_description_loader import JobDescriptionLoader

job_description_loader = JobDescriptionLoader("../files/job_description.txt")
job_description = job_description_loader.get_job_description()
prompt_loader = PromptLoader("../prompts")
json_loader = JsonLoader("../files/information.json")


class TestProcessSection:
    def __init__(self):
        self.processor = OpenAIRunner()

    def test_process_skills(self):
        skills = json_loader.get_skills()
        prompt = prompt_loader.get_skills_prompt()
        
        # Call the method
        result = self.processor.process_skills(prompt, skills, job_description)
        print("Skills from the Json file: \n")
        print(skills)
        # Print the result to the console
        print("Skills Prompt: \n")
        print(prompt)
        print("Result of process_skills:")
        print(result)

test_process_section = TestProcessSection()
test_process_section.test_process_skills()