from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class DateIndexSchema(BaseTableSchema):
    """Schema for date_index table."""
    
    @property
    def table_name(self) -> str:
        return "date_index"
    
    @property
    def description(self) -> str:
        return "Date index for papers"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def primary_key(self) -> str:
        return "date"
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("date", pa.string()),
            pa.field("total_count", pa.int64()),
            pa.field("fetched_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
