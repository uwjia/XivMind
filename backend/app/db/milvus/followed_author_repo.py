from app.db.base import FollowedAuthorRepository
from app.db.milvus.client import milvus_client, Collection
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid


class MilvusFollowedAuthorRepository(FollowedAuthorRepository):
    def __init__(self):
        self._collection: Optional[Collection] = None

    def _get_collection(self) -> Collection:
        if not self._collection:
            self._collection = milvus_client.get_collection("followed_authors")
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
            "author_name": entity.get("author_name", ""),
            "paper_count": int(entity.get("paper_count", 0)),
            "latest_published": entity.get("latest_published") or None,
            "notes": entity.get("notes") or None,
            "followed_at": entity.get("followed_at", ""),
        }

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        collection = self._get_collection()
        author_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        insert_data = [
            [author_id],
            [self._safe_str(data.get("author_name"))],
            [data.get("paper_count", 0)],
            [self._safe_str(data.get("latest_published"))],
            [self._safe_str(data.get("notes"))],
            [now],
            [[0.0] * 8],
        ]

        collection.insert(insert_data)

        return {
            "id": author_id,
            "author_name": self._safe_str(data.get("author_name")),
            "paper_count": data.get("paper_count", 0),
            "latest_published": self._safe_str(data.get("latest_published")) or None,
            "notes": self._safe_str(data.get("notes")) or None,
            "followed_at": now,
        }

    def remove(self, id: str) -> bool:
        collection = self._get_collection()
        collection.load()
        collection.delete(f'id == "{id}"')
        return True

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr=f'id == "{id}"',
            output_fields=["id", "author_name", "paper_count", "latest_published", "notes", "followed_at"]
        )
        if results:
            return self._entity_to_response(results[0])
        return None

    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_collection()
        collection.load()
        total = collection.num_entities
        results = collection.query(
            expr='id != ""',
            output_fields=["id", "author_name", "paper_count", "latest_published", "notes", "followed_at"],
            limit=offset + limit,
        )
        sorted_results = sorted(
            results,
            key=lambda x: x.get("followed_at", ""),
            reverse=True
        )
        paginated = sorted_results[offset:offset + limit]
        return [self._entity_to_response(r) for r in paginated], total

    def exists(self, id: str) -> bool:
        return self.get(id) is not None

    def get_by_author_name(self, author_name: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        escaped_name = author_name.replace('"', '\\"')
        results = collection.query(
            expr=f'author_name == "{escaped_name}"',
            output_fields=["id", "author_name", "paper_count", "latest_published", "notes", "followed_at"]
        )
        if results:
            return self._entity_to_response(results[0])
        return None

    def is_followed(self, author_name: str) -> bool:
        return self.get_by_author_name(author_name) is not None

    def update_notes(self, author_name: str, notes: str) -> bool:
        collection = self._get_collection()
        
        existing = self.get_by_author_name(author_name)
        if not existing:
            return False
        
        collection.load()
        collection.delete(f'id == "{existing["id"]}"')
        
        insert_data = [
            [existing["id"]],
            [existing["author_name"]],
            [existing["paper_count"]],
            [existing["latest_published"] or ""],
            [notes or ""],
            [existing["followed_at"]],
            [[0.0] * 8],
        ]
        collection.insert(insert_data)
        return True

    def update_paper_info(self, author_name: str, paper_count: int, latest_published: str) -> bool:
        collection = self._get_collection()
        
        existing = self.get_by_author_name(author_name)
        if not existing:
            return False
        
        collection.load()
        collection.delete(f'id == "{existing["id"]}"')
        
        insert_data = [
            [existing["id"]],
            [existing["author_name"]],
            [paper_count],
            [latest_published or ""],
            [existing["notes"] or ""],
            [existing["followed_at"]],
            [[0.0] * 8],
        ]
        collection.insert(insert_data)
        return True
