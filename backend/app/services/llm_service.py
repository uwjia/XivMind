"""LLM Service for managing multiple LLM providers."""
import logging
from typing import List, Dict, Any, Optional

from app.config import get_settings
from app.services.llm import LLMProvider, OpenAIProvider, AnthropicProvider, GLMProvider, OllamaProvider

logger = logging.getLogger(__name__)


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
        
        logger.info(f"[LLM Service] Creating provider: {provider}, model: {model or 'default'}")
        
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
                model=model or self.settings.LLM_MODEL or "glm-5",
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
        logger.info(f"[LLM Service] Initialized {provider} provider with model: {self._provider.get_model_name()}")
    
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
    
    def _get_provider(self, provider: Optional[str], model: Optional[str]) -> LLMProvider:
        """Get or create a provider instance."""
        if provider:
            cache_key = f"{provider}:{model or 'default'}"
            if cache_key not in self._providers_cache:
                self._providers_cache[cache_key] = self._create_provider(provider, model)
            return self._providers_cache[cache_key]
        else:
            self._initialize()
            return self._provider
    
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
        active_provider = self._get_provider(provider, model)
        
        logger.info(f"[LLM Service] ask_question - Provider: {active_provider.get_provider_name()}, Model: {active_provider.get_model_name()}")
        
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
    
    async def ask_question_with_memory(
        self,
        question: str,
        papers: List[Dict[str, Any]],
        memory_context: Optional[str] = None,
        core_memory = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate an answer with memory-based personalization.
        
        This method enhances the basic ask_question with:
        - User profile context (research interests, preferences)
        - Relevant conversation history (included in memory_context)
        - Personalized response style (language, summary format)
        
        Args:
            question: The user's question
            papers: List of relevant papers to use as context
            memory_context: Pre-built memory context string (includes user profile and history)
            core_memory: User's CoreMemory object with preferences (for language/style settings)
            provider: Optional provider to use (overrides default)
            model: Optional model to use
            **kwargs: Additional parameters for the LLM
        
        Returns:
            Generated answer string with personalization
        """
        active_provider = self._get_provider(provider, model)
        
        logger.info(f"[LLM Service] ask_question_with_memory - Provider: {active_provider.get_provider_name()}, Model: {active_provider.get_model_name()}, Memory: {memory_context is not None}")
        
        system_prompt = self.SYSTEM_PROMPT
        
        language_instruction = ""
        if core_memory and hasattr(core_memory, 'language_preference'):
            if core_memory.language_preference == "zh-CN":
                language_instruction = "\n\n**IMPORTANT: You MUST respond in Chinese (中文). All your output must be in Chinese language.**"
            elif core_memory.language_preference == "en-US":
                language_instruction = "\n\n**IMPORTANT: You MUST respond in English.**"
        
        if language_instruction:
            system_prompt = language_instruction + "\n\n" + system_prompt
        
        if memory_context:
            system_prompt += f"\n\n## User Memory Context\n{memory_context}"
        
        if core_memory:
            if hasattr(core_memory, 'summary_style'):
                if core_memory.summary_style == "brief":
                    system_prompt += "\n\nPlease answer concisely, avoid being verbose."
                elif core_memory.summary_style == "bullet_points":
                    system_prompt += "\n\nPlease use bullet points to answer the question."
                elif core_memory.summary_style == "detailed":
                    system_prompt += "\n\nPlease answer in detail, providing sufficient information."
            
            #if hasattr(core_memory, 'custom_instructions') and core_memory.custom_instructions:
            #    system_prompt += f"\n\nUser Custom Instructions: {core_memory.custom_instructions}"
        
        # logger.info(f"[LLM Service] ask_question_with_memory - System Prompt: {system_prompt}")
        
        context = self._build_context(papers)
        
        user_language_hint = ""
        if core_memory and hasattr(core_memory, 'language_preference'):
            if core_memory.language_preference == "zh-CN":
                user_language_hint = "\n\n请用中文回答这个问题。"
            elif core_memory.language_preference == "en-US":
                user_language_hint = "\n\nPlease answer this question in English."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Context:
{context}

Question: {question}

Please answer the question based on the provided context. If the context doesn't contain 
enough information to fully answer the question, please say so and provide what information 
is available. Reference specific papers when relevant.{user_language_hint}"""}
        ]
        
        return await active_provider.generate(messages, **kwargs)
    
    def get_model_name(self, provider: Optional[str] = None, model: Optional[str] = None) -> str:
        """Return the current model name."""
        active_provider = self._get_provider(provider, model)
        return active_provider.get_model_name()
    
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
        active_provider = self._get_provider(provider, model)
        
        logger.info(f"[LLM Service] generate - Provider: {active_provider.get_provider_name()}, Model: {active_provider.get_model_name()}")
        
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
        active_provider = self._get_provider(provider, model)
        
        logger.info(f"[LLM Service] generate_with_messages - Provider: {active_provider.get_provider_name()}, Model: {active_provider.get_model_name()}, Messages: {len(messages)}")
        
        return await active_provider.generate(messages, **kwargs)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat with the LLM and return a structured response.
        
        This method is designed for memory extraction and other use cases
        that need the full response structure.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            provider: Optional provider to use (overrides default)
            model: Optional model to use
            **kwargs: Additional parameters for the LLM
        
        Returns:
            Dict with 'content' key containing the response
        """
        active_provider = self._get_provider(provider, model)
        
        logger.info(f"[LLM Service] chat - Provider: {active_provider.get_provider_name()}, Model: {active_provider.get_model_name()}")
        
        content = await active_provider.generate(messages, **kwargs)
        return {"content": content}


llm_service = LLMService()
