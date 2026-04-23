import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.base import PaperCodeRepository
from app.db.lancedb.client import lancedb_client
from app.db.lancedb.schemas.paper_codes import PaperCodeSchema

logger = logging.getLogger(__name__)


class LanceDBPaperCodeRepository(PaperCodeRepository):
    """Repository for paper code repository links."""
    
    def __init__(self):
        self._table = None
        self.schema = PaperCodeSchema()
    
    def _get_table(self):
        if self._table is None:
            self._table = lancedb_client.get_table("paper_codes")
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
            "url": row.get("url", ""),
            "platform": row.get("platform", ""),
            "owner": row.get("owner", ""),
            "repo": row.get("repo", ""),
            "is_official": row.get("is_official", True),
            "stars": row.get("stars", 0),
            "language": row.get("language", ""),
            "fetched_at": row.get("fetched_at", ""),
        }
    
    def upsert_paper_codes(self, codes: List[Dict[str, Any]]) -> int:
        """Upsert paper code records using merge_insert."""
        if not codes:
            return 0
        
        table = self._get_table()
        now = datetime.utcnow().isoformat()
        records = []
        
        for code in codes:
            paper_id = self._safe_str(code.get("paper_id"))
            record = {
                "id": paper_id,
                "paper_id": paper_id,
                "url": self._safe_str(code.get("url")),
                "platform": self._safe_str(code.get("platform")),
                "owner": self._safe_str(code.get("owner")),
                "repo": self._safe_str(code.get("repo")),
                "is_official": code.get("is_official", True),
                "stars": code.get("stars", 0) or 0,
                "language": self._safe_str(code.get("language")),
                "fetched_at": self._safe_str(code.get("fetched_at") or now),
            }
            records.append(record)
        
        try:
            table.merge_insert("id") \
                .when_matched_update_all() \
                .when_not_matched_insert_all() \
                .execute(records)
            return len(records)
        except Exception as e:
            logger.error(f"Failed to upsert paper codes with merge_insert: {e}")
            raise
    
    def get_code_by_paper_id(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get code repository for a paper."""
        table = self._get_table()
        
        if table is None or table.count_rows() == 0:
            return None
        
        try:
            results = table.search().where(f"id = '{paper_id}'").limit(1).to_pandas()
            if len(results) == 0:
                return None
            return self._entity_to_response(results.iloc[0])
        except Exception as e:
            logger.warning(f"Failed to get code for paper {paper_id}: {e}")
            return None
    
    def get_paper_ids_with_code(self) -> List[str]:
        """Get all paper IDs that have code repositories."""
        table = self._get_table()
        
        if table is None or table.count_rows() == 0:
            return []
        
        try:
            df = table.to_pandas()
            return df["paper_id"].unique().tolist()
        except Exception as e:
            logger.warning(f"Failed to get paper IDs with code: {e}")
            return []
    
    def check_batch(self, paper_ids: List[str]) -> Dict[str, bool]:
        """Check which papers have code repositories."""
        if not paper_ids:
            return {}
        
        result = {pid: False for pid in paper_ids}
        
        table = self._get_table()
        
        if table is None or table.count_rows() == 0:
            return result
        
        try:
            import lance
            lance_ds = table.to_lance()
            escaped_ids = [pid.replace("'", "''") for pid in paper_ids]
            ids_str = ", ".join(f"'{pid}'" for pid in escaped_ids)
            filter_str = f"id IN ({ids_str})"
            
            scanner = lance_ds.scanner(
                columns=["id"],
                filter=filter_str,
            )
            df = scanner.to_table().to_pandas()
            
            found_ids = set(df["id"].tolist())
            
            for pid in found_ids:
                if pid in result:
                    result[pid] = True
            
            return result
        except Exception as e:
            logger.warning(f"Failed to check batch for code: {e}")
            df = table.to_pandas()
            
            if df.empty or "id" not in df.columns:
                return result
            
            found_ids = set(df[df["id"].isin(paper_ids)]["id"].tolist())
            
            for pid in found_ids:
                if pid in result:
                    result[pid] = True
            
            return result
    
    def get_codes_by_paper_ids(self, paper_ids: List[str]) -> Dict[str, Optional[Dict[str, Any]]]:
        """Get code repositories for multiple papers."""
        if not paper_ids:
            return {}
        
        result = {pid: None for pid in paper_ids}
        
        table = self._get_table()
        
        if table is None or table.count_rows() == 0:
            return result
        
        try:
            import lance
            lance_ds = table.to_lance()
            escaped_ids = [pid.replace("'", "''") for pid in paper_ids]
            ids_str = ", ".join(f"'{pid}'" for pid in escaped_ids)
            filter_str = f"id IN ({ids_str})"
            
            scanner = lance_ds.scanner(
                columns=["id", "paper_id", "url", "platform", "owner", "repo", "is_official", "stars", "language", "fetched_at"],
                filter=filter_str,
            )
            df = scanner.to_table().to_pandas()
            
            for _, row in df.iterrows():
                paper_id = row.get("id")
                if paper_id in result:
                    result[paper_id] = self._entity_to_response(row)
            
            return result
        except Exception as e:
            logger.warning(f"Failed to get codes for papers: {e}")
            df = table.to_pandas()
            
            if df.empty or "id" not in df.columns:
                return result
            
            filtered = df[df["id"].isin(paper_ids)]
            for _, row in filtered.iterrows():
                paper_id = row.get("id")
                if paper_id in result:
                    result[paper_id] = self._entity_to_response(row)
            
            return result
