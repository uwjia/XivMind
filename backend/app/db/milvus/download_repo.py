from app.db.base import DownloadRepository
from app.db.milvus.client import milvus_client, Collection
from app.config import get_settings
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import uuid

settings = get_settings()

class MilvusDownloadRepository(DownloadRepository):
    def __init__(self):
        self._collection: Optional[Collection] = None

    def _get_collection(self) -> Collection:
        if not self._collection:
            self._collection = milvus_client.get_collection("downloads")
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
            "pdf_url": entity.get("pdf_url", ""),
            "status": entity.get("status", "pending"),
            "progress": entity.get("progress", 0),
            "file_path": entity.get("file_path", ""),
            "file_size": entity.get("file_size", 0),
            "error_message": entity.get("error_message", ""),
            "created_at": entity.get("created_at", ""),
            "updated_at": entity.get("updated_at", ""),
        }

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        collection = self._get_collection()
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        title = self._safe_str(data.get("title"), 1024)

        insert_data = [
            [task_id],
            [self._safe_str(data.get("paper_id"))],
            [self._safe_str(data.get("arxiv_id"))],
            [title],
            [self._safe_str(data.get("pdf_url"))],
            ["pending"],
            [0],
            [""],
            [0],
            [""],
            [now],
            [now],
            [[0.0] * 8],
        ]

        collection.insert(insert_data)

        return {
            "id": task_id,
            "paper_id": self._safe_str(data.get("paper_id")),
            "arxiv_id": self._safe_str(data.get("arxiv_id")),
            "title": title,
            "pdf_url": self._safe_str(data.get("pdf_url")),
            "status": "pending",
            "progress": 0,
            "file_path": "",
            "file_size": 0,
            "error_message": "",
            "created_at": now,
            "updated_at": now,
        }

    def remove(self, id: str) -> bool:
        collection = self._get_collection()
        collection.load()
        collection.delete(f'id == "{id}"')
        return True

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'id == "{id}"', output_fields=["*"])
        if results:
            return self._entity_to_response(results[0])
        return None

    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_collection()
        collection.load()
        total = collection.num_entities
        results = collection.query(
            expr='id != ""',
            output_fields=["*"],
            limit=offset + limit,
        )
        sorted_results = sorted(
            results,
            key=lambda x: x.get("created_at", ""),
            reverse=True
        )
        paginated = sorted_results[offset:offset + limit]
        return [self._entity_to_response(r) for r in paginated], total

    def exists(self, id: str) -> bool:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'id == "{id}"', output_fields=["id"])
        return len(results) > 0

    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr=f'paper_id == "{paper_id}"',
            output_fields=["*"]
        )
        if results:
            return self._entity_to_response(results[0])
        return None

    def get_all_by_paper_id(self, paper_id: str) -> List[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr=f'paper_id == "{paper_id}"',
            output_fields=["*"]
        )
        return [self._entity_to_response(r) for r in results]

    def update_status(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        file_path: Optional[str] = None,
        file_size: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        collection = self._get_collection()
        collection.load()
        results = collection.query(expr=f'id == "{task_id}"', output_fields=["*"])
        if not results:
            return False

        entity = results[0]
        entity["status"] = status
        entity["progress"] = progress
        if file_path is not None:
            entity["file_path"] = file_path
        if file_size:
            entity["file_size"] = file_size
        if error_message is not None:
            entity["error_message"] = error_message
        entity["updated_at"] = datetime.utcnow().isoformat()

        title = self._safe_str(entity.get("title"), 1024)

        insert_data = [
            [self._safe_str(entity.get("id"))],
            [self._safe_str(entity.get("paper_id"))],
            [self._safe_str(entity.get("arxiv_id"))],
            [title],
            [self._safe_str(entity.get("pdf_url"))],
            [self._safe_str(entity.get("status"))],
            [entity.get("progress", 0) or 0],
            [self._safe_str(entity.get("file_path"))],
            [entity.get("file_size", 0) or 0],
            [self._safe_str(entity.get("error_message"))],
            [self._safe_str(entity.get("created_at"))],
            [self._safe_str(entity.get("updated_at"))],
            [[0.0] * 8],
        ]

        collection.delete(f'id == "{task_id}"')
        collection.insert(insert_data)
        return True

    def reset_incomplete_tasks(self) -> int:
        collection = self._get_collection()
        collection.load()
        results = collection.query(
            expr='status == "downloading" or status == "pending"',
            output_fields=["*"],
            limit=settings.MILVUS_QUERY_BATCH_SIZE,
        )
        
        if not results:
            return 0
        
        count = 0
        for entity in results:
            entity["status"] = "failed"
            entity["error_message"] = "Download interrupted - please retry"
            entity["updated_at"] = datetime.utcnow().isoformat()
            
            title = self._safe_str(entity.get("title"), 1024)

            insert_data = [
                [self._safe_str(entity.get("id"))],
                [self._safe_str(entity.get("paper_id"))],
                [self._safe_str(entity.get("arxiv_id"))],
                [title],
                [self._safe_str(entity.get("pdf_url"))],
                ["failed"],
                [entity.get("progress", 0) or 0],
                [self._safe_str(entity.get("file_path"))],
                [entity.get("file_size", 0) or 0],
                ["Download interrupted - please retry"],
                [self._safe_str(entity.get("created_at"))],
                [self._safe_str(entity.get("updated_at"))],
                [[0.0] * 8],
            ]

            collection.delete(f'id == "{entity.get("id")}"')
            collection.insert(insert_data)
            count += 1
        
        return count
