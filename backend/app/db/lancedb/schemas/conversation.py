from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class ConversationMetaSchema(BaseTableSchema):
    """Schema for conversation_meta table."""
    
    @property
    def table_name(self) -> str:
        return "conversation_meta"
    
    @property
    def description(self) -> str:
        return "Conversation metadata storage"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("session_id", pa.string()),
            pa.field("user_id", pa.string()),
            pa.field("title", pa.string()),
            pa.field("mode", pa.string()),
            pa.field("starred", pa.bool_()),
            pa.field("pinned", pa.bool_()),
            pa.field("created_at", pa.string()),
            pa.field("updated_at", pa.string()),
            pa.field("message_count", pa.int64()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
