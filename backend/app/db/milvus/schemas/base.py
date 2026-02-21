from abc import ABC, abstractmethod
from typing import List, Any
from pymilvus import FieldSchema, CollectionSchema, DataType


class BaseCollectionSchema(ABC):
    """Abstract base class for Milvus collection schemas."""
    
    @property
    @abstractmethod
    def collection_name(self) -> str:
        """Return the collection name."""
        pass
    
    @property
    @abstractmethod
    def schema_version(self) -> int:
        """Return the schema version."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return the collection description."""
        pass
    
    @property
    @abstractmethod
    def embedding_dim(self) -> int:
        """Return the embedding dimension."""
        pass
    
    @property
    @abstractmethod
    def index_nlist(self) -> int:
        """Return the index nlist parameter."""
        pass
    
    @abstractmethod
    def get_fields(self) -> List[FieldSchema]:
        """Return the list of field schemas."""
        pass
    
    def get_collection_schema(self) -> CollectionSchema:
        """Build and return the CollectionSchema."""
        return CollectionSchema(
            fields=self.get_fields(),
            description=self.description
        )
    
    def get_index_params(self) -> dict:
        """Return the index parameters."""
        return {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": self.index_nlist},
        }
    
    def get_schema_version_fields(self) -> List[FieldSchema]:
        """Return fields for schema version collection."""
        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="version", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=8),
        ]
    
    def get_schema_version_collection_name(self) -> str:
        """Return the schema version collection name."""
        return f"{self.collection_name}_schema_version"
