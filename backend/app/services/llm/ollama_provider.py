"""Ollama LLM provider."""
import json
import logging
from typing import List, Dict, Optional

from .base import LLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Local Ollama LLM provider."""
    
    def __init__(self, base_url: str, model: str, temperature: float = 0.7, max_tokens: int = 2048):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        self._available_models: Optional[List[str]] = None
    
    def _get_client(self):
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(timeout=120.0)
        return self._client
    
    async def _get_available_models(self) -> List[str]:
        """Get list of available models from Ollama."""
        if self._available_models is not None:
            return self._available_models
        
        try:
            client = self._get_client()
            response = await client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                self._available_models = [m.get("name", "") for m in data.get("models", [])]
            else:
                self._available_models = []
        except Exception:
            self._available_models = []
        
        return self._available_models
    
    async def check_available(self) -> tuple[bool, str]:
        """Check if Ollama service and model are available.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            client = self._get_client()
            
            response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
            if response.status_code != 200:
                return False, f"Ollama service returned status {response.status_code}"
            
            data = response.json()
            models = data.get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            if self.model in model_names:
                return True, ""
            
            model_base = self.model.split(":")[0]
            matching_model = next((m for m in model_names if m.startswith(model_base + ":") or m == model_base), None)
            
            if matching_model:
                self.model = matching_model
                return True, ""
            
            available = ", ".join(model_names) if model_names else "none"
            return False, f"Model '{self.model}' not found. Available models: {available}"
            
        except Exception as e:
            return False, f"Cannot connect to Ollama service ({self.base_url}): {str(e)}"
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        available, error = await self.check_available()
        if not available:
            raise ValueError(f"Ollama not available: {error}")
        
        client = self._get_client()
        
        logger.info(f"[Ollama] Calling model: {self.model}, base_url: {self.base_url}, temperature: {kwargs.get('temperature', self.temperature)}")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", self.temperature),
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
            }
        }
        
        response = await client.post(
            f"{self.base_url}/api/chat",
            json=payload,
        )
        
        if response.status_code == 404:
            raise ValueError(f"Model '{self.model}' not found. Please run: ollama pull {self.model}")
        
        response.raise_for_status()
        
        result = response.json()
        return result["message"]["content"]
    
    def get_model_name(self) -> str:
        return f"ollama/{self.model}"
    
    def get_provider_name(self) -> str:
        return "ollama"
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
