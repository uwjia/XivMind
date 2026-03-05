import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from app.db.base import PaperRepository
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBPaperRepository(PaperRepository):
    """LanceDB implementation for Paper storage."""
    
    def __init__(self):
        self._papers_table = None
        self._date_index_table = None
        self._embedding_index_table = None
    
    def _get_papers_table(self):
        if self._papers_table is None:
            self._papers_table = lancedb_client.get_table("papers")
        return self._papers_table
    
    def _get_date_index_table(self):
        if self._date_index_table is None:
            self._date_index_table = lancedb_client.get_table("date_index")
        return self._date_index_table
    
    def _get_embedding_index_table(self):
        if self._embedding_index_table is None:
            self._embedding_index_table = lancedb_client.get_table("embedding_index")
        return self._embedding_index_table
    
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
            "authors": json.loads(row.get("authors", "[]")) if row.get("authors") else [],
            "primary_category": row.get("primary_category", ""),
            "categories": json.loads(row.get("categories", "[]")) if row.get("categories") else [],
            "published": row.get("published", ""),
            "updated": row.get("updated", ""),
            "pdf_url": row.get("pdf_url", ""),
            "abs_url": row.get("abs_url", ""),
            "comment": row.get("comment", ""),
            "journal_ref": row.get("journal_ref", ""),
            "doi": row.get("doi", ""),
            "fetched_at": row.get("fetched_at", ""),
        }
    
    def _date_index_to_response(self, row) -> Dict[str, Any]:
        return {
            "date": row.get("date", ""),
            "total_count": row.get("total_count", 0),
            "fetched_at": row.get("fetched_at", ""),
        }
    
    def _embedding_index_to_response(self, row) -> Dict[str, Any]:
        return {
            "date": row.get("date", ""),
            "total_count": row.get("total_count", 0),
            "generated_at": row.get("generated_at", ""),
            "model_name": row.get("model_name", ""),
        }
    
    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.insert_paper(data)
        return self.get_paper_by_id(self._safe_str(data.get("id")))
    
    def remove(self, id: str) -> bool:
        table = self._get_papers_table()
        table.delete(f"id = '{id}'")
        return True
    
    def get(self, id: str) -> Optional[Dict[str, Any]]:
        return self.get_paper_by_id(id)
    
    def get_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_papers_table()
        df = table.to_pandas()
        total = len(df)
        
        if total == 0:
            return [], 0
        
        df_sorted = df.sort_values(by="published", ascending=False)
        df_paginated = df_sorted.iloc[offset:offset + limit]
        
        results = [self._entity_to_response(row) for _, row in df_paginated.iterrows()]
        return results, total
    
    def exists(self, id: str) -> bool:
        table = self._get_papers_table()
        results = table.search().where(f"id = '{id}'").limit(1).to_pandas()
        return len(results) > 0
    
    def insert_paper(self, data: Dict[str, Any]) -> None:
        table = self._get_papers_table()
        now = datetime.utcnow().isoformat()
        
        record = {
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
            "embedding": [0.0] * 8,
        }
        
        table.add([record])
    
    def insert_papers_batch(self, papers: List[Dict[str, Any]]) -> int:
        if not papers:
            return 0
        
        table = self._get_papers_table()
        df = table.to_pandas()
        existing_ids = set(df["id"].tolist()) if len(df) > 0 else set()
        
        now = datetime.utcnow().isoformat()
        records = []
        inserted = 0
        
        for data in papers:
            paper_id = self._safe_str(data.get("id"), 128)
            if paper_id in existing_ids:
                continue
            
            record = {
                "id": paper_id,
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
                "embedding": [0.0] * 8,
            }
            records.append(record)
            inserted += 1
        
        if records:
            table.add(records)
        
        return inserted
    
    def get_date_index(self, date: str) -> Optional[Dict[str, Any]]:
        table = self._get_date_index_table()
        results = table.search().where(f"date = '{date}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._date_index_to_response(results.iloc[0])
    
    def insert_date_index(self, date: str, total_count: int) -> None:
        table = self._get_date_index_table()
        now = datetime.utcnow().isoformat()
        
        table.delete(f"date = '{date}'")
        
        record = {
            "date": date,
            "total_count": total_count,
            "fetched_at": now,
            "embedding": [0.0] * 8,
        }
        table.add([record])
    
    def _get_next_date(self, date: str) -> str:
        try:
            dt = datetime.strptime(date, "%Y-%m-%d")
            next_dt = dt + timedelta(days=1)
            return next_dt.strftime("%Y-%m-%d")
        except ValueError:
            return date
    
    def query_papers_by_date(
        self,
        date: str,
        category: Optional[str] = None,
        start: int = 0,
        max_results: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_papers_table()
        df = table.to_pandas()
        
        next_date = self._get_next_date(date)
        mask = (df["published"] >= date) & (df["published"] < next_date)
        
        if category:
            mask &= df["categories"].str.contains(f'"{category}"', na=False)
        
        filtered = df[mask]
        total = len(filtered)
        
        if total == 0:
            return [], 0
        
        sorted_df = filtered.sort_values(by="published", ascending=False)
        paginated = sorted_df.iloc[start:start + max_results]
        
        results = [self._entity_to_response(row) for _, row in paginated.iterrows()]
        return results, total
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        table = self._get_papers_table()
        results = table.search().where(f"id = '{paper_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._entity_to_response(results.iloc[0])
    
    def delete_date_index(self, date: str) -> None:
        table = self._get_date_index_table()
        table.delete(f"date = '{date}'")
    
    def delete_all_date_index(self) -> None:
        table = self._get_date_index_table()
        df = table.to_pandas()
        for _, row in df.iterrows():
            table.delete(f"date = '{row['date']}'")
    
    def get_all_date_indexes(self) -> List[Dict[str, Any]]:
        table = self._get_date_index_table()
        df = table.to_pandas()
        
        if len(df) == 0:
            return []
        
        sorted_df = df.sort_values(by="date", ascending=False)
        return [self._date_index_to_response(row) for _, row in sorted_df.iterrows()]
    
    def get_total_paper_count(self) -> int:
        table = self._get_papers_table()
        df = table.to_pandas()
        return len(df)
    
    def get_all_paper_ids(self) -> List[str]:
        table = self._get_papers_table()
        df = table.to_pandas()
        return df["id"].tolist() if len(df) > 0 else []
    
    def get_papers_by_ids(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        if not paper_ids:
            return []
        
        table = self._get_papers_table()
        df = table.to_pandas()
        
        if len(df) == 0:
            return []
        
        filtered = df[df["id"].isin(paper_ids)]
        return [self._entity_to_response(row) for _, row in filtered.iterrows()]
    
    def get_paper_ids_by_date_range(
        self,
        date: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[str]:
        table = self._get_papers_table()
        df = table.to_pandas()
        
        if len(df) == 0:
            return []
        
        if date:
            next_date = self._get_next_date(date)
            mask = (df["published"] >= date) & (df["published"] < next_date)
        elif date_from and date_to:
            mask = (df["published"] >= date_from) & (df["published"] <= date_to)
        elif date_from:
            mask = df["published"] >= date_from
        elif date_to:
            mask = df["published"] <= date_to
        else:
            mask = pd.Series([True] * len(df))
        
        filtered = df[mask]
        return filtered["id"].tolist()
    
    def get_paper_ids_by_filters(
        self,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 1000,
    ) -> List[str]:
        table = self._get_papers_table()
        df = table.to_pandas()
        
        if len(df) == 0:
            return []
        
        mask = pd.Series([True] * len(df))
        
        if category:
            mask &= df["categories"].str.contains(f'"{category}"', na=False)
        
        if date_from and date_to:
            mask &= (df["published"] >= date_from) & (df["published"] <= date_to)
        elif date_from:
            mask &= df["published"] >= date_from
        elif date_to:
            mask &= df["published"] <= date_to
        
        filtered = df[mask].head(limit)
        return filtered["id"].tolist()
    
    def get_embedding_index(self, date: str) -> Optional[Dict[str, Any]]:
        table = self._get_embedding_index_table()
        results = table.search().where(f"date = '{date}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._embedding_index_to_response(results.iloc[0])
    
    def insert_embedding_index(self, date: str, total_count: int, model_name: str = "") -> None:
        table = self._get_embedding_index_table()
        now = datetime.utcnow().isoformat()
        
        table.delete(f"date = '{date}'")
        
        record = {
            "date": date,
            "total_count": total_count,
            "generated_at": now,
            "model_name": model_name,
            "embedding": [0.0] * 8,
        }
        table.add([record])
    
    def get_all_embedding_indexes(self) -> List[Dict[str, Any]]:
        table = self._get_embedding_index_table()
        df = table.to_pandas()
        
        if len(df) == 0:
            return []
        
        sorted_df = df.sort_values(by="date", ascending=False)
        return [self._embedding_index_to_response(row) for _, row in sorted_df.iterrows()]
    
    def delete_embedding_index(self, date: str) -> None:
        table = self._get_embedding_index_table()
        table.delete(f"date = '{date}'")
