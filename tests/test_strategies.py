import pytest
from unittest.mock import Mock, patch
from src.llms.strategies import OpenAIStrategy, ClaudeStrategy, OllamaStrategy
from src.llms.utils.errors import APIError, ConfigurationError


@pytest.fixture
def system_instruction():
    return "You are a helpful assistant."

@pytest.fixture
def test_data():
    return {
        "prompt": "Write a test prompt",
        "data": '{"name": "John Doe", "skills": ["Python", "Testing"]}',
        "job_description": "Looking for a Python developer with testing experience"
    }

class TestLLMStrategies:
    @pytest.mark.parametrize("strategy_class,env_var", [
        (OpenAIStrategy, "OPENAI_API_KEY"),
        (ClaudeStrategy, "ANTHROPIC_API_KEY"),
        (OllamaStrategy, "OLLAMA_URI")
    ])
    def test_strategy_initialization(self, strategy_class, env_var, system_instruction, monkeypatch):
        # Test initialization with missing API key
        monkeypatch.delenv(env_var, raising=False)
        with pytest.raises(ConfigurationError):
            strategy_class(system_instruction)

        # Test successful initialization
        monkeypatch.setenv(env_var, "test_key")
        strategy = strategy_class(system_instruction)
        assert strategy.system_instruction == system_instruction
        assert strategy.temperature == strategy_class.temperature

    @pytest.mark.parametrize("strategy_class,provider", [
        (OpenAIStrategy, "OpenAI"),
        (ClaudeStrategy, "Claude"),
        (OllamaStrategy, "Ollama")
    ])
    def test_generate_content(self, strategy_class, provider, system_instruction, test_data, monkeypatch):
        # Mock API responses
        mock_response = Mock()
        if provider == "OpenAI":
            mock_response.choices = [Mock(message=Mock(content="Test response"))]
        elif provider == "Claude":
            mock_response.content = [Mock(text="Test response")]
        else:  # Ollama
            mock_response.json.return_value = {"response": "Test response"}

        # Set up strategy with mocked client
        monkeypatch.setenv(f"{provider.upper()}_API_KEY", "test_key")
        strategy = strategy_class(system_instruction)
        
        with patch.object(strategy, 'client' if provider != "Ollama" else 'requests', Mock()) as mock_client:
            if provider == "Ollama":
                mock_client.post.return_value = mock_response
            else:
                mock_client.messages.create.return_value = mock_response
            
            result = strategy.generate_content(
                test_data["prompt"],
                test_data["data"],
                test_data["job_description"]
            )
            
            assert result == "Test response"

    @pytest.mark.parametrize("strategy_class,provider", [
        (OpenAIStrategy, "OpenAI"),
        (ClaudeStrategy, "Claude"),
        (OllamaStrategy, "Ollama")
    ])
    def test_create_folder_name(self, strategy_class, provider, system_instruction, test_data, monkeypatch):
        # Mock API responses
        mock_response = Mock()
        if provider == "OpenAI":
            mock_response.choices = [Mock(message=Mock(content="Company|Position"))]
        elif provider == "Claude":
            mock_response.content = [Mock(text="Company|Position")]
        else:  # Ollama
            mock_response.json.return_value = {"response": "Company|Position"}

        # Set up strategy with mocked client
        monkeypatch.setenv(f"{provider.upper()}_API_KEY", "test_key")
        strategy = strategy_class(system_instruction)
        
        with patch.object(strategy, 'client' if provider != "Ollama" else 'requests', Mock()) as mock_client:
            if provider == "Ollama":
                mock_client.post.return_value = mock_response
            else:
                mock_client.messages.create.return_value = mock_response
            
            result = strategy.create_folder_name(
                test_data["prompt"],
                test_data["job_description"]
            )
            
            assert result == "Company|Position"

    @pytest.mark.parametrize("strategy_class,provider", [
        (OpenAIStrategy, "OpenAI"),
        (ClaudeStrategy, "Claude"),
        (OllamaStrategy, "Ollama")
    ])
    def test_api_error_handling(self, strategy_class, provider, system_instruction, test_data, monkeypatch):
        monkeypatch.setenv(f"{provider.upper()}_API_KEY", "test_key")
        strategy = strategy_class(system_instruction)
        
        with patch.object(strategy, 'client' if provider != "Ollama" else 'requests', Mock()) as mock_client:
            if provider == "Ollama":
                mock_client.post.side_effect = Exception("API Error")
            else:
                mock_client.messages.create.side_effect = Exception("API Error")
            
            with pytest.raises(APIError):
                strategy.generate_content(
                    test_data["prompt"],
                    test_data["data"],
                    test_data["job_description"]
                ) 