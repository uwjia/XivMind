from app.db.base import PaperRepository
from app.db.milvus.client import milvus_client, Collection
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json


class MilvusPaperRepository(PaperRepository):
    def __init__(self):
        self._papers_collection: Optional[Collection] = None
        self._date_index_collection: Optional[Collection] = None

    def _get_papers_collection(self) -> Collection:
        if not self._papers_collection:
            self._papers_collection = milvus_client.get_papers_collection()
        return self._papers_collection

    def _get_date_index_collection(self) -> Collection:
        if not self._date_index_collection:
            self._date_index_collection = milvus_client.get_date_index_collection()
        return self._date_index_collection

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
            "authors": json.loads(entity.get("authors", "[]")),
            "primary_category": entity.get("primary_category", ""),
            "categories": json.loads(entity.get("categories", "[]")),
            "published": entity.get("published", ""),
            "updated": entity.get("updated", ""),
            "pdf_url": entity.get("pdf_url", ""),
            "abs_url": entity.get("abs_url", ""),
            "comment": entity.get("comment", ""),
            "journal_ref": entity.get("journal_ref", ""),
            "doi": entity.get("doi", ""),
            "fetched_at": entity.get("fetched_at", ""),
        }

    def _date_index_to_response(self, entity: Dict) -> Dict[str, Any]:
        return {
            "date": entity.get("date", ""),
            "total_count": entity.get("total_count", 0),
            "fetched_at": entity.get("fetched_at", ""),
        }

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.insert_paper(data)
        return self.get_paper_by_id(self._safe_str(data.get("id")))

    def remove(self, id: str) -> bool:
        collection = self._get_papers_collection()
        collection.load()
        collection.delete(f'id == "{id}"')
        return True

    def get(self, id: str) -> Optional[Dict[str, Any]]:
        return self.get_paper_by_id(id)

    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_papers_collection()
        collection.load()
        all_results = collection.query(
            expr='id != ""',
            output_fields=["id", "title", "abstract", "authors", "primary_category",
                          "categories", "published", "updated", "pdf_url", "abs_url",
                          "comment", "journal_ref", "doi", "fetched_at"],
        )
        total = len(all_results)
        sorted_results = sorted(
            all_results,
            key=lambda x: x.get("published", ""),
            reverse=True
        )
        paginated = sorted_results[offset:offset + limit]
        return [self._entity_to_response(r) for r in paginated], total

    def exists(self, id: str) -> bool:
        collection = self._get_papers_collection()
        collection.load()
        results = collection.query(expr=f'id == "{id}"', output_fields=["id"])
        return len(results) > 0

    def insert_paper(self, data: Dict[str, Any]) -> None:
        collection = self._get_papers_collection()
        now = datetime.utcnow().isoformat()

        title = self._safe_str(data.get("title"), 2048)
        abstract = self._safe_str(data.get("abstract"), 32768)
        comment = self._safe_str(data.get("comment"), 8192)
        journal_ref = self._safe_str(data.get("journal_ref"), 1024)
        doi = self._safe_str(data.get("doi"), 256)

        insert_data = [
            [self._safe_str(data.get("id"), 128)],
            [title],
            [abstract],
            [self._safe_str(json.dumps(data.get("authors") or []), 16384)],
            [self._safe_str(data.get("primary_category"), 64)],
            [self._safe_str(json.dumps(data.get("categories") or []), 2048)],
            [self._safe_str(data.get("published"), 64)],
            [self._safe_str(data.get("updated"), 64)],
            [self._safe_str(data.get("pdf_url"), 512)],
            [self._safe_str(data.get("abs_url"), 512)],
            [comment],
            [journal_ref],
            [doi],
            [now],
            [[0.0] * 8],
        ]

        collection.insert(insert_data)
        # collection.flush()

    def insert_papers_batch(self, papers: List[Dict[str, Any]]) -> int:
        if not papers:
            return 0

        collection = self._get_papers_collection()
        collection.load()
        now = datetime.utcnow().isoformat()

        existing_results = collection.query(
            expr='id != ""',
            output_fields=["id"],
        )
        existing_ids = {r.get("id") for r in existing_results}

        ids = []
        titles = []
        abstracts = []
        authors_list = []
        primary_categories = []
        categories_list = []
        published_list = []
        updated_list = []
        pdf_urls = []
        abs_urls = []
        comments = []
        journal_refs = []
        dois = []
        fetched_at_list = []
        embeddings = []

        inserted = 0
        for data in papers:
            paper_id = self._safe_str(data.get("id"), 128)
            if paper_id in existing_ids:
                continue

            ids.append(paper_id)
            titles.append(self._safe_str(data.get("title"), 2048))
            abstracts.append(self._safe_str(data.get("abstract"), 32768))
            authors_list.append(self._safe_str(json.dumps(data.get("authors") or []), 16384))
            primary_categories.append(self._safe_str(data.get("primary_category"), 64))
            categories_list.append(self._safe_str(json.dumps(data.get("categories") or []), 2048))
            published_list.append(self._safe_str(data.get("published"), 64))
            updated_list.append(self._safe_str(data.get("updated"), 64))
            pdf_urls.append(self._safe_str(data.get("pdf_url"), 512))
            abs_urls.append(self._safe_str(data.get("abs_url"), 512))
            comments.append(self._safe_str(data.get("comment"), 8192))
            journal_refs.append(self._safe_str(data.get("journal_ref"), 1024))
            dois.append(self._safe_str(data.get("doi"), 256))
            fetched_at_list.append(now)
            embeddings.append([0.0] * 8)
            inserted += 1

        if inserted > 0:
            insert_data = [
                ids, titles, abstracts, authors_list, primary_categories,
                categories_list, published_list, updated_list, pdf_urls,
                abs_urls, comments, journal_refs, dois,
                fetched_at_list, embeddings,
            ]
            collection.insert(insert_data)
            collection.flush()

        return inserted

    def get_date_index(self, date: str) -> Optional[Dict[str, Any]]:
        collection = self._get_date_index_collection()
        collection.load()
        results = collection.query(
            expr=f'date == "{date}"',
            output_fields=["date", "total_count", "fetched_at"],
        )
        if results:
            return self._date_index_to_response(results[0])
        return None

    def insert_date_index(self, date: str, total_count: int) -> None:
        collection = self._get_date_index_collection()
        collection.load()
        now = datetime.utcnow().isoformat()

        existing = collection.query(expr=f'date == "{date}"', output_fields=["date"])
        if existing:
            collection.delete(f'date == "{date}"')

        insert_data = [
            [date],
            [total_count],
            [now],
            [[0.0] * 8],
        ]
        collection.insert(insert_data)
        collection.flush()

    def query_papers_by_date(
        self,
        date: str,
        category: Optional[str] = None,
        start: int = 0,
        max_results: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        collection = self._get_papers_collection()
        collection.load()

        all_results = collection.query(
            expr='id != ""',
            output_fields=["id", "title", "abstract", "authors", "primary_category",
                          "categories", "published", "updated", "pdf_url", "abs_url",
                          "comment", "journal_ref", "doi", "fetched_at"],
        )

        filtered = []
        for r in all_results:
            published = r.get("published", "")
            if not published.startswith(date):
                continue

            if category:
                categories_str = r.get("categories", "[]")
                try:
                    categories = json.loads(categories_str)
                    if category not in categories:
                        continue
                except json.JSONDecodeError:
                    continue

            filtered.append(r)

        sorted_results = sorted(
            filtered,
            key=lambda x: x.get("published", ""),
            reverse=True
        )

        total = len(sorted_results)
        paginated = sorted_results[start:start + max_results]

        return [self._entity_to_response(r) for r in paginated], total

    def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        collection = self._get_papers_collection()
        collection.load()
        results = collection.query(
            expr=f'id == "{paper_id}"',
            output_fields=["id", "title", "abstract", "authors", "primary_category",
                          "categories", "published", "updated", "pdf_url", "abs_url",
                          "comment", "journal_ref", "doi", "fetched_at"],
        )
        if results:
            return self._entity_to_response(results[0])
        return None

    def delete_date_index(self, date: str) -> None:
        collection = self._get_date_index_collection()
        collection.load()
        collection.delete(f'date == "{date}"')

    def delete_all_date_index(self) -> None:
        collection = self._get_date_index_collection()
        collection.load()
        all_results = collection.query(
            expr='date != ""',
            output_fields=["date"],
        )
        for r in all_results:
            collection.delete(f'date == "{r.get("date")}"')

    def get_all_date_indexes(self) -> List[Dict[str, Any]]:
        collection = self._get_date_index_collection()
        collection.load()
        results = collection.query(
            expr='date != ""',
            output_fields=["date", "total_count", "fetched_at"],
        )
        sorted_results = sorted(
            results,
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        return [self._date_index_to_response(r) for r in sorted_results]

    def get_total_paper_count(self) -> int:
        collection = self._get_papers_collection()
        collection.load()
        results = collection.query(
            expr='id != ""',
            output_fields=["id"],
        )
        return len(results)
