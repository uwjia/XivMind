from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class ConversationMetaSchema(BaseCollectionSchema):
    """Schema for conversation_meta collection."""
    
    @property
    def collection_name(self) -> str:
        return "conversation_meta"
    
    @property
    def schema_version(self) -> int:
        return 1
    
    @property
    def description(self) -> str:
        return "Conversation metadata storage"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def index_nlist(self) -> int:
        return 8
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="session_id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="mode", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="starred", dtype=DataType.BOOL),
            FieldSchema(name="pinned", dtype=DataType.BOOL),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="message_count", dtype=DataType.INT64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
