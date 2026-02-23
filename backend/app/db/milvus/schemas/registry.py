from typing import Dict, Type, List
from .base import BaseCollectionSchema
from .bookmarks import BookmarkSchema
from .downloads import DownloadSchema
from .papers import PaperSchema
from .date_index import DateIndexSchema
from .embedding_index import EmbeddingIndexSchema
from .paper_embeddings import PaperEmbeddingSchema


class SchemaRegistry:
    """Registry for Milvus collection schemas."""
    
    _schemas: Dict[str, BaseCollectionSchema] = {}
    
    @classmethod
    def register(cls, schema: BaseCollectionSchema) -> None:
        """Register a schema."""
        cls._schemas[schema.collection_name] = schema
    
    @classmethod
    def get(cls, collection_name: str) -> BaseCollectionSchema:
        """Get a schema by collection name."""
        if collection_name not in cls._schemas:
            raise ValueError(f"Schema for collection '{collection_name}' not found")
        return cls._schemas[collection_name]
    
    @classmethod
    def get_all(cls) -> List[BaseCollectionSchema]:
        """Get all registered schemas."""
        return list(cls._schemas.values())
    
    @classmethod
    def get_all_names(cls) -> List[str]:
        """Get all registered collection names."""
        return list(cls._schemas.keys())


SchemaRegistry.register(BookmarkSchema())
SchemaRegistry.register(DownloadSchema())
SchemaRegistry.register(PaperSchema())
SchemaRegistry.register(DateIndexSchema())
SchemaRegistry.register(EmbeddingIndexSchema())
SchemaRegistry.register(PaperEmbeddingSchema())
