import pytest
from unittest.mock import Mock, patch
import pandas as pd

from app.db.lancedb.paper_embedding_repo import LanceDBPaperEmbeddingRepository


class TestLanceDBPaperEmbeddingRepositoryInsertEmbedding:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_insert_embedding_success(self, repo, sample_embedding):
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.insert_embedding(
                paper_id="2301.12345",
                embedding=sample_embedding,
                model_name="text-embedding-ada-002"
            )
            
            assert result["paper_id"] == "2301.12345"
            assert result["embedding_model"] == "text-embedding-ada-002"
            assert "created_at" in result
            mock_table.add.assert_called_once()

    def test_insert_embedding_creates_valid_record(self, repo, sample_embedding):
        mock_table = Mock()
        added_record = None
        
        def capture_add(records):
            nonlocal added_record
            added_record = records[0]
        
        mock_table.add = Mock(side_effect=capture_add)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            repo.insert_embedding(
                paper_id="2301.12345",
                embedding=sample_embedding,
                model_name="test-model"
            )
            
            assert added_record["paper_id"] == "2301.12345"
            assert added_record["embedding"] == sample_embedding
            assert added_record["embedding_model"] == "test-model"


class TestLanceDBPaperEmbeddingRepositoryInsertEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_insert_embeddings_batch_success(self, repo, sample_embedding):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.add = Mock()
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": sample_embedding, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": sample_embedding, "model_name": "test-model"},
        ]
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.insert_embeddings_batch(embeddings_data)
            
            assert result == 2
            mock_table.add.assert_called_once()

    def test_insert_embeddings_batch_skip_existing(self, repo, sample_embedding):
        mock_table = Mock()
        df = pd.DataFrame([{"paper_id": "2301.12345"}])
        mock_table.to_pandas = Mock(return_value=df)
        mock_table.add = Mock()
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": sample_embedding, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": sample_embedding, "model_name": "test-model"},
        ]
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.insert_embeddings_batch(embeddings_data)
            
            assert result == 1

    def test_insert_embeddings_batch_empty(self, repo):
        mock_table = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.insert_embeddings_batch([])
            
            assert result == 0


class TestLanceDBPaperEmbeddingRepositoryUpsertEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_upsert_embeddings_batch_success(self, repo, sample_embedding):
        mock_table = Mock()
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": sample_embedding, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": sample_embedding, "model_name": "test-model"},
        ]
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.upsert_embeddings_batch(embeddings_data)
            
            assert result == 2
            assert mock_table.delete.call_count == 2
            mock_table.add.assert_called_once()

    def test_upsert_embeddings_batch_empty(self, repo):
        mock_table = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.upsert_embeddings_batch([])
            
            assert result == 0


