import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import lance
import pandas as pd
from lance.dataset import ColumnOrdering

from app.db.base import ListingsRepository
from app.db.lancedb.client import lancedb_client
from app.core.utils import safe_json_loads

logger = logging.getLogger(__name__)


class LanceDBListingsRepository(ListingsRepository):
    """LanceDB implementation for arXiv new listings storage."""
    
    def __init__(self):
        self._new_submissions_table = None
        self._cross_submissions_table = None
        self._replacement_submissions_table = None
        self._listings_date_index_table = None
    
    def _get_new_submissions_table(self):
        if self._new_submissions_table is None:
            self._new_submissions_table = lancedb_client.get_table("new_submissions")
        return self._new_submissions_table
    
    def _get_cross_submissions_table(self):
        if self._cross_submissions_table is None:
            self._cross_submissions_table = lancedb_client.get_table("cross_submissions")
        return self._cross_submissions_table
    
    def _get_replacement_submissions_table(self):
        if self._replacement_submissions_table is None:
            self._replacement_submissions_table = lancedb_client.get_table("replacement_submissions")
        return self._replacement_submissions_table
    
    def _get_listings_date_index_table(self):
        if self._listings_date_index_table is None:
            self._listings_date_index_table = lancedb_client.get_table("listings_date_index")
        return self._listings_date_index_table
    
    @staticmethod
    def _safe_str(value, max_len=None) -> str:
        if value is None:
            return ""
        s = str(value)
        return s[:max_len] if max_len else s
    
    def _entity_to_response(self, row) -> Dict[str, Any]:
        return {
            "id": row.get("id", ""),
            "title": row.get("title", ""),
            "abstract": row.get("abstract", ""),
            "authors": safe_json_loads(row.get("authors"), []),
            "primary_category": row.get("primary_category", ""),
            "categories": safe_json_loads(row.get("categories"), []),
            "published": row.get("published", ""),
            "updated": row.get("updated", ""),
            "pdf_url": row.get("pdf_url", ""),
            "abs_url": row.get("abs_url", ""),
            "comment": row.get("comment", ""),
            "journal_ref": row.get("journal_ref", ""),
            "doi": row.get("doi", ""),
            "fetched_at": row.get("fetched_at", ""),
            "listing_date": row.get("listing_date", ""),
        }
    
    def _listings_date_index_to_response(self, row) -> Dict[str, Any]:
        return {
            "date": row.get("date", ""),
            "new_count": row.get("new_count", 0),
            "cross_count": row.get("cross_count", 0),
            "replacement_count": row.get("replacement_count", 0),
            "fetched_at": row.get("fetched_at", ""),
        }
    
    def _prepare_paper_record(self, data: Dict[str, Any], listing_date: str = None) -> Dict[str, Any]:
        now = datetime.utcnow().isoformat()
        return {
            "id": self._safe_str(data.get("id"), 128),
            "title": self._safe_str(data.get("title"), 2048),
            "abstract": self._safe_str(data.get("abstract"), 32768),
            "authors": self._safe_str(json.dumps(data.get("authors") or []), 16384),
            "primary_category": self._safe_str(data.get("primary_category"), 64),
            "categories": self._safe_str(json.dumps(data.get("categories") or []), 2048),
            "published": self._safe_str(data.get("published"), 64),
            "updated": self._safe_str(data.get("updated"), 64),
            "pdf_url": self._safe_str(data.get("pdf_url"), 512),
            "abs_url": self._safe_str(data.get("abs_url"), 512),
            "comment": self._safe_str(data.get("comment"), 8192),
            "journal_ref": self._safe_str(data.get("journal_ref"), 1024),
            "doi": self._safe_str(data.get("doi"), 256),
            "fetched_at": now,
            "listing_date": listing_date or now[:10],
            "embedding": [0.0] * 8,
        }
    
    def _insert_submissions_batch(self, table, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        if not papers:
            return 0
        
        records = [self._prepare_paper_record(data, listing_date) for data in papers]
        
        try:
            table.merge_insert("id") \
                .when_matched_update_all() \
                .when_not_matched_insert_all() \
                .execute(records)
            return len(records)
        except Exception as e:
            logger.error(f"Failed to upsert submissions batch: {e}")
            table.add(records)
            return len(records)
    
    def insert_new_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        table = self._get_new_submissions_table()
        return self._insert_submissions_batch(table, papers, listing_date)
    
    def insert_cross_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        table = self._get_cross_submissions_table()
        return self._insert_submissions_batch(table, papers, listing_date)
    
    def insert_replacement_submissions_batch(self, papers: List[Dict[str, Any]], listing_date: str = None) -> int:
        table = self._get_replacement_submissions_table()
        return self._insert_submissions_batch(table, papers, listing_date)
    
    def insert_listings_date_index(
        self,
        date: str,
        new_count: int,
        cross_count: int,
        replacement_count: int
    ) -> None:
        table = self._get_listings_date_index_table()
        now = datetime.utcnow().isoformat()
        
        record = {
            "date": date,
            "new_count": new_count,
            "cross_count": cross_count,
            "replacement_count": replacement_count,
            "fetched_at": now,
            "embedding": [0.0] * 8,
        }
        
        try:
            table.merge_insert("date") \
                .when_matched_update_all() \
                .when_not_matched_insert_all() \
                .execute([record])
        except Exception as e:
            logger.error(f"Failed to upsert listings date index: {e}")
            table.add([record])
    
    def get_listings_date_indexes(self) -> List[Dict[str, Any]]:
        table = self._get_listings_date_index_table()
        
        try:
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=["date", "new_count", "cross_count", "replacement_count", "fetched_at"],
                order_by=[ColumnOrdering("date", ascending=False)],
            )
            df = scanner.to_table().to_pandas()
            return [self._listings_date_index_to_response(row) for _, row in df.iterrows()]
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner: {e}")
            df = table.to_pandas()
            if len(df) == 0:
                return []
            df_sorted = df.sort_values(by="date", ascending=False)
            return [self._listings_date_index_to_response(row) for _, row in df_sorted.iterrows()]
    
    def get_listings_date_index(self, date: str) -> Optional[Dict[str, Any]]:
        table = self._get_listings_date_index_table()
        
        try:
            results = table.search().where(f"date = '{date}'").limit(1).to_pandas()
            if len(results) > 0:
                return self._listings_date_index_to_response(results.iloc[0])
        except Exception as e:
            logger.error(f"Failed to get listings date index: {e}")
        
        return None
    
    def get_latest_listings_date_index(self) -> Optional[Dict[str, Any]]:
        table = self._get_listings_date_index_table()
        
        try:
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=["date", "new_count", "cross_count", "replacement_count", "fetched_at"],
                order_by=[ColumnOrdering("date", ascending=False)],
                limit=1,
            )
            df = scanner.to_table().to_pandas()
            if len(df) > 0:
                return self._listings_date_index_to_response(df.iloc[0])
        except Exception as e:
            logger.error(f"Failed to get latest listings date index: {e}")
        
        return None
    
    def _get_submissions_by_date(
        self,
        table,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        try:
            lance_ds = table.to_lance()
            filter_str = f"listing_date == '{date}'"

            total = lance_ds.scanner(columns=["id"], filter=filter_str).to_table().num_rows

            if total == 0:
                return [], 0

            scanner = lance_ds.scanner(
                columns=[
                    "id", "title", "abstract", "authors", "primary_category",
                    "categories", "published", "updated", "pdf_url", "abs_url",
                    "comment", "journal_ref", "doi", "fetched_at", "listing_date"
                ],
                filter=filter_str,
                limit=max_results,
                offset=start,
                order_by=[ColumnOrdering("published", ascending=False)],
            )
            df = scanner.to_table().to_pandas()
            
            results = [self._entity_to_response(row) for _, row in df.iterrows()]
            return results, total
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner: {e}")
            df = table.to_pandas()
            total = len(df)
            if total == 0:
                return [], 0
            df_sorted = df.sort_values(by="published", ascending=False)
            df_paginated = df_sorted.iloc[start:start + max_results]
            results = [self._entity_to_response(row) for _, row in df_paginated.iterrows()]
            return results, total
    
    def get_new_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_new_submissions_table()
        return self._get_submissions_by_date(table, date, start, max_results)
    
    def get_cross_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_cross_submissions_table()
        return self._get_submissions_by_date(table, date, start, max_results)
    
    def get_replacement_submissions(
        self,
        date: str,
        start: int = 0,
        max_results: int = 50
    ) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_replacement_submissions_table()
        return self._get_submissions_by_date(table, date, start, max_results)
    
    def clear_listings_by_date(self, date: str) -> None:
        new_table = self._get_new_submissions_table()
        cross_table = self._get_cross_submissions_table()
        replacement_table = self._get_replacement_submissions_table()
        index_table = self._get_listings_date_index_table()
        
        try:
            new_table.delete(f"listing_date == '{date}'")
            cross_table.delete(f"listing_date == '{date}'")
            replacement_table.delete(f"listing_date == '{date}'")
            index_table.delete(f"date = '{date}'")
        except Exception as e:
            logger.error(f"Failed to clear listings by date: {e}")
