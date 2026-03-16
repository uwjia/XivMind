import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import lance
from lance.dataset import ColumnOrdering

from app.db.base import DownloadRepository
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBDownloadRepository(DownloadRepository):
    """LanceDB implementation for Download task storage."""
    
    def __init__(self):
        self._table = None
    
    def _get_table(self):
        if self._table is None:
            self._table = lancedb_client.get_table("downloads")
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
            "paper_id": row.get("paper_id", ""),
            "arxiv_id": row.get("arxiv_id", ""),
            "title": row.get("title", ""),
            "pdf_url": row.get("pdf_url", ""),
            "status": row.get("status", "pending"),
            "progress": row.get("progress", 0),
            "file_path": row.get("file_path", ""),
            "file_size": row.get("file_size", 0),
            "error_message": row.get("error_message", ""),
            "created_at": row.get("created_at", ""),
            "updated_at": row.get("updated_at", ""),
        }
    
    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        table = self._get_table()
        task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        title = self._safe_str(data.get("title"), 1024)
        status = data.get("status", "pending")
        progress = data.get("progress", 0)
        file_path = data.get("file_path", "")
        file_size = data.get("file_size", 0)
        created_at = data.get("created_at", now)
        updated_at = data.get("updated_at", now)
        
        record = {
            "id": task_id,
            "paper_id": self._safe_str(data.get("paper_id")),
            "arxiv_id": self._safe_str(data.get("arxiv_id")),
            "title": title,
            "pdf_url": self._safe_str(data.get("pdf_url")),
            "status": status,
            "progress": progress,
            "file_path": self._safe_str(file_path) if file_path else "",
            "file_size": file_size,
            "error_message": "",
            "created_at": created_at,
            "updated_at": updated_at,
            "embedding": [0.0] * 8,
        }
        
        table.add([record])
        
        return {
            "id": task_id,
            "paper_id": self._safe_str(data.get("paper_id")),
            "arxiv_id": self._safe_str(data.get("arxiv_id")),
            "title": title,
            "pdf_url": self._safe_str(data.get("pdf_url")),
            "status": status,
            "progress": progress,
            "file_path": self._safe_str(file_path) if file_path else "",
            "file_size": file_size,
            "error_message": "",
            "created_at": created_at,
            "updated_at": updated_at,
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
                    "id", "paper_id", "arxiv_id", "title", "pdf_url",
                    "status", "progress", "file_path", "file_size",
                    "error_message", "created_at", "updated_at"
                ],
                limit=limit,
                offset=offset,
                order_by=[ColumnOrdering("created_at", ascending=False)],
            )
            df = scanner.to_table().to_pandas()
            
            results = [self._entity_to_response(row) for _, row in df.iterrows()]
            return results, total
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner, falling back to pandas: {e}")
            df = table.to_pandas()
            total = len(df)
            if total == 0:
                return [], 0
            df_sorted = df.sort_values(by="created_at", ascending=False)
            df_paginated = df_sorted.iloc[offset:offset + limit]
            results = [self._entity_to_response(row) for _, row in df_paginated.iterrows()]
            return results, total
    
    def count_completed(self) -> int:
        table = self._get_table()
        
        try:
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=["status"],
                filter="status = 'completed'",
            )
            df = scanner.to_table().to_pandas()
            return len(df)
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner for count_completed, falling back to pandas: {e}")
            df = table.to_pandas()
            return len(df[df["status"] == "completed"])
    
    def exists(self, id: str) -> bool:
        table = self._get_table()
        results = table.search().where(f"id = '{id}'").limit(1).to_pandas()
        return len(results) > 0
    
    def get_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        table = self._get_table()
        results = table.search().where(f"paper_id = '{paper_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        return self._entity_to_response(results.iloc[0])
    
    def get_all_by_paper_id(self, paper_id: str) -> List[Dict[str, Any]]:
        table = self._get_table()
        results = table.search().where(f"paper_id = '{paper_id}'").to_pandas()
        
        return [self._entity_to_response(row) for _, row in results.iterrows()]
    
    def update_status(
        self,
        task_id: str,
        status: str,
        progress: int = 0,
        file_path: Optional[str] = None,
        file_size: int = 0,
        error_message: Optional[str] = None,
    ) -> bool:
        table = self._get_table()
        results = table.search().where(f"id = '{task_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return False
        
        row = results.iloc[0]
        now = datetime.utcnow().isoformat()
        
        updated_record = {
            "id": task_id,
            "paper_id": row.get("paper_id", ""),
            "arxiv_id": row.get("arxiv_id", ""),
            "title": row.get("title", ""),
            "pdf_url": row.get("pdf_url", ""),
            "status": status,
            "progress": progress,
            "file_path": file_path if file_path is not None else row.get("file_path", ""),
            "file_size": file_size if file_size else row.get("file_size", 0),
            "error_message": error_message if error_message is not None else row.get("error_message", ""),
            "created_at": row.get("created_at", ""),
            "updated_at": now,
            "embedding": [0.0] * 8,
        }
        
        table.delete(f"id = '{task_id}'")
        table.add([updated_record])
        
        return True
    
    def reset_incomplete_tasks(self) -> int:
        table = self._get_table()
        
        try:
            lance_ds = table.to_lance()
            filter_str = "status IN ('downloading', 'pending')"
            
            scanner = lance_ds.scanner(
                columns=[
                    "id", "paper_id", "arxiv_id", "title", "pdf_url",
                    "status", "progress", "file_path", "file_size",
                    "error_message", "created_at", "updated_at"
                ],
                filter=filter_str,
            )
            incomplete = scanner.to_table().to_pandas()
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner for reset_incomplete_tasks, falling back to pandas: {e}")
            df = table.to_pandas()
            mask = df["status"].isin(["downloading", "pending"])
            incomplete = df[mask]
        
        if len(incomplete) == 0:
            return 0
        
        count = 0
        now = datetime.utcnow().isoformat()
        
        for _, row in incomplete.iterrows():
            updated_record = {
                "id": row.get("id"),
                "paper_id": row.get("paper_id", ""),
                "arxiv_id": row.get("arxiv_id", ""),
                "title": row.get("title", ""),
                "pdf_url": row.get("pdf_url", ""),
                "status": "failed",
                "progress": row.get("progress", 0),
                "file_path": row.get("file_path", ""),
                "file_size": row.get("file_size", 0),
                "error_message": "Download interrupted - please retry",
                "created_at": row.get("created_at", ""),
                "updated_at": now,
                "embedding": [0.0] * 8,
            }
            
            table.delete(f"id = '{row.get('id')}'")
            table.add([updated_record])
            count += 1
        
        return count
    
    def check_batch(self, paper_ids: List[str]) -> Dict[str, bool]:
        if not paper_ids:
            return {}
        
        table = self._get_table()
        
        try:
            paper_ids_str = ", ".join(f"'{pid}'" for pid in paper_ids)
            filter_str = f"paper_id IN ({paper_ids_str}) AND status = 'completed'"
            
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=["paper_id"],
                filter=filter_str,
            )
            df = scanner.to_table().to_pandas()
            completed_paper_ids = set(df["paper_id"].tolist())
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner for check_batch, falling back to pandas: {e}")
            df = table.to_pandas()
            completed_df = df[(df["paper_id"].isin(paper_ids)) & (df["status"] == "completed")]
            completed_paper_ids = set(completed_df["paper_id"].tolist())
        
        return {paper_id: paper_id in completed_paper_ids for paper_id in paper_ids}

    def get_incomplete(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_table()
        
        try:
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=[
                    "id", "paper_id", "arxiv_id", "title", "pdf_url",
                    "status", "progress", "file_path", "file_size",
                    "error_message", "created_at", "updated_at"
                ],
                filter="status != 'completed'",
                limit=limit,
                offset=offset,
                order_by=[ColumnOrdering("created_at", ascending=False)],
            )
            df = scanner.to_table().to_pandas()
            total = len(df)
            return [self._entity_to_response(row) for _, row in df.iterrows()], total
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner for get_incomplete, falling back to pandas: {e}")
            df = table.to_pandas()
            incomplete_df = df[df["status"] != "completed"]
            total = len(incomplete_df)
            return [self._entity_to_response(row) for _, row in incomplete_df.iterrows()], total

    def get_completed_paginated(self, limit: int = 100, offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        table = self._get_table()
        
        try:
            lance_ds = table.to_lance()
            scanner = lance_ds.scanner(
                columns=[
                    "id", "paper_id", "arxiv_id", "title", "pdf_url",
                    "status", "progress", "file_path", "file_size",
                    "error_message", "created_at", "updated_at"
                ],
                filter="status = 'completed'",
                limit=limit,
                offset=offset,
                order_by=[ColumnOrdering("created_at", ascending=False)],
            )
            df = scanner.to_table().to_pandas()
            total = len(df)
            return [self._entity_to_response(row) for _, row in df.iterrows()], total
        except Exception as e:
            logger.warning(f"Failed to use Lance scanner for get_completed_paginated, falling back to pandas: {e}")
            df = table.to_pandas()
            completed_df = df[df["status"] == "completed"]
            total = len(completed_df)
            return [self._entity_to_response(row) for _, row in completed_df.iterrows()], total
