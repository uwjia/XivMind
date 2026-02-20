from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class DownloadSchema(BaseCollectionSchema):
    """Schema for downloads collection."""
    
    @property
    def collection_name(self) -> str:
        return "downloads"
    
    @property
    def schema_version(self) -> int:
        return 2
    
    @property
    def description(self) -> str:
        return "Download tasks"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def index_nlist(self) -> int:
        return 128
    
    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128),
            FieldSchema(name="arxiv_id", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="pdf_url", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="status", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="progress", dtype=DataType.INT64),
            FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="file_size", dtype=DataType.INT64),
            FieldSchema(name="error_message", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