class TestLanceDBPaperEmbeddingRepositoryGetEmbedding:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_get_embedding_found(self, repo, sample_embedding):
        mock_table = Mock()
        df = pd.DataFrame([{
            "paper_id": "2301.12345",
            "embedding": sample_embedding,
            "embedding_model": "test-model",
            "created_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_embedding("2301.12345")
            
            assert result is not None
            assert result["paper_id"] == "2301.12345"
            assert result["embedding_model"] == "test-model"

    def test_get_embedding_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_embedding("nonexistent")
            
            assert result is None


class TestLanceDBPaperEmbeddingRepositoryGetEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_get_embeddings_batch_success(self, repo, sample_embedding):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "paper_id": "2301.12345",
                "embedding": sample_embedding,
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
            },
            {
                "paper_id": "2301.12346",
                "embedding": sample_embedding,
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
            },
        ])
        
        mock_scanner = Mock()
        mock_scanner.to_table.return_value.to_pandas.return_value = df
        mock_lance_ds = Mock()
        mock_lance_ds.scanner.return_value = mock_scanner
        mock_table.to_lance.return_value = mock_lance_ds
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_embeddings_batch(["2301.12345", "2301.12346"])
            
            assert len(result) == 2
            assert "2301.12345" in result
            assert "2301.12346" in result

    def test_get_embeddings_batch_empty_input(self, repo):
        mock_table = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_embeddings_batch([])
            
            assert result == {}

    def test_get_embeddings_batch_empty_table(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_scanner = Mock()
        mock_scanner.to_table.return_value.to_pandas.return_value = df
        mock_lance_ds = Mock()
        mock_lance_ds.scanner.return_value = mock_scanner
        mock_table.to_lance.return_value = mock_lance_ds
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_embeddings_batch(["2301.12345"])
            
            assert result == {}


class TestLanceDBPaperEmbeddingRepositorySearchSimilar:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_search_similar_success(self, repo, sample_embedding):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "paper_id": "2301.12345",
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
                "_distance": 0.1,
            },
            {
                "paper_id": "2301.12346",
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
                "_distance": 0.2,
            },
        ])
        
        mock_search = Mock()
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.search_similar(sample_embedding, top_k=5)
            
            assert len(result) == 2
            assert "similarity_score" in result[0]
            assert result[0]["similarity_score"] == 0.9

    def test_search_similar_with_paper_ids_filter(self, repo, sample_embedding):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "paper_id": "2301.12345",
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
                "_distance": 0.1,
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.search_similar(
                sample_embedding,
                top_k=5,
                paper_ids=["2301.12345", "2301.12346"]
            )
            
            assert len(result) == 1

    def test_search_similar_error(self, repo, sample_embedding):
        mock_table = Mock()
        mock_table.search = Mock(side_effect=Exception("Search error"))
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.search_similar(sample_embedding, top_k=5)
            
            assert result == []


class TestLanceDBPaperEmbeddingRepositoryDeleteEmbedding:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_delete_embedding_success(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.delete_embedding("2301.12345")
            
            assert result is True
            mock_table.delete.assert_called_once()

    def test_delete_embedding_error(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock(side_effect=Exception("Delete error"))
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.delete_embedding("2301.12345")
            
            assert result is False


class TestLanceDBPaperEmbeddingRepositoryDeleteEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_delete_embeddings_batch_success(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.delete_embeddings_batch(["2301.12345", "2301.12346"])
            
            assert result == 2

    def test_delete_embeddings_batch_empty(self, repo):
        mock_table = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.delete_embeddings_batch([])
            
            assert result == 0

    def test_delete_embeddings_batch_partial_error(self, repo):
        mock_table = Mock()
        call_count = [0]
        
        def mock_delete(query):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Delete error")
        
        mock_table.delete = Mock(side_effect=mock_delete)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.delete_embeddings_batch(["2301.12345", "2301.12346", "2301.12347"])
            
            assert result == 2


class TestLanceDBPaperEmbeddingRepositoryCountEmbeddings:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_count_embeddings(self, repo):
        mock_table = Mock()
        mock_table.count_rows.return_value = 3
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.count_embeddings()
            
            assert result == 3

    def test_count_embeddings_empty(self, repo):
        mock_table = Mock()
        mock_table.count_rows.return_value = 0
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.count_embeddings()
            
            assert result == 0


class TestLanceDBPaperEmbeddingRepositoryGetPaperIdsWithoutEmbeddings:
    @pytest.fixture
    def repo(self):
        return LanceDBPaperEmbeddingRepository()

    def test_get_paper_ids_without_embeddings(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "2301.12345"},
            {"paper_id": "2301.12346"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        all_ids = ["2301.12345", "2301.12346", "2301.12347", "2301.12348"]
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_paper_ids_without_embeddings(all_ids)
            
            assert len(result) == 2
            assert "2301.12347" in result
            assert "2301.12348" in result

    def test_get_paper_ids_without_embeddings_empty_input(self, repo):
        mock_table = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_paper_ids_without_embeddings([])
            
            assert result == []

    def test_get_paper_ids_without_embeddings_all_exist(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {"paper_id": "2301.12345"},
            {"paper_id": "2301.12346"},
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        all_ids = ["2301.12345", "2301.12346"]
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_paper_ids_without_embeddings(all_ids)
            
            assert result == []
