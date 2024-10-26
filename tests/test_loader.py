import json
from loaders.tex_loader import TexLoader
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader

class LoaderTester:
    def __init__(self):
        self.tex_loader = TexLoader("../tex_template")
        self.json_loader = JsonLoader("../files/information.json")
        self.prompt_loader = PromptLoader("../prompts")

    def test_personal_information(self):
        print(self.json_loader.get_personal_information())
    def test_skills(self):
        print(self.json_loader.get_skills())
    def test_work_experience(self):
        print(self.json_loader.get_work_experience())
    def test_tex_loader(self):
        print("\n--- Testing TexLoader ---")
        methods = [
            "get_main", "get_personal_information", "get_career_summary",
            "get_skills", "get_work_experience", "get_education",
            "get_projects", "get_awards", "get_publications"
        ]
        for method in methods:
            content = getattr(self.tex_loader, method)()
            print(f"\n{method}:")
            print(content[:200] + "..." if len(content) > 200 else content)

    def test_json_loader(self):
        print("\n--- Testing JsonLoader ---")
        methods = [
            "get_personal_information", "get_job_titles", "get_career_summary",
            "get_skills", "get_work_experience", "get_education",
            "get_projects", "get_awards", "get_publications"
        ]
        for method in methods:
            content = getattr(self.json_loader, method)()
            print(f"\n{method}:")
            print(json.dumps(content, indent=2))

    def test_prompt_loader(self):
        print("\n--- Testing PromptLoader ---")
        methods = [
            "get_personal_information_prompt", "get_job_titles_prompt",
            "get_career_summary_prompt", "get_skills_prompt",
            "get_work_experience_prompt", "get_education_prompt",
            "get_projects_prompt", "get_awards_prompt",
            "get_publications_prompt"
        ]
        for method in methods:
            content = getattr(self.prompt_loader, method)()
            print(f"\n{method}:")
            print(content[:200] + "..." if len(content) > 200 else content)

    def run_all_tests(self):
        self.test_tex_loader()
        self.test_json_loader()
        self.test_prompt_loader()

if __name__ == "__main__":
    tester = LoaderTester()
    # tester.test_json_loader()
    # tester.test_personal_information()
    # tester.test_work_experience()
    tester.test_skills()
