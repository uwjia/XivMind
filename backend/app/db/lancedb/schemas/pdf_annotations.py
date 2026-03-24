from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class PdfAnnotationSchema(BaseTableSchema):
    """Schema for pdf_annotations table."""

    @property
    def table_name(self) -> str:
        return "pdf_annotations"

    @property
    def description(self) -> str:
        return "PDF annotations"

    @property
    def embedding_dim(self) -> int:
        return 8

    @property
    def primary_key(self) -> str:
        return "id"

    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("id", pa.string()),
            pa.field("paper_id", pa.string()),
            pa.field("type", pa.string()),
            pa.field("page_number", pa.int64()),
            pa.field("position", pa.string()),
            pa.field("content", pa.string()),
            pa.field("color", pa.string()),
            pa.field("stroke_width", pa.int64()),
            pa.field("created_at", pa.string()),
            pa.field("updated_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]


class PdfReadingProgressSchema(BaseTableSchema):
    """Schema for pdf_reading_progress table."""

    @property
    def table_name(self) -> str:
        return "pdf_reading_progress"

    @property
    def description(self) -> str:
        return "PDF reading progress"

    @property
    def embedding_dim(self) -> int:
        return 8

    @property
    def primary_key(self) -> str:
        return "paper_id"

    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("paper_id", pa.string()),
            pa.field("current_page", pa.int64()),
            pa.field("total_pages", pa.int64()),
            pa.field("zoom_level", pa.float64()),
            pa.field("view_mode", pa.string()),
            pa.field("last_read_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
