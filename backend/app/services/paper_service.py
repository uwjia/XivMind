import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import re

from app.config import get_settings
from app.db.factory import get_paper_repository, get_paper_embedding_repository
from app.db.subject_utils import DEFAULT_SUBJECT, SUPPORTED_SUBJECTS
from app.services.arxiv_client import ArxivClient
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)
settings = get_settings()


class PaperService:

    def __init__(self):
        self.embedding_repo = get_paper_embedding_repository()
        self.arxiv_client = ArxivClient()

    def _get_paper_repo(self, subject: str = DEFAULT_SUBJECT):
        """Get paper repository for specific subject."""
        return get_paper_repository(subject)

    def _get_category_from_subject(self, subject: str) -> str:
        """Convert subject (e.g., 'cs') to category wildcard (e.g., 'cs*')."""
        if subject in SUPPORTED_SUBJECTS:
            return f"{subject}*"
        return "cs*"  # Default fallback

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

    async def _fetch_and_store_papers(self, date: str, category: str, subject: str = DEFAULT_SUBJECT) -> Dict[str, Any]:
        """
        Fetch papers from arXiv and store them in subject-specific table.
        
        Returns:
            Dict with 'count' and 'inserted' keys, or 'error' on failure.
        """
        paper_repo = self._get_paper_repo(subject)
        try:
            logger.info(f"Fetching {category or 'all'} papers for {date} (subject: {subject})")
            papers = await self.arxiv_client.fetch_all_papers_for_date(date, category)
            
            if papers:
                inserted = paper_repo.upsert_papers_batch(papers)
                logger.info(f"Upserted {inserted} papers for {date} (subject: {subject})")
                paper_repo.insert_date_index(date, len(papers))
                return {"count": len(papers), "inserted": inserted}
            else:
                paper_repo.insert_date_index(date, 0)
                return {"count": 0, "inserted": 0}
        except Exception as e:
            logger.error(f"Failed to fetch papers for {date} (subject: {subject}): {e}")
            paper_repo.insert_date_index(date, 0)
            return {"count": 0, "inserted": 0, "error": str(e)}

    async def query_papers(
        self,
        date: str,
        category: Optional[str] = None,
        start: int = 0,
        max_results: int = 50,
        subject: str = DEFAULT_SUBJECT
    ) -> Dict[str, Any]:
        """
        Query papers for a specific date.

        Strategy:
        1. Normalize the date format
        2. Check if the date is in the future (return empty result)
        3. Check if we have data for this date
        4. If not, fetch papers for this date from arXiv with subject filter
        5. Store all papers
        6. Filter by category and return with pagination
        """
        paper_repo = self._get_paper_repo(subject)
        fetch_category = self._get_category_from_subject(subject)

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

        date_info = paper_repo.get_date_index(normalized_date)

        if not date_info or date_info.get("total_count", 0) == 0:
            logger.info(f"No local data for {normalized_date} (subject: {subject}), fetching from arXiv with category {fetch_category}")
            result = await self._fetch_and_store_papers(normalized_date, fetch_category, subject)
            if "error" in result:
                return {
                    "papers": [],
                    "total": 0,
                    "start": start,
                    "max_results": max_results,
                    "error": result["error"],
                }

        papers, total = paper_repo.query_papers_by_date(
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

    def get_paper_by_id(self, paper_id: str, subject: str = DEFAULT_SUBJECT) -> Optional[Dict[str, Any]]:
        """Get a single paper by ID."""
        paper_repo = self._get_paper_repo(subject)
        return paper_repo.get_paper_by_id(paper_id)

    def get_papers_by_ids(self, paper_ids: List[str], subject: str = DEFAULT_SUBJECT) -> List[Dict[str, Any]]:
        """Get multiple papers by their IDs."""
        paper_repo = self._get_paper_repo(subject)
        return paper_repo.get_papers_by_ids(paper_ids)

    def clear_date_index(self, date: str, subject: str = DEFAULT_SUBJECT) -> None:
        """Clear date index for a specific date."""
        paper_repo = self._get_paper_repo(subject)
        normalized_date = self._normalize_date(date)
        paper_repo.delete_date_index(normalized_date)

    def clear_all_date_index(self, subject: str = DEFAULT_SUBJECT) -> None:
        """Clear all date index cache."""
        paper_repo = self._get_paper_repo(subject)
        paper_repo.delete_all_date_index()

    async def fetch_papers_for_date(self, date: str, subject: str = DEFAULT_SUBJECT) -> Dict[str, Any]:
        """
        Manually fetch and store papers for a specific date.
        Returns the result of the fetch operation.
        """
        paper_repo = self._get_paper_repo(subject)
        category = self._get_category_from_subject(subject)

        try:
            normalized_date = self._normalize_date(date)
        except ValueError as e:
            logger.error(f"Invalid date format: {e}")
            return {
                "success": False,
                "date": date,
                "subject": subject,
                "count": 0,
                "error": str(e),
            }

        if self._is_future_date(normalized_date):
            return {
                "success": False,
                "date": normalized_date,
                "subject": subject,
                "count": 0,
                "error": "Cannot fetch papers for future dates",
            }

        paper_repo.delete_date_index(normalized_date)

        result = await self._fetch_and_store_papers(normalized_date, category, subject)

        if "error" in result:
            return {
                "success": False,
                "date": normalized_date,
                "subject": subject,
                "count": result["count"],
                "error": result["error"],
            }

        return {
            "success": True,
            "date": normalized_date,
            "subject": subject,
            "count": result["count"],
        }

    def get_all_date_indexes(self, subject: str = DEFAULT_SUBJECT) -> List[Dict[str, Any]]:
        """Get all date index records."""
        paper_repo = self._get_paper_repo(subject)
        return paper_repo.get_all_date_indexes()

    def get_statistics(self, subject: str = DEFAULT_SUBJECT) -> Dict[str, Any]:
        """Get statistics about stored papers."""
        paper_repo = self._get_paper_repo(subject)
        indexes = paper_repo.get_all_date_indexes()
        total_days = len([i for i in indexes if i.get("total_count", 0) > 0])
        total_papers = paper_repo.get_total_paper_count()
        total_embeddings = self.embedding_repo.count_embeddings()
        
        return {
            "total_days": total_days,
            "total_papers": total_papers,
            "total_embeddings": total_embeddings,
            "indexes": indexes,
            "subject": subject,
        }

    async def search_papers_semantic(
        self,
        query: str,
        top_k: int = 10,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        subject: str = DEFAULT_SUBJECT,
    ) -> Dict[str, Any]:
        """
        Search papers using semantic similarity.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            category: Optional category filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            subject: Subject to search in
        
        Returns:
            Dict with papers and metadata
        """
        paper_repo = self._get_paper_repo(subject)
        try:
            query_embedding, model_name = embedding_service.encode(query)
            
            candidate_ids = None
            if category or date_from or date_to:
                candidate_ids = paper_repo.get_paper_ids_by_filters(
                    category=category,
                    date_from=date_from,
                    date_to=date_to,
                    limit=settings.MILVUS_QUERY_BATCH_SIZE,
                )
                
                if not candidate_ids:
                    return {
                        "papers": [],
                        "total": 0,
                        "query": query,
                        "model": model_name,
                    }
            
            similar_papers = self.embedding_repo.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                paper_ids=candidate_ids,
            )
            
            if not similar_papers:
                return {
                    "papers": [],
                    "total": 0,
                    "query": query,
                    "model": model_name,
                }
            
            paper_ids = [p["paper_id"] for p in similar_papers]
            papers = paper_repo.get_papers_by_ids(paper_ids)
            
            paper_map = {p["id"]: p for p in papers}
            results = []
            for sp in similar_papers:
                paper = paper_map.get(sp["paper_id"])
                if paper:
                    paper["similarity_score"] = sp["similarity_score"]
                    results.append(paper)
            
            return {
                "papers": results,
                "total": len(results),
                "query": query,
                "model": model_name,
            }
            
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {
                "papers": [],
                "total": 0,
                "query": query,
                "error": str(e),
            }

    async def get_similar_papers(
        self,
        paper_id: str,
        top_k: int = 5,
        subject: str = DEFAULT_SUBJECT,
    ) -> Dict[str, Any]:
        """
        Get papers similar to a given paper.
        
        Args:
            paper_id: Paper ID to find similar papers for
            top_k: Number of similar papers to return
            subject: Subject to search in
        
        Returns:
            Dict with similar papers
        """
        paper_repo = self._get_paper_repo(subject)
        try:
            embedding_data = self.embedding_repo.get_embedding(paper_id)
            
            if not embedding_data:
                paper = paper_repo.get_paper_by_id(paper_id)
                if not paper:
                    return {
                        "papers": [],
                        "source_paper_id": paper_id,
                        "error": "Paper not found",
                    }
                
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                embedding, model_name = embedding_service.encode(text)
                
                self.embedding_repo.insert_embedding(
                    paper_id=paper_id,
                    embedding=embedding,
                    model_name=model_name,
                )
                embedding_data = {
                    "embedding": embedding,
                    "embedding_model": model_name,
                }
            
            similar_papers = self.embedding_repo.search_similar(
                query_embedding=embedding_data["embedding"],
                top_k=top_k + 1,
            )
            
            similar_papers = [
                p for p in similar_papers 
                if p["paper_id"] != paper_id
            ][:top_k]
            
            if not similar_papers:
                return {
                    "papers": [],
                    "source_paper_id": paper_id,
                }
            
            paper_ids = [p["paper_id"] for p in similar_papers]
            papers = paper_repo.get_papers_by_ids(paper_ids)
            
            paper_map = {p["id"]: p for p in papers}
            results = []
            for sp in similar_papers:
                paper = paper_map.get(sp["paper_id"])
                if paper:
                    paper["similarity_score"] = sp["similarity_score"]
                    results.append(paper)
            
            return {
                "papers": results,
                "source_paper_id": paper_id,
            }
            
        except Exception as e:
            logger.error(f"Failed to get similar papers: {e}")
            return {
                "papers": [],
                "source_paper_id": paper_id,
                "error": str(e),
            }

    async def generate_embeddings(
        self,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        force: bool = False,
        batch_size: int = 100,
        subject: str = DEFAULT_SUBJECT,
    ) -> Dict[str, Any]:
        """
        Generate embeddings for papers.
        
        Args:
            date: Specific date to generate embeddings for
            date_from: Start date for range
            date_to: End date for range
            force: Regenerate embeddings even if they exist
            batch_size: Number of papers to process at once
            subject: Subject to generate embeddings for
        
        Returns:
            Dict with generation statistics
        """
        paper_repo = self._get_paper_repo(subject)
        try:
            paper_ids = paper_repo.get_paper_ids_by_date_range(
                date=date,
                date_from=date_from,
                date_to=date_to,
            )
            
            if not force:
                try:
                    paper_ids = self.embedding_repo.get_paper_ids_without_embeddings(paper_ids)
                except NotImplementedError as e:
                    return {
                        "success": False,
                        "generated_count": 0,
                        "skipped_count": 0,
                        "error_count": 1,
                        "error": str(e),
                    }
            
            if not paper_ids:
                total_papers = paper_repo.get_total_paper_count()
                return {
                    "success": True,
                    "generated_count": 0,
                    "skipped_count": total_papers if not force else 0,
                    "error_count": 0,
                }
            
            generated = 0
            errors = 0
            model_name = ""
            
            for i in range(0, len(paper_ids), batch_size):
                batch_ids = paper_ids[i:i + batch_size]
                papers = paper_repo.get_papers_by_ids(batch_ids)
                
                texts = [
                    f"Title: {p.get('title', '')}\nAbstract: {p.get('abstract', '')}"
                    for p in papers
                ]
                
                try:
                    embeddings, batch_model_name = embedding_service.encode_batch(texts)
                    if not model_name:
                        model_name = batch_model_name
                    
                    embeddings_data = [
                        {
                            "paper_id": papers[j]["id"],
                            "embedding": embeddings[j],
                            "model_name": batch_model_name,
                        }
                        for j in range(len(papers))
                    ]
                    
                    inserted = self.embedding_repo.upsert_embeddings_batch(embeddings_data)
                    generated += inserted
                    logger.info(f"Generated embeddings for batch {i//batch_size + 1}: {inserted} papers")
                    
                except NotImplementedError as e:
                    return {
                        "success": False,
                        "generated_count": generated,
                        "skipped_count": 0,
                        "error_count": len(batch_ids),
                        "error": str(e),
                    }
                except Exception as e:
                    logger.error(f"Failed to generate embeddings for batch: {e}")
                    errors += len(batch_ids)
            
            if generated > 0 and date:
                paper_repo.insert_embedding_index(
                    date=date,
                    total_count=generated,
                    model_name=model_name
                )
            
            return {
                "success": True,
                "generated_count": generated,
                "skipped_count": len(paper_ids) - generated if not force else 0,
                "error_count": errors,
                "model_name": model_name,
            }
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return {
                "success": False,
                "generated_count": 0,
                "skipped_count": 0,
                "error_count": 1,
                "error": str(e),
            }
    
    def get_embedding_indexes(self, subject: str = DEFAULT_SUBJECT) -> List[Dict[str, Any]]:
        """Get all embedding indexes."""
        paper_repo = self._get_paper_repo(subject)
        return paper_repo.get_all_embedding_indexes()
    
    def get_embedding_index(self, date: str, subject: str = DEFAULT_SUBJECT) -> Optional[Dict[str, Any]]:
        """Get embedding index for a specific date."""
        paper_repo = self._get_paper_repo(subject)
        return paper_repo.get_embedding_index(date)

    def query_papers_by_author(
        self,
        author: str,
        start: int = 0,
        max_results: int = 50,
        subject: str = DEFAULT_SUBJECT,
    ) -> Dict[str, Any]:
        """
        Query papers by author name.
        
        Args:
            author: Author name to search for
            start: Pagination start index
            max_results: Maximum number of results to return
            subject: Subject to search in
        
        Returns:
            Dict with papers and metadata
        """
        paper_repo = self._get_paper_repo(subject)
        papers, total = paper_repo.get_papers_by_author(
            author=author,
            start=start,
            max_results=max_results,
        )
        
        return {
            "papers": papers,
            "total": total,
            "start": start,
            "max_results": max_results,
            "author": author,
        }

    def search_papers_keyword(
        self,
        query: str,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        start: int = 0,
        max_results: int = 50,
        title_only: bool = False,
        exact_phrase: bool = False,
        subject: str = DEFAULT_SUBJECT,
    ) -> Dict[str, Any]:
        """
        Search papers by keyword in title and abstract.
        
        Args:
            query: Search query string
            category: Optional category filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            start: Pagination start index
            max_results: Maximum number of results to return
            title_only: If True, search only in title, not in abstract
            exact_phrase: If True, match exact phrase instead of splitting
            subject: Subject to search in
        
        Returns:
            Dict with papers and metadata
        """
        paper_repo = self._get_paper_repo(subject)
        papers, total = paper_repo.search_papers(
            query=query,
            category=category,
            date_from=date_from,
            date_to=date_to,
            start=start,
            max_results=max_results,
            title_only=title_only,
            exact_phrase=exact_phrase,
        )
        
        return {
            "papers": papers,
            "total": total,
            "start": start,
            "max_results": max_results,
            "query": query,
        }
