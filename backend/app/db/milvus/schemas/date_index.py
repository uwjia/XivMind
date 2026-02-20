from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class DateIndexSchema(BaseCollectionSchema):
    """Schema for date_index collection."""
    
    @property
    def collection_name(self) -> str:
        return "date_index"
    
    @property
    def schema_version(self) -> int:
        return 1
    
    @property
    def description(self) -> str:
        return "Date Index"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def index_nlist(self) -> int:
        return 8
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="date", dtype=DataType.VARCHAR, max_length=32, is_primary=True),
            FieldSchema(name="total_count", dtype=DataType.INT64),
            FieldSchema(name="fetched_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
