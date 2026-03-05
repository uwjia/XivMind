from typing import List
import pyarrow as pa
from .base import BaseTableSchema
from app.config import get_settings


class PaperEmbeddingSchema(BaseTableSchema):
    """Schema for paper_embeddings table."""
    
    @property
    def table_name(self) -> str:
        return "paper_embeddings"
    
    @property
    def description(self) -> str:
        return "Paper embeddings for semantic search"
    
    @property
    def embedding_dim(self) -> int:
        settings = get_settings()
        return settings.EMBEDDING_DIM
    
    def get_fields(self) -> List[pa.Field]:
        dim = self.embedding_dim
        return [
            pa.field("paper_id", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), dim)),
            pa.field("embedding_model", pa.string()),
            pa.field("created_at", pa.string()),
        ]
