import logging
from typing import List, Optional, Tuple

from app.config import get_settings
from app.services.embedding import (
    EmbeddingServiceInterface,
    EmbeddingServiceFactory,
)

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings with fallback support."""
    
    def __init__(self):
        self.settings = get_settings()
        self._primary_provider: Optional[EmbeddingServiceInterface] = None
        self._fallback_provider: Optional[EmbeddingServiceInterface] = None
        self._initialized = False
    
    def _initialize(self):
        if self._initialized:
            return
        
        import os
        os.environ['HF_ENDPOINT'] = self.settings.HF_ENDPOINT
        
        if self.settings.USE_LOCAL_EMBEDDING:
            self._primary_provider = EmbeddingServiceFactory.get_local_embedding_service()
            logger.info(f"Using local embedding model: {self.settings.LOCAL_EMBEDDING_MODEL}")
        elif self.settings.OPENAI_API_KEY:
            self._primary_provider = EmbeddingServiceFactory.get_openai_embedding_service()
            self._fallback_provider = EmbeddingServiceFactory.get_local_embedding_service()
            logger.info(f"Using OpenAI embedding model: {self.settings.OPENAI_EMBEDDING_MODEL}")
        else:
            self._primary_provider = EmbeddingServiceFactory.get_local_embedding_service()
            logger.info(f"No OpenAI API key, using local model: {self.settings.LOCAL_EMBEDDING_MODEL}")
        
        self._initialized = True
    
    def encode(self, text: str) -> Tuple[List[float], str]:
        """
        Encode text to embedding vector.
        
        Returns:
            Tuple of (embedding, model_name)
        """
        self._initialize()
        
        try:
            embedding, model_name = self._primary_provider.encode(text)
            return embedding, model_name
        except Exception as e:
            if self._fallback_provider:
                logger.warning(f"Primary provider failed, using fallback: {e}")
                embedding, model_name = self._fallback_provider.encode(text)
                return embedding, model_name
            raise
    
    def encode_batch(self, texts: List[str]) -> Tuple[List[List[float]], str]:
        """
        Encode multiple texts to embedding vectors.
        
        Returns:
            Tuple of (embeddings, model_name)
        """
        self._initialize()
        
        if not texts:
            return [], ""
        
        try:
            embeddings, model_name = self._primary_provider.encode_batch(
                texts, 
                batch_size=self.settings.EMBEDDING_BATCH_SIZE
            )
            return embeddings, model_name
        except Exception as e:
            if self._fallback_provider:
                logger.warning(f"Primary provider failed, using fallback: {e}")
                embeddings, model_name = self._fallback_provider.encode_batch(
                    texts,
                    batch_size=self.settings.EMBEDDING_BATCH_SIZE
                )
                return embeddings, model_name
            raise
    
    def get_dimension(self) -> int:
        """Get the embedding dimension of the current provider."""
        self._initialize()
        return self._primary_provider.get_dimension()
    
    def get_model_name(self) -> str:
        """Get the model name of the current provider."""
        self._initialize()
        return self._primary_provider.get_model_name()
    
    def is_available(self) -> bool:
        """Check if embedding service is available."""
        try:
            self._initialize()
            return True
        except Exception:
            return False


embedding_service = EmbeddingService()
