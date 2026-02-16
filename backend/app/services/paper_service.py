import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import re

from app.db.factory import get_paper_repository
from app.services.arxiv_client import ArxivClient

logger = logging.getLogger(__name__)


class PaperService:
    def __init__(self):
        self.paper_repo = get_paper_repository()
        self.arxiv_client = ArxivClient()

    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize various date formats to YYYY-MM-DD.
        
        Supported formats:
        - YYYY-MM-DD (e.g., '2026-02-10')
        - YYYYMMDDHHMMSS (e.g., '20260210000000')
        - YYYYMMDD (e.g., '20260210')
        """
        date_str = date_str.strip()
        
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        if re.match(r'^\d{8}', date_str):
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        
        raise ValueError(f"Unsupported date format: {date_str}")

    def _is_future_date(self, date_str: str) -> bool:
        """Check if the given date is in the future."""
        try:
            normalized = self._normalize_date(date_str)
            request_date = datetime.strptime(normalized, "%Y-%m-%d").date()
            today = datetime.now(timezone.utc).date()
            return request_date > today
        except ValueError:
            return False

    async def query_papers(
        self,
        date: str,
        category: Optional[str] = None,
        start: int = 0,
        max_results: int = 50
    ) -> Dict[str, Any]:
        """
        Query papers for a specific date.
        
        Strategy:
        1. Normalize the date format
        2. Check if the date is in the future (return empty result)
        3. Check if we have data for this date
        4. If not, fetch ALL papers for this date from arXiv
        5. Store all papers
        6. Filter by category and return with pagination
        """
        try:
            normalized_date = self._normalize_date(date)
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            return {
                "papers": [],
                "total": 0,
                "start": start,
                "max_results": max_results,
            }
        
        if self._is_future_date(normalized_date):
            logger.warning(f"Requested date {normalized_date} is in the future, returning empty result")
            return {
                "papers": [],
                "total": 0,
                "start": start,
                "max_results": max_results,
            }
        
        date_info = self.paper_repo.get_date_index(normalized_date)
        
        if not date_info or date_info.get("total_count", 0) == 0:
            logger.info(f"No local data for {normalized_date}, fetching from arXiv")
            try:
                papers = await self.arxiv_client.fetch_all_papers_for_date(normalized_date)
                
                if papers:
                    inserted = self.paper_repo.insert_papers_batch(papers)
                    logger.info(f"Inserted {inserted} papers for {normalized_date}")
                    
                    self.paper_repo.insert_date_index(normalized_date, len(papers))
                else:
                    self.paper_repo.insert_date_index(normalized_date, 0)
            except Exception as e:
                logger.warning(f"Failed to fetch papers from arXiv for {normalized_date}: {e}")
                self.paper_repo.insert_date_index(normalized_date, 0)
        
        papers, total = self.paper_repo.query_papers_by_date(
            date=normalized_date,
            category=category,
            start=start,
            max_results=max_results
        )
        
        return {
            "papers": papers,
            "total": total,
            "start": start,
            "max_results": max_results,
        }

    def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get a single paper by ID."""
        return self.paper_repo.get_paper_by_id(paper_id)

    def clear_date_index(self, date: str) -> None:
        """Clear date index for a specific date."""
        normalized_date = self._normalize_date(date)
        self.paper_repo.delete_date_index(normalized_date)

    def clear_all_date_index(self) -> None:
        """Clear all date index cache."""
        self.paper_repo.delete_all_date_index()

    async def fetch_papers_for_date(self, date: str) -> Dict[str, Any]:
        """
        Manually fetch and store papers for a specific date.
        Returns the result of the fetch operation.
        """
        try:
            normalized_date = self._normalize_date(date)
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            return {
                "success": False,
                "date": date,
                "count": 0,
                "error": str(e),
            }
        
        if self._is_future_date(normalized_date):
            return {
                "success": False,
                "date": normalized_date,
                "count": 0,
                "error": "Cannot fetch papers for future dates",
            }
        
        self.paper_repo.delete_date_index(normalized_date)
        
        try:
            logger.info(f"Manually fetching papers for {normalized_date}")
            papers = await self.arxiv_client.fetch_all_papers_for_date(normalized_date)
            
            if papers:
                inserted = self.paper_repo.insert_papers_batch(papers)
                logger.info(f"Inserted {inserted} papers for {normalized_date}")
                self.paper_repo.insert_date_index(normalized_date, len(papers))
                return {
                    "success": True,
                    "date": normalized_date,
                    "count": len(papers),
                }
            else:
                self.paper_repo.insert_date_index(normalized_date, 0)
                return {
                    "success": True,
                    "date": normalized_date,
                    "count": 0,
                }
        except Exception as e:
            logger.error(f"Failed to fetch papers for {normalized_date}: {e}")
            self.paper_repo.insert_date_index(normalized_date, 0)
            return {
                "success": False,
                "date": normalized_date,
                "count": 0,
                "error": str(e),
            }

    def get_all_date_indexes(self) -> List[Dict[str, Any]]:
        """Get all date index records."""
        return self.paper_repo.get_all_date_indexes()

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored papers."""
        indexes = self.paper_repo.get_all_date_indexes()
        total_days = len([i for i in indexes if i.get("total_count", 0) > 0])
        total_papers = self.paper_repo.get_total_paper_count()
        
        return {
            "total_days": total_days,
            "total_papers": total_papers,
            "indexes": indexes,
        }
