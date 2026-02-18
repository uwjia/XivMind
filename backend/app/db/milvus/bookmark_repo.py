from app.db.base import BookmarkRepository
from app.db.milvus.client import milvus_client, Collection
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid
import json


class MilvusBookmarkRepository(BookmarkRepository):
    def __init__(self):
        self._collection: Optional[Collection] = None

    def _get_collection(self) -> Collection:
        if not self._collection:
            self._collection = milvus_client.get_bookmarks_collection()
        return self._collection

    @staticmethod
    def _safe_str(value, max_len=None) -> str:
        if value is None:
            return ""
        s = str(value)
        return s[:max_len] if max_len else s

    def _entity_to_response(self, entity: Dict) -> Dict[str, Any]:
        return {
            "id": entity.get("id", ""),
            "paper_id": entity.get("paper_id", ""),
            "arxiv_id": entity.get("arxiv_id", ""),
            "title": entity.get("title", ""),
            "authors": json.loads(entity.get("authors", "[]")),
            "abstract": entity.get("abstract", ""),
            "comment": entity.get("comment", ""),
            "journal_ref": entity.get("journal_ref", ""),
            "doi": entity.get("doi", ""),
            "primary_category": entity.get("primary_category", ""),
            "categories": json.loads(entity.get("categories", "[]")),
            "pdf_url": entity.get("pdf_url", ""),
            "abs_url": entity.get("abs_url", ""),
            "published": entity.get("published", ""),
            "updated": entity.get("updated", ""),
            "created_at": entity.get("created_at", ""),
        }

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        collection = self._get_collection()
        bookmark_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        title = self._safe_str(data.get("title"), 1024)
        abstract = self._safe_str(data.get("abstract"), 16384)
        comment = self._safe_str(data.get("comment"), 4096)
        journal_ref = self._safe_str(data.get("journal_ref"), 1024)
        doi = self._safe_str(data.get("doi"), 256)

        insert_data = [
            [bookmark_id],
            [self._safe_str(data.get("paper_id"))],
            [self._safe_str(data.get("arxiv_id"))],
            [title],
            [json.dumps(data.get("authors") or [])],
            [abstract],
            [comment],
            [journal_ref],
            [doi],
            [self._safe_str(data.get("primary_category"))],
            [json.dumps(data.get("categories") or [])],
            [self._safe_str(data.get("pdf_url"))],
            [self._safe_str(data.get("abs_url"))],
            [self._safe_str(data.get("published"))],
            [self._safe_str(data.get("updated"))],
            [now],
            [[0.0] * 1536],
        ]

        collection.insert(insert_data)

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
        collection = self._get_collection()
        collection.load()
        collection.delete(f'paper_id == "{id}"')
        return True

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'id == "{id}"', output_fields=[
            "id", "paper_id", "arxiv_id", "title", "authors", "abstract",
            "comment", "journal_ref", "doi", "primary_category", 
            "categories", "pdf_url", "abs_url", "published", "updated", "created_at"
        ])
        if results:
            return self._entity_to_response(results[0])
        return None

    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_collection()
        collection.load()
        all_results = collection.query(
            expr='id != ""',
            output_fields=["id", "paper_id", "arxiv_id", "title", "authors", "abstract",
                          "comment", "journal_ref", "doi", "primary_category",
                          "categories", "pdf_url", "abs_url", "published", "updated", "created_at"],
        )
        total = len(all_results)
        sorted_results = sorted(
            all_results,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        paginated = sorted_results[offset:offset + limit]
        return [self._entity_to_response(r) for r in paginated], total

    def exists(self, id: str) -> bool:
        return self.is_bookmarked(id)

    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr=f'paper_id == "{paper_id}"',
            output_fields=[
                "id", "paper_id", "arxiv_id", "title", "authors", "abstract",
                "comment", "journal_ref", "doi", "primary_category",
                "categories", "pdf_url", "abs_url", "published", "updated", "created_at"
            ]
        )
        if results:
            return self._entity_to_response(results[0])
        return None

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr=f'paper_id like "%{query}%" or title like "%{query}%" or abstract like "%{query}%"',
            output_fields=["id", "paper_id", "arxiv_id", "title", "authors", "abstract",
                          "comment", "journal_ref", "doi", "primary_category",
                          "categories", "pdf_url", "abs_url", "published", "updated", "created_at"],
            limit=limit,
        )
        return [self._entity_to_response(r) for r in results]

    def is_bookmarked(self, paper_id: str) -> bool:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'paper_id == "{paper_id}"', output_fields=["id"])
        return len(results) > 0
