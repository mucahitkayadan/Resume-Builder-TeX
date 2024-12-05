import logging
from typing import Any, Dict, Tuple
from .strategies.base import LLMStrategy
from src.generator.utils.string_utils import get_company_name_and_job_title
from src.llms.strategies import OpenAIStrategy, ClaudeStrategy, OllamaStrategy, GeminiStrategy
from ..loaders.prompt_loader import PromptLoader
from config.llm_config import LLMConfig

logger = logging.getLogger(__name__)

class LLMRunner:
    def __init__(self, strategy: LLMStrategy):
        self.strategy = strategy
        self.prompt_loader = PromptLoader()

    @classmethod
    def create_with_config(cls, model_type: str, model_name: str, temperature: float, prompt_loader: PromptLoader) -> 'LLMRunner':
        """Factory method to create LLMRunner with specific configuration"""
        try:
            strategy_map = {
                "OpenAI": OpenAIStrategy,
                "Claude": ClaudeStrategy,
                "Ollama": OllamaStrategy,
                "Gemini": GeminiStrategy
            }
            
            strategy_class = strategy_map.get(model_type)
            if not strategy_class:
                raise ValueError(f"Unsupported model type: {model_type}")
            
            strategy = strategy_class(prompt_loader.get_system_prompt())
            strategy.model = model_name
            strategy.temperature = temperature
            
            return cls(strategy)
        except Exception as e:
            logger.error(f"Error creating LLMRunner: {e}")
            # Default to OpenAI if there's an error
            strategy = OpenAIStrategy(prompt_loader.get_system_prompt())
            strategy.model = LLMConfig.OPENAI_MODEL.name
            strategy.temperature = LLMConfig.OPENAI_MODEL.default_temperature
            return cls(strategy)

    def update_config(self, model_type: str, model_name: str, temperature: float):
        """Update the existing runner with new configuration"""
        strategy_map = {
            "OpenAI": OpenAIStrategy,
            "Claude": ClaudeStrategy,
            "Ollama": OllamaStrategy,
            "Gemini": GeminiStrategy
        }
        
        strategy_class = strategy_map.get(model_type)
        if not strategy_class:
            raise ValueError(f"Unsupported model type: {model_type}")
            
        new_strategy = strategy_class(self.prompt_loader.get_system_prompt())
        new_strategy.model = model_name
        new_strategy.temperature = temperature
        self.strategy = new_strategy

    def generate_content(self, prompt: str, data: str, job_description: str) -> str:
        return self.strategy.generate_content(prompt, data, job_description)

    def create_company_name_and_job_title(self, naming_prompt: str, job_description: str) -> Tuple[str, str]:
        return get_company_name_and_job_title(self.strategy.create_folder_name(naming_prompt, job_description))

    def get_config(self) -> Dict[str, Any]:
        return {
            'type': self.strategy.__class__.__name__,
            'model': self.strategy.model,
            'temperature': self.strategy.temperature
        }
    
    def set_config(self, config: Dict[str, Any]):
        self.strategy = self._get_ai_strategy(config['model_type'])
        self.strategy.model = config['model']
        self.strategy.temperature = config['temperature']

    def _get_ai_strategy(self, model_type: str):
        """Get the appropriate AI strategy based on model type."""
        strategy_map = {
            "OpenAI": OpenAIStrategy,
            "Claude": ClaudeStrategy,
            "Ollama": OllamaStrategy,
            "Gemini": GeminiStrategy
        }
        strategy_class = strategy_map.get(model_type)
        if not strategy_class:
            raise ValueError(f"Unsupported model type: {model_type}")
        return strategy_class(self.prompt_loader.get_system_prompt())

