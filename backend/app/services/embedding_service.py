import logging
import os
from typing import List, Optional, Tuple
from abc import ABC, abstractmethod

from app.config import get_settings

_settings = get_settings()
os.environ['HF_ENDPOINT'] = _settings.HF_ENDPOINT

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    @abstractmethod
    def encode(self, text: str) -> List[float]:
        """Encode a single text to embedding vector."""
        pass
    
    @abstractmethod
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts to embedding vectors."""
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """Return the embedding dimension."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model name."""
        pass


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.api_key = api_key
        self.model = model
        self._client = None
        self._dimension = 1536
    
    def _get_client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client
    
    def encode(self, text: str) -> List[float]:
        """Encode a single text using OpenAI API."""
        client = self._get_client()
        try:
            response = client.embeddings.create(
                input=text,
                model=self.model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts using OpenAI API."""
        if not texts:
            return []
        
        client = self._get_client()
        try:
            response = client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI batch embedding error: {e}")
            raise
    
    def get_dimension(self) -> int:
        return self._dimension
    
    def get_model_name(self) -> str:
        return self.model


class LocalEmbeddingProvider(EmbeddingProvider):
    """Local embedding provider using sentence-transformers."""
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "auto",
        batch_size: int = 32,
    ):
        self.model_name = model_name
        self.device = device
        self.batch_size = batch_size
        self._model = None
        self._dimension = 384
        self._device = None
    
    def _get_device(self):
        """Get the device to use for inference."""
        if self._device is not None:
            return self._device
        
        if self.device == "auto":
            try:
                import torch
                if torch.cuda.is_available():
                    self._device = "cuda"
                    logger.info("Using CUDA GPU for embedding")
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self._device = "mps"
                    logger.info("Using Apple MPS for embedding")
                else:
                    self._device = "cpu"
                    logger.info("Using CPU for embedding")
            except ImportError:
                self._device = "cpu"
                logger.info("PyTorch not available, using CPU for embedding")
        else:
            self._device = self.device
            logger.info(f"Using specified device: {self._device}")
        
        return self._device
    
    def _get_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                device = self._get_device()
                self._model = SentenceTransformer(self.model_name, device=device)
                self._dimension = self._model.get_sentence_embedding_dimension()
                logger.info(f"Loaded embedding model '{self.model_name}' on {device}")
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model
    
    def encode(self, text: str) -> List[float]:
        """Encode a single text using local model."""
        model = self._get_model()
        embedding = model.encode(
            text, 
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embedding.tolist()
    
    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """Encode multiple texts using local model with GPU acceleration."""
        if not texts:
            return []
        
        model = self._get_model()
        embeddings = model.encode(
            texts, 
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=self.batch_size,
            show_progress_bar=False,
        )
        return [emb.tolist() for emb in embeddings]
    
    def get_dimension(self) -> int:
        return self._dimension
    
    def get_model_name(self) -> str:
        return f"local:{self.model_name}"


class EmbeddingService:
    """Service for generating text embeddings with fallback support."""
    
    def __init__(self):
        self.settings = get_settings()
        self._primary_provider: Optional[EmbeddingProvider] = None
        self._fallback_provider: Optional[EmbeddingProvider] = None
        self._initialized = False
    
    def _initialize(self):
        if self._initialized:
            return
        
        if self.settings.USE_LOCAL_EMBEDDING:
            self._primary_provider = LocalEmbeddingProvider(
                model_name=self.settings.LOCAL_EMBEDDING_MODEL,
                device=self.settings.EMBEDDING_DEVICE,
                batch_size=self.settings.EMBEDDING_BATCH_SIZE,
            )
            logger.info(f"Using local embedding model: {self.settings.LOCAL_EMBEDDING_MODEL}")
        elif self.settings.OPENAI_API_KEY:
            self._primary_provider = OpenAIEmbeddingProvider(
                api_key=self.settings.OPENAI_API_KEY,
                model=self.settings.OPENAI_EMBEDDING_MODEL
            )
            self._fallback_provider = LocalEmbeddingProvider(
                model_name=self.settings.LOCAL_EMBEDDING_MODEL,
                device=self.settings.EMBEDDING_DEVICE,
                batch_size=self.settings.EMBEDDING_BATCH_SIZE,
            )
            logger.info(f"Using OpenAI embedding model: {self.settings.OPENAI_EMBEDDING_MODEL}")
        else:
            self._primary_provider = LocalEmbeddingProvider(
                model_name=self.settings.LOCAL_EMBEDDING_MODEL,
                device=self.settings.EMBEDDING_DEVICE,
                batch_size=self.settings.EMBEDDING_BATCH_SIZE,
            )
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
            embedding = self._primary_provider.encode(text)
            return embedding, self._primary_provider.get_model_name()
        except Exception as e:
            if self._fallback_provider:
                logger.warning(f"Primary provider failed, using fallback: {e}")
                embedding = self._fallback_provider.encode(text)
                return embedding, self._fallback_provider.get_model_name()
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
            embeddings = self._primary_provider.encode_batch(texts)
            return embeddings, self._primary_provider.get_model_name()
        except Exception as e:
            if self._fallback_provider:
                logger.warning(f"Primary provider failed, using fallback: {e}")
                embeddings = self._fallback_provider.encode_batch(texts)
                return embeddings, self._fallback_provider.get_model_name()
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
