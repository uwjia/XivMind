from typing import List
import pyarrow as pa
from .base import BaseTableSchema
from app.config import get_settings


class RecallMemorySchema(BaseTableSchema):
    """Schema for recall_memories table."""
    
    @property
    def table_name(self) -> str:
        return "recall_memories"
    
    @property
    def description(self) -> str:
        return "Recall memories for conversation history with semantic search"
    
    @property
    def embedding_dim(self) -> int:
        settings = get_settings()
        return settings.EMBEDDING_DIM
    
    def get_fields(self) -> List[pa.Field]:
        dim = self.embedding_dim
        return [
            pa.field("memory_id", pa.string()),
            pa.field("user_id", pa.string()),
            pa.field("session_id", pa.string()),
            pa.field("content", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), dim)),
            pa.field("importance_score", pa.float32()),
            pa.field("access_count", pa.int64()),
            pa.field("timestamp", pa.string()),
            pa.field("category", pa.string()),
            pa.field("auto_created", pa.bool_()),
            pa.field("ttl_days", pa.int64()),
            pa.field("metadata", pa.string()),
        ]


class ArchivalMemorySchema(BaseTableSchema):
    """Schema for archival_memories table."""
    
    @property
    def table_name(self) -> str:
        return "archival_memories"
    
    @property
    def description(self) -> str:
        return "Archival memories for long-term knowledge storage"
    
    @property
    def embedding_dim(self) -> int:
        settings = get_settings()
        return settings.EMBEDDING_DIM
    
    def get_fields(self) -> List[pa.Field]:
        dim = self.embedding_dim
        return [
            pa.field("memory_id", pa.string()),
            pa.field("user_id", pa.string()),
            pa.field("content_type", pa.string()),
            pa.field("title", pa.string()),
            pa.field("content", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), dim)),
            pa.field("source_papers", pa.string()),
            pa.field("tags", pa.string()),
            pa.field("created_at", pa.string()),
            pa.field("last_accessed", pa.string()),
        ]


class CoreMemorySchema(BaseTableSchema):
    """Schema for core_memories table."""
    
    @property
    def table_name(self) -> str:
        return "core_memories"
    
    @property
    def description(self) -> str:
        return "Core memory storage for user preferences"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("user_id", pa.string()),
            pa.field("research_interests", pa.string()),
            pa.field("preferred_domains", pa.string()),
            pa.field("frequently_used_skills", pa.string()),
            pa.field("language_preference", pa.string()),
            pa.field("summary_style", pa.string()),
            pa.field("custom_instructions", pa.string()),
            pa.field("created_at", pa.string()),
            pa.field("updated_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), 8)),
        ]


class MemoryConfigSchema(BaseTableSchema):
    """Schema for memory_config table."""
    
    @property
    def table_name(self) -> str:
        return "memory_config"
    
    @property
    def description(self) -> str:
        return "Memory configuration storage"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("user_id", pa.string()),
            pa.field("auto_capture", pa.bool_()),
            pa.field("auto_recall", pa.bool_()),
            pa.field("capture_max_chars", pa.int64()),
            pa.field("recall_top_k", pa.int64()),
            pa.field("recall_min_score", pa.float32()),
            pa.field("auto_forget_days", pa.int64()),
            pa.field("importance_threshold", pa.float32()),
            pa.field("extract", pa.bool_()),
            pa.field("embedding", pa.list_(pa.float32(), 8)),
        ]
