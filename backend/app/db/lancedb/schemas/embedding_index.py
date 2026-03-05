from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class EmbeddingIndexSchema(BaseTableSchema):
    """Schema for embedding_index table."""
    
    @property
    def table_name(self) -> str:
        return "embedding_index"
    
    @property
    def description(self) -> str:
        return "Embedding index for papers"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("date", pa.string()),
            pa.field("total_count", pa.int64()),
            pa.field("generated_at", pa.string()),
            pa.field("model_name", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
