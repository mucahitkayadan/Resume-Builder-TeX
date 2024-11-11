import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from engine.ai_strategies import AIStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AIRunner:
    def __init__(self, strategy: AIStrategy):
        self.strategy = strategy

    def set_strategy(self, strategy: AIStrategy):
        self.strategy = strategy

    def process_section(self, prompt: str, data: str, job_description: str) -> str:
        return self.strategy.process_section(prompt, data, job_description)

    def create_folder_name(self, folder_name_prompt: str, job_description: str) -> str:
        return self.strategy.create_folder_name(folder_name_prompt, job_description)

    def get_model_name(self) -> Optional[str]:
        return getattr(self.strategy, 'model', None)

    def get_temperature(self) -> Optional[float]:
        return getattr(self.strategy, 'temperature', None)

    def get_strategy_info(self) -> Dict[str, Any]:
        return {
            'type': self.strategy.__class__.__name__,
            'model': self.get_model_name(),
            'temperature': self.get_temperature()
        }
