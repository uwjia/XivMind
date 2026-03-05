import logging
from typing import List, Tuple, Optional
import asyncio

from app.services.embedding.base import EmbeddingServiceInterface

logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not installed. Install with: pip install openai")


EMBEDDING_DIMENSIONS = {
    "text-embedding-ada-002": 1536,
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


class OpenAIEmbeddingService(EmbeddingServiceInterface):
    def __init__(
        self,
        api_key: str,
        model_name: str = "text-embedding-ada-002",
        base_url: Optional[str] = None,
    ):
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "openai is not installed. "
                "Install with: pip install openai"
            )
        
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url
        self._client: Optional[OpenAI] = None
        self.dimension = EMBEDDING_DIMENSIONS.get(model_name, 1536)
    
    @property
    def client(self) -> OpenAI:
        if self._client is None:
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self._client = OpenAI(**client_kwargs)
            logger.info(f"OpenAI client initialized for model: {self.model_name}")
        return self._client
    
    def encode(self, text: str) -> Tuple[List[float], str]:
        if not text or not text.strip():
            return [0.0] * self.dimension, self.model_name
        
        try:
            response = self.client.embeddings.create(
                input=text,
                model=self.model_name,
            )
            embedding = response.data[0].embedding
            return embedding, self.model_name
        except Exception as e:
            logger.error(f"Failed to encode text with OpenAI: {e}")
            return [0.0] * self.dimension, self.model_name
    
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
    ) -> Tuple[List[List[float]], str]:
        if not texts:
            return [], self.model_name
        
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch = [t if t and t.strip() else " " for t in batch]
            
            try:
                response = self.client.embeddings.create(
                    input=batch,
                    model=self.model_name,
                )
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Failed to encode batch with OpenAI: {e}")
                all_embeddings.extend([[0.0] * self.dimension] * len(batch))
        
        return all_embeddings, self.model_name
    
    async def encode_async(self, text: str) -> Tuple[List[float], str]:
        if not text or not text.strip():
            return [0.0] * self.dimension, self.model_name
        
        try:
            client = self.client
            loop = asyncio.get_event_loop()
            
            def _encode():
                response = client.embeddings.create(
                    input=text,
                    model=self.model_name,
                )
                return response.data[0].embedding
            
            embedding = await loop.run_in_executor(None, _encode)
            return embedding, self.model_name
        except Exception as e:
            logger.error(f"Failed to encode text async with OpenAI: {e}")
            return [0.0] * self.dimension, self.model_name
    
    async def encode_batch_async(
        self,
        texts: List[str],
        batch_size: int = 32,
    ) -> Tuple[List[List[float]], str]:
        if not texts:
            return [], self.model_name
        
        all_embeddings = []
        client = self.client
        loop = asyncio.get_event_loop()
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch = [t if t and t.strip() else " " for t in batch]
            
            try:
                def _encode_batch(b=batch):
                    response = client.embeddings.create(
                        input=b,
                        model=self.model_name,
                    )
                    return [item.embedding for item in response.data]
                
                batch_embeddings = await loop.run_in_executor(None, _encode_batch)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                logger.error(f"Failed to encode batch async with OpenAI: {e}")
                all_embeddings.extend([[0.0] * self.dimension] * len(batch))
        
        return all_embeddings, self.model_name
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return self.model_name
