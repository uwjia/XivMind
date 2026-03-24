from typing import List
from pymilvus import FieldSchema, DataType
from .base import BaseCollectionSchema


class PdfAnnotationSchema(BaseCollectionSchema):
    """Schema for pdf_annotations collection."""

    @property
    def collection_name(self) -> str:
        return "pdf_annotations"

    @property
    def schema_version(self) -> int:
        return 2

    @property
    def description(self) -> str:
        return "PDF annotations"

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
            FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="page_number", dtype=DataType.INT64),
            FieldSchema(name="position", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=8192),
            FieldSchema(name="color", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="stroke_width", dtype=DataType.INT64),
            FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]


class PdfReadingProgressSchema(BaseCollectionSchema):
    """Schema for pdf_reading_progress collection."""

    @property
    def collection_name(self) -> str:
        return "pdf_reading_progress"

    @property
    def schema_version(self) -> int:
        return 1

    @property
    def description(self) -> str:
        return "PDF reading progress"

    @property
    def embedding_dim(self) -> int:
        return 1536

    @property
    def index_nlist(self) -> int:
        return 128

    def get_fields(self) -> List[FieldSchema]:
        return [
            FieldSchema(name="paper_id", dtype=DataType.VARCHAR, max_length=128, is_primary=True),
            FieldSchema(name="current_page", dtype=DataType.INT64),
            FieldSchema(name="total_pages", dtype=DataType.INT64),
            FieldSchema(name="zoom_level", dtype=DataType.FLOAT),
            FieldSchema(name="view_mode", dtype=DataType.VARCHAR, max_length=32),
            FieldSchema(name="last_read_at", dtype=DataType.VARCHAR, max_length=64),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
        ]
