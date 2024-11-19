from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ModelConfig:
    name: str
    default_temperature: float
    max_tokens: Optional[int] = None
    default_options: Dict[str, Any] = field(default_factory=dict)

class LLMConfig:
    # Provider configurations
    PROVIDER_CONFIG = {
        "OpenAI": {"env_var": "OPENAI_API_KEY", "is_uri": False},
        "Claude": {"env_var": "ANTHROPIC_API_KEY", "is_uri": False},
        "Ollama": {"env_var": "OLLAMA_URI", "is_uri": True}
    }

    # Model configurations
    OPENAI_MODEL = ModelConfig(
        name="gpt-4o",
        default_temperature=0.1,
        max_tokens=4000
    )

    CLAUDE_MODEL = ModelConfig(
        name="claude-3-sonnet-latest",
        default_temperature=0.1,
        max_tokens=4000
    )

    OLLAMA_MODEL = ModelConfig(
        name="llama3.1",
        default_temperature=0.1,
        default_options={
            "num_predict": 2048,
            "top_k": 40,
            "top_p": 0.9,
            "repeat_penalty": 1.1
        }
    )

    # Default URIs and folder names
    OLLAMA_DEFAULT_URI = "http://localhost:11434"

    # Error messages
    MISSING_API_KEY_ERROR = "Missing API key for {} service. Please set the appropriate environment variable."
    MISSING_URI_ERROR = "Missing URI for {} service. Using default: {}"

    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key from environment variables."""
        config = cls.PROVIDER_CONFIG.get(provider)
        if not config:
            return None
        return os.getenv(config["env_var"])

    @classmethod
    def get_provider_config(cls, provider: str) -> Optional[str]:
        """Get provider configuration (API key or URI)."""
        config = cls.PROVIDER_CONFIG.get(provider)
        if not config:
            return None
            
        value = os.getenv(config["env_var"])
        if config["is_uri"]:
            return value or cls.OLLAMA_DEFAULT_URI
        return value

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