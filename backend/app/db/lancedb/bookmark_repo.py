import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.db.base import BookmarkRepository
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBBookmarkRepository(BookmarkRepository):
    """LanceDB implementation for Bookmark storage."""
    
    def __init__(self):
        self._table = None
    
    def _get_table(self):
        if self._table is None:
            self._table = lancedb_client.get_table("bookmarks")
        return self._table
    
    @staticmethod
    def _safe_str(value, max_len=None) -> str:
        if value is None:
            return ""
        s = str(value)
        return s[:max_len] if max_len else s
    
    def _entity_to_response(self, row) -> Dict[str, Any]:
        return {
            "id": row.get("id", ""),
            "paper_id": row.get("paper_id", ""),
            "arxiv_id": row.get("arxiv_id", ""),
            "title": row.get("title", ""),
            "authors": json.loads(row.get("authors", "[]")) if row.get("authors") else [],
            "abstract": row.get("abstract", ""),
            "comment": row.get("comment", ""),
            "journal_ref": row.get("journal_ref", ""),
            "doi": row.get("doi", ""),
            "primary_category": row.get("primary_category", ""),
            "categories": json.loads(row.get("categories", "[]")) if row.get("categories") else [],
            "pdf_url": row.get("pdf_url", ""),
            "abs_url": row.get("abs_url", ""),
            "published": row.get("published", ""),
            "updated": row.get("updated", ""),
            "created_at": row.get("created_at", ""),
        }
    
    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        table = self._get_table()
        bookmark_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        title = self._safe_str(data.get("title"), 1024)
        abstract = self._safe_str(data.get("abstract"), 16384)
        comment = self._safe_str(data.get("comment"), 4096)
        journal_ref = self._safe_str(data.get("journal_ref"), 1024)
        doi = self._safe_str(data.get("doi"), 256)
        
        record = {
            "id": bookmark_id,
            "paper_id": self._safe_str(data.get("paper_id")),
            "arxiv_id": self._safe_str(data.get("arxiv_id")),
            "title": title,
            "authors": json.dumps(data.get("authors") or []),
            "abstract": abstract,
            "comment": comment,
            "journal_ref": journal_ref,
            "doi": doi,
            "primary_category": self._safe_str(data.get("primary_category")),
            "categories": json.dumps(data.get("categories") or []),
            "pdf_url": self._safe_str(data.get("pdf_url")),
            "abs_url": self._safe_str(data.get("abs_url")),
            "published": self._safe_str(data.get("published")),
            "updated": self._safe_str(data.get("updated")),
            "created_at": now,
            "embedding": [0.0] * 1536,
        }
        
        table.add([record])
        
        return {
            "id": bookmark_id,
            "paper_id": self._safe_str(data.get("paper_id")),
            "arxiv_id": self._safe_str(data.get("arxiv_id")),
            "title": title,
            "authors": data.get("authors") or [],
            "abstract": abstract,
            "comment": comment,
            "journal_ref": journal_ref,
            "doi": doi,
            "primary_category": self._safe_str(data.get("primary_category")),
            "categories": data.get("categories") or [],
            "pdf_url": self._safe_str(data.get("pdf_url")),
            "abs_url": self._safe_str(data.get("abs_url")),
            "published": self._safe_str(data.get("published")),
            "updated": self._safe_str(data.get("updated")),
            "created_at": now,
        }
    
    def remove(self, id: str) -> bool:
        table = self._get_table()
        table.delete(f"paper_id = '{id}'")
        return True
    
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        table = self._get_table()
        results = table.search().where(f"id = '{id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._entity_to_response(results.iloc[0])
    
    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_table()
        df = table.to_pandas()
        total = len(df)
        
        if total == 0:
            return [], 0
        
        df_sorted = df.sort_values(by="created_at", ascending=False)
        df_paginated = df_sorted.iloc[offset:offset + limit]
        
        results = [self._entity_to_response(row) for _, row in df_paginated.iterrows()]
        return results, total
    
    def exists(self, id: str) -> bool:
        return self.is_bookmarked(id)
    
    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        table = self._get_table()
        results = table.search().where(f"paper_id = '{paper_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._entity_to_response(results.iloc[0])
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        table = self._get_table()
        df = table.to_pandas()
        
        query_lower = query.lower()
        mask = (
            df["paper_id"].str.lower().str.contains(query_lower, na=False) |
            df["title"].str.lower().str.contains(query_lower, na=False) |
            df["abstract"].str.lower().str.contains(query_lower, na=False)
        )
        filtered = df[mask].head(limit)
        
        return [self._entity_to_response(row) for _, row in filtered.iterrows()]
    
    def is_bookmarked(self, paper_id: str) -> bool:
        table = self._get_table()
        results = table.search().where(f"paper_id = '{paper_id}'").limit(1).to_pandas()
        return len(results) > 0

    def check_batch(self, paper_ids: List[str]) -> Dict[str, bool]:
        if not paper_ids:
            return {}
        
        result = {pid: False for pid in paper_ids}
        
        table = self._get_table()
        df = table.to_pandas()
        
        if df.empty or "paper_id" not in df.columns:
            return result
        
        bookmarked_ids = set(df[df["paper_id"].isin(paper_ids)]["paper_id"].tolist())
        
        for pid in bookmarked_ids:
            if pid in result:
                result[pid] = True
        
        return result
