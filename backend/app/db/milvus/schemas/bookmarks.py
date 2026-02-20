from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class BookmarkSchema(BaseCollectionSchema):
    """Schema for bookmarks collection."""
    
    @property
    def collection_name(self) -> str:
        return "bookmarks"
    
    @property
    def schema_version(self) -> int:
        return 3
    
    @property
    def description(self) -> str:
        return "Bookmarked papers"
    
    @property
    def embedding_dim(self) -> int:
        return 1536
    
    @property
    def index_nlist(self) -> int:
        return 128
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="arxiv_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="authors", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="abstract", dtype=DataType.VARCHAR, max_length=16384),
            FieldSchema(name="comment", dtype=DataType.VARCHAR, max_length=4096),
            FieldSchema(name="journal_ref", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="doi", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="primary_category", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="categories", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="pdf_url", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="abs_url", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="published", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="updated", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
