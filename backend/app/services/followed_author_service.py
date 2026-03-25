import logging
from typing import Dict, List, Tuple, Any, Optional

from app.db.base import FollowedAuthorRepository
from app.db.factory import get_followed_author_repository

logger = logging.getLogger(__name__)


class FollowedAuthorService:
    def __init__(self, repo: FollowedAuthorRepository = None):
        self.repo = repo or get_followed_author_repository()
        self._paper_service = None

    @property
    def paper_service(self):
        if self._paper_service is None:
            from app.services.paper_service import PaperService
            self._paper_service = PaperService()
        return self._paper_service

    def _get_author_paper_info(self, author_name: str) -> Tuple[int, Optional[str]]:
        """
        Query author's paper count and latest published date.
        
        Returns:
            Tuple of (paper_count, latest_published)
        """
        try:
            result = self.paper_service.query_papers_by_author(
                author=author_name,
                start=0,
                max_results=1
            )
            total = result.get("total", 0)
            papers = result.get("papers", [])
            
            latest_published = None
            if papers and len(papers) > 0:
                latest_published = papers[0].get("published")
            
            return total, latest_published
        except Exception as e:
            logger.warning(f"Failed to get author paper info for {author_name}: {e}")
            return 0, None

    def follow_author(
        self,
        author_name: str,
        paper_count: int = None,
        latest_published: str = None,
        notes: str = None,
        auto_fetch: bool = True,
    ) -> Dict[str, Any]:
        if self.repo.is_followed(author_name):
            existing = self.repo.get_by_author_name(author_name)
            if paper_count is not None or latest_published is not None:
                self.repo.update_paper_info(author_name, paper_count or 0, latest_published or "")
            return existing
        
        if auto_fetch and (paper_count is None or latest_published is None):
            fetched_count, fetched_date = self._get_author_paper_info(author_name)
            if paper_count is None:
                paper_count = fetched_count
            if latest_published is None:
                latest_published = fetched_date
        
        data = {
            "author_name": author_name,
            "paper_count": paper_count or 0,
            "latest_published": latest_published,
            "notes": notes,
        }
        return self.repo.add(data)

    def unfollow_author(self, author_name: str) -> bool:
        existing = self.repo.get_by_author_name(author_name)
        if not existing:
            return False
        return self.repo.remove(existing["id"])

    def is_followed(self, author_name: str) -> bool:
        return self.repo.is_followed(author_name)

    def get_all_followed(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        return self.repo.get_all(limit, offset)

    def get_by_author_name(self, author_name: str) -> Optional[Dict[str, Any]]:
        return self.repo.get_by_author_name(author_name)

    def update_notes(self, author_name: str, notes: str) -> bool:
        return self.repo.update_notes(author_name, notes)

    def update_paper_info(self, author_name: str, paper_count: int, latest_published: str) -> bool:
        return self.repo.update_paper_info(author_name, paper_count, latest_published)
