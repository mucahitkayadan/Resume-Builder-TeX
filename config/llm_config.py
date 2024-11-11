from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ModelConfig:
    name: str
    default_temperature: float
    max_tokens: int
    default_options: Dict[str, Any]

class LLMConfig:
    # Default model configurations
    OPENAI_MODEL = ModelConfig(
        name="gpt4o-mini",
        default_temperature=0.1,
        max_tokens=1000,
        default_options={
            "presence_penalty": 0,
            "frequency_penalty": 0.3,
        }
    )

    CLAUDE_MODEL = ModelConfig(
        name="claude-3-5-sonnet-latest",
        default_temperature=0.1,
        max_tokens=1000,
        default_options={}
    )

    OLLAMA_MODEL = ModelConfig(
        name="llama3.1",
        default_temperature=0.1,
        max_tokens=1000,
        default_options={
            "stream": False
        }
    )

    # API endpoints
    OLLAMA_DEFAULT_URI = "http://localhost:11434"

    # Error messages
    MISSING_API_KEY_ERROR = "{} API key not found in environment variables"
    EMPTY_RESPONSE_ERROR = "Received empty content from {} API"
    UNKNOWN_FOLDER_NAME = "Unknown_Company|Unknown_Position"
    ERROR_FOLDER_NAME = "Error_Company|Error_Position"

    # Prompt templates
    SECTION_PROMPT_TEMPLATE = """
    {prompt}

    Here is the personal information in JSON format:
    <data>
    {data}
    </data>

    Job Description:
    <job_description>
    {job_description}
    </job_description>
    """.strip()

    FOLDER_NAME_PROMPT_TEMPLATE = """
    {prompt}

    Job Description:
    <job_description>
    {job_description}
    </job_description>
    """.strip()