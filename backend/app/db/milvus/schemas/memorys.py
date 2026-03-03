from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema
from app.config import get_settings


class RecallMemorySchema(BaseCollectionSchema):
    """Schema for recall_memories collection."""
    
    @property
    def collection_name(self) -> str:
        return "recall_memories"
    
    @property
    def schema_version(self) -> int:
        return 1
    
    @property
    def description(self) -> str:
        return "Recall memories for conversation history with semantic search"
    
    @property
    def embedding_dim(self) -> int:
        settings = get_settings()
        return settings.EMBEDDING_DIM
    
    @property
    def index_nlist(self) -> int:
        return 128
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="memory_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="session_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="importance_score", dtype=DataType.FLOAT),
            FieldSchema(name="access_count", dtype=DataType.INT64),
            FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=64),
        ]


class ArchivalMemorySchema(BaseCollectionSchema):
    """Schema for archival_memories collection."""
    
    @property
    def collection_name(self) -> str:
        return "archival_memories"
    
    @property
    def schema_version(self) -> int:
        return 1
    
    @property
    def description(self) -> str:
        return "Archival memories for long-term knowledge storage"
    
    @property
    def embedding_dim(self) -> int:
        settings = get_settings()
        return settings.EMBEDDING_DIM
    
    @property
    def index_nlist(self) -> int:
        return 128
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="memory_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="content_type", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="source_papers", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="tags", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="last_accessed", dtype=DataType.VARCHAR, max_length=64),
        ]


class CoreMemorySchema(BaseCollectionSchema):
    """Schema for core_memories collection."""
    
    @property
    def collection_name(self) -> str:
        return "core_memories"
    
    @property
    def schema_version(self) -> int:
        return 1
    
    @property
    def description(self) -> str:
        return "Core memory storage for user preferences"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def index_nlist(self) -> int:
        return 8
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="research_interests", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="preferred_domains", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="frequently_used_skills", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="language_preference", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="summary_style", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="custom_instructions", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
