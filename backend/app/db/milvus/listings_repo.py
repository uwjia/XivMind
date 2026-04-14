from app.db.base import ListingsRepository
from app.db.milvus.client import milvus_client, Collection
from app.config import get_settings
from app.core.utils import safe_json_loads
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

settings = get_settings()


class MilvusListingsRepository(ListingsRepository):
    def __init__(self):
        self._new_submissions_collection: Optional[Collection] = None
        self._cross_submissions_collection: Optional[Collection] = None
        self._replacement_submissions_collection: Optional[Collection] = None
        self._listings_date_index_collection: Optional[Collection] = None

    def _get_new_submissions_collection(self) -> Collection:
        if not self._new_submissions_collection:
            self._new_submissions_collection = milvus_client.get_collection("new_submissions")
        return self._new_submissions_collection

    def _get_cross_submissions_collection(self) -> Collection:
        if not self._cross_submissions_collection:
            self._cross_submissions_collection = milvus_client.get_collection("cross_submissions")
        return self._cross_submissions_collection

    def _get_replacement_submissions_collection(self) -> Collection:
        if not self._replacement_submissions_collection:
            self._replacement_submissions_collection = milvus_client.get_collection("replacement_submissions")
        return self._replacement_submissions_collection

    def _get_listings_date_index_collection(self) -> Collection:
        if not self._listings_date_index_collection:
            self._listings_date_index_collection = milvus_client.get_collection("listings_date_index")
        return self._listings_date_index_collection

    @staticmethod
    def _safe_str(value, max_len=None) -> str:
        if value is None:
            return ""
        s = str(value)
        return s[:max_len] if max_len else s

    def _entity_to_response(self, entity: Dict) -> Dict[str, Any]:
        return {
            "id": entity.get("id", ""),
            "title": entity.get("title", ""),
            "abstract": entity.get("abstract", ""),
            "authors": safe_json_loads(entity.get("authors"), []),
            "primary_category": entity.get("primary_category", ""),
            "categories": safe_json_loads(entity.get("categories"), []),
            "published": entity.get("published", ""),
            "updated": entity.get("updated", ""),
            "pdf_url": entity.get("pdf_url", ""),
            "abs_url": entity.get("abs_url", ""),
            "comment": entity.get("comment", ""),
            "journal_ref": entity.get("journal_ref", ""),
            "doi": entity.get("doi", ""),
            "fetched_at": entity.get("fetched_at", ""),
            "listing_date": entity.get("listing_date", ""),
        }

    def _listings_date_index_to_response(self, entity: Dict) -> Dict[str, Any]:
        return {
            "date": entity.get("date", ""),
            "new_count": entity.get("new_count", 0),
            "cross_count": entity.get("cross_count", 0),
            "replacement_count": entity.get("replacement_count", 0),
            "fetched_at": entity.get("fetched_at", ""),
        }

    def _prepare_paper_data(self, data: Dict[str, Any], now: str) -> List:
        return [
            self._safe_str(data.get("id"), 128),
            self._safe_str(data.get("title"), 2048),
            self._safe_str(data.get("abstract"), 32768),
            self._safe_str(json.dumps(data.get("authors") or []), 16384),
            self._safe_str(data.get("primary_category"), 64),
            self._safe_str(json.dumps(data.get("categories") or []), 2048),
            self._safe_str(data.get("published"), 64),
            self._safe_str(data.get("updated"), 64),
            self._safe_str(data.get("pdf_url"), 512),
            self._safe_str(data.get("abs_url"), 512),
            self._safe_str(data.get("comment"), 8192),
            self._safe_str(data.get("journal_ref"), 1024),
            self._safe_str(data.get("doi"), 256),
            now,
            [0.0] * 8,
        ]

    def _insert_submissions_batch(self, collection: Collection, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        if not papers:
            return 0

        collection.load()
        now = datetime.utcnow().isoformat()
        listing_date_val = listing_date or now[:10]

        insert_data = [
            [self._safe_str(p.get("id"), 128) for p in papers],
            [self._safe_str(p.get("title"), 2048) for p in papers],
            [self._safe_str(p.get("abstract"), 32768) for p in papers],
            [self._safe_str(json.dumps(p.get("authors") or []), 16384) for p in papers],
            [self._safe_str(p.get("primary_category"), 64) for p in papers],
            [self._safe_str(json.dumps(p.get("categories") or []), 2048) for p in papers],
            [self._safe_str(p.get("published"), 64) for p in papers],
            [self._safe_str(p.get("updated"), 64) for p in papers],
            [self._safe_str(p.get("pdf_url"), 512) for p in papers],
            [self._safe_str(p.get("abs_url"), 512) for p in papers],
            [self._safe_str(p.get("comment"), 8192) for p in papers],
            [self._safe_str(p.get("journal_ref"), 1024) for p in papers],
            [self._safe_str(p.get("doi"), 256) for p in papers],
            [now] * len(papers),
            [listing_date_val] * len(papers),
            [[0.0] * 8] * len(papers),
        ]

        collection.upsert(insert_data)
        return len(papers)

    def insert_new_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        collection = self._get_new_submissions_collection()
        return self._insert_submissions_batch(collection, papers, listing_date)

    def insert_cross_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        collection = self._get_cross_submissions_collection()
        return self._insert_submissions_batch(collection, papers, listing_date)

    def insert_replacement_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        collection = self._get_replacement_submissions_collection()
        return self._insert_submissions_batch(collection, papers, listing_date)

    def insert_listings_date_index(
        self,
        date: str,
        new_count: int,
        cross_count: int,
        replacement_count: int
    ) -> None:
        collection = self._get_listings_date_index_collection()
        now = datetime.utcnow().isoformat()

        insert_data = [
            [date],
            [new_count],
            [cross_count],
            [replacement_count],
            [now],
            [[0.0] * 8],
        ]

        collection.upsert(insert_data)

    def get_listings_date_indexes(self) -> List[Dict[str, Any]]:
        collection = self._get_listings_date_index_collection()
        collection.load()

        results = collection.query(
            expr='date != ""',
            output_fields=["date", "new_count", "cross_count", "replacement_count", "fetched_at"],
        )

        sorted_results = sorted(results, key=lambda x: x.get("date", ""), reverse=True)
        return [self._listings_date_index_to_response(r) for r in sorted_results]

    def get_listings_date_index(self, date: str) -> Optional[Dict[str, Any]]:
        collection = self._get_listings_date_index_collection()
        collection.load()

        results = collection.query(
            expr=f'date == "{date}"',
            output_fields=["date", "new_count", "cross_count", "replacement_count", "fetched_at"],
        )

        if results:
            return self._listings_date_index_to_response(results[0])
        return None

    def get_latest_listings_date_index(self) -> Optional[Dict[str, Any]]:
        collection = self._get_listings_date_index_collection()
        collection.load()

        results = collection.query(
            expr='date != ""',
            output_fields=["date", "new_count", "cross_count", "replacement_count", "fetched_at"],
            limit=1,
        )

        if results:
            sorted_results = sorted(results, key=lambda x: x.get("date", ""), reverse=True)
            return self._listings_date_index_to_response(sorted_results[0])
        return None

    def _get_submissions_by_date(
        self,
        collection: Collection,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        collection.load()

        results = collection.query(
            expr=f'listing_date == "{date}"',
            output_fields=["id", "title", "abstract", "authors", "primary_category",
                          "categories", "published", "updated", "pdf_url", "abs_url",
                          "comment", "journal_ref", "doi", "fetched_at", "listing_date"],
        )

        total = len(results)
        sorted_results = sorted(results, key=lambda x: x.get("published", ""), reverse=True)
        paginated = sorted_results[start:start + max_results]
        return [self._entity_to_response(r) for r in paginated], total

    def get_new_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_new_submissions_collection()
        return self._get_submissions_by_date(collection, date, start, max_results)

    def get_cross_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_cross_submissions_collection()
        return self._get_submissions_by_date(collection, date, start, max_results)

    def get_replacement_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_replacement_submissions_collection()
        return self._get_submissions_by_date(collection, date, start, max_results)

    def clear_listings_by_date(self, date: str) -> None:
        new_collection = self._get_new_submissions_collection()
        cross_collection = self._get_cross_submissions_collection()
        replacement_collection = self._get_replacement_submissions_collection()
        index_collection = self._get_listings_date_index_collection()

        new_collection.load()
        cross_collection.load()
        replacement_collection.load()
        index_collection.load()

        new_collection.delete(f'listing_date == "{date}"')
        cross_collection.delete(f'listing_date == "{date}"')
        replacement_collection.delete(f'listing_date == "{date}"')
        index_collection.delete(f'date == "{date}"')
