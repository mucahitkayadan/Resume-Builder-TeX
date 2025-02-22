import sys
from pathlib import Path

from config.llm_config import LLMConfig
from src.llms.strategies.claude_strategy import ClaudeStrategy
from src.llms.strategies.gemini_strategy import GeminiStrategy
from src.llms.strategies.ollama_strategy import OllamaStrategy
from src.llms.strategies.openai_strategy import OpenAIStrategy
from src.llms.utils.errors import APIError, ConfigurationError

# Add the project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)


# flake8: noqa: C901
def llm_strategy_tester(
    strategy_name: str,
    strategy_class,
    api_key_env: str,
) -> None:
    print(f"\n=== Testing {strategy_name} Strategy ===")

    # Test initialization
    print("\nTesting initialization...")
    try:
        config = LLMConfig.get_provider_config(strategy_name)
        if not config:
            if LLMConfig.PROVIDER_CONFIG[strategy_name]["is_uri"]:
                print(f"! Using default URI: {LLMConfig.OLLAMA_DEFAULT_URI}")
            else:
                raise ConfigurationError(
                    LLMConfig.MISSING_API_KEY_ERROR.format(strategy_name)
                )

        strategy = strategy_class("You are a helpful assistant.")
        print(f"✓ Successfully initialized {strategy_name}")
        print(f"Model: {strategy.model}")
        print(f"Temperature: {strategy.temperature}")
    except ConfigurationError as e:
        print(f"✗ Initialization failed: {e}")
        return
    except Exception as e:
        print(f"✗ Unexpected error during initialization: {e}")
        return

    # Test content generation
    print("\nTesting content generation...")
    test_prompt = "Write a short test response"
    test_data = '{"name": "John Doe", "skills": ["Python", "Testing"]}'
    test_job = "Looking for a Python developer with testing experience"

    try:
        response = strategy.generate_content(test_prompt, test_data, test_job)
        print("✓ Successfully generated content")
        print(f"Response: {response[:100]}...")  # First 100 chars
    except APIError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    # Test folder name creation
    print("\nTesting folder name creation...")
    try:
        folder_name = strategy.create_folder_name(
            "Generate a folder name for this job application", test_job
        )
        print("✓ Successfully created folder name")
        print(f"Folder name: {folder_name}")
    except APIError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def main():
    strategies = [
        ("OpenAI", OpenAIStrategy, "OPENAI_API_KEY"),
        ("Claude", ClaudeStrategy, "ANTHROPIC_API_KEY"),
        ("Ollama", OllamaStrategy, "OLLAMA_URI"),
        ("Gemini", GeminiStrategy, "GEMINI_API_KEY"),
    ]

    for strategy_name, strategy_class, api_key_env in strategies:
        llm_strategy_tester(strategy_name, strategy_class, api_key_env)
        print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
