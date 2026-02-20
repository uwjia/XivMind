from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class PaperSchema(BaseCollectionSchema):
    """Schema for papers collection."""
    
    @property
    def collection_name(self) -> str:
        return "papers"
    
    @property
    def schema_version(self) -> int:
        return 3
    
    @property
    def description(self) -> str:
        return "Papers"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def index_nlist(self) -> int:
        return 128
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=128, is_primary=True),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="abstract", dtype=DataType.VARCHAR, max_length=32768),
            FieldSchema(name="authors", dtype=DataType.VARCHAR, max_length=16384),
            FieldSchema(name="primary_category", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="categories", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="published", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="updated", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="pdf_url", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="abs_url", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="comment", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="journal_ref", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="doi", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="fetched_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
