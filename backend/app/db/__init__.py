from app.db.base import (
    BaseRepository,
    BookmarkRepository,
    DownloadRepository,
)
from app.db.factory import (
    get_bookmark_repository,
    get_download_repository,
    get_paper_repository,
    get_paper_embedding_repository,
    get_conversation_repository,
    get_memory_repository,
    reset_repositories,
)
from app.db.sqlite.bookmark_repo import SQLiteBookmarkRepository
from app.db.sqlite.download_repo import SQLiteDownloadRepository

__all__ = [
    "BaseRepository",
    "BookmarkRepository",
    "DownloadRepository",
    "get_bookmark_repository",
    "get_download_repository",
    "get_paper_repository",
    "get_paper_embedding_repository",
    "get_conversation_repository",
    "get_memory_repository",
    "reset_repositories",
    "SQLiteBookmarkRepository",
    "SQLiteDownloadRepository",
]

_LAZY_EXPORTS = {
    "SQLitePaperRepository": "app.db.sqlite.paper_repo:SQLitePaperRepository",
    "SQLitePaperEmbeddingRepository": "app.db.sqlite.paper_embedding_repo:SQLitePaperEmbeddingRepository",
    "SQLiteMemoryRepository": "app.db.sqlite.memory_repo:SQLiteMemoryRepository",
    "SQLiteConversationRepository": "app.db.sqlite.conversation_repo:SQLiteConversationRepository",
    "LanceDBClient": "app.db.lancedb.client:LanceDBClient",
    "LanceDBBookmarkRepository": "app.db.lancedb.bookmark_repo:LanceDBBookmarkRepository",
    "LanceDBDownloadRepository": "app.db.lancedb.download_repo:LanceDBDownloadRepository",
    "LanceDBPaperRepository": "app.db.lancedb.paper_repo:LanceDBPaperRepository",
    "LanceDBPaperEmbeddingRepository": "app.db.lancedb.paper_embedding_repo:LanceDBPaperEmbeddingRepository",
    "LanceDBMemoryRepository": "app.db.lancedb.memory_repo:LanceDBMemoryRepository",
    "LanceDBConversationRepository": "app.db.lancedb.conversation_repo:LanceDBConversationRepository",
    "MilvusClient": "app.db.milvus.client:MilvusClient",
    "MilvusBookmarkRepository": "app.db.milvus.bookmark_repo:MilvusBookmarkRepository",
    "MilvusDownloadRepository": "app.db.milvus.download_repo:MilvusDownloadRepository",
    "MilvusPaperRepository": "app.db.milvus.paper_repo:MilvusPaperRepository",
    "MilvusPaperEmbeddingRepository": "app.db.milvus.paper_embedding_repo:MilvusPaperEmbeddingRepository",
    "MilvusMemoryRepository": "app.db.milvus.memory_repo:MilvusMemoryRepository",
    "MilvusConversationRepository": "app.db.milvus.conversation_repo:MilvusConversationRepository",
}

__all__.extend(_LAZY_EXPORTS.keys())


def __getattr__(name: str):
    if name in _LAZY_EXPORTS:
        module_path, class_name = _LAZY_EXPORTS[name].rsplit(":", 1)
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
