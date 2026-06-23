from typing import List, Dict, Type
from .base import BaseTableSchema
from .bookmarks import BookmarkSchema
from .downloads import DownloadSchema
from .papers import PaperSchema, create_subject_paper_schema
from .date_index import DateIndexSchema, create_subject_date_index_schema
from .embedding_index import EmbeddingIndexSchema
from .paper_embeddings import PaperEmbeddingSchema
from .memorys import RecallMemorySchema, ArchivalMemorySchema, CoreMemorySchema, MemoryConfigSchema
from .conversation import ConversationMetaSchema
from .pdf_annotations import PdfAnnotationSchema, PdfReadingProgressSchema
from .followed_authors import FollowedAuthorSchema
from .author_rank import AuthorRankSchema, AuthorAnalysisStatsSchema
from .new_submissions import NewSubmissionsSchema, create_subject_new_submissions_schema
from .cross_submissions import CrossSubmissionsSchema, create_subject_cross_submissions_schema
from .replacement_submissions import ReplacementSubmissionsSchema, create_subject_replacement_submissions_schema
from .listings_date_index import ListingsDateIndexSchema, create_subject_listings_date_index_schema
from .paper_codes import PaperCodeSchema

from app.db.subject_utils import SUPPORTED_SUBJECTS, get_subject_table_name


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
    
    @classmethod
    def register_subject_schemas(cls) -> None:
        """Register subject-specific schemas for all supported subjects."""
        for subject in SUPPORTED_SUBJECTS:
            # Skip cs (default) - already registered with base schemas
            if subject == 'cs':
                continue
            
            # Register paper-related schemas
            cls.register(create_subject_paper_schema(subject))
            cls.register(create_subject_date_index_schema(subject))
            
            # Register listings-related schemas
            cls.register(create_subject_new_submissions_schema(subject))
            cls.register(create_subject_cross_submissions_schema(subject))
            cls.register(create_subject_replacement_submissions_schema(subject))
            cls.register(create_subject_listings_date_index_schema(subject))


# Register base schemas (for cs/default subject)
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

# Register subject-specific schemas
SchemaRegistry.register_subject_schemas()

