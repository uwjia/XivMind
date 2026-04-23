from app.db.base import PaperCodeRepository
from app.db.milvus.client import milvus_client, Collection
from typing import Dict, List, Optional, Any
from datetime import datetime


class MilvusPaperCodeRepository(PaperCodeRepository):
    def __init__(self):
        self._collection: Optional[Collection] = None

    def _get_collection(self) -> Collection:
        if not self._collection:
            self._collection = milvus_client.get_collection("paper_codes")
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
            "url": entity.get("url", ""),
            "platform": entity.get("platform", ""),
            "owner": entity.get("owner", ""),
            "repo": entity.get("repo", ""),
            "is_official": entity.get("is_official", True),
            "stars": entity.get("stars", 0) or 0,
            "language": entity.get("language", ""),
            "fetched_at": entity.get("fetched_at", ""),
        }

    def upsert_paper_codes(self, codes: List[Dict[str, Any]]) -> int:
        if not codes:
            return 0
        
        collection = self._get_collection()
        now = datetime.utcnow().isoformat()
        count = 0
        
        for code in codes:
            paper_id = self._safe_str(code.get("paper_id"))
            try:
                upsert_data = [
                    [paper_id],
                    [paper_id],
                    [self._safe_str(code.get("url"))],
                    [self._safe_str(code.get("platform"))],
                    [self._safe_str(code.get("owner"))],
                    [self._safe_str(code.get("repo"))],
                    [code.get("is_official", True)],
                    [code.get("stars", 0) or 0],
                    [self._safe_str(code.get("language"))],
                    [self._safe_str(code.get("fetched_at") or now)],
                    [[0.0] * 8],
                ]
                collection.upsert(upsert_data)
                count += 1
            except Exception:
                pass
        
        collection.load()
        return count

    def get_code_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_collection()
        collection.load()
        
        try:
            results = collection.query(
                expr=f'id == "{paper_id}"',
                output_fields=["id", "paper_id", "url", "platform", "owner", "repo", "is_official", "stars", "language", "fetched_at"]
            )
            if not results:
                return None
            return self._entity_to_response(results[0])
        except Exception:
            return None

    def get_paper_ids_with_code(self) -> List[str]:
        collection = self._get_collection()
        collection.load()
        
        try:
            results = collection.query(
                expr="",
                output_fields=["paper_id"]
            )
            return list(set(r.get("paper_id") for r in results if r.get("paper_id")))
        except Exception:
            return []

    def check_batch(self, paper_ids: List[str]) -> Dict[str, bool]:
        if not paper_ids:
            return {}
        
        result = {pid: False for pid in paper_ids}
        collection = self._get_collection()
        collection.load()
        
        try:
            ids_str = ', '.join(f'"{pid}"' for pid in paper_ids)
            results = collection.query(
                expr=f'id in [{ids_str}]',
                output_fields=["id"]
            )
            for r in results:
                paper_id = r.get("id")
                if paper_id in result:
                    result[paper_id] = True
        except Exception:
            pass
        
        return result

    def get_codes_by_paper_ids(self, paper_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        if not paper_ids:
            return {}
        
        result = {pid: None for pid in paper_ids}
        collection = self._get_collection()
        collection.load()
        
        try:
            ids_str = ', '.join(f'"{pid}"' for pid in paper_ids)
            results = collection.query(
                expr=f'id in [{ids_str}]',
                output_fields=["id", "paper_id", "url", "platform", "owner", "repo", "is_official", "stars", "language", "fetched_at"]
            )
            for r in results:
                paper_id = r.get("id")
                if paper_id in result:
                    result[paper_id] = self._entity_to_response(r)
        except Exception:
            pass
        
        return result
