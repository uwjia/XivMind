import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.db.milvus.paper_embedding_repo import MilvusPaperEmbeddingRepository


class TestMilvusPaperEmbeddingRepository:
    @pytest.fixture
    def mock_collection(self):
        collection = Mock()
        collection.load = Mock()
        collection.insert = Mock()
        collection.flush = Mock()
        collection.query = Mock(return_value=[])
        collection.search = Mock(return_value=[])
        collection.delete = Mock()
        return collection

    @pytest.fixture
    def repo(self, mock_collection):
        with patch('app.db.milvus.paper_embedding_repo.milvus_client') as mock_client:
            mock_client.get_collection.return_value = mock_collection
            repo = MilvusPaperEmbeddingRepository()
            repo._collection = mock_collection
            return repo

    def test_insert_embedding(self, repo, mock_collection):
        embedding = [0.1] * 1536
        
        result = repo.insert_embedding(
            paper_id="2301.12345",
            embedding=embedding,
            model_name="text-embedding-ada-002"
        )

        assert result["paper_id"] == "2301.12345"
        assert result["embedding_model"] == "text-embedding-ada-002"
        assert "created_at" in result
        mock_collection.insert.assert_called_once()
        mock_collection.flush.assert_called_once()

    def test_insert_embeddings_batch(self, repo, mock_collection):
        mock_collection.query.return_value = []
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": [0.1] * 1536, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": [0.2] * 1536, "model_name": "test-model"},
        ]
        
        result = repo.insert_embeddings_batch(embeddings_data)

        assert result == 2
        mock_collection.insert.assert_called_once()

    def test_insert_embeddings_batch_skip_existing(self, repo, mock_collection):
        mock_collection.query.return_value = [
            {"paper_id": "2301.12345"},
        ]
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": [0.1] * 1536, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": [0.2] * 1536, "model_name": "test-model"},
        ]
        
        result = repo.insert_embeddings_batch(embeddings_data)

        assert result == 1

    def test_insert_embeddings_batch_empty(self, repo, mock_collection):
        result = repo.insert_embeddings_batch([])
        assert result == 0
        mock_collection.insert.assert_not_called()

    def test_get_embedding(self, repo, mock_collection):
        mock_collection.query.return_value = [
            {
                "paper_id": "2301.12345",
                "embedding": [0.1] * 1536,
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
            }
        ]
        
        result = repo.get_embedding("2301.12345")

        assert result is not None
        assert result["paper_id"] == "2301.12345"
        assert result["embedding_model"] == "test-model"

    def test_get_embedding_not_found(self, repo, mock_collection):
        mock_collection.query.return_value = []
        
        result = repo.get_embedding("nonexistent")

        assert result is None

    def test_get_embeddings_batch(self, repo, mock_collection):
        mock_collection.query.return_value = [
            {"paper_id": "2301.12345", "embedding": [0.1] * 1536, "embedding_model": "test-model", "created_at": "2024-01-01"},
            {"paper_id": "2301.12346", "embedding": [0.2] * 1536, "embedding_model": "test-model", "created_at": "2024-01-01"},
        ]
        
        result = repo.get_embeddings_batch(["2301.12345", "2301.12346"])

        assert len(result) == 2
        assert "2301.12345" in result
        assert "2301.12346" in result

    def test_get_embeddings_batch_empty(self, repo, mock_collection):
        result = repo.get_embeddings_batch([])
        assert result == {}

    def test_search_similar(self, repo, mock_collection):
        mock_hit = Mock()
        mock_hit.entity.get = Mock(side_effect=lambda x: {
            "paper_id": "2301.12345",
            "embedding_model": "test-model",
            "created_at": "2024-01-01",
        }.get(x))
        mock_hit.score = 0.95
        
        mock_search_result = [mock_hit]
        mock_collection.search.return_value = [mock_search_result]
        
        query_embedding = [0.1] * 1536
        result = repo.search_similar(query_embedding, top_k=5)

        assert len(result) == 1
        assert result[0]["paper_id"] == "2301.12345"
        assert result[0]["similarity_score"] == 0.95

    def test_search_similar_with_filter(self, repo, mock_collection):
        mock_hit = Mock()
        mock_hit.entity.get = Mock(side_effect=lambda x: {
            "paper_id": "2301.12345",
            "embedding_model": "test-model",
            "created_at": "2024-01-01",
        }.get(x))
        mock_hit.score = 0.95
        
        mock_collection.search.return_value = [[mock_hit]]
        
        query_embedding = [0.1] * 1536
        result = repo.search_similar(
            query_embedding, 
            top_k=5, 
            paper_ids=["2301.12345", "2301.12346"]
        )

        assert len(result) == 1
        mock_collection.search.assert_called_once()
        call_kwargs = mock_collection.search.call_args[1]
        assert call_kwargs["expr"] is not None

    def test_search_similar_empty_result(self, repo, mock_collection):
        mock_collection.search.return_value = []
        
        query_embedding = [0.1] * 1536
        result = repo.search_similar(query_embedding, top_k=5)

        assert result == []

    def test_delete_embedding(self, repo, mock_collection):
        result = repo.delete_embedding("2301.12345")

        assert result is True
        mock_collection.delete.assert_called_once()
        mock_collection.flush.assert_called_once()

    def test_delete_embedding_error(self, repo, mock_collection):
        mock_collection.delete.side_effect = Exception("Delete error")
        
        result = repo.delete_embedding("2301.12345")

        assert result is False

    def test_delete_embeddings_batch(self, repo, mock_collection):
        result = repo.delete_embeddings_batch(["2301.12345", "2301.12346"])

        assert result == 2
        mock_collection.delete.assert_called_once()

    def test_delete_embeddings_batch_empty(self, repo, mock_collection):
        result = repo.delete_embeddings_batch([])
        assert result == 0

    def test_delete_embeddings_batch_error(self, repo, mock_collection):
        mock_collection.delete.side_effect = Exception("Delete error")
        
        result = repo.delete_embeddings_batch(["2301.12345"])

        assert result == 0

    def test_count_embeddings(self, repo, mock_collection):
        mock_collection.query.return_value = [
            {"paper_id": "2301.12345"},
            {"paper_id": "2301.12346"},
            {"paper_id": "2301.12347"},
        ]
        
        result = repo.count_embeddings()

        assert result == 3

    def test_get_paper_ids_without_embeddings(self, repo, mock_collection):
        mock_collection.query.return_value = [
            {"paper_id": "2301.12345"},
            {"paper_id": "2301.12346"},
        ]
        
        all_ids = ["2301.12345", "2301.12346", "2301.12347", "2301.12348"]
        result = repo.get_paper_ids_without_embeddings(all_ids)

        assert len(result) == 2
        assert "2301.12347" in result
        assert "2301.12348" in result

    def test_get_paper_ids_without_embeddings_empty_input(self, repo, mock_collection):
        result = repo.get_paper_ids_without_embeddings([])
        assert result == []
