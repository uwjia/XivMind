import pytest
from unittest.mock import Mock, patch
import pandas as pd

from app.db.lancedb.download_repo import LanceDBDownloadRepository


class TestLanceDBDownloadRepositoryAdd:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_add_success(self, repo, sample_download_data):
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.add(sample_download_data)
            
            assert "id" in result
            assert result["paper_id"] == sample_download_data["paper_id"]
            assert result["title"] == sample_download_data["title"]
            assert result["status"] == "pending"
            assert result["progress"] == 0
            mock_table.add.assert_called_once()

    def test_add_creates_valid_record(self, repo, sample_download_data):
        mock_table = Mock()
        added_record = None
        
        def capture_add(records):
            nonlocal added_record
            added_record = records[0]
        
        mock_table.add = Mock(side_effect=capture_add)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            repo.add(sample_download_data)
            
            assert "id" in added_record
            assert "created_at" in added_record
            assert "updated_at" in added_record
            assert "embedding" in added_record
            assert added_record["status"] == "pending"
            assert added_record["progress"] == 0

    def test_add_with_long_title_truncation(self, repo):
        long_title = "A" * 2000
        data = {
            "paper_id": "2301.12345",
            "title": long_title,
        }
        
        mock_table = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.add(data)
            
            assert len(result["title"]) == 1024


class TestLanceDBDownloadRepositoryRemove:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_remove_success(self, repo):
        mock_table = Mock()
        mock_table.delete = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.remove("test-task-id")
            
            assert result is True
            mock_table.delete.assert_called_once_with("id = 'test-task-id'")


class TestLanceDBDownloadRepositoryGet:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_get_existing_task(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": "test-task-id",
            "paper_id": "2301.12345",
            "arxiv_id": "2301.12345",
            "title": "Test Paper",
            "pdf_url": "https://arxiv.org/pdf/2301.12345.pdf",
            "status": "completed",
            "progress": 100,
            "file_path": "/path/to/file.pdf",
            "file_size": 1234567,
            "error_message": "",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get("test-task-id")
            
            assert result is not None
            assert result["id"] == "test-task-id"
            assert result["status"] == "completed"

    def test_get_nonexistent_task(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get("nonexistent")
            
            assert result is None


class TestLanceDBDownloadRepositoryGetAll:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_get_all_with_data(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.00001",
                "arxiv_id": "2301.00001",
                "title": "Paper 1",
                "pdf_url": "url1",
                "status": "completed",
                "progress": 100,
                "file_path": "/path/1.pdf",
                "file_size": 1000,
                "error_message": "",
                "created_at": "2024-01-03T00:00:00",
                "updated_at": "2024-01-03T00:00:00",
            },
            {
                "id": "2",
                "paper_id": "2301.00002",
                "arxiv_id": "2301.00002",
                "title": "Paper 2",
                "pdf_url": "url2",
                "status": "pending",
                "progress": 0,
                "file_path": "",
                "file_size": 0,
                "error_message": "",
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
            },
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results, total = repo.get_all()
            
            assert total == 2
            assert len(results) == 2

    def test_get_all_empty(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results, total = repo.get_all()
            
            assert total == 0
            assert results == []

    def test_get_all_with_pagination(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": str(i),
                "paper_id": f"2301.0000{i}",
                "arxiv_id": f"2301.0000{i}",
                "title": f"Paper {i}",
                "pdf_url": f"url{i}",
                "status": "completed",
                "progress": 100,
                "file_path": f"/path/{i}.pdf",
                "file_size": 1000 * i,
                "error_message": "",
                "created_at": f"2024-01-0{i}T00:00:00",
                "updated_at": f"2024-01-0{i}T00:00:00",
            }
            for i in range(1, 6)
        ])
        mock_table.to_pandas = Mock(return_value=df)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            results, total = repo.get_all(limit=2, offset=1)
            
            assert total == 5
            assert len(results) == 2


class TestLanceDBDownloadRepositoryExists:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_exists_true(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{"id": "test-id"}])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.exists("test-id")
            
            assert result is True

    def test_exists_false(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.exists("nonexistent")
            
            assert result is False


class TestLanceDBDownloadRepositoryGetByPaperId:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_get_by_paper_id_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": "test-id",
            "paper_id": "2301.12345",
            "arxiv_id": "2301.12345",
            "title": "Test Paper",
            "pdf_url": "url",
            "status": "completed",
            "progress": 100,
            "file_path": "/path.pdf",
            "file_size": 1000,
            "error_message": "",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_by_paper_id("2301.12345")
            
            assert result is not None
            assert result["paper_id"] == "2301.12345"

    def test_get_by_paper_id_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_by_paper_id("nonexistent")
            
            assert result is None


class TestLanceDBDownloadRepositoryGetAllByPaperId:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_get_all_by_paper_id(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.12345",
                "arxiv_id": "2301.12345",
                "title": "Test Paper",
                "pdf_url": "url",
                "status": "completed",
                "progress": 100,
                "file_path": "/path1.pdf",
                "file_size": 1000,
                "error_message": "",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
            {
                "id": "2",
                "paper_id": "2301.12345",
                "arxiv_id": "2301.12345",
                "title": "Test Paper",
                "pdf_url": "url",
                "status": "failed",
                "progress": 50,
                "file_path": "",
                "file_size": 0,
                "error_message": "Error",
                "created_at": "2024-01-02T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
            },
        ])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.get_all_by_paper_id("2301.12345")
            
            assert len(result) == 2


