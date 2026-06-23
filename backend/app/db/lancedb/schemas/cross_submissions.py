from typing import List
import pyarrow as pa
from .base import BaseTableSchema

from app.db.subject_utils import get_subject_table_name


class CrossSubmissionsSchema(BaseTableSchema):
    """Schema for cross_submissions table."""
    
    @property
    def table_name(self) -> str:
        return "cross_submissions"
    
    @property
    def description(self) -> str:
        return "Cross submissions from arXiv listings"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def primary_key(self) -> str:
        return "id"
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("id", pa.string()),
            pa.field("title", pa.string()),
            pa.field("abstract", pa.string()),
            pa.field("authors", pa.string()),
            pa.field("primary_category", pa.string()),
            pa.field("categories", pa.string()),
            pa.field("published", pa.string()),
            pa.field("updated", pa.string()),
            pa.field("pdf_url", pa.string()),
            pa.field("abs_url", pa.string()),
            pa.field("comment", pa.string()),
            pa.field("journal_ref", pa.string()),
            pa.field("doi", pa.string()),
            pa.field("fetched_at", pa.string()),
            pa.field("listing_date", pa.string()),
            pa.field("embedding", pa.list_(pa.float32()))
        ]


class SubjectCrossSubmissionsSchema(BaseTableSchema):
    """Schema for subject-specific cross_submissions table."""
    
    def __init__(self, subject: str):
        self._subject = subject
        self._table_name = get_subject_table_name("cross_submissions", subject)
    
    @property
    def table_name(self) -> str:
        return self._table_name
    
    @property
    def description(self) -> str:
        return f"Cross submissions for {self._subject} from arXiv listings"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def primary_key(self) -> str:
        return "id"
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("id", pa.string()),
            pa.field("title", pa.string()),
            pa.field("abstract", pa.string()),
            pa.field("authors", pa.string()),
            pa.field("primary_category", pa.string()),
            pa.field("categories", pa.string()),
            pa.field("published", pa.string()),
            pa.field("updated", pa.string()),
            pa.field("pdf_url", pa.string()),
            pa.field("abs_url", pa.string()),
            pa.field("comment", pa.string()),
            pa.field("journal_ref", pa.string()),
            pa.field("doi", pa.string()),
            pa.field("fetched_at", pa.string()),
            pa.field("listing_date", pa.string()),
            pa.field("embedding", pa.list_(pa.float32()))
        ]


def create_subject_cross_submissions_schema(subject: str) -> SubjectCrossSubmissionsSchema:
    """Create a subject-specific cross submissions schema."""
    return SubjectCrossSubmissionsSchema(subject)
