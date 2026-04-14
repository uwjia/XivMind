from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class ListingsDateIndexSchema(BaseTableSchema):
    """Schema for listings_date_index table."""
    
    @property
    def table_name(self) -> str:
        return "listings_date_index"
    
    @property
    def description(self) -> str:
        return "Date index for arXiv new listings"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def primary_key(self) -> str:
        return "date"
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("date", pa.string()),
            pa.field("new_count", pa.int64()),
            pa.field("cross_count", pa.int64()),
            pa.field("replacement_count", pa.int64()),
            pa.field("fetched_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
