from app.db.base import BookmarkRepository
from app.db.factory import get_bookmark_repository
from typing import Dict, List, Optional, Tuple, Any


class BookmarkService:
    def __init__(self, repository: Optional[BookmarkRepository] = None):
        self._repository = repository or get_bookmark_repository()

    def add_bookmark(self, bookmark_data: Dict[str, Any]) -> Dict[str, Any]:
        return self._repository.add(bookmark_data)

    def remove_bookmark(self, paper_id: str) -> bool:
        return self._repository.remove(paper_id)

    def is_bookmarked(self, paper_id: str) -> bool:
        return self._repository.is_bookmarked(paper_id)

    def get_all_bookmarks(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        return self._repository.get_all(limit, offset)

    def search_bookmarks(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self._repository.search(query, limit)

    def get_bookmark(self, paper_id: str) -> Optional[Dict[str, Any]]:
        return self._repository.get_by_paper_id(paper_id)


bookmark_service = BookmarkService()
