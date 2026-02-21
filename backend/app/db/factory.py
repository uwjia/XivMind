from app.db.base import BookmarkRepository, DownloadRepository, PaperRepository, PaperEmbeddingRepository
from app.db.milvus.bookmark_repo import MilvusBookmarkRepository
from app.db.milvus.download_repo import MilvusDownloadRepository
from app.db.milvus.paper_repo import MilvusPaperRepository
from app.db.milvus.paper_embedding_repo import MilvusPaperEmbeddingRepository
from app.db.sqlite.bookmark_repo import SQLiteBookmarkRepository
from app.db.sqlite.download_repo import SQLiteDownloadRepository
from app.db.sqlite.paper_repo import SQLitePaperRepository
from app.config import get_settings


_bookmark_repo: BookmarkRepository | None = None
_download_repo: DownloadRepository | None = None
_paper_repo: PaperRepository | None = None
_paper_embedding_repo: PaperEmbeddingRepository | None = None


def get_bookmark_repository() -> BookmarkRepository:
    global _bookmark_repo
    if _bookmark_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            _bookmark_repo = SQLiteBookmarkRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            _bookmark_repo = MilvusBookmarkRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _bookmark_repo


def get_download_repository() -> DownloadRepository:
    global _download_repo
    if _download_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            _download_repo = SQLiteDownloadRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            _download_repo = MilvusDownloadRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _download_repo


def get_paper_repository() -> PaperRepository:
    global _paper_repo
    if _paper_repo is None:
        settings = get_settings()
        db_type = settings.DATABASE_TYPE.lower()
        
        if db_type == "sqlite":
            _paper_repo = SQLitePaperRepository(settings.SQLITE_DB_PATH)
        elif db_type == "milvus":
            _paper_repo = MilvusPaperRepository()
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    return _paper_repo


def get_paper_embedding_repository() -> PaperEmbeddingRepository:
    global _paper_embedding_repo
    if _paper_embedding_repo is None:
        _paper_embedding_repo = MilvusPaperEmbeddingRepository()
    
    return _paper_embedding_repo


def reset_repositories():
    global _bookmark_repo, _download_repo, _paper_repo, _paper_embedding_repo
    _bookmark_repo = None
    _download_repo = None
    _paper_repo = None
    _paper_embedding_repo = None
