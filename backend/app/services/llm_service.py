import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app.config import get_settings

logger = logging.getLogger(__name__)


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


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 2048):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client
    
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        client = self._get_client()
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content
    
    def get_model_name(self) -> str:
        return self.model


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
        
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )
        
        return response.choices[0].message.content
    
    def get_model_name(self) -> str:
        return self.model


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
        import json
        
        available, error = await self.check_available()
        if not available:
            raise ValueError(f"Ollama not available: {error}")
        
        client = self._get_client()
        
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
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


class LLMService:
    """Service for generating responses using LLM."""
    
    SYSTEM_PROMPT = """You are a helpful AI research assistant specialized in academic papers from arXiv. 
Your role is to help users understand research papers, answer questions about scientific topics, 
and provide insights based on the paper abstracts provided in the context.

When answering questions:
1. Be accurate and cite relevant papers from the context when applicable
2. If the context doesn't contain enough information, say so honestly
3. Explain complex concepts in a clear and accessible way
4. When referencing papers, use the format: [Title] (Authors, Year)

Always be helpful, accurate, and scholarly in your responses."""
    
    PROVIDER_CONFIG = {
        "openai": {
            "name": "OpenAI",
            "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "description": "OpenAI GPT models (requires OPENAI_API_KEY)",
        },
        "anthropic": {
            "name": "Anthropic",
            "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
            "description": "Anthropic Claude models (requires OPENAI_API_KEY as API key)",
        },
        "glm": {
            "name": "BigModel (GLM)",
            "models": ["glm-4.7", "glm-5", "glm-4-flash", "glm-4-long"],
            "description": "GLM models (requires GLM_API_KEY)",
        },
        "ollama": {
            "name": "Ollama",
            "models": ["llama3", "gemma3:4b", "mistral", "qwen2", "deepseek-coder"],
            "description": "Local Ollama Service",
        },
    }
    
    def __init__(self):
        self.settings = get_settings()
        self._provider: Optional[LLMProvider] = None
        self._providers_cache: Dict[str, LLMProvider] = {}
    
    def _create_provider(self, provider_name: str, model: Optional[str] = None) -> LLMProvider:
        """Create a provider instance."""
        provider = provider_name.lower()
        
        if provider == "openai":
            if not self.settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for OpenAI provider")
            return OpenAIProvider(
                api_key=self.settings.OPENAI_API_KEY,
                model=model or self.settings.LLM_MODEL,
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS,
            )
        
        elif provider == "anthropic":
            api_key = self.settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("API key is required for Anthropic provider")
            return AnthropicProvider(
                api_key=api_key,
                model=model or self.settings.LLM_MODEL,
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS,
            )
        
        elif provider == "glm":
            if not self.settings.GLM_API_KEY:
                raise ValueError("GLM_API_KEY is required for GLM provider")
            return GLMProvider(
                api_key=self.settings.GLM_API_KEY,
                model=model or self.settings.LLM_MODEL or "glm-4-plus",
                base_url=self.settings.GLM_BASE_URL,
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS,
            )
        
        elif provider == "ollama":
            return OllamaProvider(
                base_url=self.settings.OLLAMA_BASE_URL,
                model=model or self.settings.OLLAMA_MODEL or "llama3",
                temperature=self.settings.LLM_TEMPERATURE,
                max_tokens=self.settings.LLM_MAX_TOKENS,
            )
        
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}. Supported: openai, anthropic, glm, ollama")
    
    def _initialize(self):
        if self._provider is not None:
            return
        
        provider = self.settings.LLM_PROVIDER.lower()
        self._provider = self._create_provider(provider)
        logger.info(f"Initialized {provider} provider with model: {self._provider.get_model_name()}")
    
    def get_providers(self) -> List[Dict[str, Any]]:
        """Get list of all available LLM providers."""
        providers = []
        
        for provider_id, config in self.PROVIDER_CONFIG.items():
            available = self._check_provider_available(provider_id)
            providers.append({
                "id": provider_id,
                "name": config["name"],
                "models": config["models"],
                "available": available,
                "description": config["description"],
            })
        
        return providers
    
    def _check_provider_available(self, provider: str) -> bool:
        """Check if a provider is available (has required credentials)."""
        try:
            if provider == "openai":
                return bool(self.settings.OPENAI_API_KEY)
            elif provider == "anthropic":
                return bool(self.settings.OPENAI_API_KEY)
            elif provider == "glm":
                return bool(self.settings.GLM_API_KEY)
            elif provider == "ollama":
                return True
            return False
        except Exception:
            return False
    
    def _build_context(self, papers: List[Dict[str, Any]]) -> str:
        """Build context string from papers."""
        if not papers:
            return "No relevant papers found in the database."
        
        context_parts = ["Here are some relevant papers from the database:\n"]
        
        for i, paper in enumerate(papers[:10], 1):
            title = paper.get("title", "Unknown Title")
            authors = paper.get("authors", [])
            authors_str = ", ".join(authors[:3]) if authors else "Unknown Authors"
            if len(authors) > 3:
                authors_str += " et al."
            
            abstract = paper.get("abstract", "No abstract available.")
            if len(abstract) > 500:
                abstract = abstract[:500] + "..."
            
            published = paper.get("published", "")
            year = published[:4] if published else "Unknown Year"
            
            context_parts.append(f"""
Paper {i}:
Title: {title}
Authors: {authors_str}
Year: {year}
Abstract: {abstract}
""")
        
        return "\n".join(context_parts)
    
    async def ask_question(
        self, 
        question: str, 
        papers: List[Dict[str, Any]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate an answer to a question using relevant papers as context.
        
        Args:
            question: The user's question
            papers: List of relevant papers to use as context
            provider: Optional provider to use (overrides default)
            model: Optional model to use
            **kwargs: Additional parameters for the LLM
        
        Returns:
            Generated answer string
        """
        if provider:
            cache_key = f"{provider}:{model or 'default'}"
            if cache_key not in self._providers_cache:
                self._providers_cache[cache_key] = self._create_provider(provider, model)
            active_provider = self._providers_cache[cache_key]
        else:
            self._initialize()
            active_provider = self._provider
        
        context = self._build_context(papers)
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"""Context:
{context}

Question: {question}

Please answer the question based on the provided context. If the context doesn't contain 
enough information to fully answer the question, please say so and provide what information 
is available. Reference specific papers when relevant."""}
        ]
        
        return await active_provider.generate(messages, **kwargs)
    
    def get_model_name(self, provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """Return the current model name."""
        if provider:
            cache_key = f"{provider}:{model or 'default'}"
            if cache_key not in self._providers_cache:
                self._providers_cache[cache_key] = self._create_provider(provider, model)
            return self._providers_cache[cache_key].get_model_name()
        
        self._initialize()
        return self._provider.get_model_name()
    
    def is_available(self, provider: Optional[str] = None) -> bool:
        """Check if LLM service is available.
        
        Args:
            provider: Optional provider to check. If None, checks the default provider.
        """
        try:
            if provider:
                return self._check_provider_available(provider)
            self._initialize()
            return True
        except Exception as e:
            logger.warning(f"LLM service not available: {e}")
            return False
    
    async def generate(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM with a simple prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            provider: Optional provider to use (overrides default)
            model: Optional model to use
            **kwargs: Additional parameters for the LLM
        
        Returns:
            Generated response string
        """
        if provider:
            cache_key = f"{provider}:{model or 'default'}"
            if cache_key not in self._providers_cache:
                self._providers_cache[cache_key] = self._create_provider(provider, model)
            active_provider = self._providers_cache[cache_key]
        else:
            self._initialize()
            active_provider = self._provider
        
        messages = [{"role": "user", "content": prompt}]
        return await active_provider.generate(messages, **kwargs)

    async def generate_with_messages(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response from the LLM with structured messages.
        
        This method is designed for SubAgents and other use cases that require
        full control over the message structure, including system prompts and
        conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
                     Roles can be 'system', 'user', 'assistant', or 'tool'.
            provider: Optional provider to use (overrides default)
            model: Optional model to use
            **kwargs: Additional parameters for the LLM (temperature, max_tokens, etc.)
        
        Returns:
            Generated response string
        """
        if provider:
            cache_key = f"{provider}:{model or 'default'}"
            if cache_key not in self._providers_cache:
                self._providers_cache[cache_key] = self._create_provider(provider, model)
            active_provider = self._providers_cache[cache_key]
        else:
            self._initialize()
            active_provider = self._provider
        
        return await active_provider.generate(messages, **kwargs)


llm_service = LLMService()
