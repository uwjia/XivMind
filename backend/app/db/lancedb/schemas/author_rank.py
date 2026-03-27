from typing import List
import pyarrow as pa
from .base import BaseTableSchema


class AuthorRankSchema(BaseTableSchema):
    """Schema for author_ranks table."""
    
    @property
    def table_name(self) -> str:
        return "author_ranks"
    
    @property
    def description(self) -> str:
        return "Author ranking data with network metrics"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def primary_key(self) -> str:
        return "author_id"
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("author_id", pa.string()),
            pa.field("name", pa.string()),
            pa.field("paper_count", pa.int64()),
            pa.field("pagerank", pa.float64()),
            pa.field("degree_centrality", pa.float64()),
            pa.field("betweenness_centrality", pa.float64()),
            pa.field("clustering_coeff", pa.float64()),
            pa.field("primary_category", pa.string()),
            pa.field("first_year", pa.int64()),
            pa.field("latest_year", pa.int64()),
            pa.field("collaborator_count", pa.int64()),
            pa.field("calculated_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]


class AuthorAnalysisStatsSchema(BaseTableSchema):
    """Schema for author_analysis_stats table."""
    
    @property
    def table_name(self) -> str:
        return "author_analysis_stats"
    
    @property
    def description(self) -> str:
        return "Author analysis statistics and metadata"
    
    @property
    def embedding_dim(self) -> int:
        return 8
    
    @property
    def primary_key(self) -> str:
        return "key"
    
    def get_fields(self) -> List[pa.Field]:
        return [
            pa.field("key", pa.string()),
            pa.field("value", pa.string()),
            pa.field("updated_at", pa.string()),
            pa.field("embedding", pa.list_(pa.float32())),
        ]
