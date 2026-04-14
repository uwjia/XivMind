from typing import Dict, Any, List, Optional
from app.db.base import PaperEmbeddingRepository


class SQLitePaperEmbeddingRepository(PaperEmbeddingRepository):
    """SQLite implementation of PaperEmbeddingRepository.
    
    This is a stub implementation that raises NotImplementedError
    because paper embedding functionality requires Milvus vector database.
    """
    
    def _not_supported(self):
        raise NotImplementedError(
            "Paper embedding functionality is not available in SQLite mode. "
            "Please use LanceDB or Milvus for vector similarity search features."
        )

    def insert_embedding(
        self, 
        paper_id: str, 
        embedding: List[float], 
        model_name: str
    ) -> Dict[str, Any]:
        self._not_supported()

    def insert_embeddings_batch(
        self, 
        embeddings_data: List[Dict[str, Any]]
    ) -> int:
        self._not_supported()

    def upsert_embeddings_batch(
        self, 
        embeddings_data: List[Dict[str, Any]]
    ) -> int:
        self._not_supported()

    def get_embedding(self, paper_id: str) -> Optional[Dict[str, Any]]:
        self._not_supported()

    def get_embeddings_batch(self, paper_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        self._not_supported()

    def search_similar(
        self, 
        query_embedding: List[float], 
        top_k: int = 10,
        paper_ids: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        self._not_supported()

    def delete_embedding(self, paper_id: str) -> bool:
        self._not_supported()

    def delete_embeddings_batch(self, paper_ids: List[str]) -> int:
        self._not_supported()

    def count_embeddings(self) -> int:
        self._not_supported()

    def get_paper_ids_without_embeddings(
        self, 
        all_paper_ids: List[str]
    ) -> List[str]:
        self._not_supported()
