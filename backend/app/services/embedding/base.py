from abc import ABC, abstractmethod
from typing import List, Tuple, Optional


class EmbeddingServiceInterface(ABC):
    """Abstract base class for embedding services."""
    
    @abstractmethod
    def encode(self, text: str) -> Tuple[List[float], str]:
        """
        Encode a single text into an embedding vector.
        
        Args:
            text: The text to encode
            
        Returns:
            Tuple of (embedding vector, model identifier)
        """
        pass
    
    @abstractmethod
    def encode_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
    ) -> Tuple[List[List[float]], str]:
        """
        Encode multiple texts into embedding vectors.
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for processing (default: 32)
            
        Returns:
            Tuple of (list of embedding vectors, model identifier)
        """
        pass
    
    @abstractmethod
    def get_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            The dimension of the embedding vectors
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name of the embedding model.
        
        Returns:
            The model name
        """
        pass
