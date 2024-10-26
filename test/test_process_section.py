import unittest
from unittest.mock import Mock, patch
from engine.runners import AIRunner
from engine.ai_strategies import OpenAIStrategy, ClaudeStrategy
from loaders.json_loader import JsonLoader
from loaders.prompt_loader import PromptLoader
from loaders.job_description_loader import JobDescriptionLoader

class TestProcessSection(unittest.TestCase):
    def setUp(self):
        self.json_loader = JsonLoader("../files/information.json")
        self.prompt_loader = PromptLoader("../prompts")
        self.job_description_loader = JobDescriptionLoader("../created_resumes/akraya_machine_learning_engineer/job_description.txt")
        
        # Create strategies with mocked clients
        self.openai_strategy = OpenAIStrategy("gpt-4", 0.7)
        self.claude_strategy = ClaudeStrategy("claude-2", 0.7)
        
        # Create AIRunner with OpenAI strategy as default
        self.ai_runner = AIRunner(self.openai_strategy)

    @patch('openai.OpenAI')
    def test_process_personal_information_openai(self, mock_openai):
        # Create a mock for the OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client

        # Create a mock for the chat completions create method
        mock_create = Mock()
        mock_client.chat.completions.create = mock_create

        # Create a mock for the response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Processed personal information"))]
        mock_create.return_value = mock_response

        # Assign the mock client to the strategy
        self.openai_strategy.client = mock_client

        prompt = self.prompt_loader.get_personal_information_prompt()
        data = self.json_loader.get_personal_information()
        job_description = self.job_description_loader.get_job_description()

        result = self.ai_runner.process_section(prompt, str(data), job_description)
        
        self.assertEqual(result, "Processed personal information")
        mock_create.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_process_personal_information_claude(self, mock_anthropic):
        self.ai_runner.set_strategy(self.claude_strategy)
        
        # Create a mock for the Anthropic client
        mock_client = Mock()
        mock_anthropic.return_value = mock_client

        # Create a mock for the completions create method
        mock_create = Mock()
        mock_client.completions.create = mock_create

        # Create a mock for the response
        mock_response = Mock(completion="Processed personal information")
        mock_create.return_value = mock_response

        # Assign the mock client to the strategy
        self.claude_strategy.client = mock_client

        prompt = self.prompt_loader.get_personal_information_prompt()
        data = self.json_loader.get_personal_information()
        job_description = self.job_description_loader.get_job_description()

        result = self.ai_runner.process_section(prompt, str(data), job_description)
        
        self.assertEqual(result, "Processed personal information")
        mock_create.assert_called_once()

    # Add more tests for other sections and scenarios as needed

if __name__ == '__main__':
    unittest.main()
