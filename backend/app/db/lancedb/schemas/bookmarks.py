from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class BookmarkSchema(BaseTableSchema):
    """Schema for bookmarks table."""
    
    @property
    def table_name(self) -> str:
        return "bookmarks"
    
    @property
    def description(self) -> str:
        return "Bookmarked papers"
    
    @property
    def embedding_dim(self) -> int:
        return 1536
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("id", pa.string()),
            pa.field("paper_id", pa.string()),
            pa.field("arxiv_id", pa.string()),
            pa.field("title", pa.string()),
            pa.field("authors", pa.string()),
            pa.field("abstract", pa.string()),
            pa.field("comment", pa.string()),
            pa.field("journal_ref", pa.string()),
            pa.field("doi", pa.string()),
            pa.field("primary_category", pa.string()),
            pa.field("categories", pa.string()),
            pa.field("pdf_url", pa.string()),
            pa.field("abs_url", pa.string()),
            pa.field("published", pa.string()),
            pa.field("updated", pa.string()),
            pa.field("created_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
