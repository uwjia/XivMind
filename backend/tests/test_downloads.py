import pytest
import os
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.downloads import router, ws_manager
from app.models import DownloadTaskCreate, DownloadTaskResponse, DownloadStatus


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_download_service():
    with patch('app.routers.downloads.download_service') as mock:
        yield mock


@pytest.fixture
def mock_download_manager():
    with patch('app.routers.downloads.download_manager') as mock:
        mock.is_task_running.return_value = False
        mock.get_running_count.return_value = 0
        mock._running_tasks = {}
        yield mock


@pytest.fixture
def sample_task_data():
    return {
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
    }


@pytest.fixture
def sample_task_response():
    return {
        "id": "test-task-id-123",
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "status": DownloadStatus.PENDING.value,
        "progress": 0,
        "file_path": None,
        "file_size": 0,
        "error_message": None,
        "created_at": "2024-01-03T00:00:00",
        "updated_at": "2024-01-03T00:00:00",
    }


class TestCreateDownloadTask:
    def test_create_task_success(self, client, mock_download_service, mock_download_manager, sample_task_data, sample_task_response):
        mock_download_service.get_all_tasks.return_value = ([], 0)
        mock_download_service.create_task.return_value = sample_task_response
        mock_download_manager.start_download = AsyncMock()
        mock_download_manager.add_progress_callback = Mock()
        
        response = client.post("/downloads", json=sample_task_data)
        
        assert response.status_code == 200
        assert response.json()["paper_id"] == "2301.12345v1"
        assert response.json()["status"] == DownloadStatus.PENDING.value
        mock_download_service.create_task.assert_called_once()

    def test_create_task_missing_required_fields(self, client, mock_download_service):
        incomplete_data = {
            "arxiv_id": "2301.12345",
        }
        
        response = client.post("/downloads", json=incomplete_data)
        
        assert response.status_code == 422

    def test_create_task_returns_existing_pending_task(self, client, mock_download_service, mock_download_manager, sample_task_data, sample_task_response):
        existing_task = sample_task_response.copy()
        existing_task["status"] = DownloadStatus.PENDING.value
        mock_download_service.get_all_tasks.return_value = ([existing_task], 1)
        
        response = client.post("/downloads", json=sample_task_data)
        
        assert response.status_code == 200
        assert response.json()["status"] == DownloadStatus.PENDING.value
        mock_download_service.create_task.assert_not_called()

    def test_create_task_returns_existing_downloading_task(self, client, mock_download_service, mock_download_manager, sample_task_data, sample_task_response):
        existing_task = sample_task_response.copy()
        existing_task["status"] = DownloadStatus.DOWNLOADING.value
        mock_download_service.get_all_tasks.return_value = ([existing_task], 1)
        
        response = client.post("/downloads", json=sample_task_data)
        
        assert response.status_code == 200
        assert response.json()["status"] == DownloadStatus.DOWNLOADING.value
        mock_download_service.create_task.assert_not_called()

    def test_create_task_service_error(self, client, mock_download_service, mock_download_manager, sample_task_data):
        mock_download_service.get_all_tasks.return_value = ([], 0)
        mock_download_service.create_task.side_effect = Exception("Database error")
        
        response = client.post("/downloads", json=sample_task_data)
        
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]


class TestGetDownloadTasks:
    def test_get_tasks_default_params(self, client, mock_download_service, sample_task_response):
        mock_download_service.get_all_tasks.return_value = ([sample_task_response], 1)
        
        response = client.get("/downloads")
        
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert len(response.json()["items"]) == 1
        mock_download_service.get_all_tasks.assert_called_once_with(limit=100, offset=0)

    def test_get_tasks_with_pagination(self, client, mock_download_service, sample_task_response):
        mock_download_service.get_all_tasks.return_value = ([sample_task_response], 10)
        
        response = client.get("/downloads?limit=10&offset=5")
        
        assert response.status_code == 200
        mock_download_service.get_all_tasks.assert_called_once_with(limit=10, offset=5)

    def test_get_tasks_empty_list(self, client, mock_download_service):
        mock_download_service.get_all_tasks.return_value = ([], 0)
        
        response = client.get("/downloads")
        
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    def test_get_tasks_invalid_limit(self, client, mock_download_service):
        response = client.get("/downloads?limit=0")
        assert response.status_code == 422

    def test_get_tasks_invalid_offset(self, client, mock_download_service):
        response = client.get("/downloads?offset=-1")
        assert response.status_code == 422

    def test_get_tasks_limit_exceeds_max(self, client, mock_download_service):
        response = client.get("/downloads?limit=1001")
        assert response.status_code == 422


