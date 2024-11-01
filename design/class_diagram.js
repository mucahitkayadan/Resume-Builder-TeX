classDiagram
    class ResumeCreator {
        -runner: Any
        -json_loader: JsonLoader
        -prompt_loader: PromptLoader
        -db_manager: DatabaseManager
        -logger: Logger
        -tex_loader: TexLoader
        -hardcoder: HardcodeSections
        +generate_resume(job_description: str, company_name: str, job_title: str, model_type: str, model_name: str, temperature: float, selected_sections: Dict[str, str]) : Generator[Tuple[str, float], None, None]
        -create_output_directory(company_name: str, job_title: str) : str
        -hardcode_section(section: str) : str
        -hardcode_awards() : str
        -hardcode_publications() : str
    }

    class CoverLetterCreator {
        -runner: Any
        -json_loader: JsonLoader
        -prompt_loader: PromptLoader
        -logger: Logger
        -db_manager: DatabaseManager
        +generate_cover_letter(job_description: str, resume_id: int, company_name: str, job_title: str) : str
    }

    class BaseRunner {
        <<abstract>>
        #model: Any
        +process_section(prompt: str, data: str, job_description: str) : str
        +process_personal_information(prompt: str, personal_info: Dict[str, Any], job_description: str) : str
        +process_career_summary(prompt: str, career_summary: Dict[str, Any], job_description: str) : str
        +process_skills(prompt: str, skills: Dict[str, List[str]], job_description: str) : str
        +process_work_experience(prompt: str, work_experience: List[Dict[str, Any]], job_description: str) : str
        +process_education(prompt: str, education: List[Dict[str, Any]], job_description: str) : str
        +process_projects(prompt: str, projects: List[Dict[str, Any]], job_description: str) : str
        +create_folder_name(prompt: str, job_description: str) : str
    }

    class OpenAIRunner {
        +process_section(prompt: str, data: str, job_description: str) : str
    }

    class ClaudeRunner {
        +process_section(prompt: str, data: str, job_description: str) : str
    }

    class HardcodeSections {
        -json_loader: JsonLoader
        -tex_loader: TexLoader
        +hardcode_section(section: str) : str
        -hardcode_personal_information() : str
        -hardcode_career_summary() : str
        -hardcode_skills() : str
        -hardcode_work_experience() : str
        -hardcode_education() : str
        -hardcode_projects() : str
        -hardcode_awards() : str
        -hardcode_publications() : str
    }

    class DatabaseManager {
        -conn: Connection
        +get_preamble(template_id: int) : str
        +insert_resume(company_name: str, job_title: str, job_description: str, content_dict: Dict[str, str], pdf_content: bytes, model_type: str, model_name: str, temperature: float) : int
        +get_resume(resume_id: int) : Dict[str, Any]
        +update_cover_letter(resume_id: int, cover_letter_content: str, pdf_content: bytes) : None
    }

    class JsonLoader {
        -data: Dict[str, Any]
        +get_personal_information() : Dict[str, Any]
        +get_career_summary() : Dict[str, Any]
        +get_skills() : Dict[str, List[str]]
        +get_work_experience() : List[Dict[str, Any]]
        +get_education() : List[Dict[str, Any]]
        +get_projects() : List[Dict[str, Any]]
        +get_awards() : List[Dict[str, Any]]
        +get_publications() : List[Dict[str, Any]]
    }

    class PromptLoader {
        -prompts: Dict[str, str]
        +get_personal_information_prompt() : str
        +get_career_summary_prompt() : str
        +get_skills_prompt() : str
        +get_work_experience_prompt() : str
        +get_education_prompt() : str
        +get_projects_prompt() : str
        +get_awards_prompt() : str
        +get_publications_prompt() : str
        +get_cover_letter_prompt() : str
    }

    class TexLoader {
        -db_manager: DatabaseManager
        +safe_format_template(template_name: str, **kwargs) : str
    }

    ResumeCreator --> BaseRunner
    ResumeCreator --> JsonLoader
    ResumeCreator --> PromptLoader
    ResumeCreator --> DatabaseManager
    ResumeCreator --> TexLoader
    ResumeCreator --> HardcodeSections
    CoverLetterCreator --> BaseRunner
    CoverLetterCreator --> JsonLoader
    CoverLetterCreator --> PromptLoader
    CoverLetterCreator --> DatabaseManager
    BaseRunner <|-- OpenAIRunner
    BaseRunner <|-- ClaudeRunner
    HardcodeSections --> JsonLoader
    HardcodeSections --> TexLoader
    TexLoader --> DatabaseManager

