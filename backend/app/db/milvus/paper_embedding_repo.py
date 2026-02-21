from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pymilvus import Collection
import logging

from app.db.milvus.client import milvus_client
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MilvusPaperEmbeddingRepository:
    """Repository for paper embeddings in Milvus."""
    
    def __init__(self):
        self._collection: Optional[Collection] = None
    
    def _get_collection(self) -> Collection:
        if not self._collection:
            self._collection = milvus_client.get_collection("paper_embeddings")
        return self._collection
    
    def insert_embedding(
        self, 
        paper_id: str, 
        embedding: List[float], 
        model_name: str
    ) -> Dict[str, Any]:
        """Insert a single paper embedding."""
        collection = self._get_collection()
        now = datetime.utcnow().isoformat()
        
        insert_data = [
            [paper_id],
            [embedding],
            [model_name],
            [now],
        ]
        
        collection.insert(insert_data)
        collection.flush()
        
        return {
            "paper_id": paper_id,
            "embedding_model": model_name,
            "created_at": now,
        }
    
    def insert_embeddings_batch(
        self, 
        embeddings_data: List[Dict[str, Any]]
    ) -> int:
        """
        Insert multiple paper embeddings.
        
        Args:
            embeddings_data: List of dicts with paper_id, embedding, model_name
        
        Returns:
            Number of embeddings inserted
        """
        if not embeddings_data:
            return 0
        
        collection = self._get_collection()
        collection.load()
        
        paper_ids_to_insert = [d.get("paper_id") for d in embeddings_data]
        
        existing_ids = set()
        batch_size = settings.MILVUS_QUERY_BATCH_SIZE
        for i in range(0, len(paper_ids_to_insert), batch_size):
            batch = paper_ids_to_insert[i:i + batch_size]
            ids_str = ", ".join([f'"{pid}"' for pid in batch])
            results = collection.query(
                expr=f'paper_id in [{ids_str}]',
                output_fields=["paper_id"],
            )
            existing_ids.update(r.get("paper_id") for r in results)
        
        paper_ids = []
        embeddings = []
        model_names = []
        created_ats = []
        
        inserted = 0
        now = datetime.utcnow().isoformat()
        
        for data in embeddings_data:
            paper_id = data.get("paper_id")
            if paper_id in existing_ids:
                continue
            
            paper_ids.append(paper_id)
            embeddings.append(data.get("embedding", []))
            model_names.append(data.get("model_name", ""))
            created_ats.append(now)
            inserted += 1
        
        if inserted > 0:
            insert_data = [paper_ids, embeddings, model_names, created_ats]
            collection.insert(insert_data)
            collection.flush()
        
        return inserted
    
    def get_embedding(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Get embedding for a single paper."""
        collection = self._get_collection()
        collection.load()
        
        results = collection.query(
            expr=f'paper_id == "{paper_id}"',
            output_fields=["paper_id", "embedding", "embedding_model", "created_at"],
        )
        
        if results:
            return {
                "paper_id": results[0].get("paper_id"),
                "embedding": results[0].get("embedding"),
                "embedding_model": results[0].get("embedding_model"),
                "created_at": results[0].get("created_at"),
            }
        return None
    
    def get_embeddings_batch(self, paper_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get embeddings for multiple papers."""
        if not paper_ids:
            return {}
        
        collection = self._get_collection()
        collection.load()
        
        if len(paper_ids) > settings.MILVUS_QUERY_BATCH_SIZE:
            logger.warning(f"get_embeddings_batch: paper_ids truncated from {len(paper_ids)} to {settings.MILVUS_QUERY_BATCH_SIZE}")
            paper_ids = paper_ids[:settings.MILVUS_QUERY_BATCH_SIZE]
        
        ids_str = ", ".join([f'"{pid}"' for pid in paper_ids])
        results = collection.query(
            expr=f'paper_id in [{ids_str}]',
            output_fields=["paper_id", "embedding", "embedding_model", "created_at"],
        )
        
        return {
            r.get("paper_id"): {
                "paper_id": r.get("paper_id"),
                "embedding": r.get("embedding"),
                "embedding_model": r.get("embedding_model"),
                "created_at": r.get("created_at"),
            }
            for r in results
        }
    
    def search_similar(
        self, 
        query_embedding: List[float], 
        top_k: int = 10,
        paper_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar papers by embedding.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            paper_ids: Optional list of paper IDs to filter (max MILVUS_QUERY_BATCH_SIZE)
        
        Returns:
            List of similar papers with similarity scores
        """
        collection = self._get_collection()
        collection.load()
        
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 128},
        }
        
        expr = None
        if paper_ids and len(paper_ids) > 0:
            if len(paper_ids) > settings.MILVUS_QUERY_BATCH_SIZE:
                logger.warning(f"paper_ids filter truncated from {len(paper_ids)} to {settings.MILVUS_QUERY_BATCH_SIZE} to avoid Milvus query size limit")
                paper_ids = paper_ids[:settings.MILVUS_QUERY_BATCH_SIZE]
            ids_str = ", ".join([f'"{pid}"' for pid in paper_ids])
            expr = f'paper_id in [{ids_str}]'
        
        results = collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=expr,
            output_fields=["paper_id", "embedding_model", "created_at"],
        )
        
        similar_papers = []
        if results and len(results) > 0:
            for hit in results[0]:
                similar_papers.append({
                    "paper_id": hit.entity.get("paper_id"),
                    "similarity_score": hit.score,
                    "embedding_model": hit.entity.get("embedding_model"),
                    "created_at": hit.entity.get("created_at"),
                })
        
        return similar_papers
    
    def delete_embedding(self, paper_id: str) -> bool:
        """Delete embedding for a paper."""
        collection = self._get_collection()
        collection.load()
        
        try:
            collection.delete(f'paper_id == "{paper_id}"')
            collection.flush()
            return True
        except Exception as e:
            logger.error(f"Failed to delete embedding for {paper_id}: {e}")
            return False
    
    def delete_embeddings_batch(self, paper_ids: List[str]) -> int:
        """Delete embeddings for multiple papers."""
        if not paper_ids:
            return 0
        
        collection = self._get_collection()
        collection.load()
        
        deleted = 0
        batch_size = settings.MILVUS_QUERY_BATCH_SIZE
        
        for i in range(0, len(paper_ids), batch_size):
            batch = paper_ids[i:i + batch_size]
            try:
                ids_str = ", ".join([f'"{pid}"' for pid in batch])
                collection.delete(f'paper_id in [{ids_str}]')
                deleted += len(batch)
            except Exception as e:
                logger.error(f"Failed to delete embeddings batch: {e}")
        
        collection.flush()
        return deleted
    
    def count_embeddings(self) -> int:
        """Get total number of embeddings."""
        collection = self._get_collection()
        collection.load()
        
        stats = collection.num_entities
        return stats
    
    def get_paper_ids_without_embeddings(
        self, 
        all_paper_ids: List[str]
    ) -> List[str]:
        """Get paper IDs that don't have embeddings yet."""
        if not all_paper_ids:
            return []
        
        collection = self._get_collection()
        collection.load()
        
        existing_ids = set()
        batch_size = settings.MILVUS_QUERY_BATCH_SIZE
        
        for i in range(0, len(all_paper_ids), batch_size):
            batch = all_paper_ids[i:i + batch_size]
            ids_str = ", ".join([f'"{pid}"' for pid in batch])
            results = collection.query(
                expr=f'paper_id in [{ids_str}]',
                output_fields=["paper_id"],
            )
            existing_ids.update(r.get("paper_id") for r in results)
        
        return [pid for pid in all_paper_ids if pid not in existing_ids]