class TestGetDownloadTask:
    def test_get_task_success(self, client, mock_download_service, sample_task_response):
        mock_download_service.get_task.return_value = sample_task_response
        
        response = client.get("/downloads/test-task-id-123")
        
        assert response.status_code == 200
        assert response.json()["id"] == "test-task-id-123"
        mock_download_service.get_task.assert_called_once_with("test-task-id-123")

    def test_get_task_not_found(self, client, mock_download_service):
        mock_download_service.get_task.return_value = None
        
        response = client.get("/downloads/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_task_service_error(self, client, mock_download_service):
        mock_download_service.get_task.side_effect = Exception("Connection error")
        
        response = client.get("/downloads/test-task-id-123")
        
        assert response.status_code == 500


class TestDeleteDownloadTask:
    def test_delete_task_success(self, client, mock_download_service, mock_download_manager):
        mock_download_service.delete_task.return_value = True
        
        response = client.delete("/downloads/test-task-id-123")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        mock_download_service.delete_task.assert_called_once_with("test-task-id-123")

    def test_delete_running_task(self, client, mock_download_service, mock_download_manager):
        mock_download_manager.is_task_running.return_value = True
        mock_download_manager.cancel_download = AsyncMock(return_value=True)
        mock_download_service.delete_task.return_value = True
        
        response = client.delete("/downloads/test-task-id-123")
        
        assert response.status_code == 200
        mock_download_manager.cancel_download.assert_called_once()

    def test_delete_task_service_error(self, client, mock_download_service, mock_download_manager):
        mock_download_service.delete_task.side_effect = Exception("Database error")
        
        response = client.delete("/downloads/test-task-id-123")
        
        assert response.status_code == 500


class TestRetryDownloadTask:
    def test_retry_task_success(self, client, mock_download_service, mock_download_manager, sample_task_response):
        sample_task_response["status"] = DownloadStatus.FAILED.value
        mock_download_service.get_task.return_value = sample_task_response
        mock_download_manager.retry_download = AsyncMock(return_value=True)
        mock_download_manager.add_progress_callback = Mock()
        
        response = client.post("/downloads/test-task-id-123/retry")
        
        assert response.status_code == 200
        mock_download_manager.retry_download.assert_called_once()

    def test_retry_task_not_found(self, client, mock_download_service):
        mock_download_service.get_task.return_value = None
        
        response = client.post("/downloads/nonexistent-id/retry")
        
        assert response.status_code == 404

    def test_retry_task_failed(self, client, mock_download_service, mock_download_manager, sample_task_response):
        mock_download_service.get_task.return_value = sample_task_response
        mock_download_manager.retry_download = AsyncMock(return_value=False)
        
        response = client.post("/downloads/test-task-id-123/retry")
        
        assert response.status_code == 500


class TestCancelDownloadTask:
    def test_cancel_task_success(self, client, mock_download_service, mock_download_manager, sample_task_response):
        mock_download_manager.cancel_download = AsyncMock(return_value=True)
        mock_download_service.get_task.return_value = sample_task_response
        
        response = client.post("/downloads/test-task-id-123/cancel")
        
        assert response.status_code == 200
        mock_download_manager.cancel_download.assert_called_once()

    def test_cancel_task_not_running(self, client, mock_download_service, mock_download_manager):
        mock_download_manager.cancel_download = AsyncMock(return_value=False)
        
        response = client.post("/downloads/test-task-id-123/cancel")
        
        assert response.status_code == 404


class TestOpenDownloadFile:
    def test_open_file_success(self, client, mock_download_service):
        sample_task = {
            "id": "test-task-id-123",
            "file_path": "/path/to/file.pdf",
        }
        mock_download_service.get_task.return_value = sample_task
        
        with patch('os.path.exists', return_value=True):
            with patch('platform.system', return_value='Windows'):
                with patch('os.startfile') as mock_startfile:
                    response = client.post("/downloads/test-task-id-123/open")
                    
                    assert response.status_code == 200
                    assert "opened successfully" in response.json()["message"]
                    mock_startfile.assert_called_once_with("/path/to/file.pdf")

    def test_open_file_task_not_found(self, client, mock_download_service):
        mock_download_service.get_task.return_value = None
        
        response = client.post("/downloads/nonexistent-id/open")
        
        assert response.status_code == 404

    def test_open_file_no_file_path(self, client, mock_download_service):
        sample_task = {
            "id": "test-task-id-123",
            "file_path": None,
        }
        mock_download_service.get_task.return_value = sample_task
        
        response = client.post("/downloads/test-task-id-123/open")
        
        assert response.status_code == 404
        assert "File path not found" in response.json()["detail"]

    def test_open_file_not_exists(self, client, mock_download_service):
        sample_task = {
            "id": "test-task-id-123",
            "file_path": "/path/to/nonexistent.pdf",
        }
        mock_download_service.get_task.return_value = sample_task
        
        with patch('os.path.exists', return_value=False):
            response = client.post("/downloads/test-task-id-123/open")
            
            assert response.status_code == 404
            assert "does not exist" in response.json()["detail"]

    def test_open_file_on_macos(self, client, mock_download_service):
        sample_task = {
            "id": "test-task-id-123",
            "file_path": "/path/to/file.pdf",
        }
        mock_download_service.get_task.return_value = sample_task
        
        with patch('os.path.exists', return_value=True):
            with patch('platform.system', return_value='Darwin'):
                with patch('subprocess.run') as mock_run:
                    response = client.post("/downloads/test-task-id-123/open")
                    
                    assert response.status_code == 200
                    mock_run.assert_called_once_with(["open", "/path/to/file.pdf"])

    def test_open_file_on_linux(self, client, mock_download_service):
        sample_task = {
            "id": "test-task-id-123",
            "file_path": "/path/to/file.pdf",
        }
        mock_download_service.get_task.return_value = sample_task
        
        with patch('os.path.exists', return_value=True):
            with patch('platform.system', return_value='Linux'):
                with patch('subprocess.run') as mock_run:
                    response = client.post("/downloads/test-task-id-123/open")
                    
                    assert response.status_code == 200
                    mock_run.assert_called_once_with(["xdg-open", "/path/to/file.pdf"])


class TestGetRunningStatus:
    def test_get_running_status_empty(self, client, mock_download_manager):
        mock_download_manager.get_running_count.return_value = 0
        mock_download_manager._running_tasks = {}
        
        response = client.get("/downloads/status/running")
        
        assert response.status_code == 200
        assert response.json()["running_count"] == 0
        assert response.json()["running_tasks"] == []

    def test_get_running_status_with_tasks(self, client, mock_download_manager):
        mock_download_manager.get_running_count.return_value = 2
        mock_task = Mock()
        mock_task.paper_id = "2301.12345"
        mock_download_manager.get_task.return_value = mock_task
        mock_download_manager._running_tasks = {
            "task-1": Mock(),
            "task-2": Mock(),
        }
        
        response = client.get("/downloads/status/running")
        
        assert response.status_code == 200
        assert response.json()["running_count"] == 2


class TestDownloadSorting:
    def test_tasks_sorted_by_created_at_descending(self, client, mock_download_service):
        task1 = {
            "id": "1",
            "paper_id": "2301.00001v1",
            "title": "Old Task",
            "pdf_url": "https://arxiv.org/pdf/2301.00001v1.pdf",
            "status": DownloadStatus.COMPLETED.value,
            "progress": 100,
            "file_path": "/path/1.pdf",
            "file_size": 1000,
            "error_message": None,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        task2 = {
            "id": "2",
            "paper_id": "2301.00002v1",
            "title": "New Task",
            "pdf_url": "https://arxiv.org/pdf/2301.00002v1.pdf",
            "status": DownloadStatus.COMPLETED.value,
            "progress": 100,
            "file_path": "/path/2.pdf",
            "file_size": 2000,
            "error_message": None,
            "created_at": "2024-01-03T00:00:00",
            "updated_at": "2024-01-03T00:00:00",
        }
        task3 = {
            "id": "3",
            "paper_id": "2301.00003v1",
            "title": "Middle Task",
            "pdf_url": "https://arxiv.org/pdf/2301.00003v1.pdf",
            "status": DownloadStatus.COMPLETED.value,
            "progress": 100,
            "file_path": "/path/3.pdf",
            "file_size": 3000,
            "error_message": None,
            "created_at": "2024-01-02T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
        }
        
        mock_download_service.get_all_tasks.return_value = (
            [task2, task3, task1],
            3
        )
        
        response = client.get("/downloads")
        
        assert response.status_code == 200
        items = response.json()["items"]
        assert items[0]["paper_id"] == "2301.00002v1"
        assert items[1]["paper_id"] == "2301.00003v1"
        assert items[2]["paper_id"] == "2301.00001v1"


class TestDownloadStatusValues:
    def test_status_pending(self, client, mock_download_service, sample_task_response):
        sample_task_response["status"] = DownloadStatus.PENDING.value
        mock_download_service.get_task.return_value = sample_task_response
        
        response = client.get("/downloads/test-task-id-123")
        
        assert response.json()["status"] == "pending"

    def test_status_downloading(self, client, mock_download_service, sample_task_response):
        sample_task_response["status"] = DownloadStatus.DOWNLOADING.value
        sample_task_response["progress"] = 50
        mock_download_service.get_task.return_value = sample_task_response
        
        response = client.get("/downloads/test-task-id-123")
        
        assert response.json()["status"] == "downloading"
        assert response.json()["progress"] == 50

    def test_status_completed(self, client, mock_download_service, sample_task_response):
        sample_task_response["status"] = DownloadStatus.COMPLETED.value
        sample_task_response["progress"] = 100
        sample_task_response["file_path"] = "/path/to/file.pdf"
        sample_task_response["file_size"] = 1234567
        mock_download_service.get_task.return_value = sample_task_response
        
        response = client.get("/downloads/test-task-id-123")
        
        assert response.json()["status"] == "completed"
        assert response.json()["progress"] == 100
        assert response.json()["file_path"] == "/path/to/file.pdf"

    def test_status_failed(self, client, mock_download_service, sample_task_response):
        sample_task_response["status"] = DownloadStatus.FAILED.value
        sample_task_response["error_message"] = "Network error"
        mock_download_service.get_task.return_value = sample_task_response
        
        response = client.get("/downloads/test-task-id-123")
        
        assert response.json()["status"] == "failed"
        assert response.json()["error_message"] == "Network error"
