from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class PaperCodeSchema(BaseCollectionSchema):
    """Schema for paper_codes collection."""
    
    @property
    def collection_name(self) -> str:
        return "paper_codes"
    
    @property
    def schema_version(self) -> int:
        return 1
    
    @property
    def description(self) -> str:
        return "Paper code repository links"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def index_nlist(self) -> int:
        return 128
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=128, is_primary=True),
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="platform", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="owner", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="repo", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="is_official", dtype=DataType.BOOL),
            FieldSchema(name="stars", dtype=DataType.INT64),
            FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="fetched_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
