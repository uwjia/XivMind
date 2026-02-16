from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any


class BaseRepository(ABC):
    """Abstract base class for all repositories."""

    @abstractmethod
    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new record."""
        pass

    @abstractmethod
    def remove(self, id: str) -> bool:
        """Remove a record by ID."""
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        """Get a record by ID."""
        pass

    @abstractmethod
    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """Get all records with pagination."""
        pass

    @abstractmethod
    def exists(self, id: str) -> bool:
        """Check if a record exists."""
        pass


class BookmarkRepository(BaseRepository):
    """Abstract repository for bookmarks."""

    @abstractmethod
    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get bookmark by paper ID."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search bookmarks by query."""
        pass

    @abstractmethod
    def is_bookmarked(self, paper_id: str) -> bool:
        """Check if paper is bookmarked."""
        pass


class DownloadRepository(BaseRepository):
    """Abstract repository for download tasks."""

    @abstractmethod
    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get download task by paper ID."""
        pass

    @abstractmethod
    def get_all_by_paper_id(self, paper_id: str) -> List[Dict[str, Any]]:
        """Get all download tasks by paper ID."""
        pass

    @abstractmethod
    def update_status(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        file_path: Optional[str] = None,
        file_size: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update download task status."""
        pass

    @abstractmethod
    def reset_incomplete_tasks(self) -> int:
        """Reset all incomplete tasks to failed status."""
        pass


class PaperRepository(BaseRepository):
    """Abstract repository for papers."""

    @abstractmethod
    def insert_paper(self, data: Dict[str, Any]) -> None:
        """Insert a single paper."""
        pass

    @abstractmethod
    def insert_papers_batch(self, papers: List[Dict[str, Any]]) -> int:
        """Insert multiple papers, return count of inserted papers."""
        pass

    @abstractmethod
    def get_date_index(self, date: str) -> Optional[Dict[str, Any]]:
        """Get date index by date string."""
        pass

    @abstractmethod
    def insert_date_index(self, date: str, total_count: int) -> None:
        """Insert or update date index."""
        pass

    @abstractmethod
    def query_papers_by_date(
        self,
        date: str,
        category: Optional[str] = None,
        start: int = 0,
        max_results: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Query papers by date with optional category filter."""
        pass

    @abstractmethod
    def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get paper by ID."""
        pass

    @abstractmethod
    def delete_date_index(self, date: str) -> None:
        """Delete date index by date."""
        pass

    @abstractmethod
    def delete_all_date_index(self) -> None:
        """Delete all date indexes."""
        pass

    @abstractmethod
    def get_all_date_indexes(self) -> List[Dict[str, Any]]:
        """Get all date indexes."""
        pass

    @abstractmethod
    def get_total_paper_count(self) -> int:
        """Get total count of papers."""
        pass
