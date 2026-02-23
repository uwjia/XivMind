from app.db.base import PaperRepository
from app.db.milvus.client import milvus_client, Collection
from app.config import get_settings
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

settings = get_settings()


class MilvusPaperRepository(PaperRepository):
    def __init__(self):
        self._papers_collection: Optional[Collection] = None
        self._date_index_collection: Optional[Collection] = None
        self._embedding_index_collection: Optional[Collection] = None

    def _get_papers_collection(self) -> Collection:
        if not self._papers_collection:
            self._papers_collection = milvus_client.get_collection("papers")
        return self._papers_collection

    def _get_date_index_collection(self) -> Collection:
        if not self._date_index_collection:
            self._date_index_collection = milvus_client.get_collection("date_index")
        return self._date_index_collection

    def _get_embedding_index_collection(self) -> Collection:
        if not self._embedding_index_collection:
            self._embedding_index_collection = milvus_client.get_collection("embedding_index")
        return self._embedding_index_collection

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
        total = collection.num_entities
        
        results = collection.query(
            expr='id != ""',
            output_fields=["id", "title", "abstract", "authors", "primary_category",
                          "categories", "published", "updated", "pdf_url", "abs_url",
                          "comment", "journal_ref", "doi", "fetched_at"],
            limit=offset + limit,
        )
        sorted_results = sorted(
            results,
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

        paper_ids_to_insert = [self._safe_str(p.get("id"), 128) for p in papers]
        
        existing_ids = set()
        batch_size = settings.MILVUS_QUERY_BATCH_SIZE
        for i in range(0, len(paper_ids_to_insert), batch_size):
            batch = paper_ids_to_insert[i:i + batch_size]
            ids_str = ", ".join([f'"{pid}"' for pid in batch])
            results = collection.query(
                expr=f'id in [{ids_str}]',
                output_fields=["id"],
            )
            existing_ids.update(r.get("id") for r in results)

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

        next_date = self._get_next_date(date)
        base_expr = f'published >= "{date}" && published < "{next_date}"'
        
        if category:
            expr = f'{base_expr} && categories like "%\\"{category}\\"%"'
        else:
            expr = base_expr

        results = collection.query(
            expr=expr,
            output_fields=["id", "title", "abstract", "authors", "primary_category",
                          "categories", "published", "updated", "pdf_url", "abs_url",
                          "comment", "journal_ref", "doi", "fetched_at"],
        )

        sorted_results = sorted(
            results,
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
        collection.delete('date != ""')
        collection.flush()

    def get_all_date_indexes(self) -> List[Dict[str, Any]]:
        collection = self._get_date_index_collection()
        collection.load()
        total = collection.num_entities
        results = collection.query(
            expr='date != ""',
            output_fields=["date", "total_count", "fetched_at"],
            limit=total,
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
        return collection.num_entities

    def get_all_paper_ids(self) -> List[str]:
        """Get all paper IDs."""
        collection = self._get_papers_collection()
        collection.load()
        total = collection.num_entities
        results = collection.query(
            expr='id != ""',
            output_fields=["id"],
            limit=total,
        )
        return [r.get("id") for r in results if r.get("id")]

    def get_papers_by_ids(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        """Get papers by a list of IDs."""
        if not paper_ids:
            return []
        
        collection = self._get_papers_collection()
        collection.load()
        
        all_results = []
        batch_size = settings.MILVUS_QUERY_BATCH_SIZE
        
        for i in range(0, len(paper_ids), batch_size):
            batch = paper_ids[i:i + batch_size]
            ids_str = ", ".join([f'"{pid}"' for pid in batch])
            results = collection.query(
                expr=f'id in [{ids_str}]',
                output_fields=["id", "title", "abstract", "authors", "primary_category",
                              "categories", "published", "updated", "pdf_url", "abs_url",
                              "comment", "journal_ref", "doi", "fetched_at"],
            )
            all_results.extend(results)
        
        return [self._entity_to_response(r) for r in all_results]

    def get_paper_ids_by_date_range(
        self,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[str]:
        """Get paper IDs filtered by date or date range."""
        collection = self._get_papers_collection()
        collection.load()
        
        if date:
            next_date = self._get_next_date(date)
            expr = f'published >= "{date}" && published < "{next_date}"'
        elif date_from and date_to:
            expr = f'published >= "{date_from}" && published <= "{date_to}"'
        elif date_from:
            expr = f'published >= "{date_from}"'
        elif date_to:
            expr = f'published <= "{date_to}"'
        else:
            expr = 'id != ""'
        
        results = collection.query(
            expr=expr,
            output_fields=["id"],
            limit=settings.MILVUS_QUERY_BATCH_SIZE,
        )
        
        return [r.get("id") for r in results if r.get("id")]

    def get_paper_ids_by_filters(
        self,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = settings.MILVUS_QUERY_BATCH_SIZE,
    ) -> List[str]:
        """Get paper IDs filtered by category and/or date range.
        
        This method pushes filtering to the database level for better performance.
        """
        collection = self._get_papers_collection()
        collection.load()
        
        conditions = []
        
        if category:
            conditions.append(f'categories like "%\\"{category}\\"%"')
        
        if date_from and date_to:
            conditions.append(f'published >= "{date_from}" && published <= "{date_to}"')
        elif date_from:
            conditions.append(f'published >= "{date_from}"')
        elif date_to:
            conditions.append(f'published <= "{date_to}"')
        
        if conditions:
            expr = " && ".join(conditions)
        else:
            expr = 'id != ""'
        
        results = collection.query(
            expr=expr,
            output_fields=["id"],
            limit=limit,
        )
        
        return [r.get("id") for r in results if r.get("id")]

    def _get_next_date(self, date: str) -> str:
        """Get the next date for range query."""
        from datetime import datetime, timedelta
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            next_dt = dt + timedelta(days=1)
            return next_dt.strftime("%Y-%m-%d")
        except ValueError:
            return date

    def _embedding_index_to_response(self, entity: Dict) -> Dict[str, Any]:
        return {
            "date": entity.get("date", ""),
            "total_count": entity.get("total_count", 0),
            "generated_at": entity.get("generated_at", ""),
            "model_name": entity.get("model_name", ""),
        }

    def get_embedding_index(self, date: str) -> Optional[Dict[str, Any]]:
        """Get embedding index by date string."""
        collection = self._get_embedding_index_collection()
        collection.load()
        results = collection.query(
            expr=f'date == "{date}"',
            output_fields=["date", "total_count", "generated_at", "model_name"],
        )
        if results:
            return self._embedding_index_to_response(results[0])
        return None

    def insert_embedding_index(self, date: str, total_count: int, model_name: str = "") -> None:
        """Insert or update embedding index."""
        collection = self._get_embedding_index_collection()
        collection.load()
        now = datetime.utcnow().isoformat()

        existing = collection.query(expr=f'date == "{date}"', output_fields=["date"])
        if existing:
            collection.delete(f'date == "{date}"')

        insert_data = [
            [date],
            [total_count],
            [now],
            [self._safe_str(model_name, 128)],
            [[0.0] * 8],
        ]
        collection.insert(insert_data)
        collection.flush()

    def get_all_embedding_indexes(self) -> List[Dict[str, Any]]:
        """Get all embedding indexes."""
        collection = self._get_embedding_index_collection()
        collection.load()
        total = collection.num_entities
        results = collection.query(
            expr='date != ""',
            output_fields=["date", "total_count", "generated_at", "model_name"],
            limit=total,
        )
        sorted_results = sorted(
            results,
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        return [self._embedding_index_to_response(r) for r in sorted_results]

    def delete_embedding_index(self, date: str) -> None:
        """Delete embedding index by date."""
        collection = self._get_embedding_index_collection()
        collection.load()
        collection.delete(f'date == "{date}"')
        collection.flush()
