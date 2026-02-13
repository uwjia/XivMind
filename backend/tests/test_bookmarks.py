import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.routers.bookmarks import router
from app.models import BookmarkCreate, BookmarkResponse, BookmarkListResponse, MessageResponse


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def mock_bookmark_service():
    with patch('app.routers.bookmarks.bookmark_service') as mock:
        yield mock


@pytest.fixture
def sample_bookmark_data():
    return {
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "authors": ["Author One", "Author Two"],
        "abstract": "This is a test abstract.",
        "comment": "Test comment",
        "primary_category": "cs.AI",
        "categories": ["cs.AI", "cs.LG"],
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "published": "2024-01-01T00:00:00",
        "updated": "2024-01-02T00:00:00",
    }


@pytest.fixture
def sample_bookmark_response():
    return {
        "id": "test-id-123",
        "paper_id": "2301.12345v1",
        "arxiv_id": "2301.12345",
        "title": "Test Paper Title",
        "authors": ["Author One", "Author Two"],
        "abstract": "This is a test abstract.",
        "comment": "Test comment",
        "primary_category": "cs.AI",
        "categories": ["cs.AI", "cs.LG"],
        "pdf_url": "https://arxiv.org/pdf/2301.12345v1.pdf",
        "abs_url": "https://arxiv.org/abs/2301.12345",
        "published": "2024-01-01T00:00:00",
        "updated": "2024-01-02T00:00:00",
        "created_at": "2024-01-03T00:00:00",
    }


class TestAddBookmark:
    def test_add_bookmark_success(self, client, mock_bookmark_service, sample_bookmark_data, sample_bookmark_response):
        mock_bookmark_service.add_bookmark.return_value = sample_bookmark_response
        
        response = client.post("/bookmarks", json=sample_bookmark_data)
        
        assert response.status_code == 200
        assert response.json()["paper_id"] == "2301.12345v1"
        assert response.json()["title"] == "Test Paper Title"
        mock_bookmark_service.add_bookmark.assert_called_once()

    def test_add_bookmark_missing_required_fields(self, client, mock_bookmark_service):
        incomplete_data = {
            "arxiv_id": "2301.12345",
        }
        
        response = client.post("/bookmarks", json=incomplete_data)
        
        assert response.status_code == 422

    def test_add_bookmark_service_error(self, client, mock_bookmark_service, sample_bookmark_data):
        mock_bookmark_service.add_bookmark.side_effect = Exception("Database error")
        
        response = client.post("/bookmarks", json=sample_bookmark_data)
        
        assert response.status_code == 500
        assert "Database error" in response.json()["detail"]


class TestRemoveBookmark:
    def test_remove_bookmark_success(self, client, mock_bookmark_service):
        mock_bookmark_service.remove_bookmark.return_value = True
        
        response = client.delete("/bookmarks/2301.12345v1")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Bookmark removed successfully"
        mock_bookmark_service.remove_bookmark.assert_called_once_with("2301.12345v1")

    def test_remove_bookmark_service_error(self, client, mock_bookmark_service):
        mock_bookmark_service.remove_bookmark.side_effect = Exception("Not found")
        
        response = client.delete("/bookmarks/2301.12345v1")
        
        assert response.status_code == 500


class TestCheckBookmark:
    def test_check_bookmark_exists(self, client, mock_bookmark_service):
        mock_bookmark_service.is_bookmarked.return_value = True
        
        response = client.get("/bookmarks/check/2301.12345v1")
        
        assert response.status_code == 200
        assert response.json()["is_bookmarked"] is True
        assert response.json()["paper_id"] == "2301.12345v1"

    def test_check_bookmark_not_exists(self, client, mock_bookmark_service):
        mock_bookmark_service.is_bookmarked.return_value = False
        
        response = client.get("/bookmarks/check/2301.12345v1")
        
        assert response.status_code == 200
        assert response.json()["is_bookmarked"] is False

    def test_check_bookmark_service_error(self, client, mock_bookmark_service):
        mock_bookmark_service.is_bookmarked.side_effect = Exception("Connection error")
        
        response = client.get("/bookmarks/check/2301.12345v1")
        
        assert response.status_code == 500


