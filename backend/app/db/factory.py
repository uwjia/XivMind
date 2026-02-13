from app.db.base import BookmarkRepository, DownloadRepository
from app.db.milvus.bookmark_repo import MilvusBookmarkRepository
from app.db.milvus.download_repo import MilvusDownloadRepository
from app.db.sqlite.bookmark_repo import SQLiteBookmarkRepository
from app.db.sqlite.download_repo import SQLiteDownloadRepository
from app.config import get_settings


_bookmark_repo: BookmarkRepository | None = None
_download_repo: DownloadRepository | None = None


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


def reset_repositories():
    global _bookmark_repo, _download_repo
    _bookmark_repo = None
    _download_repo = None
