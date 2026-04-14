import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import lance
from lance.dataset import ColumnOrdering

from app.db.base import FollowedAuthorRepository
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBFollowedAuthorRepository(FollowedAuthorRepository):
    """LanceDB implementation for Followed Author storage."""
    
    def __init__(self):
        self._table = None
    
    def _get_table(self):
        if self._table is None:
            self._table = lancedb_client.get_table("followed_authors")
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
            "author_name": row.get("author_name", ""),
            "paper_count": int(row.get("paper_count", 0)),
            "latest_published": row.get("latest_published") or None,
            "notes": row.get("notes") or None,
            "followed_at": row.get("followed_at", ""),
        }
    
    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        table = self._get_table()
        author_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        record = {
            "id": author_id,
            "author_name": self._safe_str(data.get("author_name")),
            "paper_count": data.get("paper_count", 0),
            "latest_published": self._safe_str(data.get("latest_published")),
            "notes": self._safe_str(data.get("notes")),
            "followed_at": now,
            "embedding": [0.0] * 8,
        }
        
        table.add([record])
        
        return {
            "id": author_id,
            "author_name": self._safe_str(data.get("author_name")),
            "paper_count": data.get("paper_count", 0),
            "latest_published": self._safe_str(data.get("latest_published")) or None,
            "notes": self._safe_str(data.get("notes")) or None,
            "followed_at": now,
        }
    
    def remove(self, id: str) -> bool:
        table = self._get_table()
        table.delete(f"id = '{id}'")
        return True
    
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        table = self._get_table()
        results = table.search().where(f"id = '{id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._entity_to_response(results.iloc[0])
    
    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_table()
        
        total = table.count_rows()
        
        if total == 0:
            return [], 0
        
        try:
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=[
                    "id", "author_name", "paper_count", "latest_published",
                    "notes", "followed_at"
                ],
                filter=None,
                limit=limit,
                offset=offset,
                order_by=[ColumnOrdering("followed_at", ascending=False)],
            )
            df = scanner.to_table().to_pandas()
            
            results = [self._entity_to_response(row) for _, row in df.iterrows()]
            return results, total
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner, falling back to pandas: {e}")
            df = table.to_pandas()
            if df.empty or "followed_at" not in df.columns:
                return [], total
            df_sorted = df.sort_values(by="followed_at", ascending=False)
            df_paginated = df_sorted.iloc[offset:offset + limit]
            results = [self._entity_to_response(row) for _, row in df_paginated.iterrows()]
            return results, total
    
    def exists(self, id: str) -> bool:
        return self.get(id) is not None
    
    def get_by_author_name(self, author_name: str) -> Optional[Dict[str, Any]]:
        table = self._get_table()
        escaped_name = author_name.replace("'", "''")
        results = table.search().where(f"author_name = '{escaped_name}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._entity_to_response(results.iloc[0])
    
    def is_followed(self, author_name: str) -> bool:
        return self.get_by_author_name(author_name) is not None
    
    def update_notes(self, author_name: str, notes: str) -> bool:
        table = self._get_table()
        escaped_name = author_name.replace("'", "''")
        
        existing = self.get_by_author_name(author_name)
        if not existing:
            return False
        
        record = {
            "id": existing["id"],
            "author_name": existing["author_name"],
            "paper_count": existing["paper_count"],
            "latest_published": existing["latest_published"] or "",
            "notes": notes or "",
            "followed_at": existing["followed_at"],
            "embedding": [0.0] * 8,
        }
        
        table.delete(f"id = '{existing['id']}'")
        table.add([record])
        return True
    
    def update_paper_info(self, author_name: str, paper_count: int, latest_published: str) -> bool:
        table = self._get_table()
        
        existing = self.get_by_author_name(author_name)
        if not existing:
            return False
        
        record = {
            "id": existing["id"],
            "author_name": existing["author_name"],
            "paper_count": paper_count,
            "latest_published": latest_published or "",
            "notes": existing["notes"] or "",
            "followed_at": existing["followed_at"],
            "embedding": [0.0] * 8,
        }
        
        table.delete(f"id = '{existing['id']}'")
        table.add([record])
        return True