class TestLanceDBDownloadRepositoryUpdateStatus:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_update_status_success(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": "test-task-id",
            "paper_id": "2301.12345",
            "arxiv_id": "2301.12345",
            "title": "Test Paper",
            "pdf_url": "url",
            "status": "pending",
            "progress": 0,
            "file_path": "",
            "file_size": 0,
            "error_message": "",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.update_status(
                "test-task-id",
                status="downloading",
                progress=50,
            )
            
            assert result is True
            mock_table.delete.assert_called_once()
            mock_table.add.assert_called_once()

    def test_update_status_with_file_path(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": "test-task-id",
            "paper_id": "2301.12345",
            "arxiv_id": "2301.12345",
            "title": "Test Paper",
            "pdf_url": "url",
            "status": "downloading",
            "progress": 50,
            "file_path": "",
            "file_size": 0,
            "error_message": "",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.update_status(
                "test-task-id",
                status="completed",
                progress=100,
                file_path="/path/to/file.pdf",
                file_size=1234567,
            )
            
            assert result is True

    def test_update_status_with_error(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([{
            "id": "test-task-id",
            "paper_id": "2301.12345",
            "arxiv_id": "2301.12345",
            "title": "Test Paper",
            "pdf_url": "url",
            "status": "downloading",
            "progress": 50,
            "file_path": "",
            "file_size": 0,
            "error_message": "",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }])
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.update_status(
                "test-task-id",
                status="failed",
                error_message="Network error",
            )
            
            assert result is True

    def test_update_status_task_not_found(self, repo):
        mock_table = Mock()
        df = pd.DataFrame()
        
        mock_search = Mock()
        mock_search.where = Mock(return_value=mock_search)
        mock_search.limit = Mock(return_value=mock_search)
        mock_search.to_pandas = Mock(return_value=df)
        mock_table.search = Mock(return_value=mock_search)
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            result = repo.update_status("nonexistent", status="completed")
            
            assert result is False


class TestLanceDBDownloadRepositoryResetIncompleteTasks:
    @pytest.fixture
    def repo(self):
        return LanceDBDownloadRepository()

    def test_reset_incomplete_tasks(self, repo):
        mock_table = Mock()
        df = pd.DataFrame([
            {
                "id": "1",
                "paper_id": "2301.00001",
                "arxiv_id": "2301.00001",
                "title": "Pending Task",
                "pdf_url": "url1",
                "status": "pending",
                "progress": 0,
                "file_path": "",
                "file_size": 0,
                "error_message": "",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
            {
                "id": "2",
                "paper_id": "2301.00002",
                "arxiv_id": "2301.00002",
                "title": "Downloading Task",
                "pdf_url": "url2",
                "status": "downloading",
                "progress": 50,
                "file_path": "",
                "file_size": 0,
                "error_message": "",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            },
        ])
        
        mock_table_result = Mock()
        mock_table_result.to_pandas.return_value = df
        
        mock_scanner = Mock()
        mock_scanner.to_table.return_value = mock_table_result
        
        mock_lance_ds = Mock()
        mock_lance_ds.scanner.return_value = mock_scanner
        mock_table.to_lance.return_value = mock_lance_ds
        mock_table.delete = Mock()
        mock_table.add = Mock()
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            count = repo.reset_incomplete_tasks()
            
            assert count == 2

    def test_reset_incomplete_tasks_none(self, repo):
        mock_table = Mock()
        df = pd.DataFrame(columns=[
            "id", "paper_id", "arxiv_id", "title", "pdf_url",
            "status", "progress", "file_path", "file_size",
            "error_message", "created_at", "updated_at"
        ])
        
        mock_table_result = Mock()
        mock_table_result.to_pandas.return_value = df
        
        mock_scanner = Mock()
        mock_scanner.to_table.return_value = mock_table_result
        
        mock_lance_ds = Mock()
        mock_lance_ds.scanner.return_value = mock_scanner
        mock_table.to_lance.return_value = mock_lance_ds
        
        with patch.object(repo, '_get_table', return_value=mock_table):
            count = repo.reset_incomplete_tasks()
            
            assert count == 0


class TestLanceDBDownloadRepositorySafeStr:
    def test_safe_str_with_none(self):
        result = LanceDBDownloadRepository._safe_str(None)
        assert result == ""

    def test_safe_str_with_value(self):
        result = LanceDBDownloadRepository._safe_str("test")
        assert result == "test"

    def test_safe_str_with_max_len(self):
        result = LanceDBDownloadRepository._safe_str("test string", max_len=4)
        assert result == "test"
