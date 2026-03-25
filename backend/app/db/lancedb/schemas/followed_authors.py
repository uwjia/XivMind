from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class FollowedAuthorSchema(BaseTableSchema):
    """Schema for followed_authors table."""
    
    @property
    def table_name(self) -> str:
        return "followed_authors"
    
    @property
    def description(self) -> str:
        return "Followed authors"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("id", pa.string()),
            pa.field("author_name", pa.string()),
            pa.field("paper_count", pa.int64()),
            pa.field("latest_published", pa.string()),
            pa.field("notes", pa.string()),
            pa.field("followed_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
