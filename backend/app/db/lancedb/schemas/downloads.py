from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class DownloadSchema(BaseTableSchema):
    """Schema for downloads table."""
    
    @property
    def table_name(self) -> str:
        return "downloads"
    
    @property
    def description(self) -> str:
        return "Download tasks"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("id", pa.string()),
            pa.field("paper_id", pa.string()),
            pa.field("arxiv_id", pa.string()),
            pa.field("title", pa.string()),
            pa.field("pdf_url", pa.string()),
            pa.field("status", pa.string()),
            pa.field("progress", pa.int64()),
            pa.field("file_path", pa.string()),
            pa.field("file_size", pa.int64()),
            pa.field("error_message", pa.string()),
            pa.field("created_at", pa.string()),
            pa.field("updated_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
