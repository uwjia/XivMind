import logging
from typing import Optional

from app.config import get_settings
from app.services.embedding.base import EmbeddingServiceInterface
from app.services.embedding.local_embedding import LocalEmbeddingService
from app.services.embedding.openai_embedding import OpenAIEmbeddingService

logger = logging.getLogger(__name__)


class EmbeddingServiceFactory:
    """Factory for creating embedding service instances."""
    
    _local_instance: Optional[LocalEmbeddingService] = None
    _openai_instance: Optional[OpenAIEmbeddingService] = None
    _current_provider: Optional[str] = None
    
    @classmethod
    def get_local_embedding_service(
        cls,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
    ) -> LocalEmbeddingService:
        """Get or create a local embedding service instance."""
        settings = get_settings()
        
        if model_name is None:
            model_name = settings.LOCAL_EMBEDDING_MODEL
        if device is None:
            device = settings.EMBEDDING_DEVICE
        
        if cls._local_instance is None or cls._local_instance.model_name != model_name:
            cls._local_instance = LocalEmbeddingService(
                model_name=model_name,
                device=device,
            )
            logger.info(f"Created local embedding service with model: {model_name}")
        
        return cls._local_instance
    
    @classmethod
    def get_openai_embedding_service(
        cls,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> OpenAIEmbeddingService:
        """Get or create an OpenAI embedding service instance."""
        settings = get_settings()
        
        if api_key is None:
            api_key = settings.OPENAI_API_KEY
        if model_name is None:
            model_name = settings.OPENAI_EMBEDDING_MODEL
        if base_url is None:
            base_url = settings.OPENAI_BASE_URL or None
        
        if cls._openai_instance is None or cls._openai_instance.model_name != model_name:
            cls._openai_instance = OpenAIEmbeddingService(
                api_key=api_key,
                model_name=model_name,
                base_url=base_url if base_url else None,
            )
            logger.info(f"Created OpenAI embedding service with model: {model_name}")
        
        return cls._openai_instance
    
    @classmethod
    def get_embedding_service(
        cls,
        provider: Optional[str] = None,
        **kwargs,
    ) -> EmbeddingServiceInterface:
        """
        Get an embedding service instance based on provider.
        
        Args:
            provider: "local" or "openai". If None, uses settings.
            **kwargs: Additional arguments passed to the service constructor.
        
        Returns:
            An embedding service instance.
        """
        settings = get_settings()
        
        if provider is None:
            provider = "local" if settings.USE_LOCAL_EMBEDDING else "openai"
        
        if provider == "local":
            return cls.get_local_embedding_service(**kwargs)
        elif provider == "openai":
            return cls.get_openai_embedding_service(**kwargs)
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")
    
    @classmethod
    def get_current_provider(cls) -> str:
        """Get the current embedding provider from settings."""
        settings = get_settings()
        return "local" if settings.USE_LOCAL_EMBEDDING else "openai"
    
    @classmethod
    def get_current_dimension(cls) -> int:
        """Get the embedding dimension for the current provider."""
        settings = get_settings()
        return settings.EMBEDDING_DIM
    
    @classmethod
    def reset(cls):
        """Reset all cached instances."""
        cls._local_instance = None
        cls._openai_instance = None
        cls._current_provider = None
        logger.info("Embedding service factory reset")


def get_embedding_service(provider: Optional[str] = None) -> EmbeddingServiceInterface:
    """
    Convenience function to get an embedding service.
    
    Args:
        provider: "local" or "openai". If None, uses settings.
    
    Returns:
        An embedding service instance.
    """
    return EmbeddingServiceFactory.get_embedding_service(provider=provider)


def get_embedding_dimension(provider: Optional[str] = None) -> int:
    """
    Get the embedding dimension for a provider.
    
    Args:
        provider: "local" or "openai". If None, uses current provider.
    
    Returns:
        The embedding dimension.
    """
    if provider is None:
        return EmbeddingServiceFactory.get_current_dimension()
    
    service = EmbeddingServiceFactory.get_embedding_service(provider=provider)
    return service.get_dimension()
