import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.db.base import PaperEmbeddingRepository
from app.db.lancedb.client import lancedb_client

logger = logging.getLogger(__name__)


class LanceDBPaperEmbeddingRepository(PaperEmbeddingRepository):
    """LanceDB implementation for Paper Embedding storage."""
    
    def __init__(self):
        self._table = None
    
    def _get_table(self):
        if self._table is None:
            self._table = lancedb_client.get_table("paper_embeddings")
        return self._table
    
    def insert_embedding(
        self,
        paper_id: str,
        embedding: List[float],
        model_name: str,
    ) -> Dict[str, Any]:
        table = self._get_table()
        now = datetime.utcnow().isoformat()
        
        record = {
            "paper_id": paper_id,
            "embedding": embedding,
            "embedding_model": model_name,
            "created_at": now,
        }
        
        table.add([record])
        
        return {
            "paper_id": paper_id,
            "embedding_model": model_name,
            "created_at": now,
        }
    
    def insert_embeddings_batch(
        self,
        embeddings_data: List[Dict[str, Any]],
    ) -> int:
        if not embeddings_data:
            return 0
        
        table = self._get_table()
        df = table.to_pandas()
        existing_ids = set(df["paper_id"].tolist()) if len(df) > 0 else set()
        
        now = datetime.utcnow().isoformat()
        records = []
        inserted = 0
        
        for data in embeddings_data:
            paper_id = data.get("paper_id")
            if paper_id in existing_ids:
                continue
            
            record = {
                "paper_id": paper_id,
                "embedding": data.get("embedding", []),
                "embedding_model": data.get("model_name", ""),
                "created_at": now,
            }
            records.append(record)
            inserted += 1
        
        if records:
            table.add(records)
        
        return inserted
    
    def upsert_embeddings_batch(
        self,
        embeddings_data: List[Dict[str, Any]],
    ) -> int:
        if not embeddings_data:
            return 0
        
        table = self._get_table()
        now = datetime.utcnow().isoformat()
        
        records = []
        paper_ids_to_delete = []
        
        for data in embeddings_data:
            paper_id = data.get("paper_id")
            paper_ids_to_delete.append(paper_id)
            
            record = {
                "paper_id": paper_id,
                "embedding": data.get("embedding", []),
                "embedding_model": data.get("model_name", ""),
                "created_at": now,
            }
            records.append(record)
        
        for paper_id in paper_ids_to_delete:
            table.delete(f"paper_id = '{paper_id}'")
        
        if records:
            table.add(records)
        
        return len(records)
    
    def get_embedding(self, paper_id: str) -> Optional[Dict[str, Any]]:
        table = self._get_table()
        results = table.search().where(f"paper_id = '{paper_id}'").limit(1).to_pandas()
        
        if len(results) == 0:
            return None
        
        row = results.iloc[0]
        return {
            "paper_id": row.get("paper_id"),
            "embedding": list(row.get("embedding")) if row.get("embedding") else None,
            "embedding_model": row.get("embedding_model"),
            "created_at": row.get("created_at"),
        }
    
    def get_embeddings_batch(self, paper_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        if not paper_ids:
            return {}
        
        table = self._get_table()
        df = table.to_pandas()
        
        if len(df) == 0:
            return {}
        
        filtered = df[df["paper_id"].isin(paper_ids)]
        
        result = {}
        for _, row in filtered.iterrows():
            pid = row.get("paper_id")
            result[pid] = {
                "paper_id": pid,
                "embedding": list(row.get("embedding")) if row.get("embedding") else None,
                "embedding_model": row.get("embedding_model"),
                "created_at": row.get("created_at"),
            }
        
        return result
    
    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 10,
        paper_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        table = self._get_table()
        
        try:
            if paper_ids and len(paper_ids) > 0:
                paper_ids_str = ",".join([f"'{pid}'" for pid in paper_ids])
                results = table.search(
                    query_embedding,
                    vector_column_name="embedding"
                ).where(f"paper_id in ({paper_ids_str})").limit(top_k).to_pandas()
            else:
                results = table.search(
                    query_embedding,
                    vector_column_name="embedding"
                ).limit(top_k).to_pandas()
            
            similar_papers = []
            for _, row in results.iterrows():
                similar_papers.append({
                    "paper_id": row.get("paper_id"),
                    "similarity_score": 1 - row.get("_distance", 0),
                    "embedding_model": row.get("embedding_model"),
                    "created_at": row.get("created_at"),
                })
            
            return similar_papers
        except Exception as e:
            logger.error(f"Failed to search similar papers: {e}")
            return []
    
    def delete_embedding(self, paper_id: str) -> bool:
        table = self._get_table()
        
        try:
            table.delete(f"paper_id = '{paper_id}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete embedding for {paper_id}: {e}")
            return False
    
    def delete_embeddings_batch(self, paper_ids: List[str]) -> int:
        if not paper_ids:
            return 0
        
        table = self._get_table()
        deleted = 0
        
        for paper_id in paper_ids:
            try:
                table.delete(f"paper_id = '{paper_id}'")
                deleted += 1
            except Exception as e:
                logger.error(f"Failed to delete embedding for {paper_id}: {e}")
        
        return deleted
    
    def count_embeddings(self) -> int:
        table = self._get_table()
        df = table.to_pandas()
        return len(df)
    
    def get_paper_ids_without_embeddings(
        self,
        all_paper_ids: List[str],
    ) -> List[str]:
        if not all_paper_ids:
            return []
        
        table = self._get_table()
        df = table.to_pandas()
        existing_ids = set(df["paper_id"].tolist()) if len(df) > 0 else set()
        
        return [pid for pid in all_paper_ids if pid not in existing_ids]
