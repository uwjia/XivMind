from typing import List
import pyarrow as pa
from .base import BaseTableSchema

from app.db.subject_utils import get_subject_table_name


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


class SubjectListingsDateIndexSchema(BaseTableSchema):
    """Schema for subject-specific listings_date_index table."""
    
    def __init__(self, subject: str):
        self._subject = subject
        self._table_name = get_subject_table_name("listings_date_index", subject)
    
    @property
    def table_name(self) -> str:
        return self._table_name
    
    @property
    def description(self) -> str:
        return f"Date index for {self._subject} arXiv listings"
    
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


def create_subject_listings_date_index_schema(subject: str) -> SubjectListingsDateIndexSchema:
    """Create a subject-specific listings date index schema."""
    return SubjectListingsDateIndexSchema(subject)
