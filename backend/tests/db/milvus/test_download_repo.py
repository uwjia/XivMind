import pytest
from unittest.mock import Mock, patch

from app.db.milvus.download_repo import MilvusDownloadRepository


class TestMilvusDownloadRepositoryAdd:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_add_success(self, repo, sample_download_data):
        mock_collection = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.add(sample_download_data)
            
            assert "id" in result
            assert result["paper_id"] == sample_download_data["paper_id"]
            assert result["title"] == sample_download_data["title"]
            assert result["status"] == "pending"
            assert result["progress"] == 0
            mock_collection.insert.assert_called_once()

    def test_add_creates_valid_insert_data(self, repo, sample_download_data):
        mock_collection = Mock()
        inserted_data = None
        
        def capture_insert(data):
            nonlocal inserted_data
            inserted_data = data
        
        mock_collection.insert = Mock(side_effect=capture_insert)
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            repo.add(sample_download_data)
            
            assert inserted_data is not None
            assert len(inserted_data) == 13
            assert inserted_data[5][0] == "pending"
            assert inserted_data[6][0] == 0

    def test_add_with_long_title_truncation(self, repo):
        long_title = "A" * 2000
        data = {
            "paper_id": "2301.12345",
            "title": long_title,
        }
        
        mock_collection = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.add(data)
            
            assert len(result["title"]) == 1024


class TestMilvusDownloadRepositoryRemove:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_remove_success(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.delete = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.remove("test-task-id")
            
            assert result is True
            mock_collection.delete.assert_called_once()


class TestMilvusDownloadRepositoryGet:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_get_existing_task(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_download_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get("test-task-id")
            
            assert result is not None
            assert result["id"] == "test-task-id"
            assert result["status"] == "completed"

    def test_get_nonexistent_task(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get("nonexistent")
            
            assert result is None


class TestMilvusDownloadRepositoryGetAll:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_get_all_with_data(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 2
        mock_collection.query = Mock(return_value=[
            {**sample_download_entity, "id": "1", "created_at": "2024-01-03T00:00:00"},
            {**sample_download_entity, "id": "2", "created_at": "2024-01-02T00:00:00"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results, total = repo.get_all()
            
            assert total == 2
            assert len(results) == 2

    def test_get_all_empty(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 0
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results, total = repo.get_all()
            
            assert total == 0
            assert results == []

    def test_get_all_with_pagination(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.num_entities = 5
        mock_collection.query = Mock(return_value=[
            {**sample_download_entity, "id": str(i), "created_at": f"2024-01-0{i}T00:00:00"}
            for i in range(1, 6)
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            results, total = repo.get_all(limit=2, offset=1)
            
            assert total == 5
            assert len(results) == 2


class TestMilvusDownloadRepositoryExists:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_exists_true(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_download_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.exists("test-id")
            
            assert result is True

    def test_exists_false(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.exists("nonexistent")
            
            assert result is False


class TestMilvusDownloadRepositoryGetByPaperId:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_get_by_paper_id_found(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_download_entity])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_by_paper_id("2301.12345v1")
            
            assert result is not None
            assert result["paper_id"] == "2301.12345v1"

    def test_get_by_paper_id_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_by_paper_id("nonexistent")
            
            assert result is None


class TestMilvusDownloadRepositoryGetAllByPaperId:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_get_all_by_paper_id(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_download_entity, "id": "1"},
            {**sample_download_entity, "id": "2"},
        ])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.get_all_by_paper_id("2301.12345v1")
            
            assert len(result) == 2


class TestMilvusDownloadRepositoryUpdateStatus:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_update_status_success(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_download_entity])
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.update_status(
                "test-task-id",
                status="downloading",
                progress=50,
            )
            
            assert result is True
            mock_collection.delete.assert_called_once()
            mock_collection.insert.assert_called_once()

    def test_update_status_with_file_path(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_download_entity])
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.update_status(
                "test-task-id",
                status="completed",
                progress=100,
                file_path="/path/to/file.pdf",
                file_size=1234567,
            )
            
            assert result is True

    def test_update_status_with_error(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[sample_download_entity])
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.update_status(
                "test-task-id",
                status="failed",
                error_message="Network error",
            )
            
            assert result is True

    def test_update_status_task_not_found(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            result = repo.update_status("nonexistent", status="completed")
            
            assert result is False


class TestMilvusDownloadRepositoryResetIncompleteTasks:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_reset_incomplete_tasks(self, repo, sample_download_entity):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[
            {**sample_download_entity, "id": "1", "status": "pending"},
            {**sample_download_entity, "id": "2", "status": "downloading"},
        ])
        mock_collection.delete = Mock()
        mock_collection.insert = Mock()
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.download_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                count = repo.reset_incomplete_tasks()
                
                assert count == 2

    def test_reset_incomplete_tasks_none(self, repo):
        mock_collection = Mock()
        mock_collection.load = Mock()
        mock_collection.query = Mock(return_value=[])
        
        with patch.object(repo, '_get_collection', return_value=mock_collection):
            with patch('app.db.milvus.download_repo.settings') as mock_settings:
                mock_settings.MILVUS_QUERY_BATCH_SIZE = 1000
                count = repo.reset_incomplete_tasks()
                
                assert count == 0


class TestMilvusDownloadRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = MilvusDownloadRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = MilvusDownloadRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = MilvusDownloadRepository._safe_str("test string", max_len=4)
        assert result == "test"


class TestMilvusDownloadRepositoryEntityToResponse:
    @pytest.fixture
    def repo(self):
        return MilvusDownloadRepository()

    def test_entity_to_response(self, repo, sample_download_entity):
        result = repo._entity_to_response(sample_download_entity)
        
        assert result["id"] == sample_download_entity["id"]
        assert result["paper_id"] == sample_download_entity["paper_id"]
        assert result["status"] == sample_download_entity["status"]

    def test_entity_to_response_with_missing_fields(self, repo):
        entity = {"id": "test-id"}
        result = repo._entity_to_response(entity)
        
        assert result["id"] == "test-id"
        assert result["status"] == "pending"
        assert result["progress"] == 0
