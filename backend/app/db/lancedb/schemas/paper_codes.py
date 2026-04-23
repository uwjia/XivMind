from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class PaperCodeSchema(BaseTableSchema):
    """Schema for paper_codes table - stores code repository links."""
    
    @property
    def table_name(self) -> str:
        return "paper_codes"
    
    @property
    def description(self) -> str:
        return "Paper code repository links"
    
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
            pa.field("url", pa.string()),
            pa.field("platform", pa.string()),
            pa.field("owner", pa.string()),
            pa.field("repo", pa.string()),
            pa.field("is_official", pa.bool_()),
            pa.field("stars", pa.int64()),
            pa.field("language", pa.string()),
            pa.field("fetched_at", pa.string()),
        ]
