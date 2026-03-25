from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class FollowedAuthorSchema(BaseCollectionSchema):
    """Schema for followed_authors collection."""
    
    @property
    def collection_name(self) -> str:
        return "followed_authors"
    
    @property
    def schema_version(self) -> int:
        return 1
    
    @property
    def description(self) -> str:
        return "Followed authors"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def index_nlist(self) -> int:
        return 8
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="author_name", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="paper_count", dtype=DataType.INT64),
            FieldSchema(name="latest_published", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="notes", dtype=DataType.VARCHAR, max_length=2048),
            FieldSchema(name="followed_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
