from app.config import get_settings


_bookmark_repo = None
_download_repo = None
_paper_repo = None
_paper_embedding_repo = None
_conversation_repo = None
_memory_repo = None
_pdf_annotation_repo = None
_followed_author_repo = None
_author_rank_repo = None
_paper_reader = None


def get_paper_reader():
    """Get paper reader instance based on database type."""
    global _paper_reader
    if _paper_reader is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.paper_reader import SQLitePaperReader
            _paper_reader = SQLitePaperReader()
        elif db_type == "milvus":
            from app.db.milvus.paper_reader import MilvusPaperReader
            _paper_reader = MilvusPaperReader()
        elif db_type == "lancedb":
            from app.db.lancedb.paper_reader import LanceDBPaperReader
            _paper_reader = LanceDBPaperReader()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _paper_reader


def get_bookmark_repository():
    global _bookmark_repo
    if _bookmark_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.bookmark_repo import SQLiteBookmarkRepository
            _bookmark_repo = SQLiteBookmarkRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            from app.db.milvus.bookmark_repo import MilvusBookmarkRepository
            _bookmark_repo = MilvusBookmarkRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.bookmark_repo import LanceDBBookmarkRepository
            _bookmark_repo = LanceDBBookmarkRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _bookmark_repo


def get_download_repository():
    global _download_repo
    if _download_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.download_repo import SQLiteDownloadRepository
            _download_repo = SQLiteDownloadRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            from app.db.milvus.download_repo import MilvusDownloadRepository
            _download_repo = MilvusDownloadRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.download_repo import LanceDBDownloadRepository
            _download_repo = LanceDBDownloadRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _download_repo


def get_paper_repository():
    global _paper_repo
    if _paper_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.paper_repo import SQLitePaperRepository
            _paper_repo = SQLitePaperRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            from app.db.milvus.paper_repo import MilvusPaperRepository
            _paper_repo = MilvusPaperRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.paper_repo import LanceDBPaperRepository
            _paper_repo = LanceDBPaperRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _paper_repo


def get_paper_embedding_repository():
    global _paper_embedding_repo
    if _paper_embedding_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.paper_embedding_repo import SQLitePaperEmbeddingRepository
            _paper_embedding_repo = SQLitePaperEmbeddingRepository()
        elif db_type == "milvus":
            from app.db.milvus.paper_embedding_repo import MilvusPaperEmbeddingRepository
            _paper_embedding_repo = MilvusPaperEmbeddingRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.paper_embedding_repo import LanceDBPaperEmbeddingRepository
            _paper_embedding_repo = LanceDBPaperEmbeddingRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _paper_embedding_repo


def get_conversation_repository():
    global _conversation_repo
    if _conversation_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.conversation_repo import SQLiteConversationRepository
            _conversation_repo = SQLiteConversationRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            from app.db.milvus.conversation_repo import MilvusConversationRepository
            _conversation_repo = MilvusConversationRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.conversation_repo import LanceDBConversationRepository
            _conversation_repo = LanceDBConversationRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _conversation_repo


def get_memory_repository():
    global _memory_repo
    if _memory_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.memory_repo import SQLiteMemoryRepository
            _memory_repo = SQLiteMemoryRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            from app.db.milvus.memory_repo import MilvusMemoryRepository
            _memory_repo = MilvusMemoryRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.memory_repo import LanceDBMemoryRepository
            _memory_repo = LanceDBMemoryRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _memory_repo


def get_pdf_annotation_repository():
    global _pdf_annotation_repo
    if _pdf_annotation_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.pdf_annotation_repo import SQLitePdfAnnotationRepository
            _pdf_annotation_repo = SQLitePdfAnnotationRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            from app.db.milvus.pdf_annotation_repo import MilvusPdfAnnotationRepository
            _pdf_annotation_repo = MilvusPdfAnnotationRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.pdf_annotation_repo import LanceDBPdfAnnotationRepository
            _pdf_annotation_repo = LanceDBPdfAnnotationRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _pdf_annotation_repo


def get_followed_author_repository():
    global _followed_author_repo
    if _followed_author_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.followed_author_repo import SQLiteFollowedAuthorRepository
            _followed_author_repo = SQLiteFollowedAuthorRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            from app.db.milvus.followed_author_repo import MilvusFollowedAuthorRepository
            _followed_author_repo = MilvusFollowedAuthorRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.followed_author_repo import LanceDBFollowedAuthorRepository
            _followed_author_repo = LanceDBFollowedAuthorRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _followed_author_repo


def get_author_rank_repository():
    global _author_rank_repo
    if _author_rank_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            from app.db.sqlite.author_rank_repo import SQLiteAuthorRankRepository
            _author_rank_repo = SQLiteAuthorRankRepository()
        elif db_type == "milvus":
            from app.db.milvus.author_rank_repo import MilvusAuthorRankRepository
            _author_rank_repo = MilvusAuthorRankRepository()
        elif db_type == "lancedb":
            from app.db.lancedb.author_rank_repo import LanceDBAuthorRankRepository
            _author_rank_repo = LanceDBAuthorRankRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _author_rank_repo


def reset_repositories():
    global _bookmark_repo, _download_repo, _paper_repo, _paper_embedding_repo, _conversation_repo, _memory_repo, _pdf_annotation_repo, _followed_author_repo, _author_rank_repo, _paper_reader
    _bookmark_repo = None
    _download_repo = None
    _paper_repo = None
    _paper_embedding_repo = None
    _conversation_repo = None
    _memory_repo = None
    _pdf_annotation_repo = None
    _followed_author_repo = None
    _author_rank_repo = None
    _paper_reader = None
