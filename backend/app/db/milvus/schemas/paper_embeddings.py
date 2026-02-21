from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema
from app.config import get_settings


class PaperEmbeddingSchema(BaseCollectionSchema):
    """Schema for paper_embeddings collection."""
    
    @property
    def collection_name(self) -> str:
        return "paper_embeddings"
    
    @property
    def schema_version(self) -> int:
        return 2
    
    @property
    def description(self) -> str:
        return "Paper embeddings for semantic search"
    
    @property
    def embedding_dim(self) -> int:
        settings = get_settings()
        return settings.EMBEDDING_DIM
    
    @property
    def index_nlist(self) -> int:
        return 128
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128, is_primary=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="embedding_model", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
        ]
