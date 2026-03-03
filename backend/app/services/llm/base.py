from abc import ABC, abstractmethod
from typing import List, Dict


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """Generate response from messages."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the provider name."""
        pass
