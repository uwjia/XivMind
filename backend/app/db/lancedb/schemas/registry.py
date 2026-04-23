from typing import List, Dict, Type
from .base import BaseTableSchema
from .bookmarks import BookmarkSchema
from .downloads import DownloadSchema
from .papers import PaperSchema
from .date_index import DateIndexSchema
from .embedding_index import EmbeddingIndexSchema
from .paper_embeddings import PaperEmbeddingSchema
from .memorys import RecallMemorySchema, ArchivalMemorySchema, CoreMemorySchema, MemoryConfigSchema
from .conversation import ConversationMetaSchema
from .pdf_annotations import PdfAnnotationSchema, PdfReadingProgressSchema
from .followed_authors import FollowedAuthorSchema
from .author_rank import AuthorRankSchema, AuthorAnalysisStatsSchema
from .new_submissions import NewSubmissionsSchema
from .cross_submissions import CrossSubmissionsSchema
from .replacement_submissions import ReplacementSubmissionsSchema
from .listings_date_index import ListingsDateIndexSchema
from .paper_codes import PaperCodeSchema


class SchemaRegistry:
    """Registry for LanceDB table schemas."""
    
    _schemas: Dict[str, BaseTableSchema] = {}
    
    @classmethod
    def register(cls, schema: BaseTableSchema) -> None:
        """Register a schema."""
        cls._schemas[schema.table_name] = schema
    
    @classmethod
    def get(cls, table_name: str) -> BaseTableSchema:
        """Get a schema by table name."""
        if table_name not in cls._schemas:
            raise ValueError(f"Schema for table '{table_name}' not found")
        return cls._schemas[table_name]
    
    @classmethod
    def get_all(cls) -> List[BaseTableSchema]:
        """Get all registered schemas."""
        return list(cls._schemas.values())
    
    @classmethod
    def get_all_names(cls) -> List[str]:
        """Get all registered table names."""
        return list(cls._schemas.keys())


SchemaRegistry.register(BookmarkSchema())
SchemaRegistry.register(DownloadSchema())
SchemaRegistry.register(PaperSchema())
SchemaRegistry.register(DateIndexSchema())
SchemaRegistry.register(EmbeddingIndexSchema())
SchemaRegistry.register(PaperEmbeddingSchema())
SchemaRegistry.register(RecallMemorySchema())
SchemaRegistry.register(ArchivalMemorySchema())
SchemaRegistry.register(CoreMemorySchema())
SchemaRegistry.register(MemoryConfigSchema())
SchemaRegistry.register(ConversationMetaSchema())
SchemaRegistry.register(PdfAnnotationSchema())
SchemaRegistry.register(PdfReadingProgressSchema())
SchemaRegistry.register(FollowedAuthorSchema())
SchemaRegistry.register(AuthorRankSchema())
SchemaRegistry.register(AuthorAnalysisStatsSchema())
SchemaRegistry.register(NewSubmissionsSchema())
SchemaRegistry.register(CrossSubmissionsSchema())
SchemaRegistry.register(ReplacementSubmissionsSchema())
SchemaRegistry.register(ListingsDateIndexSchema())
SchemaRegistry.register(PaperCodeSchema())