class TestGetBookmarks:
    def test_get_bookmarks_default_params(self, client, mock_bookmark_service, sample_bookmark_response):
        mock_bookmark_service.get_all_bookmarks.return_value = ([sample_bookmark_response], 1)
        
        response = client.get("/bookmarks")
        
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert len(response.json()["items"]) == 1
        mock_bookmark_service.get_all_bookmarks.assert_called_once_with(limit=100, offset=0)

    def test_get_bookmarks_with_pagination(self, client, mock_bookmark_service, sample_bookmark_response):
        mock_bookmark_service.get_all_bookmarks.return_value = ([sample_bookmark_response], 10)
        
        response = client.get("/bookmarks?limit=10&offset=5")
        
        assert response.status_code == 200
        mock_bookmark_service.get_all_bookmarks.assert_called_once_with(limit=10, offset=5)

    def test_get_bookmarks_empty_list(self, client, mock_bookmark_service):
        mock_bookmark_service.get_all_bookmarks.return_value = ([], 0)
        
        response = client.get("/bookmarks")
        
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    def test_get_bookmarks_invalid_limit(self, client, mock_bookmark_service):
        response = client.get("/bookmarks?limit=0")
        assert response.status_code == 422

    def test_get_bookmarks_invalid_offset(self, client, mock_bookmark_service):
        response = client.get("/bookmarks?offset=-1")
        assert response.status_code == 422

    def test_get_bookmarks_limit_exceeds_max(self, client, mock_bookmark_service):
        response = client.get("/bookmarks?limit=1001")
        assert response.status_code == 422


class TestSearchBookmarks:
    def test_search_bookmarks_success(self, client, mock_bookmark_service, sample_bookmark_response):
        mock_bookmark_service.search_bookmarks.return_value = [sample_bookmark_response]
        
        response = client.get("/bookmarks/search?query=test")
        
        assert response.status_code == 200
        assert response.json()["total"] == 1
        assert len(response.json()["items"]) == 1
        mock_bookmark_service.search_bookmarks.assert_called_once_with(query="test", limit=10)

    def test_search_bookmarks_with_limit(self, client, mock_bookmark_service, sample_bookmark_response):
        mock_bookmark_service.search_bookmarks.return_value = [sample_bookmark_response]
        
        response = client.get("/bookmarks/search?query=test&limit=5")
        
        assert response.status_code == 200
        mock_bookmark_service.search_bookmarks.assert_called_once_with(query="test", limit=5)

    def test_search_bookmarks_no_results(self, client, mock_bookmark_service):
        mock_bookmark_service.search_bookmarks.return_value = []
        
        response = client.get("/bookmarks/search?query=nonexistent")
        
        assert response.status_code == 200
        assert response.json()["total"] == 0
        assert response.json()["items"] == []

    def test_search_bookmarks_missing_query(self, client, mock_bookmark_service):
        response = client.get("/bookmarks/search")
        assert response.status_code == 422

    def test_search_bookmarks_empty_query(self, client, mock_bookmark_service):
        response = client.get("/bookmarks/search?query=")
        assert response.status_code == 422

    def test_search_bookmarks_invalid_limit(self, client, mock_bookmark_service):
        response = client.get("/bookmarks/search?query=test&limit=0")
        assert response.status_code == 422

    def test_search_bookmarks_limit_exceeds_max(self, client, mock_bookmark_service):
        response = client.get("/bookmarks/search?query=test&limit=101")
        assert response.status_code == 422


class TestBookmarkSorting:
    def test_bookmarks_sorted_by_created_at_descending(self, client, mock_bookmark_service):
        bookmark1 = {
            "id": "1",
            "paper_id": "2301.00001v1",
            "title": "Old Paper",
            "created_at": "2024-01-01T00:00:00",
        }
        bookmark2 = {
            "id": "2",
            "paper_id": "2301.00002v1",
            "title": "New Paper",
            "created_at": "2024-01-03T00:00:00",
        }
        bookmark3 = {
            "id": "3",
            "paper_id": "2301.00003v1",
            "title": "Middle Paper",
            "created_at": "2024-01-02T00:00:00",
        }
        
        mock_bookmark_service.get_all_bookmarks.return_value = (
            [bookmark2, bookmark3, bookmark1],
            3
        )
        
        response = client.get("/bookmarks")
        
        assert response.status_code == 200
        items = response.json()["items"]
        assert items[0]["paper_id"] == "2301.00002v1"
        assert items[1]["paper_id"] == "2301.00003v1"
        assert items[2]["paper_id"] == "2301.00001v1"
