import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.db.milvus.paper_embedding_repo import MilvusPaperEmbeddingRepository


class TestMilvusPaperEmbeddingRepositoryInsertEmbedding:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_insert_embedding_success(self, repo):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.insert_embedding(
                paper_id="2301.12345",
                embedding=[0.1] * 1536,
                model_name="text-embedding-ada-002"
            )
            
            assert result["paper_id"] == "2301.12345"
            assert result["embedding_model"] == "text-embedding-ada-002"
            assert "created_at" in result
            mock_collection.insert.assert_called_once()

    def test_insert_embedding_creates_valid_data(self, repo):
        mock_collection = Mock()
        inserted_data = None
        
        def capture_insert(data):
            nonlocal inserted_data
            inserted_data = data
        
        mock_collection.insert = Mock(side_effect=capture_insert)
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            repo.insert_embedding(
                paper_id="2301.12345",
                embedding=[0.1] * 1536,
                model_name="test-model"
            )
            
            assert inserted_data is not None
            assert len(inserted_data) == 4
            assert inserted_data[0][0] == "2301.12345"
            assert inserted_data[2][0] == "test-model"


class TestMilvusPaperEmbeddingRepositoryInsertEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_insert_embeddings_batch_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        mock_collection.upsert = Mock()
        mock_collection.flush = Mock()
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": [0.1] * 1536, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": [0.1] * 1536, "model_name": "test-model"},
        ]
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.insert_embeddings_batch(embeddings_data)
                
                assert result == 2
                mock_collection.upsert.assert_called_once()

    def test_insert_embeddings_batch_skip_existing(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{"paper_id": "2301.12345"}])
        mock_collection.upsert = Mock()
        mock_collection.flush = Mock()
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": [0.1] * 1536, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": [0.1] * 1536, "model_name": "test-model"},
        ]
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.insert_embeddings_batch(embeddings_data)
                
                assert result == 1

    def test_insert_embeddings_batch_empty(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.insert_embeddings_batch([])
            
            assert result == 0


class TestMilvusPaperEmbeddingRepositoryUpsertEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_upsert_embeddings_batch_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.upsert = Mock()
        mock_collection.flush = Mock()
        
        embeddings_data = [
            {"paper_id": "2301.12345", "embedding": [0.1] * 1536, "model_name": "test-model"},
            {"paper_id": "2301.12346", "embedding": [0.1] * 1536, "model_name": "test-model"},
        ]
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.upsert_embeddings_batch(embeddings_data)
            
            assert result == 2
            mock_collection.upsert.assert_called_once()

    def test_upsert_embeddings_batch_empty(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.upsert_embeddings_batch([])
            
            assert result == 0


class TestMilvusPaperEmbeddingRepositoryGetEmbedding:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_get_embedding_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[{
            "paper_id": "2301.12345",
            "embedding": [0.1] * 1536,
            "embedding_model": "test-model",
            "created_at": "2024-01-01T00:00:00",
        }])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_embedding("2301.12345")
            
            assert result is not None
            assert result["paper_id"] == "2301.12345"
            assert result["embedding_model"] == "test-model"

    def test_get_embedding_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_embedding("nonexistent")
            
            assert result is None


class TestMilvusPaperEmbeddingRepositoryGetEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_get_embeddings_batch_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {
                "paper_id": "2301.12345",
                "embedding": [0.1] * 1536,
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
            },
            {
                "paper_id": "2301.12346",
                "embedding": [0.1] * 1536,
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
            },
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_embeddings_batch(["2301.12345", "2301.12346"])
                
                assert len(result) == 2
                assert "2301.12345" in result
                assert "2301.12346" in result

    def test_get_embeddings_batch_empty_input(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_embeddings_batch([])
            
            assert result == {}

    def test_get_embeddings_batch_truncates_large_input(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        paper_ids = [f"2301.{i:05d}" for i in range(2000)]
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_embeddings_batch(paper_ids)
                
                assert result == {}


class TestMilvusPaperEmbeddingRepositorySearchSimilar:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_search_similar_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        
        mock_hit = Mock()
        mock_hit.score = 0.9
        mock_hit.entity = {
            "paper_id": "2301.12345",
            "embedding_model": "test-model",
            "created_at": "2024-01-01T00:00:00",
        }
        
        mock_collection.search = Mock(return_value=[[mock_hit]])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.search_similar([0.1] * 1536, top_k=5)
            
            assert len(result) == 1
            assert "similarity_score" in result[0]
            assert result[0]["similarity_score"] == pytest.approx((0.9 + 1) / 2, rel=1e-3)

    def test_search_similar_with_paper_ids_filter(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        
        mock_hit = Mock()
        mock_hit.score = 0.85
        mock_hit.entity = {
            "paper_id": "2301.12345",
            "embedding_model": "test-model",
            "created_at": "2024-01-01T00:00:00",
        }
        
        mock_collection.search = Mock(return_value=[[mock_hit]])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.search_similar(
                    [0.1] * 1536,
                    top_k=5,
                    paper_ids=["2301.12345", "2301.12346"]
                )
                
                assert len(result) == 1
                mock_collection.search.assert_called_once()
                call_kwargs = mock_collection.search.call_args[1]
                assert call_kwargs["expr"] == 'paper_id in ["2301.12345", "2301.12346"]'

    def test_search_similar_empty_results(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.search = Mock(return_value=[[]])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.search_similar([0.1] * 1536, top_k=5)
            
            assert result == []

    def test_search_similar_with_entity_dict_format(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        
        mock_hit = Mock()
        mock_hit.score = 0.9
        mock_hit.entity = {
            "entity": {
                "paper_id": "2301.12345",
                "embedding_model": "test-model",
                "created_at": "2024-01-01T00:00:00",
            }
        }
        
        mock_collection.search = Mock(return_value=[[mock_hit]])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.search_similar([0.1] * 1536, top_k=5)
            
            assert len(result) == 1
            assert result[0]["paper_id"] == "2301.12345"


class TestMilvusPaperEmbeddingRepositoryDeleteEmbedding:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_delete_embedding_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.delete_embedding("2301.12345")
            
            assert result is True
            mock_collection.delete.assert_called_once()

    def test_delete_embedding_error(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock(side_effect=Exception("Delete error"))
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.delete_embedding("2301.12345")
            
            assert result is False


class TestMilvusPaperEmbeddingRepositoryDeleteEmbeddingsBatch:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_delete_embeddings_batch_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.delete_embeddings_batch(["2301.12345", "2301.12346"])
                
                assert result == 2

    def test_delete_embeddings_batch_empty(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.delete_embeddings_batch([])
            
            assert result == 0

    def test_delete_embeddings_batch_partial_error(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        call_count = [0]
        
        def mock_delete(expr):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Delete error")
        
        mock_collection.delete = Mock(side_effect=mock_delete)
        mock_collection.flush = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1
                result = repo.delete_embeddings_batch(["2301.12345", "2301.12346", "2301.12347"])
                
                assert result == 2


class TestMilvusPaperEmbeddingRepositoryCountEmbeddings:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_count_embeddings(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 100
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.count_embeddings()
            
            assert result == 100


class TestMilvusPaperEmbeddingRepositoryGetPaperIdsWithoutEmbeddings:
    @pytest.fixture
    def repo(self):
        return MilvusPaperEmbeddingRepository()

    def test_get_paper_ids_without_embeddings(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"paper_id": "2301.12345"},
            {"paper_id": "2301.12346"},
        ])
        
        all_ids = ["2301.12345", "2301.12346", "2301.12347", "2301.12348"]
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_paper_ids_without_embeddings(all_ids)
                
                assert len(result) == 2
                assert "2301.12347" in result
                assert "2301.12348" in result

    def test_get_paper_ids_without_embeddings_empty_input(self, repo):
        mock_collection = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_paper_ids_without_embeddings([])
            
            assert result == []

    def test_get_paper_ids_without_embeddings_all_exist(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {"paper_id": "2301.12345"},
            {"paper_id": "2301.12346"},
        ])
        
        all_ids = ["2301.12345", "2301.12346"]
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.paper_embedding_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                result = repo.get_paper_ids_without_embeddings(all_ids)
                
                assert result == []
