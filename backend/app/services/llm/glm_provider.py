"""GLM (ZhipuAI) LLM provider."""
import logging
from typing import List, Dict

from .base import LLMProvider

logger = logging.getLogger(__name__)


class GLMProvider(LLMProvider):
    """ZhipuAI GLM LLM provider (OpenAI-compatible API)."""
    
    def __init__(self, api_key: str, model: str, base_url: str, temperature: float = 0.7, max_tokens: int = 2048):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        client = self._get_client()
        
        logger.info(f"[GLM] Calling model: {self.model}, base_url: {self.base_url}, temperature: {kwargs.get('temperature', self.temperature)}")
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content
    
    def get_model_name(self) -> str:
        return self.model
    
    def get_provider_name(self) -> str:
        return "glm"
