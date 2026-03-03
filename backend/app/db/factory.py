from app.config import get_settings


_bookmark_repo = None
_download_repo = None
_paper_repo = None
_paper_embedding_repo = None
_conversation_repo = None
_memory_repo = None


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
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _memory_repo


def reset_repositories():
    global _bookmark_repo, _download_repo, _paper_repo, _paper_embedding_repo, _conversation_repo, _memory_repo
    _bookmark_repo = None
    _download_repo = None
    _paper_repo = None
    _paper_embedding_repo = None
    _conversation_repo = None
    _memory_repo = None
