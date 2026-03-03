"""Anthropic Claude LLM provider."""
import logging
from typing import List, Dict

from .base import LLMProvider

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude LLM provider."""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 2048):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            from anthropic import AsyncAnthropic
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        client = self._get_client()
        
        system_message = ""
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                chat_messages.append(msg)
        
        logger.info(f"[Anthropic] Calling model: {self.model}, temperature: {kwargs.get('temperature', self.temperature)}")
        
        response = await client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            system=system_message if system_message else None,
            messages=chat_messages,
        )
        
        return response.content[0].text
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "anthropic"
